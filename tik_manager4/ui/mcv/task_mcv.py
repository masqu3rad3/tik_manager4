
import webbrowser
from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
from tik_manager4.core import filelog
from tik_manager4.ui.dialog.feedback import Feedback
import tik_manager4.ui.dialog.task_dialog
from tik_manager4.ui.widgets.common import HorizontalSeparator, TikIconButton
from tik_manager4.ui.widgets.style import ColorKeepingDelegate
from tik_manager4.ui.mcv.filter import FilterModel, FilterWidget
from tik_manager4.objects.guard import Guard

from tik_manager4.ui import pick

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")


class TikTaskItem(QtGui.QStandardItem):
    """Item class for the task view"""
    color_dict = {
        "asset": (0, 187, 184),
        "shot": (0, 115, 255),
        "global": (255, 141, 28),
        "other": (255, 255, 255),
        "deleted": (255, 0, 0),
    }

    def __init__(self, task_obj):
        """
        Initialize the item with the given task object.
        Args:
            task_obj (tik_manager4.objects.task.Task): Task object
        """
        super(TikTaskItem, self).__init__()

        # # test
        _icon = pick.icon(f"{task_obj.type}.png")
        self.setIcon(_icon)

        self.task = task_obj
        #
        self.fnt = QtGui.QFont("Open Sans", 12)
        self.fnt.setBold(True)
        self.setEditable(False)

        self._state = None

        self.setText(task_obj.nice_name or task_obj.name)

        self.refresh()

    def refresh(self):
        """Refresh the item"""
        self.set_state(self.task.state)

        if self.task.deleted:
            self.setForeground(QtGui.QColor(255, 0, 0))
            self.setFont(QtGui.QFont("Open Sans", 12, italic=True))
            _icon = pick.icon(f"{self.task.type}-ghost.png")
            self.setIcon(_icon)

    def set_state(self, state):
        """Set the state of the item.

        Args:
            state (str): State of the task
        """
        self._state = state
        _color = self.color_dict.get(self.task.type, (255, 255, 255))
        self.fnt.setStrikeOut(state == "omitted")
        self.setFont(self.fnt)
        self.setForeground(QtGui.QColor(*_color))

        # it its deleted make is transparent and italic
        if state == "deleted":
            self.setForeground(QtGui.QColor(255, 0, 0, 100))
            self.setFont(QtGui.QFont("Open Sans", 12, italic=True))


class TikTaskColumnItem(QtGui.QStandardItem):
    def __init__(self, text):
        super(TikTaskColumnItem, self).__init__(text)
        self.setEditable(False)


class TikTaskModel(QtGui.QStandardItemModel):
    columns = ["name", "id", "path"]
    filter_key = "super"

    def __init__(self):
        """Initialize the model"""
        super(TikTaskModel, self).__init__()
        self.purgatory_mode = False
        self.setHorizontalHeaderLabels(self.columns)

        self._tasks = []

    def clear(self):
        """Clear the model"""
        self._tasks = []
        self.setRowCount(0)

    def append_task(self, task_obj):
        """Append a task to the model"""
        self._tasks.append(task_obj)
        _task_item = TikTaskItem(task_obj)
        pid = TikTaskColumnItem(str(task_obj.id))
        path = TikTaskColumnItem(task_obj.path)

        self.appendRow(
            [
                _task_item,
                pid,
                path,
            ]
        )
        return _task_item

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

    def is_multi_subproject(self):
        """Return True if the tasks in the model belong to multiple subprojects."""
        sub_ids = list(set([task.parent_sub.id for task in self._tasks]))
        print(sub_ids)
        if len(sub_ids) <= 1:
            return False
        else: return True

class TikTaskView(QtWidgets.QTreeView):
    item_selected = QtCore.Signal(object)
    refresh_requested = QtCore.Signal()
    task_resurrected = QtCore.Signal()
    new_task_requested = QtCore.Signal()

    def __init__(self):
        """Initialize the view"""
        super(TikTaskView, self).__init__()
        self.purgatory_mode = False
        self.setItemDelegate(ColorKeepingDelegate())
        self.guard = Guard()
        self._feedback = Feedback(parent=self)
        self.setUniformRowHeights(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        # do not show branches
        self.setRootIsDecorated(False)

        self.model = TikTaskModel()
        self.proxy_model = FilterModel(parent=self)
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setRecursiveFilteringEnabled(True)
        self.setSortingEnabled(True)
        # sort it alphabetically
        self.sortByColumn(0, QtCore.Qt.AscendingOrder)

        self.setModel(self.proxy_model)

        self.is_management_locked = False

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

    def get_column_sizes(self):
        """Return all column sizes in a dictionary."""
        return {x: int(self.columnWidth(x)) for x in range(self.model.columnCount())}

    def set_column_sizes(self, column_sizes):
        """Set the column sizes from the given dictionary."""
        for column, size in column_sizes.items():
            self.setColumnWidth(int(column), size)

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
        # get the selected item
        selected_item = self.get_selected_item()
        self.model.clear()
        for task in tasks_gen:
            # if the task is already in model, skip it
            if self.model.find_item_by_id_column(task.id):
                continue

            self.model.append_task(task)
        self.expandAll()
        # if the item still exists, select it
        if selected_item:
            self.select_by_id(selected_item.task.id)

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

    def _right_click_on_blank(self, menu, position):
        act_refresh = menu.addAction(self.tr("Refresh"))
        act_refresh.triggered.connect(self.refresh)
        act_create_task = menu.addAction(self.tr("New Task"))
        act_create_task.setEnabled(not self.is_management_locked)
        # if the tasks are coming from multiple subprojects, disable the action
        if self.model.is_multi_subproject():
            act_create_task.setEnabled(False)
            act_create_task.setToolTip("Cannot create task when multiple subprojects are shown.")

        # when clicked, emit the new_task_requested signal
        act_create_task.triggered.connect(lambda _=None: self.new_task_requested.emit())
        menu.exec_(self.sender().viewport().mapToGlobal(position))

    def right_click_menu(self, position):
        indexes = self.sender().selectedIndexes()
        index_under_pointer = self.indexAt(position)
        right_click_menu = QtWidgets.QMenu(self)
        if not index_under_pointer.isValid():
            self._right_click_on_blank(right_click_menu, position)
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

        if self.purgatory_mode:
            if item.task.deleted:
                act_resurrect = right_click_menu.addAction(self.tr("Resurrect Task"))
                act_resurrect.setEnabled(not self.is_management_locked)
                act_resurrect.triggered.connect(
                    lambda _=None, x=item: self.on_resurrect(item)
                )
                right_click_menu.addSeparator()
        else:
            act_edit_task = right_click_menu.addAction(self.tr("Edit Task"))
            right_click_menu.addSeparator()

            act_edit_task.triggered.connect(lambda _=None, x=item: self.edit_task(item))

            revive_item_act = right_click_menu.addAction(self.tr("Revive Task"))
            revive_item_act.setEnabled(not self.is_management_locked)
            revive_item_act.triggered.connect(lambda _=None, x=item: self.revive_task(item))
            omit_item_act = right_click_menu.addAction(self.tr("Omit Task"))
            omit_item_act.setEnabled(not self.is_management_locked)
            omit_item_act.triggered.connect(lambda _=None, x=item: self.omit_task(item))

            act_delete_task = right_click_menu.addAction(self.tr("Delete Task"))
            act_delete_task.setEnabled(not self.is_management_locked)
            act_delete_task.triggered.connect(lambda _=None, x=item: self.delete_task(item))

            right_click_menu.addSeparator()

        open_url_act = right_click_menu.addAction(self.tr("Open URL"))
        open_url_act.setVisible(self.is_management_locked)
        # open_url_act.triggered.connect(lambda _=None, x=item: self.open_url_requested.emit(item))
        open_url_act.triggered.connect(lambda _=None, x=item: self.open_url(item))

        # emit signal to open the url
        right_click_menu.exec_(self.sender().viewport().mapToGlobal(position))

    def on_resurrect(self, item):
        """Resurrect the task"""
        state, msg = item.task.resurrect()
        if not state:
            self._feedback.pop_info("Task Not Resurrected", msg, critical=True)
            return
        self.task_resurrected.emit()
        self.refresh()
        return
        # send a signal to the subproject view to refresh.
        # this is just in case if the resurrected task was under a deleted subproject
        # In that case, the subproject gets resurrected as well.


    def open_url(self, item):
        if not self.guard.management_handler:
            return
        url = self.guard.management_handler.get_entity_url(item.task.type, item.task.id)
        if url:
            webbrowser.open(url)

    def edit_task(self, item):
        if item.task.check_permissions(level=2) == -1:
            message, title = LOG.get_last_message()
            self._feedback.pop_info(title.capitalize(), message)
            return
        _dialog = tik_manager4.ui.dialog.task_dialog.EditTask(
            item.task, parent_sub=item.task.parent_sub, parent=self,
            management_locked=self.is_management_locked
        )
        state = _dialog.exec_()
        if state:
            # emit clicked signal
            self.refresh()
            self.item_selected.emit(_dialog.task_object)
        else:
            pass

    def revive_task(self, item):
        if item.task.check_permissions(level=2) == -1:
            message, title = LOG.get_last_message()
            self._feedback.pop_info(title.capitalize(), message)
            return
        item.task.revive()
        item.refresh()

    def omit_task(self, item):
        if item.task.check_permissions(level=2) == -1:
            message, title = LOG.get_last_message()
            self._feedback.pop_info(title.capitalize(), message)
            return
        item.task.omit()
        item.refresh()

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
                    # "ARE YOU SURE?".format(item.task.name),
                    "ARE YOU SURE?".format(item.task.nice_name),
                    buttons=["ok", "cancel"],
                )
                if really_sure != "ok":
                    return

            state, msg = item.task.parent_sub.delete_task(item.task.name)
            if state:
                # find the item in the model and remove it
                for row_id in range(self.model.rowCount()):
                    if self.model.item(row_id).task == item.task:
                        self.model.removeRow(row_id)
                        break
            else:
                # msg = LOG.last_message()
                self._feedback.pop_info(
                    title="Task Not Deleted", text=msg, critical=True
                )
        else:
            return

    def refresh(self):
        """Re-populate the model."""
        self.refresh_requested.emit()


class TikTaskLayout(QtWidgets.QVBoxLayout):
    def __init__(self):
        """Initialize the layout"""
        super(TikTaskLayout, self).__init__()
        self._purgatory_mode = False
        header_lay = QtWidgets.QHBoxLayout()
        header_lay.setContentsMargins(0, 0, 0, 0)
        self.addLayout(header_lay)
        self.label = QtWidgets.QLabel("Tasks")
        self.label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_lay.addWidget(self.label)
        header_lay.addStretch()
        # add a refresh button
        self.refresh_btn = TikIconButton(icon_name="refresh", circle=True, size=18, icon_size=14)
        header_lay.addWidget(self.refresh_btn)
        # self.addWidget(self.label)
        self.addWidget(HorizontalSeparator(color=(0, 255, 255)))

        self.task_view = TikTaskView()
        self.addWidget(self.task_view)

        self.filter_widget = FilterWidget(self.task_view.proxy_model)
        self.addWidget(self.filter_widget)

        # Hide all columns except the first one
        for idx in range(1, self.task_view.header().count()):
            self.task_view.hideColumn(idx)

        self.refresh_btn.clicked.connect(self.refresh)

    def set_purgatory_mode(self, value):
        self.purgatory_mode = value

    @property
    def purgatory_mode(self):
        return self._purgatory_mode

    @purgatory_mode.setter
    def purgatory_mode(self, value):
        self._purgatory_mode = value
        self.task_view.purgatory_mode = value
        self.task_view.model.purgatory_mode = value
        self.refresh()

    def refresh(self):
        self.task_view.refresh()

    def get_active_task(self):
        """Get the selected item and return the task object."""
        selected_item = self.task_view.get_selected_item()
        if selected_item:
            return selected_item.task
        return None
