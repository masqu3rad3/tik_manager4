import sys
import os
from tik_manager4.ui.Qt import QtWidgets, QtCore

from PyQt5 import QtCore, QtGui, QtWidgets

from tik_manager4.ui.mcv.subproject_tree import TikProjectLayout
from tik_manager4.ui.mcv.task_tree import TikTaskLayout
import tik_manager4

if __name__ == '__main__':
    test_project_path = os.path.join(os.path.expanduser("~"), "t4_test_manual_DO_NOT_USE")
    tik = tik_manager4.initialize("Standalone")
    tik.user.set("Admin", "1234")
    tik.project.set(test_project_path)

    app = QtWidgets.QApplication(sys.argv)
    test_dialog = QtWidgets.QDialog()
    test_dialog.resize(1200, 800)

    master_lay = QtWidgets.QVBoxLayout(test_dialog)

    dirname = os.path.dirname(os.path.abspath(__file__))
    tik_manager_dir = os.path.abspath(os.path.join(dirname, os.pardir, "tik_manager4", "ui"))
    QtCore.QDir.addSearchPath("css", os.path.join(tik_manager_dir, "theme"))
    QtCore.QDir.addSearchPath("rc", os.path.join(tik_manager_dir, "theme/rc"))

    style_file = QtCore.QFile("css:tikManager.qss")
    style_file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
    test_dialog.setStyleSheet(str(style_file.readAll(), 'utf-8'))

    splitter = QtWidgets.QSplitter(test_dialog, orientation=QtCore.Qt.Horizontal)
    master_lay.addWidget(splitter)
    left_widget = QtWidgets.QWidget(splitter)
    left_layout = QtWidgets.QVBoxLayout(left_widget)
    left_layout.setContentsMargins(0, 0, 0, 0)

    right_widget = QtWidgets.QWidget(splitter)
    right_layout = QtWidgets.QVBoxLayout(right_widget)
    right_layout.setContentsMargins(0, 0, 0, 0)
    # splitter.setChildrenCollapsible(False)

    # view = TikSubView()
    # view.set_project(tik.project)
    # view.hide_columns(["id", "path", "resolution", "fps"])
    sub_projects = TikProjectLayout(tik.project)
    sub_projects.sub_view.hide_columns(["id", "path", "resolution", "fps"])
    left_layout.addLayout(sub_projects)

    tasks = TikTaskLayout()
    tasks.task_view.hide_columns(["id", "path"])
    right_layout.addLayout(tasks)

    test_dialog.setLayout(master_lay)


    # sub_projects.sub_view.item_selected.connect(lambda x: print(x))
    sub_projects.sub_view.item_selected.connect(tasks.task_view.set_tasks)

    test_dialog.show()
    # view.show()
    sys.exit(app.exec_())
