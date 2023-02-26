import sys
import os
from tik_manager4.ui.Qt import QtWidgets, QtCore

# from PyQt5 import QtCore, QtGui, QtWidgets

from tik_manager4.ui.mcv.subproject_tree import TikProjectLayout
from tik_manager4.ui.mcv.task_tree import TikTaskLayout
from tik_manager4.ui.mcv.category import TikCategoryLayout

import tik_manager4

if __name__ == '__main__':
    test_project_path = os.path.join(os.path.expanduser("~"), "t4_stress_test_DO_NOT_USE")
    # test_project_path = os.path.join(os.path.expanduser("~"), "t4_test_manual_DO_NOT_USE")
    # test_project_path = os.path.join(os.path.expanduser("~"), "t4_test_project_DO_NOT_USE")

    if not os.path.exists(test_project_path):
        raise Exception("Test project path does not exist: {}".format(test_project_path))

    tik = tik_manager4.initialize("Standalone")
    tik.user.set("Admin", "1234")
    tik.set_project(test_project_path)

    app = QtWidgets.QApplication(sys.argv)
    test_dialog = QtWidgets.QDialog()
    test_dialog.resize(1200, 800)
    #
    master_lay = QtWidgets.QVBoxLayout(test_dialog)
    #
    dirname = os.path.dirname(os.path.abspath(__file__))
    tik_manager_dir = os.path.abspath(os.path.join(dirname, os.pardir, "tik_manager4", "ui"))
    QtCore.QDir.addSearchPath("css", os.path.join(tik_manager_dir, "theme"))
    QtCore.QDir.addSearchPath("rc", os.path.join(tik_manager_dir, "theme/rc"))
    #
    style_file = QtCore.QFile("css:tikManager.qss")
    style_file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
    test_dialog.setStyleSheet(str(style_file.readAll(), 'utf-8'))
    #
    splitter = QtWidgets.QSplitter(test_dialog, orientation=QtCore.Qt.Horizontal)
    master_lay.addWidget(splitter)
    left_widget = QtWidgets.QWidget(splitter)
    left_layout = QtWidgets.QVBoxLayout(left_widget)
    left_layout.setContentsMargins(0, 0, 0, 0)
    #
    right_widget = QtWidgets.QWidget(splitter)
    right_layout = QtWidgets.QVBoxLayout(right_widget)
    right_layout.setContentsMargins(0, 0, 0, 0)
    # splitter.setChildrenCollapsible(False)
    # #
    category_widget = QtWidgets.QWidget(splitter)
    category_layout = QtWidgets.QVBoxLayout(category_widget)
    category_layout.setContentsMargins(0, 0, 0, 0)

    # view = TikSubView()
    # view.set_project(tik.project)
    # view.hide_columns(["id", "path", "resolution", "fps"])
    sub_projects = TikProjectLayout(tik.project)
    # sub_projects.sub_view.hide_columns(["id", "path", "resolution", "fps"])
    # sub_projects.sub_view.hide_columns(["path", "resolution", "fps"])
    sub_projects.sub_view.hide_columns(["id", "path"])
    left_layout.addLayout(sub_projects)
    # #
    tasks = TikTaskLayout()
    tasks.task_view.hide_columns(["id", "path"])
    right_layout.addLayout(tasks)
    # # #
    categories = TikCategoryLayout()
    categories.work_tree_view.hide_columns(["id", "path"])
    category_layout.addLayout(categories)
    # #
    test_dialog.setLayout(master_lay)
    # # #
    # # #
    sub_projects.sub_view.item_selected.connect(tasks.task_view.set_tasks)
    sub_projects.sub_view.add_item.connect(tasks.task_view.add_task)
    tasks.task_view.item_selected.connect(categories.set_task)
    # #
    test_dialog.show()
    #
    # view.show()
    sys.exit(app.exec_())
