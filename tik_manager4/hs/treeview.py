import sys
from pprint import pprint
import json
import os
# from PyQt5 import QtWidgets, QtCore, QtGui, Qt
from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
from tik_manager4.core import utils
from tik_manager4.objects import main


# test_project_path = os.path.join(os.path.expanduser("~"), "t4_test_manual_DO_NOT_USE")
#
# # http://pharma-sas.com/common-manipulation-of-qtreeview-using-pyqt5/
#
#
# tik = main.Main()
# tik.project.set(test_project_path)

# pprint(tik.project.get_sub_tree())
# print(tik.project.__class__)
class TikTreeItem(QtGui.QStandardItem):
    color_dict = {
        "subproject": (255, 255, 255)
    }
    def __init__(self, txt='', font_size=12, set_bold=False, rgb=None, *args, **kwargs):
        super(TikTreeItem, self).__init__(*args, **kwargs)

        self.data = None
        #
        fnt = QtGui.QFont('Open Sans', font_size)
        fnt.setBold(set_bold)
        self.setEditable(False)

        if rgb:
            self.setForeground(QtGui.QColor(*rgb))
        self.setFont(fnt)
        self.setText(txt)


class TikTreeModel(QtGui.QStandardItemModel):
    columns = ["name", "id", "path", "resolution", "fps"]

    def __init__(self, structure_object):
        super(TikTreeModel, self).__init__()

        self.setHorizontalHeaderLabels(self.columns)

        self.project = None
        self.set_data(structure_object)

    def set_data(self, structure_object):
        self.project = self.check_data(structure_object)

    @staticmethod
    def check_data(structure_object):
        """checks if this is a proper structural data"""
        if not isinstance(structure_object, main.project.Project):
            raise Exception("The data that feeds into the TikTreeModel must be a Project object")
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
            "categories": [category.name for category in self.project.categories],
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
            parent_row = current[2]

            for neighbour in list(sub.subs.values()):
                if neighbour not in visited:
                    # print(neighbour.path)
                    sub_data = {
                        "id": neighbour.id,
                        "name": neighbour.name,
                        "path": neighbour.path,
                        # "resolution": neighbour.resolution,
                        # "fps": neighbour.fps,
                        # "categories": list(neighbour.categories.keys()),
                        "categories": [category.name for category in neighbour.categories],
                        "subs": [],  # this will be filled with the while loop
                    }
                    if neighbour.resolution != self.project.resolution:
                        sub_data["resolution"] = neighbour.resolution
                    if neighbour.fps != self.project.fps:
                        sub_data["fps"] = neighbour.fps
                    parent["subs"].append(sub_data)

                    _item = self.append_sub(neighbour, parent_row)

                    # add the categories
                    for category in neighbour.categories:
                        self.append_category(category, _item)
                    # visited.append([sub_data, neighbour])
                    visited.append(neighbour)
                    queue.append([sub_data, neighbour, _item])

        return all_data

    def append_sub(self, sub_data, parent):
        name = TikTreeItem(sub_data.name)
        pid = TikTreeItem(str(sub_data.id))
        path = TikTreeItem(sub_data.path)
        res = TikTreeItem(str(sub_data.resolution))
        fps = TikTreeItem(str(sub_data.fps))
        parent.appendRow([
            name,
            pid,
            path,
            res,
            fps
        ]
        )
        return name

    def append_category(self, category_obj, parent):
        category_name = TikTreeItem(category_obj.name, rgb=(255,255,0))
        category_id = TikTreeItem(str(category_obj.id), rgb=(255,255,0))
        parent.appendRow([category_name, category_id])
        return category_name



class TikTreeView(QtWidgets.QTreeView):
    # columns = ["name", "id", "path", "resolution", "fps"]
    def __init__(self, project_obj=None):
        super(TikTreeView, self).__init__()
        self.setUniformRowHeights(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSortingEnabled(True)
        # self.model = TikTreeModel(tik.project) # build the model with tik.project object

        # self.setModel(self.model)
        # self.model.populate()

        self.model = None
        if project_obj:
            self.set_project(project_obj)

        # SIGNALS

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.right_click_menu)
        # self.clicked.connect(lambda x: print(type(x)))
        self.clicked.connect(self.test)

        # TODO make this part re-usable
        dirname = os.path.dirname(os.path.abspath(__file__))
        tik_manager_dir = os.path.abspath(os.path.join(dirname, os.pardir))
        print(tik_manager_dir)
        QtCore.QDir.addSearchPath("css", os.path.join(tik_manager_dir, "theme"))
        QtCore.QDir.addSearchPath("rc", os.path.join(tik_manager_dir, "theme/rc"))

        # stylesheetFile = os.path.join(tik_manager_dir, "theme", "tikManager.qss")
        style_file = QtCore.QFile("css:tikManager.qss")
        style_file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
        self.setStyleSheet(str(style_file.readAll(), 'utf-8'))
        # utils.apply_stylesheet(style_file, self)

    def test(self, idx):
        # name = idx.data(role=QtCore.Qt.DisplayRole)
        _item = self.model.itemFromIndex(idx)
        # print(_item.extra_data)
        # print(name)

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
        self.model = TikTreeModel(project_obj)
        self.setModel(self.model)
        self.model.populate()

    def right_click_menu(self, position):
        indexes = self.sender().selectedIndexes()
        index_under_pointer = self.indexAt(position)
        if not index_under_pointer.isValid():
            return
        item = self.model.itemFromIndex(index_under_pointer)
        if len(indexes) > 0:
            level = 0
            index = indexes[0]
            while index.parent().isValid():
                index = index.parent()
                level += 1
        else:
            level = 0
        right_click_menu = QtWidgets.QMenu()
        act_new_category = right_click_menu.addAction(self.tr("New Sub-Project"))
        # act_new_category.triggered.connect(partial(self.TreeItem_Add, level, mdlIdx))
        act_new_category = right_click_menu.addAction(self.tr("New Category"))
        act_new_task = right_click_menu.addAction(self.tr("New Task"))
        # if item.parent() != None:
        #     insert_up = right_click_menu.addAction(self.tr("Insert Item Above"))
        #     # insert_up.triggered.connect(partial(self.TreeItem_InsertUp, level, mdlIdx))
        #     insert_down = right_click_menu.addAction(self.tr("Insert Item Below"))
        #     # insert_down.triggered.connect(partial(self.TreeItem_InsertDown, level, mdlIdx))
        #     act_del = right_click_menu.addAction(self.tr("Delete Item"))
        #     # act_del.triggered.connect(partial(self.TreeItem_Delete, item))
        right_click_menu.exec_(self.sender().viewport().mapToGlobal(position))

    # def set_data(self):
    #     parent1 = TikTreeItem("TestingA")
    #     child1 = TikTreeItem("testChildA")
    #     child2 = TikTreeItem("asdfasdf")
    #
    #     parent1.appendRow([child1, child2])
    #
    #     # parent.appendRow([
    #     #     QStandardItem(value['short_name']),
    #     #     QStandardItem(value['height']),
    #     #     QStandardItem(value['weight'])
    #     # ])
    #
    #     self.model.appendRow([parent1])


if __name__ == '__main__':
    # pprint(tik.project.get_data())



    test_project_path = os.path.join(os.path.expanduser("~"), "t4_test_manual_DO_NOT_USE")
    tik = main.Main()
    tik.project._set(test_project_path)

    app = QtWidgets.QApplication(sys.argv)

    # selfLoc = os.path.dirname(os.path.abspath(__file__))
    # tik_manager_dir = os.path.abspath(os.path.join(selfLoc, os.pardir))
    # stylesheetFile = os.path.join(tik_manager_dir, "theme", "tikManager.qss")
    # utils.apply_stylesheet(stylesheetFile, app)


    view = TikTreeView()
    view.set_project(tik.project)
    view.hide_columns(["id", "path", "resolution", "fps"])
    # view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
    # model = TikTreeModel()
    # model.setHorizontalHeaderLabels(['col1', 'col2', 'col3'])
    # view.setModel(model)
    # model.test_populate()
    # view.set_data()

    # view.clicked.connect(lambda x: print(type(x)))

    view.show()
    sys.exit(app.exec_())
