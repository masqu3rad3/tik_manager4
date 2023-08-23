"""Dialog to create previews for the current scene."""

from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui

from tik_manager4.ui.widgets.validated_string import ValidatedString
from tik_manager4.ui.widgets import common

class PreviewDialog(QtWidgets.QDialog):
    def __init__(self, work_object, version, resolution=None, *args, **kwargs):
        super(PreviewDialog, self).__init__(*args, **kwargs)
        self.version = version
        self.work = work_object
        self.resolution = resolution or self.work.guard.project_settings.get_property("resolution", [1920, 1080])
        self.setWindowTitle("Create Preview")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.master_layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.master_layout)
        self.build_ui()

    def resolve_name(self):
        """Resolve the name of the preview."""
        _label = self.preview_name_le.text()
        _camera = self.cameras_combo.currentText()
        _version = self.version
        _resolved_name = self.work.resolve_name(_name)
        self.resolved_text.setText(_resolved_name)

    def build_ui(self):
        """Build the UI."""
        self.resolved_text = common.ResolvedText()
        form_layout = QtWidgets.QFormLayout()
        self.master_layout.addLayout(form_layout)
        preview_name_lbl = QtWidgets.QLabel("Preview Label: ")
        self.preview_name_le = ValidatedString("test", allow_empty=True)
        form_layout.addRow(preview_name_lbl, self.preview_name_le)

        camera_lbl = QtWidgets.QLabel("Camera: ")
        self.cameras_combo = QtWidgets.QComboBox()
        self.cameras_combo.addItems(self.work._dcc_handler.get_scene_cameras() or [])
        form_layout.addRow(camera_lbl, self.cameras_combo)

        resolution_lbl = QtWidgets.QLabel("Resolution: ")
        # try to get the resolution from the parent subproject
        resolution_layout = QtWidgets.QHBoxLayout()
        self.resolution_x_sp = QtWidgets.QSpinBox()
        self.resolution_x_sp.setRange(1, 99999)
        self.resolution_x_sp.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.resolution_x_sp.setValue(self.resolution[0])
        self.resolution_y_sp = QtWidgets.QSpinBox()
        self.resolution_y_sp.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.resolution_y_sp.setRange(1, 99999)
        self.resolution_y_sp.setValue(self.resolution[1])
        resolution_layout.addWidget(self.resolution_x_sp)
        resolution_layout.addWidget(self.resolution_y_sp)
        form_layout.addRow(resolution_lbl, resolution_layout)

        # add a button box to create the preview or cancel
        button_box = common.TikButtonBox(parent=self)
        self.master_layout.addWidget(button_box)
        _create_preview_btn = button_box.addButton(
            "Create Preview", QtWidgets.QDialogButtonBox.AcceptRole
        )
        _cancel_btn = button_box.addButton("Cancel", QtWidgets.QDialogButtonBox.RejectRole)

        # SIGNALS
        button_box.accepted.connect(self.create_preview)
        button_box.rejected.connect(self.close)

    def create_preview(self):
        """Create the preview."""
        _name = self.preview_name_le.text()
        _camera = self.cameras_combo.currentText()
        _resolution = [self.resolution_x_sp.value(), self.resolution_y_sp.value()]
        print(_name, _camera, _resolution)
        self.work.make_preview(self.version, _name, _camera, _resolution, settings=self.work.guard.project_settings)

# Test the dialog
if __name__ == "__main__":
    import sys
    import tik_manager4
    from tik_manager4.ui import pick

    app = QtWidgets.QApplication(sys.argv)
    tik = tik_manager4.initialize("Standalone")
    tik.user.set("Admin", "1234")
    # tik.user.set("Generic", "1234")
    all_tasks = tik.project.find_tasks_by_wildcard("*")
    for task in all_tasks:
        works = task.find_works_by_wildcard("*")
        if works:
            break
    work = works[0]
    dialog = PreviewDialog(work, 1)
    _style_file = pick.style_file()
    dialog.setStyleSheet(str(_style_file.readAll(), "utf-8"))
    dialog.show()
    sys.exit(app.exec_())



