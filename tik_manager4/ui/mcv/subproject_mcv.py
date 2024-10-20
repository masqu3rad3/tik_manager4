from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
import tik_manager4.ui.dialog.subproject_dialog
import tik_manager4.ui.dialog.task_dialog
from tik_manager4.ui.widgets.common import VerticalSeparator, TikIconButton
from tik_manager4.ui.dialog.feedback import Feedback
import tik_manager4
from tik_manager4.ui import pick


class TikSubItem(QtGui.QStandardItem):
    def __init__(self, sub_obj):
        super(TikSubItem, self).__init__()

        self.subproject = sub_obj

        # test
        icon_name = self.subproject.metadata.get_value("mode", fallback_value="global")
        icon = pick.icon("{}.png".format(icon_name))
        self.setIcon(icon)
        #
        fnt = QtGui.QFont("Open Sans", 12)
        fnt.setBold(False)
        self.setEditable(False)
        self.setForeground(QtGui.QColor(255, 255, 255))
        self.setFont(fnt)
        self.setText(sub_obj.name)


class TikColumnItem(QtGui.QStandardItem):
    def __init__(self, name, overridden=False):
        super(TikColumnItem, self).__init__()

        self.setEditable(False)
        self.setText(name)
        self.set_overridden(overridden)

    def set_value(self, value):
        self.setText(str(value))

    def set_overridden(self, value):
        if value:
            self.tag_overridden()
        else:
            self.tag_normal()

    def tag_overridden(self):
        fnt = QtGui.QFont("Open Sans", 10)
        fnt.setBold(False)
        # make it yellow
        self.setForeground(QtGui.QColor(255, 255, 0))
        self.setFont(fnt)

    def tag_normal(self):
        fnt = QtGui.QFont("Open Sans", 10)
        fnt.setBold(False)
        self.setFont(fnt)


class TikSubModel(QtGui.QStandardItemModel):
    def __init__(self, structure_object):
        super(TikSubModel, self).__init__()
        self.columns = ["name", "id", "path"] + list(
            structure_object.metadata_definitions.properties.keys()
        )
        self.setHorizontalHeaderLabels(self.columns)

        self.project = None
        self.root_item = None
        self.set_data(structure_object)

    def set_data(self, structure_object):
        self.project = structure_object

    def populate(self):
        self.setRowCount(0)
        visited = []
        queue = []

        # start with the initial dictionary with self subproject
        all_data = {
            "id": self.project.id,
            "name": self.project.name,
            "path": self.project.path,
            "tasks": self.project.tasks,
            "subs": [],  # this will be filled with the while loop
        }

        # add the initial dictionary and self into the queue
        # Each queue item is a list.
        # first element is the dictionary point and second is the subproject object
        parent_row = self
        self.root_item = TikSubItem(self.project)
        # make the self.root_item invisible
        self.root_item.setForeground(QtGui.QColor(0, 0, 0, 0))
        self.root_item.setText("Project Root")
        parent_row.appendRow(self.root_item)
        queue.append([all_data, self.project, self.root_item])

        while queue:
            current = queue.pop(0)
            parent = current[0]
            sub = current[1]
            parent_row = current[2]

            for neighbour in list(sub.subs.values()):
                if neighbour not in visited:
                    sub_data = {
                        "id": neighbour.id,
                        "name": neighbour.name,
                        "path": neighbour.path,
                        "tasks": neighbour.tasks,
                        "subs": [],  # this will be filled with the while loop
                    }
                    parent["subs"].append(sub_data)
                    _item = self.append_sub(neighbour, parent_row)

                    # add tasks
                    visited.append(neighbour)
                    queue.append([sub_data, neighbour, _item])

        return all_data

    def append_sub(self, sub_obj, parent):
        _sub_item = TikSubItem(sub_obj)
        # generate the column texts
        # name, id and path are mandatory, start with them
        _row = [_sub_item, TikColumnItem(str(sub_obj.id)), TikColumnItem(sub_obj.path)]
        for column in self.columns[3:]:  # skip the first 3 columns which are mandatory
            # get the override status
            _column_value = sub_obj.metadata.get_value(column, "")
            _overridden = sub_obj.metadata.is_overridden(column)
            _column_item = TikColumnItem(str(_column_value), _overridden)
            _row.append(_column_item)

        parent.appendRow(_row)
        return _sub_item

    def update_item(self, item, sub_obj):
        """Update the item with the new subproject object"""
        item.subproject = sub_obj
        item.setText(sub_obj.name)

        # get the parent item
        _parent = item.parent()

        # get the row of the item
        _row = item.row()

        for index, column in enumerate(self.columns):
            if _parent:
                _column_item = _parent.child(_row, index)
            else:
                _column_item = self.item(_row, index)
            if isinstance(_column_item, TikColumnItem):
                _column_value = sub_obj.metadata.get_value(column, "")
                _overridden = sub_obj.metadata.is_overridden(column)
                _column_item.set_overridden(_overridden)
                _column_item.set_value(str(_column_value))

    def find_item_by_id_column(self, unique_id):
        """Search entire tree and find the matching item."""

        # get EVERY item in this model
        _all_items = self.findItems(
            "*", QtCore.Qt.MatchWildcard | QtCore.Qt.MatchRecursive
        )
        for x in _all_items:
            if isinstance(x, TikSubItem):
                if x.subproject.id == unique_id:
                    return x


class TikSubView(QtWidgets.QTreeView):
    item_selected = QtCore.Signal(object)
    add_item = QtCore.Signal(object)

    def __init__(self, project_obj=None, right_click_enabled=True):
        super(TikSubView, self).__init__()
        self._recursive_task_scan = False
        self._feedback = Feedback(parent=self)
        self.setUniformRowHeights(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.model = None
        self.proxy_model = None
        if project_obj:
            self.set_project(project_obj)

        # SIGNALS

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        if right_click_enabled:
            self.customContextMenuRequested.connect(self.right_click_menu)

        # create another context menu for columns
        self.header().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.header().customContextMenuRequested.connect(self.header_right_click_menu)

        self.setItemsExpandable(True)

        # show the root
        self.setRootIsDecorated(False)

        # allow multiple selection but only with ctrl
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Control:
            self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key_Control:
            self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        else:
            super().keyReleaseEvent(event)

    # override the right click Event
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        else:
            super().mouseReleaseEvent(event)

    def expand_first_item(self):
        """Try to expand the first item in the tree"""
        index = self.proxy_model.mapFromSource(self.model.index(0, 0))
        self.expand(index)

    def select_first_item(self):
        """Select the first item in the tree"""
        index = self.proxy_model.mapFromSource(self.model.index(0, 0))
        self.setCurrentIndex(index)

    def find_items_in_tree(self, root_item, text):
        matched_items = []

        # Search for items in the root item
        matched_items += root_item.findItems(text, QtCore.Qt.MatchExactly, column=1)

        # Recursively search for items in each child item
        for child_item in root_item.childItems():
            matched_items += self.find_items_in_tree(child_item, text)

        return matched_items

    def get_items_count(self):
        """Return the number of items in the tree under selected one"""

        # count all items
        _all_items = self.model.findItems(
            "*", QtCore.Qt.MatchWildcard | QtCore.Qt.MatchRecursive
        )
        return len(_all_items)

    def select_by_id(self, unique_id):
        """Look at the id column and select
        the subproject item that matched the unique id."""

        match_item = self.model.find_item_by_id_column(unique_id)
        if match_item:
            idx = match_item.index()
            idx = idx.sibling(idx.row(), 0)
            index = self.proxy_model.mapFromSource(idx)
            self.setCurrentIndex(index)
            return True

        return False

    def selectionChanged(self, *args, **kwargs):
        super(TikSubView, self).selectionChanged(*args, **kwargs)
        self.get_tasks()

    def get_selected_items(self):
        """Return the current item."""
        selected_items = []
        # get selected indexes
        selected_indexes = self.selectedIndexes()
        # idx = self.currentIndex()
        for idx in selected_indexes:
            if not idx.isValid():
                return None
            idx = idx.sibling(idx.row(), 0)

            # the id needs to mapped from proxy to source
            index = self.proxy_model.mapToSource(idx)
            _item = self.model.itemFromIndex(index)
            if _item not in selected_items:
                selected_items.append(_item)
        return selected_items

    def set_recursive_task_scan(self, value):
        self._recursive_task_scan = value
        # refresh the view
        self.get_tasks()

    def _save_expanded_state(self, index, expanded_state):
        """Stores the subproject ids of the expanded items"""
        view_index = self.proxy_model.mapFromSource(index)
        if self.isExpanded(view_index):
            # get the item from index
            _item = self.model.itemFromIndex(index)
            expanded_state.append(_item.subproject.id)

        for row in range(self.model.rowCount(index)):
            child_index = self.model.index(row, 0, index)
            self._save_expanded_state(child_index, expanded_state)

    def _restore_expanded_state(self, index, expanded_state):
        """Restores the expanded state of the items by matching the subproject ids"""
        view_index = self.proxy_model.mapFromSource(index)
        _item = self.model.itemFromIndex(index)
        if _item:
            if _item.subproject.id in expanded_state:
                self.expand(view_index)

        for row in range(self.model.rowCount(index)):
            child_index = self.model.index(row, 0, index)
            self._restore_expanded_state(child_index, expanded_state)

    def get_expanded_state(self):
        """Returns the subproject ids of the expanded items"""
        expanded_state = []
        self._save_expanded_state(QtCore.QModelIndex(), expanded_state)
        return expanded_state

    def set_expanded_state(self, expanded_state):
        """Sets the expanded state of the items by matching the subproject ids"""
        self._restore_expanded_state(QtCore.QModelIndex(), expanded_state)

    def refresh(self):
        """Re-populates the model keeping the expanded state"""
        # store the expanded items
        expanded_state = self.get_expanded_state()
        self.model.populate()
        self.set_expanded_state(expanded_state)
        self.clearSelection()
        self.select_first_item()

    def expandAll(self):
        super(TikSubView, self).expandAll()
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)
        self.resizeColumnToContents(2)
        self.resizeColumnToContents(3)
        self.resizeColumnToContents(4)

    @staticmethod
    def collect_tasks(sub_items, recursive=True):
        if not isinstance(sub_items, list):
            sub_items = [sub_items]
        for sub_item in sub_items:
            if not isinstance(sub_item, tik_manager4.objects.subproject.Subproject):
                # just to prevent crashes if something goes wrong
                return
            for key, value in sub_item.scan_tasks().items():
                yield value

            if recursive:
                queue = list(sub_item.subs.values())
                while queue:
                    sub = queue.pop(0)
                    for key, value in sub.scan_tasks().items():
                        yield value
                    queue.extend(list(sub.subs.values()))

    def get_tasks(self, idx=None):
        """Returns the tasks of the selected subproject"""

        selected_indexes = self.selectedIndexes()

        if not selected_indexes:
            return
        sub_project_objects = []
        for idx in selected_indexes:
            # Make sure the idx is pointing to the first column
            first_idx = idx.sibling(idx.row(), 0)
            # The id needs to be mapped from proxy to source
            index = self.proxy_model.mapToSource(first_idx)
            _item = self.model.itemFromIndex(index) or self.model.root_item
            if _item:
                sub_project_objects.append(_item.subproject)
        _tasks = self.collect_tasks(
            sub_project_objects, recursive=self._recursive_task_scan
        )
        self.item_selected.emit(_tasks)

    def hide_columns(self, columns):
        """If the given column exists in the model, hides it"""
        if not isinstance(columns, list):
            columns = [columns]

        for column in columns:
            if column in self.model.columns:
                self.setColumnHidden(self.model.columns.index(column), True)

    def unhide_columns(self, columns):
        """If the given column exists in the model, unhides it"""
        if not isinstance(columns, list):
            columns = [columns]

        for column in columns:
            if column in self.model.columns:
                self.setColumnHidden(self.model.columns.index(column), False)

    def toggle_column(self, column, state):
        """Hide/unhide the given column."""
        if state:
            self.unhide_columns(column)
        else:
            self.hide_columns(column)

    def hide_all_columns(self):
        """Hides all columns."""
        for column in self.model.columns:
            self.hide_columns(column)

    def show_columns(self, list_of_columns):
        """Shows the given columns."""
        for column in list_of_columns:
            self.unhide_columns(column)

    def get_visible_columns(self):
        """Returns the visible columns."""
        return [
            self.model.columns[x]
            for x in range(self.model.columnCount())
            if not self.isColumnHidden(x)
        ]

    def get_column_sizes(self):
        """Return all column sizes in a dictionary."""
        return {x: int(self.columnWidth(x)) for x in range(self.model.columnCount())}

    def set_column_sizes(self, column_sizes):
        """Set the column sizes from the given dictionary."""
        for column, size in column_sizes.items():
            self.setColumnWidth(int(column), size)

    def set_project(self, project_obj):
        self.model = TikSubModel(project_obj)

        self.proxy_model = ProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setRecursiveFilteringEnabled(True)
        self.setSortingEnabled(True)
        # set sort indicator to ascending
        self.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.setModel(self.proxy_model)
        self.model.populate()

    def filter(self, text):
        # pass
        self.proxy_model.setFilterRegExp(
            QtCore.QRegExp(text, QtCore.Qt.CaseInsensitive, QtCore.QRegExp.RegExp)
        )

    def header_right_click_menu(self, position):
        """Creates a right click menu for the header"""

        menu = QtWidgets.QMenu(self)

        # add checkable actions for each column
        for column in self.model.columns:
            action = QtWidgets.QAction(column, self)
            action.setCheckable(True)
            action.setChecked(not self.isColumnHidden(self.model.columns.index(column)))
            # connect the action to the column's visibility
            action.toggled.connect(lambda state, c=column: self.toggle_column(c, state))
            menu.addAction(action)
        # add a separator
        menu.addSeparator()
        # add a ALL item to select all columns
        all_action = QtWidgets.QAction("All", self)
        menu.addAction(all_action)
        all_action.triggered.connect(lambda: self.show_columns(self.model.columns))
        # add a NONE item to select no columns
        none_action = QtWidgets.QAction("None", self)
        menu.addAction(none_action)
        none_action.triggered.connect(lambda: self.hide_all_columns())
        menu.exec_(self.mapToGlobal(position))

    def right_click_menu(self, position):
        indexes = self.sender().selectedIndexes()
        index_under_pointer = self.indexAt(position)
        if not index_under_pointer.isValid():
            # If nothing is selected, that means we are referring to the root item
            item = self.model.root_item
        else:
            # make sure the idx is pointing to the first column
            index_under_pointer = index_under_pointer.sibling(
                index_under_pointer.row(), 0
            )
            mapped_index = self.proxy_model.mapToSource(index_under_pointer)
            item = self.model.itemFromIndex(mapped_index)
        if len(indexes) > 0:
            level = 0
            index = indexes[0]
            while index.parent().isValid():
                index = index.parent()
                level += 1
        else:
            level = 0
        right_click_menu = QtWidgets.QMenu(self)
        act_new_sub = right_click_menu.addAction(self.tr("New Sub-Project"))
        act_new_sub.triggered.connect(lambda _=None, x=item: self.new_sub_project(item))
        act_edit_sub = right_click_menu.addAction(self.tr("Edit Sub-Project"))
        act_edit_sub.triggered.connect(
            lambda _=None, x=item: self.edit_sub_project(item)
        )
        act_delete_sub = right_click_menu.addAction(self.tr("Delete Sub-Project(s)"))
        act_delete_sub.triggered.connect(
            lambda _=None, x=item: self.delete_sub_project(item)
        )

        right_click_menu.addSeparator()

        act_new_task = right_click_menu.addAction(self.tr("New Task"))
        act_new_task.triggered.connect(self.new_task)

        right_click_menu.addSeparator()

        act_open_project_folder = right_click_menu.addAction(
            self.tr("Open Project Folder In Explorer")
        )
        act_open_database_folder = right_click_menu.addAction(
            self.tr("Open Database Folder In Explorer")
        )
        act_open_project_folder.triggered.connect(
            lambda _=None, x=item: item.subproject.show_project_folder()
        )
        act_open_database_folder.triggered.connect(
            lambda _=None, x=item: item.subproject.show_database_folder()
        )

        right_click_menu.exec_(self.sender().viewport().mapToGlobal(position))

    def new_sub_project(self, item):
        # first check for the user permission:
        if self.model.project.check_permissions(level=2) == -1:
            message, title = self.model.project.log.get_last_message()
            self._feedback.pop_info(title.capitalize(), message)
            return
        _dialog = tik_manager4.ui.dialog.subproject_dialog.NewSubprojectDialog(
            self.model.project, parent_sub=item.subproject, parent=self
        )
        state = _dialog.exec_()
        if state:
            # TODO: is this overcomplicated?
            _new_sub = _dialog.get_created_subproject()
            # Find the parent item _new_sub id
            _items = self.model.findItems(
                str(_new_sub.parent.id), QtCore.Qt.MatchRecursive, 1
            )
            if _items:
                _item_at_id_column = _items[0]
                # find the index of the item
                _index = self.model.indexFromItem(_item_at_id_column)
                # make sure the index is pointing to the first column
                first_column_index = _index.sibling(_index.row(), 0)
                # get the item from index
                _item = self.model.itemFromIndex(first_column_index)
                # The reason we are doing this is that we may change
                # the parent of the item on new subproject UI
            else:
                _item = self.model.root_item
            self.model.append_sub(_new_sub, _item)

    def edit_sub_project(self, item):
        # first check for the user permission:
        if self.model.project.check_permissions(level=2) == -1:
            message, title = self.model.project.log.get_last_message()
            self._feedback.pop_info(title.capitalize(), message)
            return
        _dialog = tik_manager4.ui.dialog.subproject_dialog.EditSubprojectDialog(
            self.model.project, parent_sub=item.subproject, parent=self
        )
        state = _dialog.exec_()
        if state:
            # re-populate the model
            self.refresh()

    def new_task(self):
        # get the selected items
        selected_items = self.get_selected_items()
        sub_projects = [x.subproject for x in selected_items]

        # first check for the user permission:
        if self.model.project.check_permissions(level=2) == -1:
            message, title = self.model.project.log.get_last_message()
            self._feedback.pop_info(title.capitalize(), message)
            return
        _dialog = tik_manager4.ui.dialog.task_dialog.NewTask(
            self.model.project, parent_sub=sub_projects, parent=self
        )
        state = _dialog.exec_()
        if state:
            # emit clicked signal
            self.add_item.emit(_dialog.get_created_task())

    def delete_sub_project(self, item):
        # Prompt the user to confirm the deletion
        if self.model.project.check_permissions(level=3) == -1:
            message, title = self.model.project.log.get_last_message()
            self._feedback.pop_info(title.capitalize(), message)
            return

        message = "Are you sure you want to delete the sub-project: {}?".format(
            item.subproject.name
        )
        title = "Delete Sub-Project"
        sure = self._feedback.pop_question(title, message, buttons=["ok", "cancel"])
        if sure == "ok":
            # double check if the sub-project is not empty
            if not item.subproject.is_subproject_empty(item.subproject):
                message = (
                    "The sub-project is not empty.\n\n"
                    "ALL TASKS AND SUB-PROJECTS WILL BE DELETED!\n\nARE YOU "
                    "SURE YOU WANT TO CONTINUE? "
                )
                title = "NON EMPTY SUB-PROJECT"
                really_sure = self._feedback.pop_question(
                    title, message, buttons=["ok", "cancel"]
                )
                if really_sure != "ok":
                    return
            state = self.model.project.delete_sub_project(uid=item.subproject.id)
            if state != -1:
                _parent = item.parent()
                _index = _parent.index() if _parent else QtCore.QModelIndex()
                self.model.removeRow(item.row(), _index)

                # after removing the row, find the current selected one
                # and emit the clicked signal
                self.get_tasks()

            else:
                message, title = self.model.project.log.get_last_message()
                self._feedback.pop_info(title.capitalize(), message)
        else:
            return


class ProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(ProxyModel, self).__init__(parent)
        pass

    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        index = model.index(source_row, 0, QtCore.QModelIndex())

        item = model.itemFromIndex(index)
        if isinstance(item, TikSubItem):
            pass

        return super(ProxyModel, self).filterAcceptsRow(source_row, source_parent)


class TikSubProjectLayout(QtWidgets.QVBoxLayout):
    def __init__(self, project_obj, recursive_enabled=True, right_click_enabled=True):
        super(TikSubProjectLayout, self).__init__()
        self.project_obj = project_obj
        # add a label
        header_lay = QtWidgets.QHBoxLayout()
        header_lay.setContentsMargins(0, 0, 0, 0)
        self.addLayout(header_lay)
        self.label = QtWidgets.QLabel("Sub-Projects")
        self.label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_lay.addWidget(self.label)
        header_lay.addStretch()
        # add a refresh button
        self.refresh_btn = TikIconButton(
            icon_name="refresh", circle=True, size=18, icon_size=14
        )
        header_lay.addWidget(self.refresh_btn)
        self.addWidget(VerticalSeparator(color=(221, 160, 221)))

        # add a checkbox for recursive search
        if recursive_enabled:
            self.recursive_search_cb = QtWidgets.QCheckBox("Get Tasks Recursively")
            self.recursive_search_cb.setChecked(False)
            self.addWidget(self.recursive_search_cb)
        # add a search bar

        self.sub_view = TikSubView(project_obj, right_click_enabled=right_click_enabled)
        self.addWidget(self.sub_view)
        self.filter_le = QtWidgets.QLineEdit()
        self.addWidget(self.filter_le)
        self.filter_le.textChanged.connect(self.sub_view.filter)
        self.filter_le.setPlaceholderText("Filter")
        self.filter_le.setClearButtonEnabled(True)
        self.filter_le.setFocus()

        if recursive_enabled:
            self.sub_view.set_recursive_task_scan(self.recursive_search_cb.isChecked())
            self.recursive_search_cb.stateChanged.connect(
                self.sub_view.set_recursive_task_scan
            )
        self.filter_le.returnPressed.connect(self.sub_view.setFocus)

        # Hide all columns except the first one
        for idx in range(1, self.sub_view.header().count()):
            self.sub_view.hideColumn(idx)

        self.refresh_btn.clicked.connect(self.manual_refresh)

    def manual_refresh(self):
        """Refresh the layout and the view"""
        self.project_obj.structure.reload()
        self.project_obj._set(self.project_obj._absolute_path)
        self.refresh()

    def refresh(self):
        """Refresh the layout"""
        self.sub_view.refresh()

    def get_active_subproject(self):
        """Get the selected item and return the subproject object"""
        selected_items = self.sub_view.get_selected_items()
        if selected_items:
            return selected_items[0].subproject
        return None
