"""Dialog to create previews for the current scene."""

from tik_manager4.objects.preview import Preview, PreviewContext
from tik_manager4.ui.Qt import QtWidgets, QtCore
from tik_manager4.ui.dialog import feedback
from tik_manager4.ui.widgets import common
from tik_manager4.ui.widgets.pop import WaitDialog
from tik_manager4.ui.widgets.validated_string import ValidatedString
from tik_manager4.ui.widgets.value_widgets import Vector2Int


class PreviewDialog(QtWidgets.QDialog):
    """Dialog to create previews for the current scene."""
    def __init__(
        self, work_object, version, resolution=None, frame_range=None, parent=None
    ):
        super().__init__(parent=parent)

        self.setWindowTitle("Create Preview")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.feedback = feedback.Feedback(parent=self)
        self.work = work_object
        self.context = PreviewContext()
        self.preview_handler = Preview(self.context, self.work)
        self.context.set_version_number(version)
        self.context.set_resolution(
            resolution
            or self.work.guard.project_settings.get_property("resolution", [1920, 1080])
        )

        frame_range = frame_range or [1001, 1100]
        raw_ranges = self.work._dcc_handler.get_ranges()
        if raw_ranges:
            range_start = raw_ranges[0]
            range_end = raw_ranges[-1]
        else:
            range_start = 1001
            range_end = 1100
        _range = frame_range or [range_start, range_end]
        self.context.set_frame_range([_range[0] or range_start, _range[1] or range_end])

        self.context.set_label("")

        self.resolved_text = None

        self.master_layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.master_layout)
        self.build_ui()

    def resolve_name(self):
        """Resolve the name of the preview."""
        _resolved_name = self.preview_handler.resolve_preview_name()
        self.resolved_text.setText(_resolved_name[1])

    def build_ui(self):
        """Build the UI."""
        self.resolved_text = common.ResolvedText()
        self.master_layout.addWidget(self.resolved_text)

        form_layout = QtWidgets.QFormLayout()
        self.master_layout.addLayout(form_layout)
        preview_name_lbl = QtWidgets.QLabel("Preview Label: ")
        preview_name_le = ValidatedString("test", allow_empty=True)
        form_layout.addRow(preview_name_lbl, preview_name_le)

        camera_lbl = QtWidgets.QLabel("Camera: ")
        cameras_combo = QtWidgets.QComboBox()
        scene_cameras = self.work._dcc_handler.get_scene_cameras()
        if scene_cameras:
            cameras_combo.addItems(list(scene_cameras.keys()))
        form_layout.addRow(camera_lbl, cameras_combo)
        self.context.set_camera(cameras_combo.currentText() or "")

        resolution_lbl = QtWidgets.QLabel("Resolution: ")
        resolution_vc2 = Vector2Int("resolution", value=self.context.resolution)
        form_layout.addRow(resolution_lbl, resolution_vc2)

        range_lbl = QtWidgets.QLabel("Range: ")
        range_vc2 = Vector2Int("range", value=self.context.frame_range)
        form_layout.addRow(range_lbl, range_vc2)

        # add a button box to create the preview or cancel
        button_box = common.TikButtonBox(parent=self)
        self.master_layout.addWidget(button_box)
        _create_preview_btn = button_box.addButton(
            "Create Preview", QtWidgets.QDialogButtonBox.AcceptRole
        )
        _cancel_btn = button_box.addButton(
            "Cancel", QtWidgets.QDialogButtonBox.RejectRole
        )

        self.resolve_name()
        # SIGNALS
        resolution_vc2.com.valueChanged.connect(self.context.set_resolution)
        range_vc2.com.valueChanged.connect(self.context.set_frame_range)
        preview_name_le.textChanged.connect(self.context.set_label)
        preview_name_le.textChanged.connect(self.resolve_name)
        cameras_combo.currentTextChanged.connect(self.context.set_camera)
        cameras_combo.currentTextChanged.connect(self.resolve_name)
        button_box.accepted.connect(self.create_preview)
        button_box.rejected.connect(self.close)

    def create_preview(self):
        """Create the preview."""
        message_box = WaitDialog(frameless=False, parent=self)
        message_box.set_message("Creating preview. Please wait...")
        message_box.set_message_size(12)
        message_box.display()

        self.preview_handler.set_message_callback(message_box.set_message)
        self.preview_handler.settings = self.work.guard.preview_settings.properties
        state = self.preview_handler.generate(show_after=True)

        message_box.kill()
        if state:
            self.close()
        else:
            self.feedback.pop_info(
                "Preview not created", "Preview not created. Cancelled by user."
            )
