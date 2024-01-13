"""Dialog to create previews for the current scene."""

from tik_manager4.ui.Qt import QtWidgets, QtCore

from tik_manager4.ui.dialog import feedback
from tik_manager4.ui.widgets.validated_string import ValidatedString
from tik_manager4.ui.widgets import common

class PreviewDialog(QtWidgets.QDialog):
    def __init__(self, work_object, version, resolution=None, range=None, *args, **kwargs):
        super(PreviewDialog, self).__init__(*args, **kwargs)
        range = range or [1001, 1100]
        self.feedback = feedback.Feedback(parent=self)
        self.version = version
        self.work = work_object
        self.resolution = resolution or self.work.guard.project_settings.get_property("resolution", [1920, 1080])
        raw_ranges = self.work._dcc_handler.get_ranges()
        if raw_ranges:
            range_start = raw_ranges[0]
            range_end = raw_ranges[-1]
        else:
            range_start = 1001
            range_end = 1100
        _range = range or [range_start, range_end]
        self.range = [_range[0] or range_start, _range[1] or range_end]
        self.setWindowTitle("Create Preview")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.master_layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.master_layout)
        self.build_ui()

    def resolve_name(self, **kwargs):
        """Resolve the name of the preview."""
        _label = self.preview_name_le.text() or ""
        _camera = self.cameras_combo.currentText() or ""
        _version = self.version
        _resolved_name = self.work.resolve_preview_names(_version, _camera, label=_label)
        self.resolved_text.setText(_resolved_name[1])

    def build_ui(self):
        """Build the UI."""
        self.resolved_text = common.ResolvedText()
        self.master_layout.addWidget(self.resolved_text)

        form_layout = QtWidgets.QFormLayout()
        self.master_layout.addLayout(form_layout)
        preview_name_lbl = QtWidgets.QLabel("Preview Label: ")
        self.preview_name_le = ValidatedString("test", allow_empty=True)
        form_layout.addRow(preview_name_lbl, self.preview_name_le)

        camera_lbl = QtWidgets.QLabel("Camera: ")
        self.cameras_combo = QtWidgets.QComboBox()
        scene_cameras = self.work._dcc_handler.get_scene_cameras()
        if scene_cameras:
            self.cameras_combo.addItems(list(scene_cameras.keys()))
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

        range_lbl = QtWidgets.QLabel("Range: ")
        range_layout = QtWidgets.QHBoxLayout()
        self.range_start_sp = QtWidgets.QSpinBox()
        self.range_start_sp.setRange(-999999, 999999)
        self.range_start_sp.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.range_start_sp.setValue(self.range[0])
        self.range_end_sp = QtWidgets.QSpinBox()
        self.range_end_sp.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.range_end_sp.setRange(-999999, 999999)
        self.range_end_sp.setValue(self.range[1])
        range_layout.addWidget(self.range_start_sp)
        range_layout.addWidget(self.range_end_sp)
        form_layout.addRow(range_lbl, range_layout)


        # add a button box to create the preview or cancel
        button_box = common.TikButtonBox(parent=self)
        self.master_layout.addWidget(button_box)
        _create_preview_btn = button_box.addButton(
            "Create Preview", QtWidgets.QDialogButtonBox.AcceptRole
        )
        _cancel_btn = button_box.addButton("Cancel", QtWidgets.QDialogButtonBox.RejectRole)

        self.resolve_name()
        # SIGNALS
        self.preview_name_le.textChanged.connect(self.resolve_name)
        self.cameras_combo.currentTextChanged.connect(self.resolve_name)
        button_box.accepted.connect(self.create_preview)
        button_box.rejected.connect(self.close)

    def create_preview(self):
        """Create the preview."""
        _name = self.preview_name_le.text()
        _camera = self.cameras_combo.currentText()
        # _camera_code = self.work._dcc_handler.get_scene_cameras()[_camera]
        _resolution = [self.resolution_x_sp.value(), self.resolution_y_sp.value()]
        _range = [self.range_start_sp.value(), self.range_end_sp.value()]
        state = self.work.make_preview(self.version, _camera, _resolution, _range, label=_name, settings=self.work.guard.preview_settings.properties)
        if state:
            self.close()
        else:
            self.feedback.pop_info("Preview not created", "Preview not created. Cancelled by user.")




