"""Custom widgets for setting / displaying projects"""

from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
from tik_manager4.ui.widgets.common import TikButton


class TikProjectLayout(QtWidgets.QHBoxLayout):
    """Layout for displaying project information"""

    def __init__(self, project_obj):
        super(TikProjectLayout, self).__init__()
        self.project_obj = project_obj

        # self.setContentsMargins(0, 0, 0, 0)
        # self.setSpacing(0)

        _project_lbl = QtWidgets.QLabel()
        _project_lbl.setText("Project: ")
        self.addWidget(_project_lbl)

        self._project_path_le = QtWidgets.QLineEdit()
        self._project_path_le.setText(project_obj.absolute_path)
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

        # SIGNALS
        self.set_project_btn.clicked.connect(self.on_set_project)
        self.recent_projects_btn.clicked.connect(self.on_recent_projects)

    def refresh(self):
        """Refresh the project path"""
        self._project_path_le.setText(self.project_obj.absolute_path)


    def on_set_project(self, project):
        """Set the project to display"""
        # TODO pop-up set project dialog
        pass
        # self._project_path_le.setText(project.name)
        # self._project_path.setText(project.path)

    def on_recent_projects(self):
        """Display recent projects"""
        # TODO pop-up recent projects floating dialog
        pass