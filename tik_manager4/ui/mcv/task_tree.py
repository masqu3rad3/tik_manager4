from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui


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

        self.data = task_obj
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
        self.clicked.connect(self.test)

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

    def filter(self, text):
        """Filter the model"""
        self.proxy_model.setFilterRegExp(QtCore.QRegExp(text, QtCore.Qt.CaseInsensitive, QtCore.QRegExp.RegExp))
        # exclude TikTaskItems from the filter
        # self.proxy_model.setFilterKeyColumn(0)


class TikTaskLayout(QtWidgets.QVBoxLayout):
    def __init__(self):
        """Initialize the layout"""
        super(TikTaskLayout, self).__init__()
        self.task_view = TikTaskView()
        self.addWidget(self.task_view)
        self.filter_le = QtWidgets.QLineEdit()
        self.addWidget(self.filter_le)
        self.filter_le.textChanged.connect(self.task_view.filter)
        self.filter_le.setPlaceholderText("🔍")
        self.filter_le.setClearButtonEnabled(True)
        self.filter_le.setFocus()
        self.filter_le.returnPressed.connect(self.task_view.setFocus)
