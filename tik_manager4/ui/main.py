"""Main UI for Tik Manager 4."""
import logging
from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui

from tik_manager4.ui.mcv.user_mcv import TikUserLayout
from tik_manager4.ui.mcv.project_mcv import TikProjectLayout
from tik_manager4.ui.mcv.subproject_mcv import TikSubProjectLayout
from tik_manager4.ui.mcv.task_mcv import TikTaskLayout
from tik_manager4.ui.mcv.category_mcv import TikCategoryLayout
from tik_manager4.ui.mcv.version_mcv import TikVersionLayout
from tik_manager4.ui.dialog.project_dialog import NewProjectDialog, SetProjectDialog
from tik_manager4.ui.dialog.user_dialog import LoginDialog, NewUserDialog
from tik_manager4.ui.dialog.work_dialog import NewWorkDialog, NewVersionDialog
from tik_manager4.ui.dialog.feedback import Feedback
from tik_manager4.ui.widgets.common import TikButton
from tik_manager4.ui import pick
import tik_manager4._version as version
import tik_manager4

LOG = logging.getLogger(__name__)
WINDOW_NAME = "Tik Manager {}".format(version.__version__)

def launch(dcc="Standalone"):
    all_widgets = QtWidgets.QApplication.allWidgets()
    tik = tik_manager4.initialize(dcc)
    parent = tik.dcc.get_main_window()
    for entry in all_widgets:
        try:
            if entry.objectName() == WINDOW_NAME:
                entry.close()
                entry.deleteLater()
        except (AttributeError, TypeError):
            pass
    m = MainUI(tik, parent=parent)
    m.show()

class MainUI(QtWidgets.QMainWindow):
    def __init__(self, main_object, **kwargs):
        # print("MainUI init")
        # self.tik = tik_manager4.initialize(dcc)

        # self.parent = self.tik.dcc.get_main_window()
        super(MainUI, self).__init__(**kwargs)
        self.tik = main_object

        self.setWindowTitle("Tik Manager {}".format(version.__version__))
        self.setObjectName(WINDOW_NAME)

        self.feedback = Feedback(self)
        # set window size
        self.resize(1200, 800)
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)

        # set style
        _style_file = pick.style_file()
        self.setStyleSheet(str(_style_file.readAll(), 'utf-8'))
        # self.setStyleSheet(str(_style_file.readAll()))

        # self.setStyleSheet(six.text_type(_style_file.readAll(), 'utf-8'))


        # define layouts
        self.master_layout = QtWidgets.QVBoxLayout(self.central_widget)

        self.title_layout = QtWidgets.QHBoxLayout()

        project_user_layout = QtWidgets.QHBoxLayout()

        self.project_layout = QtWidgets.QHBoxLayout()

        self.user_layout = QtWidgets.QHBoxLayout()

        project_user_layout.addLayout(self.project_layout)
        # add a horizontal separator line
        line = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(2, 100)
        pixmap.fill(QtGui.QColor(100, 100, 100))
        line.setPixmap(pixmap)
        line.setFixedHeight(25)
        line.setFixedWidth(20)
        # align to the center
        line.setAlignment(QtCore.Qt.AlignCenter)
        project_user_layout.addWidget(line)

        project_user_layout.addLayout(self.user_layout)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.splitter = QtWidgets.QSplitter(self.central_widget, orientation=QtCore.Qt.Horizontal)
        self.splitter.setHandleWidth(5)

        self.main_layout.addWidget(self.splitter)

        subproject_tree_widget = QtWidgets.QWidget(self.splitter)
        self.subproject_tree_layout = QtWidgets.QVBoxLayout(subproject_tree_widget)
        self.subproject_tree_layout.setContentsMargins(2, 2, 2, 2)

        task_tree_widget = QtWidgets.QWidget(self.splitter)
        self.task_tree_layout = QtWidgets.QVBoxLayout(task_tree_widget)
        self.task_tree_layout.setContentsMargins(2, 2, 2, 2)

        category_widget = QtWidgets.QWidget(self.splitter)
        self.category_layout = QtWidgets.QVBoxLayout(category_widget)
        self.category_layout.setContentsMargins(2, 2, 2, 2)

        version_widget = QtWidgets.QWidget(self.splitter)
        self.version_layout = QtWidgets.QVBoxLayout(version_widget)
        self.version_layout.setContentsMargins(2, 2, 2, 2)

        #####################

        self.work_buttons_frame = QtWidgets.QFrame()
        self.work_buttons_frame.setMaximumHeight(50)

        self.work_buttons_layout = QtWidgets.QHBoxLayout()
        self.work_buttons_layout.addStretch()
        self.work_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.work_buttons_frame.setLayout(self.work_buttons_layout)

        self.publish_buttons_frame = QtWidgets.QFrame()
        self.publish_buttons_frame.setMaximumHeight(50)

        self.publish_buttons_layout = QtWidgets.QHBoxLayout()
        self.publish_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.publish_buttons_frame.setLayout(self.publish_buttons_layout)
        self.publish_buttons_frame.hide()

        self.master_layout.addLayout(self.title_layout)
        self.master_layout.addLayout(project_user_layout)
        self.master_layout.addLayout(self.main_layout)

        self.master_layout.addWidget(self.work_buttons_frame)
        self.master_layout.addWidget(self.publish_buttons_frame)

        #####################

        self.project_mcv = None
        self.subprojects_mcv = None
        self.tasks_mcv = None
        self.categories_mcv = None
        self.versions_mcv = None

        self.initialize_mcv()
        self.build_bars()
        self.build_buttons()
        #
        self.resume_last_selection()
        #
        self.status_bar.showMessage("Status | Ready")

    def resume_last_selection(self):
        """Resume the last selection from the user settings."""
        # project is getting handled by the project object.
        # subproject

        subproject_id = self.tik.user.last_subproject
        if subproject_id:
            # self.tik.project.find_sub_by_id(subproject_id)
            state = self.subprojects_mcv.sub_view.select_by_id(subproject_id)
            if state:
                # if its successfully set, then select the last task
                task_id = self.tik.user.last_task
                if task_id:
                    state = self.tasks_mcv.task_view.select_by_id(task_id)
                    if state:
                        # if its successfully set, then select the last category
                        category_index = self.tik.user.last_category or 0
                        self.categories_mcv.set_category_by_index(category_index)
                        work_id = self.tik.user.last_work
                        if work_id:
                            state = self.categories_mcv.work_tree_view.select_by_id(work_id)
                            if state:
                                # if its successfully set, then select the last version
                                version_id = self.tik.user.last_version
                                if version_id:
                                    self.versions_mcv.set_version(version_id)
        else:
            # if there are no subprojects, then select the first one
            self.subprojects_mcv.sub_view.select_first_item()
            LOG.info("No subproject found, selecting the first one.")

        self.subprojects_mcv.sub_view.set_expanded_state(self.tik.user.expanded_subprojects)

        # regardless from the state, always try to expand the first row
        self.subprojects_mcv.sub_view.expand_first_item()

        # set the split sizes from the user
        _sizes = self.tik.user.split_sizes or [291, 180, 290, 291]
        self.splitter.setSizes(_sizes)

        # # if there is only a single subproject, then select the first one
        # if self.subprojects_mcv.sub_view.row_count() == 1:
        #     self.subprojects_mcv.sub_view.select_first_item()

        # self.tasks_mcv.refresh()
        # self.subprojects_mcv.sub_view.select_first_item()
        # self.refresh_project()

    def initialize_mcv(self):
        self.project_mcv = TikProjectLayout(self.tik.project)
        self.project_layout.addLayout(self.project_mcv)

        self.user_mcv = TikUserLayout(self.tik.user)
        self.user_layout.addLayout(self.user_mcv)

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
        self.categories_mcv.mode_changed.connect(self.set_buttons_visibility)
        self.categories_mcv.work_tree_view.version_created.connect(self._ingest_success)
        self.categories_mcv.work_tree_view.doubleClicked.connect(self.load_work)
        self.categories_mcv.work_tree_view.load_event.connect(self.load_work)
        self.categories_mcv.work_tree_view.import_event.connect(self.load_work)


    def on_double_click(self, event):
        """Double click event for the work tree view"""
        print(event)

    def set_last_selection(self):
        """Set the last selections for the user"""
        self.tik.user.last_project = self.tik.project.name
        # get the currently selected subproject
        _subproject_item = self.subprojects_mcv.sub_view.get_selected_item()
        if _subproject_item:
            self.tik.user.last_subproject = _subproject_item.subproject.id
            _task_item = self.tasks_mcv.task_view.get_selected_item()
            if _task_item:
                # self.tik.user.last_task = _task_item.task.reference_id
                self.tik.user.last_task = _task_item.task.id
                # Do we care?
                _category_index = self.categories_mcv.get_category_index()
                # we can always safely write the category index
                self.tik.user.last_category = _category_index
                _work_item = self.categories_mcv.work_tree_view.get_selected_item()
                if _work_item:
                    self.tik.user.last_work = _work_item.work.id
                    _version_nmb = self.versions_mcv.get_selected_version()
                    # we can always safely write the version number
                    self.tik.user.last_version = _version_nmb

        self.tik.user.split_sizes = self.splitter.sizes()

    # override the closeEvent to save the window state
    def closeEvent(self, event):
        self.tik.user.last_subproject = None
        self.tik.user.last_task = None
        self.tik.user.last_category = None
        self.tik.user.last_work = None
        self.tik.user.last_version = None

        self.set_last_selection()

        # set the expanded state of the subproject tree
        self.tik.user.expanded_subprojects = self.subprojects_mcv.sub_view.get_expanded_state()

        self.tik.user.resume.apply_settings()
        a = QtWidgets.QApplication.allWidgets()
        event.accept()

    def set_buttons_visibility(self, mode):
        """Set the visibility of the buttons layout based on the mode."""

        if mode == 0:
            self.work_buttons_frame.show()
            self.publish_buttons_frame.hide()
        else:
            self.work_buttons_frame.hide()
            self.publish_buttons_frame.show()

    def build_buttons(self):
        "Build the buttons"

        # Work buttons
        save_new_work_btn = TikButton("Save New Work")
        save_new_work_btn.setMinimumSize(150, 40)
        save_version_btn = TikButton("Save Version")
        save_version_btn.setMinimumSize(150, 40)
        ingest_version_btn = TikButton("Ingest Version")
        ingest_version_btn.setMinimumSize(150, 40)
        load_btn = TikButton("Load")
        load_btn.setMinimumSize(150, 40)

        self.work_buttons_layout.addWidget(save_new_work_btn)
        self.work_buttons_layout.addWidget(save_version_btn)
        self.work_buttons_layout.addWidget(ingest_version_btn)
        self.work_buttons_layout.addStretch(1)
        self.work_buttons_layout.addWidget(load_btn)

        # Publish buttons
        reference_btn = TikButton("Reference")
        reference_btn.setMinimumSize(150, 40)

        self.publish_buttons_layout.addStretch(1)
        self.publish_buttons_layout.addWidget(reference_btn)

        # SIGNALS
        load_btn.clicked.connect(self.load_work)
        # load_btn.clicked.connect(self.test)
        save_version_btn.clicked.connect(self.on_new_version)
        ingest_version_btn.clicked.connect(self.on_ingest_version)
        save_new_work_btn.clicked.connect(self.on_new_work)

    def build_bars(self):
        """Build the menu bar."""
        menu_bar = QtWidgets.QMenuBar(self, geometry=QtCore.QRect(0, 0, 1680, 18))
        self.setMenuBar(menu_bar)
        file_menu = menu_bar.addMenu("File")
        tools_menu = menu_bar.addMenu("Tools")
        help_menu = menu_bar.addMenu("Help")

        # File Menu
        create_project = QtWidgets.QAction("&Create New Project", self)
        file_menu.addAction(create_project)
        set_project = QtWidgets.QAction("&Set Project", self)
        file_menu.addAction(set_project)
        file_menu.addSeparator()
        new_user = QtWidgets.QAction("&Add New User", self)
        file_menu.addAction(new_user)
        users_manager = QtWidgets.QAction("&Users Manager", self)
        file_menu.addAction(users_manager)
        file_menu.addSeparator()
        user_login = QtWidgets.QAction("&User Login", self)
        file_menu.addAction(user_login)
        exit_action = QtWidgets.QAction("&Exit", self)
        file_menu.addAction(exit_action)

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

        # STATUS BAR
        self.status_bar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.status_bar)

        # SIGNALS
        create_project.triggered.connect(self.on_create_new_project)
        new_user.triggered.connect(self.on_add_new_user)
        user_login.triggered.connect(self.on_login)
        set_project.triggered.connect(self.on_set_project)
        exit_action.triggered.connect(self.close)

    def test(self):
        """Test function."""
        # print("testing")
        # # _item = self.tasks_mcv.task_view.get_selected_item()
        # # print(_item)
        # # self.subprojects_mcv.sub_view.get_tasks(_index)
        # from time import time
        # start = time()
        # self.subprojects_mcv.sub_view.get_tasks()
        # end = time()
        # print("Scanning tasks took {0} seconds".format(end - start))

        print("Subprojects:")
        print(self.subprojects_mcv.sub_view.get_items_count())
        print("Tasks:")
        print(self.tasks_mcv.task_view.get_items_count())
        self.tasks_mcv.task_view.select_first_item()
        # print(_index)
        # self.refresh_subprojects()

        # import os
        # print("test")
        # project_path = self.tik.project.absolute_path
        # test_file_path = self.tik.dcc.get_scene_file()
        # # get relative path from project
        # print(test_file_path)
        # test_path = os.path.dirname(test_file_path)
        # relative_path = os.path.relpath(test_path, project_path)
        # print(relative_path)
        # database_path = self.tik.project.get_abs_database_path(relative_path)
        # print(database_path)

    def load_work(self, event=None):
        """Load the selected work or publish version."""
        # get the work item
        selected_work_item = self.categories_mcv.work_tree_view.get_selected_item()
        if not selected_work_item:
            self.feedback.pop_info(title="No work selected.", text="Please select a work to load.", critical=True)
            return
        # get the version
        selected_version = self.versions_mcv.get_selected_version()

        selected_work_item.work.load_version(selected_version)

        # TODO: implement load work

    def import_work(self):
        """Import a work into the project."""
        selected_work_item = self.categories_mcv.work_tree_view.get_selected_item()
        if not selected_work_item:
            self.feedback.pop_info(title="No work selected.", text="Please select a work to import.", critical=True)
            return
        # get the version
        selected_version = self.versions_mcv.get_selected_version()

        print(selected_work_item)
        print(selected_version)
        print("Not implemented yet.")
        # TODO: implement import work

    def _ingest_success(self):
        """Callback function for the ingest success event."""
        self.refresh_versions()
        self.status_bar.showMessage("New version ingested successfully.", 5000)

    def on_ingest_version(self):
        """Iterate a version over the selected work in the ui."""
        if not self._pre_check(level=1):
            return
        # get the selected work. If no work is selected, return
        selected_work_item = self.categories_mcv.work_tree_view.get_selected_item()
        if not selected_work_item:
            self.feedback.pop_info(title="No work selected.", text="Please select a work to ingest a version into.", critical=True)
            return
        dialog = NewVersionDialog(work_object=selected_work_item.work, parent=self, ingest=True)
        state = dialog.exec_()
        if state:
            self._ingest_success()

    def on_new_work(self):
        """Create a new work."""
        if not self._pre_check(level=1):
            return

        # first try to get the active category, and reach the task and subproject
        category = self.categories_mcv.get_active_category()
        if category:
            task = category.parent_task
            subproject = task.parent_sub
        else:
            task = None
            subproject = self.subprojects_mcv.get_active_subproject()
            existing_tasks = subproject.scan_tasks()
            if not existing_tasks:
                self.feedback.pop_info(title="No tasks found.", text="Selected Sub-object does not have any tasks under it.\nPlease create a task before creating a work.", critical=True)
                return
        print(category, task, subproject)
        # print(category.name, task.path, subproject.path)
        # print(selected_category_object, selected_task_item, selected_subproject_item)

        # if selected_subproject_item:
        #     subproject = selected_subproject_item.subproject
        #     if selected_task_item:
        #         task = selected_task_item.task

        dialog = NewWorkDialog(self.tik, parent=self, subproject=subproject, task=task, category=category)
        state = dialog.exec_()
        if state:
            self.set_last_selection()
            self.refresh_versions()
            self.status_bar.showMessage("New work created successfully.", 5000)
            self.resume_last_selection()

    def on_new_version(self):
        """Create a new version."""
        if not self._pre_check(level=1):
            return
        scene_file_path = self.tik.dcc.get_scene_file()
        if not scene_file_path:
            self.feedback.pop_info(title="Scene file cannot be found.", text="Scene file cannot be found. Please either save your scene by creating a new work or ingest it into an existing one.", critical=True)
            return
        _work = self.tik.project.find_work_by_absolute_path(scene_file_path)

        if not _work:
            self.feedback.pop_info(title="Work object cannot be found.", text="Work cannot be found. Versions can only saved on work objects.\nIf there is no work associated with current scene either create a work or use the ingest method to save it into an existing work", critical=True)
            return

        dialog = NewVersionDialog(work_object=_work, parent=self)
        state = dialog.exec_()
        if state:
            self.set_last_selection()
            self.refresh_tasks()
            self.status_bar.showMessage("New version created successfully.", 5000)
            self.resume_last_selection()

    def refresh_project(self):
        """Refresh the project ui."""
        self.project_mcv.refresh()
        self.refresh_subprojects()
        # self.subprojects_mcv.sub_view.select_first_item()

    def refresh_subprojects(self):
        """Refresh the subprojects' ui."""
        self.subprojects_mcv.refresh()
        self.refresh_tasks()

    def refresh_tasks(self):
        """Refresh the tasks' ui."""
        # self.tasks_mcv.refresh()
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
        # dialog.show()
        if dialog.exec_():
            self.tik.project = dialog.main_object
            self.status_bar.showMessage("Set project successfully")
        self.refresh_project()

    def on_create_new_project(self):
        """Create a new project."""
        if not self._pre_check(level=3):
            return
        dialog = NewProjectDialog(self.tik, parent=self)
        state = dialog.exec_()
        if state:
            self.refresh_project()
            self.status_bar.showMessage("Project created successfully")

    def on_add_new_user(self):
        if not self._pre_check(level=3):
            return
        dialog = NewUserDialog(self.tik.user, parent=self)
        state = dialog.exec_()
        if state:
            self.status_bar.showMessage("User created successfully")

    def on_login(self):
        """Login."""
        dialog = LoginDialog(self.tik.user, parent=self)
        dialog.show()

    def _pre_check(self, level):
        """Check for permissions before drawing the dialog."""
        # new projects can be created by users with level 3
        if self.tik.project.check_permissions(level=level) == -1:
            msg, _type = self.tik.log.get_last_message()
            self.feedback.pop_info(title="Permissions", text=msg)
            return False
        return True


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    # launch()
    # main = MainUI()
    # main.show()
    from time import time
    start = time()
    launch()
    end = time()
    print("Took {0} seconds".format(end - start))
    # main.test()
    # main.on_create_new_project()
    sys.exit(app.exec_())
