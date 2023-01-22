from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
from tik_manager4.core import filelog
from tik_manager4.ui.dialog.feedback import Feedback

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")


class TikTaskItem(QtGui.QStandardItem):
    color_dict = {
        "subproject": (255, 255, 255)
    }

    def __init__(self, task_obj):
        """
        Initialize the item with the given task object.
        Args:
            task_obj (tik_manager4.objects.task.Task): Task object
        """
        super(TikTaskItem, self).__init__()

        self.task = task_obj
        #
        fnt = QtGui.QFont('Open Sans', 12)
        fnt.setBold(True)
        self.setEditable(False)

        self.setForeground(QtGui.QColor(0, 255, 255))
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

    def set_tasks(self, tasks_list):
        """Set the data for the model"""
        # TODO : validate
        self._tasks.clear()
        self._tasks = tasks_list

    def populate(self):
        """Populate the model"""
        self.clear()

        for task in self._tasks:
            self.append_task(task)

    def append_task(self, sub_data):
        """Append a task to the model"""
        _sub_item = TikTaskItem(sub_data)
        pid = QtGui.QStandardItem(str(sub_data.id))
        path = QtGui.QStandardItem(sub_data.path)

        self.appendRow([
            _sub_item,
            pid,
            path,
        ]
        )
        return _sub_item


class TikTaskView(QtWidgets.QTreeView):
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

        self.setModel(self.proxy_model)

        # SIGNALS

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.right_click_menu)
        # self.clicked.connect(self.test)

        # create another context menu for columns
        self.header().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.header().customContextMenuRequested.connect(self.header_right_click_menu)

        self.expandAll()

    def expandAll(self):
        """Expand all the items in the view"""
        super(TikTaskView, self).expandAll()
        self.resizeColumnToContents(0)

    def hide_columns(self, columns):
        """ If the given column exists in the model, hides it"""
        if not isinstance(columns, list):
            columns = [columns]

        for column in columns:
            if column in self.model.columns:
                self.setColumnHidden(self.model.columns.index(column), True)

    def unhide_columns(self, columns):
        """ If the given column exists in the model, unhides it"""
        if not isinstance(columns, list):
            columns = [columns]

        for column in columns:
            if column in self.model.columns:
                self.setColumnHidden(self.model.columns.index(column), False)

    def toggle_column(self, column, state):
        """ If the given column exists in the model, unhides it"""
        if state:
            self.unhide_columns(column)
        else:
            self.hide_columns(column)

    def set_tasks(self, tasks_gen):
        """Set the data for the model"""
        # print(tasks_gen)
        # for task in tasks_gen:
        #     print(task)
        self.model.clear()
        for task in tasks_gen:
            # print(task)
            self.model.append_task(task)
        # tasks = [value for item, value in tasks_dictionary.items()]
        # self.model.set_tasks(tasks)
        # self.model.populate()
        self.expandAll()

    def add_task(self, task):
        """Add a task to the model"""
        self.model.append_task(task)
        self.expandAll()

    def filter(self, text):
        """Filter the model"""
        self.proxy_model.setFilterRegExp(QtCore.QRegExp(text, QtCore.Qt.CaseInsensitive, QtCore.QRegExp.RegExp))
        # exclude TikTaskItems from the filter
        # self.proxy_model.setFilterKeyColumn(0)

    def header_right_click_menu(self, position):
        menu = QtWidgets.QMenu()

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
        right_click_menu = QtWidgets.QMenu()
        if not index_under_pointer.isValid():
            # act_new_task = right_click_menu.addAction(self.tr("New Task"))
            # act_new_task.triggered.connect(self.new_task)
            # right_click_menu.exec_(self.sender().viewport().mapToGlobal(position))
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
        # right_click_menu = QtWidgets.QMenu()
        # act_new_task = right_click_menu.addAction(self.tr("New Task"))
        # act_new_sub.triggered.connect(lambda _, x=item: self.new_sub_project(item))
        act_edit_sub = right_click_menu.addAction(self.tr("Edit Task"))
        act_edit_sub.triggered.connect(lambda _, x=item: self.edit_sub_project(item))
        act_delete_sub = right_click_menu.addAction(self.tr("Delete Task"))
        act_delete_sub.triggered.connect(lambda _, x=item: self.delete_task(item))
        # act_new_sub.triggered.connect(partial(self.TreeItem_Add, level, mdlIdx))
        # act_new_category = right_click_menu.addAction(self.tr("New Category"))
        # act_new_task = right_click_menu.addAction(self.tr("New Task"))
        # act_new_task.triggered.connect(lambda _, x=item: self.new_task(item))
        right_click_menu.exec_(self.sender().viewport().mapToGlobal(position))

    def delete_task(self, item):
        # first check for the user permission:
        # if self.model.project._check_permissions(level=2) != -1:
        sure = self._feedback.pop_question("Delete Task", "Are you sure you want to delete this task?", buttons=["ok", "cancel"])
        if sure:
            # emit clicked signal
            # self.delete_item.emit(item)
            # self.model.remove_task(item)
            if not item.task.parent_sub.is_task_empty(item.task):
                really_sure = self._feedback.pop_question("Non Empty Task",
                                                      "The task is not empty.\n\nALL CATEGORIES WORKS AND PUBLISHES UNDER {} WILL BE REMOVED\nARE YOU SURE?".format(
                                                          item.task.name), buttons=["ok", "cancel"])
                if not really_sure:
                    return

            state = item.task.parent_sub.delete_task(item.task.name)
            if state:
                # find the item in the model and remove it
                for i in range(self.model.rowCount()):
                    if self.model.item(i).task == item.task:
                        self.model.removeRow(i)
                        break
                # self._feedback.pop_info("Task Deleted", "Task {} deleted".format(item.name))
            else:
                msg = LOG.last_message()
                self._feedback.pop_info(title="Task Not Deleted", text=msg, critical=True)
        else:
            return


class TikTaskLayout(QtWidgets.QVBoxLayout):
    def __init__(self):
        """Initialize the layout"""
        super(TikTaskLayout, self).__init__()
        self.task_view = TikTaskView()
        self.addWidget(self.task_view)
        self.filter_le = QtWidgets.QLineEdit()
        self.addWidget(self.filter_le)
        self.filter_le.textChanged.connect(self.task_view.filter)
        self.filter_le.setPlaceholderText("Filter")
        self.filter_le.setClearButtonEnabled(True)
        self.filter_le.setFocus()
        self.filter_le.returnPressed.connect(self.task_view.setFocus)
