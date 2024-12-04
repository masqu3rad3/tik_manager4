from pathlib import Path


from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.ui.dialog.feedback import Feedback
from tik_manager4.ui.widgets.pop import WaitDialog
from tik_manager4.ui.widgets.common import TikButtonBox
from tik_manager4.ui.widgets import path_browser
from tik_manager4.management.shotgrid.ui.mcv import SgProjectPickWidget


class CreateFromShotgridDialog(QtWidgets.QDialog):
    """Create a new project from the management system."""

    def __init__(self, management_handler, parent=None):
        super().__init__(parent=parent)
        all_widgets = QtWidgets.QApplication.allWidgets()
        for entry in all_widgets:
            try:
                if entry.objectName() == "CreateFromShotgridDialog":
                    entry.close()
                    entry.deleteLater()
            except (AttributeError, TypeError):
                pass

        self.tik = management_handler.tik_main
        self.feedback = Feedback(parent=self)
        self.handler = management_handler
        self.setWindowTitle("Create New Project from Shotgrid")
        self.setObjectName("CreateFromShotgridDialog")
        self.setModal(True)
        self.setMinimumSize(300, 200)
        self.resize(600, 650)

        self.master_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.master_layout)
        self.project_root_pathb = None
        self.set_project_cb = None
        self.sg_project_pick_widget = None
        self.build_ui()

    def build_ui(self):
        """Build the UI."""
        # path browser
        path_browser_layout = QtWidgets.QHBoxLayout()
        self.master_layout.addLayout(path_browser_layout)
        path_browser_lbl = QtWidgets.QLabel("Projects Root :")
        path_browser_layout.addWidget(path_browser_lbl)
        _value = Path(self.tik.project.absolute_path).parent.as_posix()
        self.project_root_pathb = path_browser.PathBrowser("project_root", value=_value)
        path_browser_layout.addWidget(self.project_root_pathb)

        self.sg_project_pick_widget = SgProjectPickWidget(self.handler, parent=self)
        self.master_layout.addWidget(self.sg_project_pick_widget)

        # create a button box as "create" and "cancel"
        button_box = TikButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )

        button_layout = QtWidgets.QHBoxLayout()
        self.master_layout.addLayout(button_layout)
        create_btn = button_box.button(QtWidgets.QDialogButtonBox.Ok)
        create_btn.setText("Create")
        button_layout.addWidget(button_box)

        self.set_project_cb = QtWidgets.QCheckBox("Set After Creation")
        self.set_project_cb.setChecked(True)
        button_layout.addWidget(self.set_project_cb)

        # SIGNALS
        button_box.accepted.connect(self.execute)
        button_box.rejected.connect(self.close)

    def execute(self):
        """Create the project."""
        project_root = self.project_root_pathb.widget.text()
        project_id = self.sg_project_pick_widget.get_selected_project_id()
        if project_id:
            self.wait_dialog = WaitDialog(
                message="Creating project from Shotgrid...",
                parent=self,
            )
            self.wait_dialog.display()

            ret = self.handler.create_from_project(
                project_root, project_id, set_project=self.set_project_cb.isChecked()
            )
            self.wait_dialog.kill()
            if not ret:
                msg, _msg_type = self.tik.log.get_last_message()
                self.feedback.pop_info(
                    title="Error Creating Project", text=msg, critical=True
                )
                return
                # get the last log message from the logger
        else:
            self.feedback.pop_info(
                title="No Project Selected",
                text="Please select a project from the list.",
                critical=True
            )
            return
        self.accept()