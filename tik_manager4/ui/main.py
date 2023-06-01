"""Main UI for Tik Manager 4."""

from tik_manager4.ui.Qt import QtWidgets, QtCore

from tik_manager4.ui.mcv.project import TikProjectLayout
from tik_manager4.ui.mcv.subproject_tree import TikSubProjectLayout
from tik_manager4.ui.mcv.task_tree import TikTaskLayout
from tik_manager4.ui.mcv.category import TikCategoryLayout
from tik_manager4.ui.mcv.version import TikVersionLayout
from tik_manager4.ui.dialog.new_project import NewProjectDialog
from tik_manager4.ui.dialog.login import LoginDialog
from tik_manager4.ui.dialog.feedback import Feedback
from tik_manager4.ui import pick
import tik_manager4._version as version
import tik_manager4



class MainUI(QtWidgets.QMainWindow):
    def __init__(self, dcc="Standalone"):
        super(MainUI, self).__init__()

        self.setWindowTitle("Tik Manager {}".format(version.__version__))
        self.tik = tik_manager4.initialize(dcc)
        self.feedback = Feedback(self)
        # set window size
        self.resize(1200, 800)
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)

        # set style
        _style_file = pick.style_file()
        self.setStyleSheet(str(_style_file.readAll(), 'utf-8'))

        # define layouts
        self.master_layout = QtWidgets.QVBoxLayout(self.central_widget)

        self.title_layout = QtWidgets.QHBoxLayout()

        self.user_layout = QtWidgets.QHBoxLayout()

        self.project_layout = QtWidgets.QHBoxLayout()

        self.main_layout = QtWidgets.QVBoxLayout()
        splitter = QtWidgets.QSplitter(self.central_widget, orientation=QtCore.Qt.Horizontal)
        self.main_layout.addWidget(splitter)
        subproject_tree_widget = QtWidgets.QWidget(splitter)
        self.subproject_tree_layout = QtWidgets.QVBoxLayout(subproject_tree_widget)
        self.subproject_tree_layout.setContentsMargins(0, 0, 0, 0)

        task_tree_widget = QtWidgets.QWidget(splitter)
        self.task_tree_layout = QtWidgets.QVBoxLayout(task_tree_widget)
        self.task_tree_layout.setContentsMargins(0, 0, 0, 0)

        category_widget = QtWidgets.QWidget(splitter)
        self.category_layout = QtWidgets.QVBoxLayout(category_widget)
        self.category_layout.setContentsMargins(0, 0, 0, 0)

        version_widget = QtWidgets.QWidget(splitter)
        self.version_layout = QtWidgets.QVBoxLayout(version_widget)
        self.version_layout.setContentsMargins(0, 0, 0, 0)

        self.buttons_layout = QtWidgets.QHBoxLayout()

        self.master_layout.addLayout(self.title_layout)
        self.master_layout.addLayout(self.user_layout)
        self.master_layout.addLayout(self.project_layout)
        self.master_layout.addLayout(self.main_layout)
        self.master_layout.addLayout(self.buttons_layout)

        self.initialize_mcv()
        self.build_menu_bar()

    def initialize_mcv(self):
        project_mcv = TikProjectLayout(self.tik.project)
        self.project_layout.addLayout(project_mcv)

        subprojects_mcv = TikSubProjectLayout(self.tik.project)
        subprojects_mcv.sub_view.hide_columns(["id", "path"])
        self.subproject_tree_layout.addLayout(subprojects_mcv)

        tasks_mcv = TikTaskLayout()
        tasks_mcv.task_view.hide_columns(["id", "path"])
        self.task_tree_layout.addLayout(tasks_mcv)

        categories_mcv = TikCategoryLayout()
        categories_mcv.work_tree_view.hide_columns(["id", "path"])
        self.category_layout.addLayout(categories_mcv)

        versions_mcv = TikVersionLayout()
        self.version_layout.addLayout(versions_mcv)

        subprojects_mcv.sub_view.item_selected.connect(tasks_mcv.task_view.set_tasks)
        subprojects_mcv.sub_view.add_item.connect(tasks_mcv.task_view.add_task)
        tasks_mcv.task_view.item_selected.connect(categories_mcv.set_task)
        categories_mcv.work_tree_view.item_selected.connect(versions_mcv.set_base)

    def build_menu_bar(self):
        """Build the menu bar."""
        menu_bar = QtWidgets.QMenuBar(self, geometry=QtCore.QRect(0, 0, 1680, 18))
        self.setMenuBar(menu_bar)
        # menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        tools_menu = menu_bar.addMenu("Tools")
        help_menu = menu_bar.addMenu("Help")

        # File Menu
        create_project = QtWidgets.QAction("&Create New Project", self)
        file_menu.addAction(create_project)
        file_menu.addSeparator()
        user_login = QtWidgets.QAction("&User Login", self)
        file_menu.addAction(user_login)
        set_project = QtWidgets.QAction("&Set Project", self)
        file_menu.addAction(set_project)

        # Tools Menu

        # Help Menu
        about = QtWidgets.QAction("&About", self)
        help_menu.addAction(about)
        online_docs = QtWidgets.QAction("&Online Documentation", self)
        help_menu.addAction(online_docs)
        help_menu.addSeparator()
        check_for_updates = QtWidgets.QAction("&Check for Updates", self)
        help_menu.addAction(check_for_updates)

        # SIGNALS
        create_project.triggered.connect(self.on_create_new_project)
        user_login.triggered.connect(self.on_login)

    def on_create_new_project(self):
        """Create a new project."""
        # check the user permissions
        if not self.tik.user.permission_level < 3:
            # required permission level is 3 or higher. Inform user
            self.feedback.pop_info(title="Permission Error", text="You do not have the required permissions to create a new project.", critical=True)
            return
        dialog = NewProjectDialog(self.tik, parent=self)
        dialog.show()
        if dialog.exec_():
            self.tik.project = dialog.main_object
            # self.__init__(self.tik.dcc)

    def on_login(self):
        """Login."""
        dialog = LoginDialog(self.tik, parent=self)
        dialog.show()
        # if dialog.exec_():
        #     self.tik = dialog.tik
            # self.__init__(self.tik.dcc)




# test the MainUI class
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main = MainUI()
    main.show()
    sys.exit(app.exec_())
