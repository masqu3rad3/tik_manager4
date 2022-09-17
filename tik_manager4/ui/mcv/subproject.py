import sys
import os
from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui, Qt
# from tik_manager4.objects import main
import tik_manager4

class TikSubItem(QtGui.QStandardItem):
    color_dict = {
        "subproject": (255, 255, 255)
    }
    def __init__(self, sub_obj):
        super(TikSubItem, self).__init__()

        self.data = sub_obj
        #
        fnt = QtGui.QFont('Open Sans', 12)
        fnt.setBold(False)
        self.setEditable(False)

        self.setForeground(QtGui.QColor(255, 255, 255))
        self.setFont(fnt)
        self.setText(sub_obj.name)

        # pid = TikSubItem(str(sub_obj.id))
        # path = TikSubItem(sub_data.path)
        # res = TikSubItem(str(sub_data.resolution))
        # fps = TikSubItem(str(sub_data.fps))

class TikTaskItem(QtGui.QStandardItem):
    color_dict = {
        "subproject": (255, 255, 255)
    }
    def __init__(self, task_obj):
        super(TikTaskItem, self).__init__()

        self.data = task_obj
        #
        fnt = QtGui.QFont('Open Sans', 12)
        fnt.setBold(True)
        self.setEditable(False)

        self.setForeground(QtGui.QColor(0, 255, 255))
        self.setFont(fnt)
        self.setText(task_obj.name)


class TikSubModel(QtGui.QStandardItemModel):
    columns = ["name", "id", "path", "resolution", "fps"]
    filter_key = "super"
    def __init__(self, structure_object):
        super(TikSubModel, self).__init__()

        self.setHorizontalHeaderLabels(self.columns)

        self.project = None
        self.set_data(structure_object)

    def set_data(self, structure_object):
        self.project = self.check_data(structure_object)

    @staticmethod
    def check_data(structure_object):
        """checks if this is a proper structural data"""
        # if not isinstance(structure_object, main.project.Project):
        #     raise Exception("The data that feeds into the TikTreeModel must be a Project object")
        return structure_object

    def populate(self):
        self.setRowCount(0)
        visited = []
        queue = []

        # start with the initial dictionary with self subproject
        all_data = {
            "id": self.project.id,
            "name": self.project.name,
            "path": self.project.path,
            "resolution": self.project.resolution,
            "fps": self.project.fps,
            "tasks": self.project.tasks,
            # "categories": [category.name for category in self.project.categories],
            "subs": [],  # this will be filled with the while loop
        }

        # add the initial dictionary and self into the queue
        # Each queue item is a list.
        # first element is the dictionary point and second is the subproject object
        parent_row = self
        queue.append([all_data, self.project, parent_row])

        while queue:
            current = queue.pop(0)
            parent = current[0]
            sub = current[1]
            sub.scan_tasks()
            parent_row = current[2]

            for neighbour in list(sub.subs.values()):
                if neighbour not in visited:
                    # print(neighbour.path)
                    sub_data = {
                        "id": neighbour.id,
                        "name": neighbour.name,
                        "path": neighbour.path,
                        "tasks": neighbour.tasks,
                        # "resolution": neighbour.resolution,
                        # "fps": neighbour.fps,
                        # "categories": list(neighbour.categories.keys()),
                        # "categories": [category.name for category in neighbour.categories],
                        "subs": [],  # this will be filled with the while loop
                    }
                    if neighbour.resolution != self.project.resolution:
                        sub_data["resolution"] = neighbour.resolution
                    if neighbour.fps != self.project.fps:
                        sub_data["fps"] = neighbour.fps
                    parent["subs"].append(sub_data)

                    _item = self.append_sub(neighbour, parent_row)

                    # add tasks
                    neighbour.scan_tasks()
                    self.append_tasks(neighbour.tasks, _item)

                    visited.append(neighbour)
                    queue.append([sub_data, neighbour, _item])

        return all_data

    def append_sub(self, sub_data, parent):
        # if self.filter_key and self.filter_key not in sub_data.name:
        #     return
        name = TikSubItem(sub_data)
        pid = QtGui.QStandardItem(str(sub_data.id))
        path = QtGui.QStandardItem(sub_data.path)
        res = QtGui.QStandardItem(str(sub_data.resolution))
        fps = QtGui.QStandardItem(str(sub_data.fps))
        # pid = TikSubItem(str(sub_data.id))
        # path = TikSubItem(sub_data.path)
        # res = TikSubItem(str(sub_data.resolution))
        # fps = TikSubItem(str(sub_data.fps))
        parent.appendRow([
            name,
            pid,
            path,
            res,
            fps
        ]
        )
        return name

    # def append_category(self, category_obj, parent):
    #     category_name = TikSubItem(category_obj.name, rgb=(255, 255, 0))
    #     category_id = TikSubItem(str(category_obj.id), rgb=(255, 255, 0))
    #     parent.appendRow([category_name, category_id])
    #     return category_name
    def append_tasks(self, tasks_dict, parent_sub):
        for _, task_obj in tasks_dict.items():
            # if self.filter_key and self.filter_key not in task_obj.name:
            #     continue
            _task = TikTaskItem(task_obj)
        # _task.data = task_obj
        # task_id = TikSubItem(str(task_obj.id), rgb=(255, 255, 0))
        # parent.appendRow([_task, task_id])
            parent_sub.appendRow([_task])
        return
    # def append_task(self, task_obj, parent):
    #     _task = TikTaskItem(task_obj)
    #     # _task.data = task_obj
    #     # task_id = TikSubItem(str(task_obj.id), rgb=(255, 255, 0))
    #     # parent.appendRow([_task, task_id])
    #     parent.appendRow([_task])
    #     return _task



class TikSubView(QtWidgets.QTreeView):
    def __init__(self, project_obj=None):
        super(TikSubView, self).__init__()
        self.setUniformRowHeights(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        # self.setSortingEnabled(True)


        self.model = None
        if project_obj:
            self.set_project(project_obj)

        # SIGNALS

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.right_click_menu)
        self.clicked.connect(self.test)

        # TODO make this part re-usable
        # dirname = os.path.dirname(os.path.abspath(__file__))
        # tik_manager_dir = os.path.abspath(os.path.join(dirname, os.pardir))
        # print(tik_manager_dir)
        # QtCore.QDir.addSearchPath("css", os.path.join(tik_manager_dir, "theme"))
        # QtCore.QDir.addSearchPath("rc", os.path.join(tik_manager_dir, "theme/rc"))
        #
        # style_file = QtCore.QFile("css:tikManager.qss")
        # style_file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
        # self.setStyleSheet(str(style_file.readAll(), 'utf-8'))
        self.expandAll()

    def expandAll(self):
        super(TikSubView, self).expandAll()
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)
        self.resizeColumnToContents(2)
        self.resizeColumnToContents(3)
        self.resizeColumnToContents(4)
    def test(self, idx):
        # the id needs to mapped from proxy to source
        index = self.proxy_model.mapToSource(idx)
        _item = self.model.itemFromIndex(index)
        # _item = self.model.itemFromIndex(idx)
        print(type(_item))
        print(_item.data)

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

    def set_project(self, project_obj):
        self.model = TikSubModel(project_obj)
        # self.model.setFilterRegExp(QtCore.QRegExp("Ass*", QtCore.Qt.CaseInsensitive, QtCore.QRegExp.RegExp))
        # self.proxy_model = QtCore.QSortFilterProxyModel()
        self.proxy_model = ProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setRecursiveFilteringEnabled(True)
        self.setSortingEnabled(True)
        # set sort indicator to ascending
        self.sortByColumn(0, QtCore.Qt.AscendingOrder)
        # self.proxy_model.sort(2, QtCore.Qt.AscendingOrder)
        # self.proxy_model.setFilterRegExp(QtCore.QRegExp("Sup*", QtCore.Qt.CaseInsensitive, QtCore.QRegExp.RegExp))
        # self.setModel(self.model)
        self.setModel(self.proxy_model)

        self.model.populate()

    def filter(self, text):
        # pass
        self.proxy_model.setFilterRegExp(QtCore.QRegExp(text, QtCore.Qt.CaseInsensitive, QtCore.QRegExp.RegExp))
        # exclude TikTaskItems from the filter
        # self.proxy_model.setFilterKeyColumn(0)


    def right_click_menu(self, position):
        indexes = self.sender().selectedIndexes()
        index_under_pointer = self.indexAt(position)
        if not index_under_pointer.isValid():
            return
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
        right_click_menu = QtWidgets.QMenu()
        act_new_sub = right_click_menu.addAction(self.tr("New Sub-Project"))
        act_new_sub.triggered.connect(lambda _, x=item: self.new_sub_project(item))
        # act_new_sub.triggered.connect(partial(self.TreeItem_Add, level, mdlIdx))
        # act_new_category = right_click_menu.addAction(self.tr("New Category"))
        act_new_task = right_click_menu.addAction(self.tr("New Task"))
        right_click_menu.exec_(self.sender().viewport().mapToGlobal(position))

    def new_sub_project(self, item):
        print(item.data.id)
        sub = self.model.project.create_sub_project("TEST", parent_uid=item.data.id)
        if sub != -1:
            self.model.append_sub(sub, item)
        else:
            print("ERROR")
            # print(self.model.project)
            print(self.model.project.log.get_last_message())


class ProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(ProxyModel, self).__init__(parent)
        pass
    def filterAcceptsRow(self, source_row, source_parent):
        # print(source_row, source_parent)
        model = self.sourceModel()
        index = model.index(source_row, 0, QtCore.QModelIndex())

        item = model.itemFromIndex(index)
        # print(item.data)
        if isinstance(item, TikSubItem):
            print(item.data.scan_tasks())
            # return False
        # for role, value in self.excludes.iteritems():
        #     data = model.data(index, role)
        #     if data == value:
        #         return False

        return super(ProxyModel, self).filterAcceptsRow(source_row, source_parent)


class TikProjectLayout(QtWidgets.QVBoxLayout):
    def __init__(self, project_obj):
        super(TikProjectLayout, self).__init__()
        self.project_obj = project_obj
        self.sub_view = TikSubView(project_obj)
        self.addWidget(self.sub_view)
        self.filter_le = QtWidgets.QLineEdit()
        self.addWidget(self.filter_le)
        self.filter_le.textChanged.connect(self.sub_view.filter)
        self.filter_le.setPlaceholderText("Filter")
        self.filter_le.setClearButtonEnabled(True)
        self.filter_le.setFocus()
        self.filter_le.returnPressed.connect(self.sub_view.setFocus)


if __name__ == '__main__':
    test_project_path = os.path.join(os.path.expanduser("~"), "t4_test_manual_DO_NOT_USE")
    tik = tik_manager4.initialize("Standalone")
    tik.user.set("Admin", "1234")
    tik.project.set(test_project_path)


    app = QtWidgets.QApplication(sys.argv)
    test_dialog = QtWidgets.QDialog()

    dirname = os.path.dirname(os.path.abspath(__file__))
    tik_manager_dir = os.path.abspath(os.path.join(dirname, os.pardir))
    QtCore.QDir.addSearchPath("css", os.path.join(tik_manager_dir, "theme"))
    QtCore.QDir.addSearchPath("rc", os.path.join(tik_manager_dir, "theme/rc"))

    style_file = QtCore.QFile("css:tikManager.qss")
    style_file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
    test_dialog.setStyleSheet(str(style_file.readAll(), 'utf-8'))

    # view = TikSubView()
    # view.set_project(tik.project)
    # view.hide_columns(["id", "path", "resolution", "fps"])
    view = TikProjectLayout(tik.project)
    test_dialog.setLayout(view)

    test_dialog.show()
    # view.show()
    sys.exit(app.exec_())
