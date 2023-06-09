"""Main UI for Tik Manager 4."""

from tik_manager4.ui.Qt import QtWidgets, QtCore

from tik_manager4.ui.mcv.project import TikProjectLayout
from tik_manager4.ui.mcv.subproject_tree import TikSubProjectLayout
from tik_manager4.ui.mcv.task_tree import TikTaskLayout
from tik_manager4.ui.mcv.category import TikCategoryLayout
from tik_manager4.ui.mcv.version import TikVersionLayout
from tik_manager4.ui.dialog.project_dialog import NewProjectDialog, SetProjectDialog
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

        self.project_mcv = None
        self.subprojects_mcv = None
        self.tasks_mcv = None
        self.categories_mcv = None
        self.versions_mcv = None

        self.initialize_mcv()
        self.build_menu_bar()

    def initialize_mcv(self):
        self.project_mcv = TikProjectLayout(self.tik.project)
        self.project_layout.addLayout(self.project_mcv)

        self.subprojects_mcv = TikSubProjectLayout(self.tik.project)
        self.subprojects_mcv.sub_view.hide_columns(["id", "path"])
        self.subproject_tree_layout.addLayout(self.subprojects_mcv)

        self.tasks_mcv = TikTaskLayout()
        self.tasks_mcv.task_view.hide_columns(["id", "path"])
        self.task_tree_layout.addLayout(self.tasks_mcv)

        self.categories_mcv = TikCategoryLayout()
        self.categories_mcv.work_tree_view.hide_columns(["id", "path"])
        self.category_layout.addLayout(self.categories_mcv)

        self.versions_mcv = TikVersionLayout()
        self.version_layout.addLayout(self.versions_mcv)

        self.project_mcv.set_project_btn.clicked.connect(self.on_set_project)
        self.project_mcv.recent_projects_btn.clicked.connect(self.on_recent_projects)
        self.subprojects_mcv.sub_view.item_selected.connect(self.tasks_mcv.task_view.set_tasks)
        self.subprojects_mcv.sub_view.add_item.connect(self.tasks_mcv.task_view.add_task)
        self.tasks_mcv.task_view.item_selected.connect(self.categories_mcv.set_task)
        self.categories_mcv.work_tree_view.item_selected.connect(self.versions_mcv.set_base)

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
        placeholder = QtWidgets.QAction("PLACEHOLDER", self)
        tools_menu.addAction(placeholder)

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
        set_project.triggered.connect(self.on_set_project)

    def refresh_project(self):
        """Refresh the project ui."""
        self.project_mcv.refresh()
        self.refresh_subprojects()

    def refresh_subprojects(self):
        """Refresh the subprojects' ui."""
        self.subprojects_mcv.refresh()
        self.refresh_tasks()

    def refresh_tasks(self):
        """Refresh the tasks' ui."""
        self.tasks_mcv.refresh()
        self.refresh_categories()

    def refresh_categories(self):
        """Refresh the categories' ui."""
        self.categories_mcv.clear()
        self.refresh_versions()

    def refresh_versions(self):
        """Refresh the versions' ui."""
        self.versions_mcv.refresh()

    def on_recent_projects(self):
        dialog = SetProjectDialog(self.tik, parent=self)
        if dialog.recents_pop_menu():
            self.refresh_project()

    def on_set_project(self):
        """Launch the set project dialog."""
        dialog = SetProjectDialog(self.tik, parent=self)
        dialog.show()
        if dialog.exec_():
            self.tik.project = dialog.main_object
            # refresh main ui
        self.refresh_project()

    def on_create_new_project(self):
        """Create a new project."""
        # check the user permissions
        if self.tik.project._check_permissions(level=3) != -1:
            dialog = NewProjectDialog(self.tik, parent=self)
            dialog.show()
            if dialog.exec_():
                self.tik.project = dialog.main_object
        else:
            message, title = self.tik.project.log.get_last_message()
            self.feedback.pop_info(title.capitalize(), message)
            return

    def on_login(self):
        """Login."""
        dialog = LoginDialog(self.tik, parent=self)
        dialog.show()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main = MainUI()
    main.show()
    sys.exit(app.exec_())
