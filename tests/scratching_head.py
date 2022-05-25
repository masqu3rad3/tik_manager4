import sys
from pprint import pprint
import json
import os
from PyQt5 import QtWidgets, QtCore, QtGui

from tik_manager4.objects import main
test_project_path = os.path.join(os.path.expanduser("~"), "t4_test_manual_DO_NOT_USE")

# http://pharma-sas.com/common-manipulation-of-qtreeview-using-pyqt5/

class TikTreeItem(QtGui.QStandardItem):
    def __init__(self, *args, **kwargs):
        super(TikTreeItem, self).__init__(*args, **kwargs)

        self.extra_data = "some_test_string"
    #
    # def data(self, *args, **kwargs):
    #     super(TikTreeItem, self).data(*args, **kwargs)
    #     print("obareyt")

class TikTreeModel(QtGui.QStandardItemModel):
    def __init__(self):
        super(TikTreeModel, self).__init__()
        
        self.setHorizontalHeaderLabels(["name", "id"])
        
    # def test_populate(self):
    #     parent1 = TikTreeItem("TestingA")
    #     child1 = TikTreeItem("testChildA")
    #
    #     parent1.appendRow(child1)
    #     self.appendRow(parent1)

class TikTreeView(QtWidgets.QTreeView):
    def __init__(self):
        super(TikTreeView, self).__init__()
        self.setUniformRowHeights(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.model = TikTreeModel()
        self.setModel(self.model)

    def set_data(self):
        parent1 = TikTreeItem("TestingA")
        child1 = TikTreeItem("testChildA")
        child2 = TikTreeItem("asdfasdf")

        parent1.appendRow([child1, child2])

        # parent.appendRow([
        #     QStandardItem(value['short_name']),
        #     QStandardItem(value['height']),
        #     QStandardItem(value['weight'])
        # ])

        self.model.appendRow([parent1])


        

tik = main.Main()
tik.project.set(test_project_path)
# pprint(tik.project.get_data())

app = QtWidgets.QApplication(sys.argv)

view = TikTreeView()
# view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
# model = TikTreeModel()
# model.setHorizontalHeaderLabels(['col1', 'col2', 'col3'])
# view.setModel(model)
# model.test_populate()
view.set_data()

view.clicked.connect(lambda x: print(type(x)))

view.show()
sys.exit(app.exec_())
