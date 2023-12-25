from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
from tik_manager4.core import filelog
from tik_manager4.ui.dialog.feedback import Feedback
import tik_manager4.ui.dialog.task_dialog
from tik_manager4.ui.widgets.common import VerticalSeparator

from tik_manager4.ui import pick

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")


class TikTaskItem(QtGui.QStandardItem):
    color_dict = {
        "asset": (0, 187, 184),
        "shot": (0, 115, 255),
        "global": (255, 141, 28),
        "other": (255, 255, 255),
    }

    def __init__(self, task_obj):
        """
        Initialize the item with the given task object.
        Args:
            task_obj (tik_manager4.objects.task.Task): Task object
        """
        super(TikTaskItem, self).__init__()

        # # test
        _icon = pick.icon("{}.png".format(task_obj.type))
        self.setIcon(_icon)

        self.task = task_obj
        #
        fnt = QtGui.QFont("Open Sans", 12)
        fnt.setBold(True)
        self.setEditable(False)

        _color = self.color_dict.get(task_obj.type, (255, 255, 255))
        self.setForeground(QtGui.QColor(*_color))

        self.setFont(fnt)
        self.setText(task_obj.name)


class TikTaskModel(QtGui.QStandardItemModel):
    columns = ["name", "id", "path"]
    filter_key = "super"

    def __init__(self):
        """Initialize the model"""
        super(TikTaskModel, self).__init__()

        self.setHorizontalHeaderLabels(self.columns)

        self._tasks = []

    def clear(self):
        """Clear the model"""
        self.setRowCount(0)

    def append_task(self, sub_data):
        """Append a task to the model"""
        # self._tasks.append(sub_data)
        _sub_item = TikTaskItem(sub_data)
        # pid = QtGui.QStandardItem(str(sub_data.reference_id))
        pid = QtGui.QStandardItem(str(sub_data.id))
        path = QtGui.QStandardItem(sub_data.path)

        self.appendRow(
            [
                _sub_item,
                pid,
                path,
            ]
        )
        return _sub_item

    def find_item_by_id_column(self, unique_id):
        """Search entire tree and find the matching item."""
        # get EVERY item in this model
        _all_items = self.findItems(
            "*", QtCore.Qt.MatchWildcard | QtCore.Qt.MatchRecursive
        )
        for x in _all_items:
            if isinstance(x, TikTaskItem):
                if x.task.id == unique_id:
                    return x


class TikTaskView(QtWidgets.QTreeView):
    item_selected = QtCore.Signal(object)

    def __init__(self):
        """Initialize the view"""
        super(TikTaskView, self).__init__()
        self._feedback = Feedback(parent=self)
        self.setUniformRowHeights(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        # do not show branches
        self.setRootIsDecorated(False)

        self.model = TikTaskModel()
        self.proxy_model = QtCore.QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setRecursiveFilteringEnabled(True)
        self.setSortingEnabled(True)
        # sort it alphabetically
        self.sortByColumn(0, QtCore.Qt.AscendingOrder)

        self.setModel(self.proxy_model)

        # SIGNALS

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.right_click_menu)

        # create another context menu for columns
        self.header().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.header().customContextMenuRequested.connect(self.header_right_click_menu)

        self.expandAll()

    def currentChanged(self, *args, **kwargs):
        super(TikTaskView, self).currentChanged(*args, **kwargs)
        self.item_clicked(self.currentIndex())

    def item_clicked(self, idx):
        """Emit the item_selected signal when an item is clicked"""
        # make sure the index is pointing to the first column
        idx = idx.sibling(idx.row(), 0)

        # the id needs to mapped from proxy to source
        index = self.proxy_model.mapToSource(idx)
        _item = self.model.itemFromIndex(index)
        if _item:
            self.item_selected.emit(_item.task)
        else:
            self.item_selected.emit(None)

    def expandAll(self):
        """Expand all the items in the view"""
        super(TikTaskView, self).expandAll()
        self.resizeColumnToContents(0)

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
        """If the given column exists in the model, unhides it"""
        if state:
            self.unhide_columns(column)
        else:
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

    def select_first_item(self):
        """Select the first item in the view."""
        idx = self.proxy_model.index(0, 0)
        self.setCurrentIndex(idx)

    def get_items_count(self):
        """Return the number of items in the view."""
        return self.proxy_model.rowCount()

    def select_by_id(self, unique_id):
        """Select the item with the given id"""
        # get the index of the item
        match_item = self.model.find_item_by_id_column(unique_id)
        if match_item:
            idx = match_item.index()
            idx = idx.sibling(idx.row(), 0)
            index = self.proxy_model.mapFromSource(idx)
            self.setCurrentIndex(index)
            return True
        return False

    def set_tasks(self, tasks_gen):
        """Set the data for the model"""
        self.model.clear()
        for task in tasks_gen:
            # if the task is already in model, skip it
            if self.model.find_item_by_id_column(task.id):
                continue

            self.model.append_task(task)
        self.expandAll()

    def get_selected_item(self):
        """Return the selected item"""
        idx = self.currentIndex()
        if not idx.isValid():
            return None
        idx = idx.sibling(idx.row(), 0)
        # the id needs to mapped from proxy to source
        index = self.proxy_model.mapToSource(idx)
        _item = self.model.itemFromIndex(index)
        return _item

    def add_tasks(self, tasks):
        """Add a task to the model"""
        _ = [self.model.append_task(x) for x in tasks]
        self.expandAll()

    def filter(self, text):
        """Filter the model"""
        self.proxy_model.setFilterRegExp(
            QtCore.QRegExp(text, QtCore.Qt.CaseInsensitive, QtCore.QRegExp.RegExp)
        )

    def header_right_click_menu(self, position):
        menu = QtWidgets.QMenu(self)

        # add checkable actions for each column
        for column in self.model.columns:
            action = QtWidgets.QAction(column, self)
            action.setCheckable(True)
            action.setChecked(not self.isColumnHidden(self.model.columns.index(column)))
            # connect the action to the column's visibility
            action.toggled.connect(lambda state, c=column: self.toggle_column(c, state))

            menu.addAction(action)

        menu.exec_(self.mapToGlobal(position))

    def right_click_menu(self, position):
        indexes = self.sender().selectedIndexes()
        index_under_pointer = self.indexAt(position)
        right_click_menu = QtWidgets.QMenu(self)
        if not index_under_pointer.isValid():
            return
        # make sure the idx is pointing to the first column
        index_under_pointer = index_under_pointer.sibling(index_under_pointer.row(), 0)
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

        act_edit_task = right_click_menu.addAction(self.tr("Edit Task"))
        act_edit_task.triggered.connect(lambda _=None, x=item: self.edit_task(item))
        act_delete_task = right_click_menu.addAction(self.tr("Delete Task"))
        act_delete_task.triggered.connect(lambda _=None, x=item: self.delete_task(item))
        right_click_menu.exec_(self.sender().viewport().mapToGlobal(position))

    def edit_task(self, item):
        if item.task.check_permissions(level=2) == -1:
            message, title = LOG.get_last_message()
            self._feedback.pop_info(title.capitalize(), message)
            return
        _dialog = tik_manager4.ui.dialog.task_dialog.EditTask(
            item.task, parent_sub=item.task.parent_sub, parent=self
        )
        state = _dialog.exec_()
        if state:
            # emit clicked signal
            self.item_selected.emit(_dialog.task_object)
        else:
            pass

    def delete_task(self, item):
        # first check for the user permission:
        if item.task.check_permissions(level=2) == -1:
            message, title = LOG.get_last_message()
            self._feedback.pop_info(title.capitalize(), message)
            return

        sure = self._feedback.pop_question(
            "Delete Task",
            "Are you sure you want to delete this task?",
            buttons=["ok", "cancel"],
        )
        if sure == "ok":
            if not item.task.parent_sub.is_task_empty(item.task):
                really_sure = self._feedback.pop_question(
                    "Non Empty Task",
                    "The task is not empty.\n\n"
                    "ALL CATEGORIES WORKS AND PUBLISHES UNDER {} WILL BE REMOVED\n"
                    "ARE YOU SURE?".format(item.task.name),
                    buttons=["ok", "cancel"],
                )
                if really_sure != "ok":
                    return

            state = item.task.parent_sub.delete_task(item.task.name)
            if state:
                # find the item in the model and remove it
                for i in range(self.model.rowCount()):
                    if self.model.item(i).task == item.task:
                        self.model.removeRow(i)
                        break
            else:
                msg = LOG.last_message()
                self._feedback.pop_info(
                    title="Task Not Deleted", text=msg, critical=True
                )
        else:
            return

    def refresh(self):
        """Re-populates the model keeping the expanded state"""
        pass


class TikTaskLayout(QtWidgets.QVBoxLayout):
    def __init__(self):
        """Initialize the layout"""
        super(TikTaskLayout, self).__init__()
        self.label = QtWidgets.QLabel("Tasks")
        self.label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.addWidget(self.label)
        self.addWidget(VerticalSeparator(color=(0, 255, 255)))

        self.task_view = TikTaskView()
        self.addWidget(self.task_view)
        self.filter_le = QtWidgets.QLineEdit()
        self.addWidget(self.filter_le)
        self.filter_le.textChanged.connect(self.task_view.filter)
        self.filter_le.setPlaceholderText("Filter")
        self.filter_le.setClearButtonEnabled(True)
        self.filter_le.setFocus()
        self.filter_le.returnPressed.connect(self.task_view.setFocus)

        # Hide all columns except the first one
        for idx in range(1, self.task_view.header().count()):
            self.task_view.hideColumn(idx)

    def refresh(self):
        self.task_view.refresh()

    def get_active_task(self):
        """Get the selected item and return the task object."""
        selected_item = self.task_view.get_selected_item()
        if selected_item:
            return selected_item.task
        return None
