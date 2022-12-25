"""Dialog for new subproject creation."""
import sys
from tik_manager4.core.settings import Settings
from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
from tik_manager4.ui import utils
from tik_manager4.ui.dialog import feedback
from tik_manager4.ui.widgets.settings_layout import SettingsLayout

# if __name__ == '__main__':
#     app = QtWidgets.QApplication(sys.argv)

class NewSubproject(QtWidgets.QDialog):
    def __init__(self, project_object, parent_sub=None, parent=None, *args, **kwargs):
        """
        Dialog for new subproject creation.

        """
        super(NewSubproject, self).__init__(parent=parent, *args, **kwargs)
        self.tik_project = project_object
        self._parent_sub = parent_sub or project_object
        self.parent = parent
        self._feedback = feedback.Feedback(parent=self)
        self.settings = Settings()
        self.setWindowTitle("New Subproject")
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setFixedSize(600, 400)
        self.setModal(True)
        self._init_ui()

        self._new_subproject = None

    def populate_settings(self):
        self.settings.add_property("name", {
            "type": "string",
            "value": "",
        })
        self.settings.add_property("path", {
            "type": "string",
            "value": "",
        })
        self.settings.add_property("description", {
            "type": "string",
            "value": "",
        })
        self.settings.add_property("parent", {
            "type": "string",
            "value": self._parent_sub.name,
        })
        self.settings.add_property("subprojects", {
            "type": "list",
            "value": [],
        })
        self.settings.add_property("tasks", {
            "type": "list",
            "value": [],
        })
        self.settings.add_property("assets", {
            "type": "list",
            "value": [],
        })
        self.settings.add_property("sequences", {
            "type": "list",
            "value": [],
        })
        self.settings.add_property("shots", {
            "type": "list",
            "value": [],
        })
    def _init_ui(self):

        self.main_layout = QtWidgets.QVBoxLayout(self)

        self.settings_layout = SettingsLayout(self.settings, parent=self)
        self.main_layout.addLayout(self.settings_layout)

        self.form_layout = QtWidgets.QFormLayout()
        self.main_layout.addLayout(self.form_layout)

        self.name_le = utils.create_row(self.form_layout, "Name: ", QtWidgets.QLineEdit)

        self.path_le = utils.create_row(self.form_layout, "Path: ", QtWidgets.QLineEdit, text=self._parent_sub.path)
        self.resolution_lbl = QtWidgets.QLabel("Resolution Override: ")
        self.resolution_hlay = QtWidgets.QHBoxLayout()
        self.resolution_hlay.setAlignment(QtCore.Qt.AlignLeft)
        self.resolution_override_cb = QtWidgets.QCheckBox()
        self.resolution_hlay.addWidget(self.resolution_override_cb)
        self.resolution_d_hlay = QtWidgets.QHBoxLayout()
        self.resolution_d_hlay.setAlignment(QtCore.Qt.AlignLeft)
        self.resolution_hlay.addLayout(self.resolution_d_hlay)
        self.resolution_x_sp = QtWidgets.QSpinBox()
        self.resolution_y_sp = QtWidgets.QSpinBox()
        self.resolution_d_hlay.addWidget(self.resolution_x_sp)
        self.resolution_d_hlay.addWidget(self.resolution_y_sp)
        self.resolution_x_sp.setRange(1, 99999)
        self.resolution_y_sp.setRange(1, 99999)
        self.resolution_x_sp.setValue(self._parent_sub.resolution[0])
        self.resolution_y_sp.setValue(self._parent_sub.resolution[1])
        self.resolution_x_sp.setFixedWidth(100)
        self.resolution_y_sp.setFixedWidth(100)
        self.resolution_x_sp.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.resolution_y_sp.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.form_layout.addRow(self.resolution_lbl, self.resolution_hlay)

        self.fps_lbl = QtWidgets.QLabel("FPS: ")
        self.fps_sp = QtWidgets.QSpinBox()
        self.fps_sp.setValue(self._parent_sub.fps)
        self.fps_sp.setRange(1, 99999)
        self.fps_sp.setFixedWidth(100)
        self.fps_sp.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.form_layout.addRow(self.fps_lbl, self.fps_sp)

        self.mode_lbl = QtWidgets.QLabel("Mode: ")
        self.mode_cb = QtWidgets.QComboBox()
        self.mode_cb.addItems(["None", "Asset", "Shot"])
        # select the mode of the parent subproject
        if self._parent_sub.mode == "asset":
            self.mode_cb.setCurrentIndex(1)
        elif self._parent_sub.mode == "shot":
            self.mode_cb.setCurrentIndex(2)
        else:
            self.mode_cb.setCurrentIndex(0)
        self.form_layout.addRow(self.mode_lbl, self.mode_cb)

        # create a button box
        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.main_layout.addWidget(self.button_box)

        # SIGNALS
        self.button_box.accepted.connect(self.create_subproject)
        self.button_box.rejected.connect(self.reject)

    def create_subproject(self):
        name = self.name_le.text()
        path = self.path_le.text()
        resolution = [self.resolution_x_sp.value(), self.resolution_y_sp.value()]
        fps = self.fps_sp.value()
        mode = self.mode_cb.currentText()
        sub = self.tik_project.create_sub_project(str(name), parent_path=path, resolution=resolution, fps=fps, mode=mode)

        if sub != -1:
            self._new_subproject = sub
            self.accept()
        else:
            msg, title = self.tik_project.log.get_last_message()
            self._feedback.pop_info(title, msg, critical=True)

    def get_created_subproject(self):
        return self._new_subproject


# test new subproject dialog
if __name__ == "__main__":
    import sys
    import os
    import tik_manager4

    app = QtWidgets.QApplication(sys.argv)

    test_project_path = os.path.join(os.path.expanduser("~"), "t4_test_manual_DO_NOT_USE")
    tik = tik_manager4.initialize("Standalone")
    tik.user.set("Admin", "1234")
    tik.project.set(test_project_path)
    dialog = NewSubproject(tik.project)
    dialog.show()
    app.exec_()

    sys.exit(app.exec_())