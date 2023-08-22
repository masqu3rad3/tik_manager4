"""Dialog to create previews for the current scene."""

from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui

from tik_manager4.ui.widgets.validated_string import ValidatedString

class PreviewDialog(QtWidgets.QDialog):
    def __init__(self, work_object, *args, **kwargs):
        super(PreviewDialog, self).__init__(*args, **kwargs)
        self.work = work_object
        self.setWindowTitle("Create Preview")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.master_layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.master_layout)

    def build_ui(self):
        """Build the UI."""
        form_layout = QtWidgets.QFormLayout()
        preview_name_lbl = QtWidgets.QLabel("Preview Name: ")
        preview_name_le = ValidatedString()
        form_layout.addRow(preview_name_lbl, preview_name_le)

        camera_lbl = QtWidgets.QLabel("Camera: ")
        cameras_combo = QtWidgets.QComboBox()
        cameras_combo.addItems(self.work._dcc_handler.get_scene_cameras())
        form_layout.addRow(camera_lbl, cameras_combo)

        resolution_lbl = QtWidgets.QLabel("Resolution: ")
        # try to get the resolution from the parent subproject
        resolution = self.work.parent_subproject.resolution

