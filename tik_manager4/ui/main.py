"""Main UI for Tik Manager 4.

Maya test:

from importlib import reload
import sys
p_path = "D:\\dev\\tik_manager4\\"
if p_path not in sys.path:
    sys.path.append(p_path)

kill_list = []
for name, _module in sys.modules.items():
    if name.startswith("tik_manager4"):
        kill_list.append(name)
for x in kill_list:
    sys.modules.pop(x)

# from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
from tik_manager4.ui import main
reload(main)
main.launch(dcc="Maya")
"""
import logging

from tik_manager4.core import utils
from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui

from tik_manager4.ui.dialog.publish_dialog import PublishSceneDialog
from tik_manager4.ui.mcv.user_mcv import TikUserLayout
from tik_manager4.ui.mcv.project_mcv import TikProjectLayout
from tik_manager4.ui.mcv.subproject_mcv import TikSubProjectLayout
from tik_manager4.ui.mcv.task_mcv import TikTaskLayout
from tik_manager4.ui.mcv.category_mcv import TikCategoryLayout
from tik_manager4.ui.mcv.version_mcv import TikVersionLayout
from tik_manager4.ui.dialog.project_dialog import NewProjectDialog, SetProjectDialog
from tik_manager4.ui.dialog.user_dialog import LoginDialog, NewUserDialog
from tik_manager4.ui.dialog.work_dialog import NewWorkDialog, NewVersionDialog
from tik_manager4.ui.dialog.preview_dialog import PreviewDialog
from tik_manager4.ui.dialog.settings_dialog import SettingsDialog
from tik_manager4.ui.dialog.feedback import Feedback
from tik_manager4.ui.widgets.common import TikButton, HorizontalSeparator
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
    return m


class MainUI(QtWidgets.QMainWindow):
    def __init__(self, main_object, **kwargs):
        super(MainUI, self).__init__(**kwargs)
        self.tik = main_object

        self.setWindowTitle(WINDOW_NAME)
        self.setObjectName(WINDOW_NAME)

        self.feedback = Feedback(self)
        # set window size
        self.resize(1200, 800)
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)

        # set style
        _style_file = pick.style_file()
        self.setStyleSheet(str(_style_file.readAll(), "utf-8"))

        # define layouts
        self.master_layout = QtWidgets.QVBoxLayout(self.central_widget)

        self.title_layout = QtWidgets.QHBoxLayout()

        project_user_layout = QtWidgets.QHBoxLayout()

        self.project_layout = QtWidgets.QHBoxLayout()
        self.user_layout = QtWidgets.QHBoxLayout()

        project_user_layout.addLayout(self.project_layout)
        line = HorizontalSeparator()
        project_user_layout.addWidget(line)

        project_user_layout.addLayout(self.user_layout)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.splitter = QtWidgets.QSplitter(
            self.central_widget, orientation=QtCore.Qt.Horizontal
        )
        self.splitter.setHandleWidth(5)
        self.splitter.setProperty("vertical", True)

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

        self.master_layout.addLayout(self.title_layout)
        self.master_layout.addLayout(project_user_layout)
        self.master_layout.addLayout(self.main_layout)

        self.master_layout.addWidget(self.work_buttons_frame)

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
        self.resume_last_state()
        #
        self.status_bar.showMessage("Status | Ready")

    def resume_last_state(self):
        """Resume the last selection from the user settings."""
        # project is getting handled by the project object.
        # subproject

        subproject_id = self.tik.user.last_subproject
        if subproject_id:
            state = self.subprojects_mcv.sub_view.select_by_id(subproject_id)
            if state:
                # if its successfully set, then select the last selected task
                task_id = self.tik.user.last_task
                if task_id:
                    state = self.tasks_mcv.task_view.select_by_id(task_id)
                    if state:
                        # if its successfully set, then select the last category
                        category_index = self.tik.user.last_category or 0
                        self.categories_mcv.set_category_by_index(category_index)
                        work_id = self.tik.user.last_work
                        if work_id:
                            state = self.categories_mcv.work_tree_view.select_by_id(
                                work_id
                            )
                            if state:
                                # if its successfully set, then select the last version
                                version_id = self.tik.user.last_version
                                if version_id:
                                    self.versions_mcv.set_version(version_id)
                    else:
                        # if the task cannot be set, then select the first one
                        self.tasks_mcv.task_view.select_first_item()
                else:
                    # if there is no task, then select the first one
                    self.tasks_mcv.task_view.select_first_item()
        else:
            # if there are no subprojects, then select the first one
            self.subprojects_mcv.sub_view.select_first_item()
            LOG.info("No subproject found, selecting the first one.")

            # if there is no task, then select the first one
            self.tasks_mcv.task_view.select_first_item()

        self.subprojects_mcv.sub_view.set_expanded_state(
            self.tik.user.expanded_subprojects
        )

        # regardless from the state, always try to expand the first row
        self.subprojects_mcv.sub_view.expand_first_item()

        # set the split sizes from the user
        _sizes = self.tik.user.split_sizes or [291, 180, 290, 291]
        self.splitter.setSizes(_sizes)

        self.subprojects_mcv.sub_view.show_columns(
            self.tik.user.visible_columns.get("subprojects", [])
        )
        self.tasks_mcv.task_view.show_columns(
            self.tik.user.visible_columns.get("tasks", [])
        )
        self.categories_mcv.work_tree_view.show_columns(
            self.tik.user.visible_columns.get("categories", [])
        )

        self.subprojects_mcv.sub_view.set_column_sizes(
            self.tik.user.column_sizes.get("subprojects", {})
        )
        self.tasks_mcv.task_view.set_column_sizes(
            self.tik.user.column_sizes.get("tasks", {})
        )
        self.categories_mcv.work_tree_view.set_column_sizes(
            self.tik.user.column_sizes.get("categories", {})
        )

    def initialize_mcv(self):
        """Initialize the model-control-views."""
        self.project_mcv = TikProjectLayout(self.tik.project)
        self.project_layout.addLayout(self.project_mcv)

        self.user_mcv = TikUserLayout(self.tik.user)
        self.user_layout.addLayout(self.user_mcv)

        self.subprojects_mcv = TikSubProjectLayout(self.tik.project)
        self.subproject_tree_layout.addLayout(self.subprojects_mcv)

        self.tasks_mcv = TikTaskLayout()
        self.tasks_mcv.task_view.hide_columns(["id", "path"])
        self.task_tree_layout.addLayout(self.tasks_mcv)

        self.categories_mcv = TikCategoryLayout()
        self.categories_mcv.work_tree_view.hide_columns(["id", "path"])
        self.category_layout.addLayout(self.categories_mcv)
        # if it is houdini, make an exception on the category tab widget
        if self.tik.dcc.name == "Houdini":
            self.categories_mcv.category_tab_widget.setMaximumSize(QtCore.QSize(16777215, 30))

        self.versions_mcv = TikVersionLayout(parent=self)
        self.version_layout.addLayout(self.versions_mcv)

        self.project_mcv.set_project_btn.clicked.connect(self.on_set_project)
        self.project_mcv.recent_projects_btn.clicked.connect(self.on_recent_projects)
        self.subprojects_mcv.sub_view.item_selected.connect(
            self.tasks_mcv.task_view.set_tasks
        )
        self.subprojects_mcv.sub_view.add_item.connect(
            self.tasks_mcv.task_view.add_tasks
        )
        self.tasks_mcv.task_view.item_selected.connect(self.categories_mcv.set_task)
        self.categories_mcv.work_tree_view.item_selected.connect(
            self.versions_mcv.set_base
        )
        # self.categories_mcv.mode_changed.connect(self.set_buttons_visibility)
        self.categories_mcv.work_tree_view.version_created.connect(self._ingest_success)
        # self.categories_mcv.work_tree_view.doubleClicked.connect(self.load_work)
        self.categories_mcv.work_tree_view.doubleClicked.connect(
            self.versions_mcv.on_load
        )
        # self.categories_mcv.work_tree_view.load_event.connect(self.load_work)
        self.categories_mcv.work_tree_view.load_event.connect(self.versions_mcv.on_load)
        # self.categories_mcv.work_tree_view.import_event.connect(self.import_work)
        self.categories_mcv.work_tree_view.import_event.connect(
            self.versions_mcv.on_import
        )
        self.versions_mcv.show_preview_btn.clicked.connect(self.on_show_preview)

    def set_last_state(self):
        """Set the last selections for the user"""
        self.tik.user.last_project = self.tik.project.name
        # get the currently selected subproject
        _subproject_item = self.subprojects_mcv.sub_view.get_selected_items()
        if _subproject_item:
            _subproject_item = _subproject_item[0]
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
                    self.tik.user.last_work = _work_item.tik_obj.id
                    _version_nmb = self.versions_mcv.get_selected_version()
                    # we can always safely write the version number
                    self.tik.user.last_version = _version_nmb

        self.tik.user.split_sizes = self.splitter.sizes()

        # get the visibilities of columns for mcvs
        columns_states = {
            "subprojects": self.subprojects_mcv.sub_view.get_visible_columns(),
            "tasks": self.tasks_mcv.task_view.get_visible_columns(),
            "categories": self.categories_mcv.work_tree_view.get_visible_columns(),
        }
        self.tik.user.visible_columns = columns_states

        column_sizes = {
            "subprojects": self.subprojects_mcv.sub_view.get_column_sizes(),
            "tasks": self.tasks_mcv.task_view.get_column_sizes(),
            "categories": self.categories_mcv.work_tree_view.get_column_sizes(),
        }
        self.tik.user.column_sizes = column_sizes

    # override the closeEvent to save the window state
    def closeEvent(self, event):
        """Override the close event to save the window state."""
        self.tik.user.last_subproject = None
        self.tik.user.last_task = None
        self.tik.user.last_category = None
        self.tik.user.last_work = None
        self.tik.user.last_version = None

        self.set_last_state()

        # set the expanded state of the subproject tree
        self.tik.user.expanded_subprojects = (
            self.subprojects_mcv.sub_view.get_expanded_state()
        )

        self.tik.user.resume.apply_settings()
        _ = QtWidgets.QApplication.allWidgets()
        event.accept()

    def build_buttons(self):
        "Build the buttons"

        # Work buttons
        save_new_work_btn = TikButton("Save New Work")
        save_new_work_btn.setMinimumSize(150, 40)
        increment_version_btn = TikButton("Increment Version")
        increment_version_btn.setMinimumSize(150, 40)
        ingest_version_btn = TikButton("Ingest Version")
        ingest_version_btn.setMinimumSize(150, 40)
        publish_scene_btn = TikButton("Publish")
        publish_scene_btn.setMinimumSize(150, 40)

        self.work_buttons_layout.addWidget(save_new_work_btn)
        self.work_buttons_layout.addWidget(increment_version_btn)
        self.work_buttons_layout.addWidget(ingest_version_btn)
        self.work_buttons_layout.addWidget(publish_scene_btn)
        self.work_buttons_layout.addStretch(1)
        increment_version_btn.clicked.connect(self.on_new_version)
        ingest_version_btn.clicked.connect(self.on_ingest_version)
        save_new_work_btn.clicked.connect(self.on_new_work)
        publish_scene_btn.clicked.connect(self.on_publish_scene)

    def build_bars(self):
        """Build the menu bar."""
        menu_bar = QtWidgets.QMenuBar(self, geometry=QtCore.QRect(0, 0, 680, 18))
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
        new_user = QtWidgets.QAction(pick.icon("user"), "&Add New User", self)
        file_menu.addAction(new_user)
        file_menu.addSeparator()
        save_new_work = QtWidgets.QAction(pick.icon("save"), "&Save New Work", self)
        file_menu.addAction(save_new_work)
        increment_version = QtWidgets.QAction("&Increment Version", self)
        file_menu.addAction(increment_version)
        ingest_version = QtWidgets.QAction("&Ingest Version", self)
        file_menu.addAction(ingest_version)
        publish_scene = QtWidgets.QAction("&Publish Scene", self)
        file_menu.addAction(publish_scene)
        file_menu.addSeparator()
        load_item = QtWidgets.QAction("&Load Item", self)
        file_menu.addAction(load_item)
        import_item = QtWidgets.QAction("&Import Item", self)
        file_menu.addAction(import_item)
        file_menu.addSeparator()
        settings_item = QtWidgets.QAction(
            pick.icon("settings"), "&Settings                    ", self
        )
        file_menu.addAction(settings_item)
        file_menu.addSeparator()
        user_login = QtWidgets.QAction(pick.icon("user"), "&User Login", self)
        file_menu.addAction(user_login)
        exit_action = QtWidgets.QAction("&Exit", self)
        file_menu.addAction(exit_action)

        # make the menu bar items wide enough to show the icons and all text
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
        settings_item.triggered.connect(self.on_settings)
        set_project.triggered.connect(self.on_set_project)
        exit_action.triggered.connect(self.close)

        save_new_work.triggered.connect(self.on_new_work)
        increment_version.triggered.connect(self.on_new_version)
        ingest_version.triggered.connect(self.on_ingest_version)
        publish_scene.triggered.connect(self.on_publish_scene)
        # load_item.triggered.connect(self.load_work)
        load_item.triggered.connect(self.versions_mcv.on_load)
        # import_item.triggered.connect(self.import_work)
        import_item.triggered.connect(self.versions_mcv.on_import)

        # check if the tik.main.dcc has a preview method
        if self.tik.dcc.preview_enabled:
            create_preview = QtWidgets.QAction(
                pick.icon("camera"), "&Create Preview", self
            )
            tools_menu.addAction(create_preview)
            create_preview.triggered.connect(self.on_create_preview)

        menu_bar.setMinimumWidth(menu_bar.sizeHint().width())

    def _ingest_success(self):
        """Callback function for the ingest success event."""
        self.refresh_versions()
        self.status_bar.showMessage("New version ingested successfully.", 5000)

    def on_settings(self):
        """Launch the settings dialog."""
        dialog = SettingsDialog(self.tik, parent=self)
        dialog.show()

    def on_publish_scene(self):
        """Bring up the publish scene dialog."""
        publish_dialog = PublishSceneDialog(self.tik.project, parent=self)
        publish_dialog.show()

    def on_ingest_version(self):
        """Iterate a version over the selected work in the ui."""
        if not self._pre_check(level=1):
            return
        # get the selected work. If no work is selected, return
        selected_work_item = self.categories_mcv.work_tree_view.get_selected_item()
        if not selected_work_item:
            self.feedback.pop_info(
                title="No work selected.",
                text="Please select a work to ingest a version into.",
                critical=True,
            )
            return
        self._new_version_pre_checks(selected_work_item.tik_obj)
        dialog = NewVersionDialog(
            work_object=selected_work_item.tik_obj, parent=self, ingest=True
        )
        state = dialog.exec_()
        if state:
            self._ingest_success()

    def __metadata_pre_checks(self, metadata):
        """Collection of pre-checks for the metadata method."""
        metadata_fps = metadata.get_value("fps", None)
        current_fps = self.tik.dcc.get_scene_fps()
        if metadata_fps and current_fps:  # if the dcc supports fps and metadata has a value
            if current_fps != metadata_fps:
                msg = f"The current fps ({current_fps}) does not match with the defined fps ({metadata_fps})."
                yield msg
        metadata_start_frame = metadata.get_value("start_frame", None)
        metadata_end_frame = metadata.get_value("end_frame", None)
        raw_frame_range = self.tik.dcc.get_ranges()
        start_mismatch = False
        end_mismatch = False
        if any([metadata_start_frame,
                metadata_end_frame]) and raw_frame_range:  # if the dcc supports range and metadata has a value
            if metadata_start_frame:
                if float(metadata_start_frame) != float(raw_frame_range[0]):
                    start_mismatch = True
            if metadata_end_frame:
                if float(metadata_end_frame) != float(raw_frame_range[-1]):
                    end_mismatch = True
            if start_mismatch or end_mismatch:
                msg = f"The current frame range ({raw_frame_range[0], raw_frame_range[-1]}) does not match with the defined frame range ({[metadata_start_frame, metadata_end_frame]})."
                yield msg

    def _new_work_pre_checks(self, subproject):
        """Collection of pre-checks for the new work method."""
        dcc_name = self.tik.project.guard.dcc
        current_dcc_version = self.tik.dcc.get_dcc_version()
        metadata_dcc_version = subproject.metadata.get_value(f"{dcc_name.lower()}_version", None)
        if metadata_dcc_version:
            if current_dcc_version != metadata_dcc_version:
                msg = f"The current dcc version ({current_dcc_version}) does not match with the defined dcc version ({metadata_dcc_version})."
                yield msg

        for msg in self.__metadata_pre_checks(subproject.metadata):
            yield msg


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
            # get the active task
            task = self.tasks_mcv.get_active_task()
            if not task:
                self.feedback.pop_info(
                    title="No tasks found.",
                    text="Selected Sub-object does not have any tasks under it.\n"
                    "Please create a task before creating a work.",
                    critical=True,
                )
                return
            subproject = task.parent_sub

        pre_checks = self._new_work_pre_checks(subproject)
        for check_msg in pre_checks:
            question = self.feedback.pop_question(
                title="Metadata Mismatch",
                text=f"{check_msg}\n\nDo you want to continue?",
                buttons=["continue", "cancel"]
            )
            if question == "cancel":
                return

        # if not self._new_work_pre_checks(subproject):
        #     return

        dialog = NewWorkDialog(
            self.tik, parent=self, subproject=subproject, task=task, category=category
        )
        state = dialog.exec_()
        if state:
            self.set_last_state()
            self.refresh_versions()
            self.status_bar.showMessage("New work created successfully.", 5000)
            self.resume_last_state()

    def _new_version_pre_checks(self, work_obj, metadata):
        """Collection of pre-checks for the new version method."""
        dcc_version_mismatch = work_obj.check_dcc_version_mismatch()
        if dcc_version_mismatch:
            msg = ("The current DCC version does not match the version of the work or metadata definition.\n\n"
                f"Current DCC version: {dcc_version_mismatch[1]}\n"
                f"Defined DCC version: {dcc_version_mismatch[1]}\n\n")
            yield msg

        for msg in self.__metadata_pre_checks(metadata):
            yield msg

    def on_new_version(self):
        """Create a new version."""
        if not self._pre_check(level=1):
            return
        scene_file_path = self.tik.dcc.get_scene_file()
        if not scene_file_path:
            self.feedback.pop_info(
                title="Scene file cannot be found.",
                text="Scene file cannot be found. "
                "Please either save your scene by creating a new work or "
                "ingest it into an existing one.",
                critical=True,
            )
            return
        work, _version = self.tik.project.find_work_by_absolute_path(scene_file_path)

        if not work:
            self.feedback.pop_info(
                title="Work object cannot be found.",
                text="Work cannot be found. Versions can only saved on work objects.\n"
                "If there is no work associated with current scene either create a work "
                "or use the ingest method to save it into an existing work",
                critical=True,
            )
            return

        # get the metadata for the checks.
        task_id = work.task_id
        parent_task = self.tik.project.find_task_by_id(task_id)
        metadata = parent_task.parent_sub.metadata
        pre_checks = self._new_version_pre_checks(work, metadata)
        for check_msg in pre_checks:
            question = self.feedback.pop_question(
                title="Metadata Mismatch",
                text=f"{check_msg}\n\nDo you want to continue?",
                buttons=["continue", "cancel"]
            )
            if question == "cancel":
                return


        dialog = NewVersionDialog(work_object=work, parent=self)
        state = dialog.exec_()
        if state:
            self.set_last_state()
            self.refresh_versions()
            self.status_bar.showMessage("New version created successfully.", 5000)
            self.resume_last_state()

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

    def on_create_preview(self):
        """Initiate a preview creation and launch the preview dialog."""
        # find the work by scene
        scene_file_path = self.tik.dcc.get_scene_file()
        if not scene_file_path:
            self.feedback.pop_info(
                title="Scene file cannot be found.",
                text="Scene file cannot be found. "
                "Please either save your scene by creating a new work or "
                "ingest it into an existing one.",
                critical=True,
            )
            return
        _work, _version = self.tik.project.find_work_by_absolute_path(scene_file_path)
        if not _work:
            self.feedback.pop_info(
                title="Work object cannot be found.",
                text="Work cannot be found. Versions can only saved on work objects.\n"
                "If there is no work associated with current scene either create a work "
                "or use the ingest method to save it into an existing work",
                critical=True,
            )
            return

        # find the task from the work
        _task = self.tik.project.find_task_by_id(_work.task_id)
        # get the resolution from the task (if any)
        _resolution = _task.parent_sub.metadata.get_value(
            "resolution", fallback_value=None
        )
        _range_start = _task.parent_sub.metadata.get_value(
            "start_frame", fallback_value=None
        )
        _range_end = _task.parent_sub.metadata.get_value(
            "end_frame", fallback_value=None
        )
        _range = [_range_start, _range_end]

        dialog = PreviewDialog(
            work_object=_work,
            version=_version,
            resolution=_resolution,
            range=_range,
            parent=self,
        )
        dialog.show()

    def on_show_preview(self):
        """Make a dropdown list for the available previews and play selected one."""

        # get the selected work object and the version
        _work_item = self.categories_mcv.work_tree_view.get_selected_item()
        _version_index = self.versions_mcv.get_selected_version()
        _version = _work_item.tik_obj.get_version(_version_index)

        preview_dict = _version.get("previews")
        if len(preview_dict.values()) == 1:
            abs_path = _work_item.tik_obj.get_abs_project_path(
                list(preview_dict.values())[0]
            )
            utils.execute(abs_path)
            return
        if not preview_dict:
            return
        zort_menu = QtWidgets.QMenu(parent=self)
        for z in list(preview_dict.keys()):
            tempAction = QtWidgets.QAction(z, self)
            zort_menu.addAction(tempAction)
            ## Take note about the usage of lambda "item=z" makes it possible using the loop, ignore -> for discarding emitted value
            tempAction.triggered.connect(
                lambda ignore=z, item=_work_item.tik_obj.get_abs_project_path(
                    preview_dict[z]
                ): utils.execute(str(item))
            )

        zort_menu.exec_((QtGui.QCursor.pos()))

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
    from time import time

    start = time()
    launch()
    end = time()
    print("Took {0} seconds".format(end - start))
    sys.exit(app.exec_())
