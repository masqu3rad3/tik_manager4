"""Custom widgets for setting / displaying projects"""

from tik_manager4.ui.Qt import QtWidgets, QtCore
from tik_manager4.ui.dialog.project_dialog import SetProjectDialog
from tik_manager4.ui.widgets.common import TikButton
from tik_manager4.ui import pick

class TikProjectWidget(QtWidgets.QWidget):
    """Widget for displaying project information"""

    project_set = QtCore.Signal(str)

    def __init__(self, main_object, parent=None):
        super().__init__()
        self.parent = parent
        self.main_object = main_object

        self.layout = TikProjectLayout(main_object, parent=self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.layout.set_project_btn.clicked.connect(self.set_project)
        self.layout.recent_projects_btn.clicked.connect(self.set_recent_project)

    def refresh(self):
        """Refresh the project path"""
        self.layout.refresh()

    def set_project(self):
        """Set the project"""
        return self.layout.set_project()

    def set_recent_project(self):
        """Set the recent project"""
        return self.layout.set_recent_project()

class TikProjectLayout(QtWidgets.QHBoxLayout):
    """Layout for displaying project information"""

    project_set = QtCore.Signal(str)

    def __init__(self, main_object, parent=None):
        super().__init__()
        self.parent = parent
        self.main_object = main_object

        self.management_icon = QtWidgets.QLabel()
        self.management_icon.setScaledContents(True)
        self.addWidget(self.management_icon)

        _project_lbl = QtWidgets.QLabel()
        _project_lbl.setText("Project: ")
        self.addWidget(_project_lbl)

        self._project_path_le = QtWidgets.QLineEdit()
        self._project_path_le.setText(main_object.project.absolute_path)
        # make it read only
        self._project_path_le.setReadOnly(True)
        self.addWidget(self._project_path_le)

        self.set_project_btn = TikButton()
        self.set_project_btn.setText("SET")
        self.set_project_btn.setToolTip("Opens up Set Project Dialog")
        self.addWidget(self.set_project_btn)

        self.recent_projects_btn = TikButton()
        self.recent_projects_btn.setText("R")
        self.recent_projects_btn.setToolTip("Set recent project")
        self.recent_projects_btn.setMaximumWidth(30)
        self.addWidget(self.recent_projects_btn)

        self.set_project_btn.clicked.connect(self.set_project)
        self.recent_projects_btn.clicked.connect(self.set_recent_project)

        self._set_management_icon()

    def _set_management_icon(self):
        """Set the management icon which indicates if the project is managed or not."""
        management_platform_name = self.main_object.project.settings.get(
            "management_platform", "tik"
        )
        logo = f"logo-{management_platform_name}.png"
        # set the size to 32x32
        self.management_icon.setPixmap(pick.pixmap(logo))
        self.management_icon.setFixedSize(40, 40)


    def refresh(self):
        """Refresh the project path"""
        self._project_path_le.setText(self.main_object.project.absolute_path)
        self.main_object.globalize_management_platform() # reinitialize the main object
        self._set_management_icon()


    def __register_project(self, project_name):
        """Register the project to the user settings and update the UI."""
        self.main_object.user.last_project = project_name
        self.main_object.user.resume.apply_settings()
        self.refresh()
        self.project_set.emit(f"{project_name} set successfully.")

    def set_project(self):
        """Set the project"""
        dialog = SetProjectDialog(self.main_object, parent=self.parent)
        state = dialog.exec_()
        # state = dialog.show()
        if state:
            self.__register_project(dialog.main_object.project.name)
        else:
            self.project_set.emit("Canceled setting project.")
        return dialog.main_object.project.name

    def set_recent_project(self):
        """Set the recent project"""
        dialog = SetProjectDialog(self.main_object, parent=self.parent)
        if dialog.recents_pop_menu():
            self.__register_project(dialog.main_object.project.name)
        return dialog.main_object.project.name
