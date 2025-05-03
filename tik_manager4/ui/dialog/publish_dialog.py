"""Dialogs for publishing files.

Maya test example:

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


from maya import cmds

file_path = "C:\\Users\\kutlu\\t4_maya_test_project_DO_NOT_USE\\test_subproject\\test_task\\Model\\Maya\\test_task_Model_test_cube_v003.ma"
cmds.file(file_path, open=True, force=True)

import tik_manager4
tik = tik_manager4.initialize("Maya")

from tik_manager4.dcc.maya.main import Dcc as maya_dcc
parent = maya_dcc().get_main_window()
# reload(tik_manager4)
from tik_manager4.objects import publisher
reload(publisher)
from tik_manager4.ui.dialog import publish_dialog
reload(publish_dialog)
from tik_manager4.ui import pick
_style_file = pick.style_file()

dialog = publish_dialog.PublishSceneDialog(tik.project, styleSheet=str(_style_file.readAll(), "utf-8"), parent=parent)
dialog.show()

"""


from time import time
import logging

from tik_manager4.objects.preview import PreviewContext
from tik_manager4.ui.Qt import QtWidgets, QtCore
from tik_manager4.ui.widgets.common import (
    TikLabel,
    ResolvedText,
    TikButtonBox,
    TikButton,
    TikIconButton,
    VerticalSeparator
)
from tik_manager4.ui.layouts.settings_layout import (
    SettingsLayout,
)
from tik_manager4.ui.layouts.collapsible_layout import CollapsibleLayout
from tik_manager4.ui.dialog.feedback import Feedback
from tik_manager4.ui import pick
from tik_manager4.ui.widgets.value_widgets import Vector2Int
from tik_manager4.ui.widgets.pop import WaitDialog

LOG = logging.getLogger(__name__)


class PublishSceneDialog(QtWidgets.QDialog):
    """Publish the current scene."""

    def __init__(self, project_object, *args, **kwargs):
        """Initialize the PublishSceneDialog."""
        super().__init__(*args, **kwargs)

        # set style
        style_file = pick.style_file()
        self.setStyleSheet(str(style_file.readAll(), "utf-8"))

        # DYNAMIC ATTRIBUTES
        self._validator_widgets = []
        self._extractor_widgets = []

        # instanciate the publisher class
        self.feedback = Feedback(parent=self)
        self.project = project_object
        self.project.publisher.resolve()

        self.check_eligibility()

        self.setWindowTitle("Publish Scene")

        self.dialog_layout = QtWidgets.QVBoxLayout(self)

        self.vertical_splitter = None
        self.horizontal_splitter = None

        # layout variables
        self.header_layout = None
        self.validation_header_lay = None
        self.validations_scroll_lay = None
        self.extract_header_lay = None
        self.extracts_scroll_lay = None
        self.bottom_layout = None

        # class widgets
        self.notes_text = None

        # preview related variables and widgets
        self.preview_context = PreviewContext()
        self.preview_context.set_enabled(False) # disable by default
        self.preview_enabled_cb = None
        self.resolution_vc2 = None
        self.range_vc2 = None

        # management related widgets
        self.management_tasks_combo = None
        self.management_status_combo = None

        # build the layouts
        self.build_ui()

        # self.resize(1000, 600)
        self.setMinimumWidth(1000)
        self.setMinimumHeight(400)

        self.horizontal_splitter.setSizes([500, 500])
        self.vertical_splitter.setSizes([600, 400])

        self.publish_finished = False


    def check_eligibility(self):
        """Checks if the current scene is eligible for publishing."""
        if not self.project.publisher.work_object:
            self.feedback.pop_info(
                title="Non-valid Scene",
                text="Current Scene does not belong to a 'Work' in this project. Please save scene as a 'Work' before publishing or switch to the correct project.",
            )
            # destroy the dialog. make it dispappear
            self.close()
            self.deleteLater()
            # raise Exception("Current Scene does not belong to a 'Work'. It is required to save scenes as a 'Work' before publishing.")
            return

    def build_ui(self):
        """Build the layouts."""
        master_layout = QtWidgets.QVBoxLayout()
        self.header_layout = QtWidgets.QVBoxLayout()
        # set margin to 0
        self.header_layout.setContentsMargins(10, 10, 10, 10)

        self._build_header()

        master_layout.addLayout(self.header_layout)

        self.vertical_splitter = QtWidgets.QSplitter(self)
        self.vertical_splitter.setOrientation(QtCore.Qt.Vertical)
        self.vertical_splitter.setHandleWidth(5)
        self.vertical_splitter.setProperty(
            "horizontal", True
        )  # the icon is horizontal shaped. IT IS NOT A BUG

        # make it non-collapsible
        self.vertical_splitter.setChildrenCollapsible(False)

        _body_layout_widget = QtWidgets.QWidget(self.vertical_splitter)
        body_layout = QtWidgets.QHBoxLayout(_body_layout_widget)
        body_layout.setContentsMargins(0, 0, 0, 0)
        self.horizontal_splitter = QtWidgets.QSplitter(_body_layout_widget)
        self.horizontal_splitter.setOrientation(QtCore.Qt.Horizontal)
        self.horizontal_splitter.setHandleWidth(5)
        self.horizontal_splitter.setProperty(
            "vertical", True
        )  # the icon is vertical shaped. IT IS NOT A BUG

        _left_layout_widget = QtWidgets.QWidget(self.horizontal_splitter)
        left_layout = QtWidgets.QVBoxLayout(_left_layout_widget)
        left_layout.setContentsMargins(5, 5, 5, 5)
        self.validation_header_lay = QtWidgets.QVBoxLayout()
        left_layout.addLayout(self.validation_header_lay)

        scroll_area_left = QtWidgets.QScrollArea(_left_layout_widget)
        scroll_area_left.setWidgetResizable(True)
        scroll_area_left_contents = QtWidgets.QWidget()
        self.validations_scroll_lay = QtWidgets.QVBoxLayout(scroll_area_left_contents)

        self._build_validations()

        scroll_area_left.setWidget(scroll_area_left_contents)

        left_layout.addWidget(scroll_area_left)

        _right_layout_widget = QtWidgets.QWidget(self.horizontal_splitter)
        right_layout = QtWidgets.QVBoxLayout(_right_layout_widget)
        right_layout.setContentsMargins(5, 5, 5, 5)
        self.extract_header_lay = QtWidgets.QVBoxLayout()
        right_layout.addLayout(self.extract_header_lay)

        scroll_area_right = QtWidgets.QScrollArea(_right_layout_widget)
        scroll_area_right.setWidgetResizable(True)
        scroll_area_right_contents = QtWidgets.QWidget()
        self.extracts_scroll_lay = QtWidgets.QVBoxLayout(scroll_area_right_contents)

        self._build_extractions()
        scroll_area_right.setWidget(scroll_area_right_contents)
        right_layout.addWidget(scroll_area_right)
        body_layout.addWidget(self.horizontal_splitter)
        _bottom_layout_widget = QtWidgets.QWidget(self.vertical_splitter)
        self.bottom_layout = QtWidgets.QVBoxLayout(_bottom_layout_widget)
        self.bottom_layout.setContentsMargins(5, 5, 5, 5)

        self._build_bottom()

        master_layout.addWidget(self.vertical_splitter)
        self.dialog_layout.addLayout(master_layout)

    def _build_header(self):
        """Fill the header layout with widgets."""
        path_layout = QtWidgets.QHBoxLayout()
        self.header_layout.addLayout(path_layout)
        name_layout = QtWidgets.QHBoxLayout()
        self.header_layout.addLayout(name_layout)

        path_header = TikLabel(text="Path: ")
        path_layout.addWidget(path_header)
        name_header = TikLabel(text="Name: ")
        name_layout.addWidget(name_header)

        # resolved path
        path = self.project.publisher.relative_scene_path or "Path Not Resolved"
        path_label = ResolvedText(path)
        path_layout.addWidget(path_label)
        path_label.set_color("white")
        path_layout.addStretch()
        name = self.project.publisher.publish_name or "Name Not Resolved"
        name_label = ResolvedText(name)
        name_label.set_color("green")
        name_layout.addWidget(name_label)
        name_layout.addStretch()

    def _build_validations(self):
        """Build the widgets on validations section."""
        validations_label = QtWidgets.QLabel("Validations")
        validations_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.validation_header_lay.addWidget(validations_label)
        separator = QtWidgets.QLabel()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        separator.setStyleSheet("background-color: rgb(221, 160, 221);")
        separator.setFixedHeight(1)
        self.validation_header_lay.addWidget(separator)

        # ADD VALIDATIONS HERE
        # -------------------
        for validator_name, validator in self.project.publisher.validators.items():
            validate_row = ValidateRow(validator_object=validator)
            self.validations_scroll_lay.addLayout(validate_row)
            self._validator_widgets.append(validate_row)
        # -------------------

        self.validations_scroll_lay.addStretch()

    def _build_extractions(self):
        """Build the widgets on extractions section."""
        extracts_label = QtWidgets.QLabel("Extracts")
        extracts_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.extract_header_lay.addWidget(extracts_label)
        separator = QtWidgets.QLabel()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        separator.setStyleSheet("background-color: rgb(221, 160, 221);")
        separator.setFixedHeight(1)
        self.extract_header_lay.addWidget(separator)

        # ADD EXTRACTS HERE
        # -------------------
        for _extractor_name, extractor in self.project.publisher.extractors.items():
            # get the metadata for the extractor
            extract_row = ExtractRow(extract_object=extractor)
            self.extracts_scroll_lay.addLayout(extract_row)
            self._extractor_widgets.append(extract_row)
        # -------------------

        self.extracts_scroll_lay.addStretch()

    @property
    def is_management_driven(self):
        """Check if the management platform is available."""
        return self.project.settings.get("management_driven", False)

    def _management_widgets(self):
        """Check if the management platform is available."""
        if not self.is_management_driven:
            return
        m_handler = self.project.guard.management_handler
        if not m_handler:
            return
        platform_name = m_handler.nice_name
        wait_dialog = WaitDialog(parent=self)
        wait_dialog.display()
        if m_handler:
            if not m_handler.is_authenticated:
                wait_dialog.set_message(f"Authenticating to {platform_name}...")
                _handler, _msg = m_handler.authenticate()
                if not _handler:
                    wait_dialog.kill()
                    ret = self.feedback.pop_question(
                        title="Authentication Failed",
                        text=f"Authentication failed for {platform_name}. Please check your credentials.\n\n Do you want to continue without {platform_name} support?",
                    )
                    if ret == "cancel":
                        return

            management_tasks_lay = QtWidgets.QHBoxLayout()
            management_tasks_lay.setContentsMargins(0, 0, 0, 0)
            self.bottom_layout.addLayout(management_tasks_lay)

            management_tasks_label = QtWidgets.QLabel(
                f"{m_handler.nice_name} Task:")

            # self.management_tasks_combo = QtWidgets.QComboBox()
            wait_dialog.set_message("Fetching Tasks...")
            tasks_data_list = self.project.publisher.get_management_tasks()
            # get the current category. This will be attempted to be selected in the combo
            current_category = self.project.publisher.work_object.category
            self.management_tasks_combo = ManagementTasksCombo(
                tasks_data_list,
                default_item_name=current_category)
            management_tasks_lay.addWidget(management_tasks_label)
            management_tasks_lay.addWidget(self.management_tasks_combo)

            separator = VerticalSeparator()
            management_tasks_lay.addWidget(separator)

            # management status
            management_status_label = QtWidgets.QLabel("Status to:")
            self.management_status_combo = QtWidgets.QComboBox()
            wait_dialog.set_message("Fetching Status Lists...")
            self.management_status_combo.addItems(
                m_handler.get_available_status_lists())
            self._status_combo_update()
            self.management_tasks_combo.currentIndexChanged.connect(
                self._status_combo_update)
            management_tasks_lay.addWidget(management_status_label)
            management_tasks_lay.addWidget(self.management_status_combo)
            management_tasks_lay.addStretch()
            wait_dialog.kill()

    def _status_combo_update(self):
        """Try to update the status combo according to the selected task."""
        if not self.is_management_driven:
            return
        status = self.management_tasks_combo.get_current_status()
        if status:
            # try to select the status from the status combo if it is available
            index = self.management_status_combo.findText(status)
            if index != -1:
                self.management_status_combo.setCurrentIndex(index)

    def _preview_widgets(self):
        """Build the preview widgets if the preview is available."""
        if not self.project.publisher.task_object:
            return
        if not self.project.publisher._dcc_handler.preview_enabled:
            return
        if self.project.publisher.task_object.type.lower() != "shot":
            return
        # if not self.project.publisher.work_object
        scene_cameras = self.project.publisher._dcc_handler.get_scene_cameras()
        if not scene_cameras:
            return

        self.preview_context.set_enabled(True)

        # get the resolution with the following priority: metadata_inherited_resolution, preview_settings_resolution, 1920x1080
        metadata_inherited_resolution = self.project.publisher.task_object.metadata.get_value("resolution", None)
        preview_settings_resolution = self.project.preview_settings.get("Resolution", [1920, 1080])
        resolution_percentage = self.project.preview_settings.get("ResolutionPercentage", 100)

        full_resolution = metadata_inherited_resolution or preview_settings_resolution
        preview_resolution = [int(x * resolution_percentage / 100) for x in full_resolution]
        self.preview_context.set_resolution(preview_resolution)

        # get the range with this priority: metadata_inherited_range, scene range, 1001-1100
        metadata_start = self.project.publisher.task_object.metadata.get_value("start_frame", None)
        metadata_end = self.project.publisher.task_object.metadata.get_value("end_frame", None)
        _raw_scene_ranges = self.project.publisher._dcc_handler.get_ranges()
        if _raw_scene_ranges:
            scene_start = _raw_scene_ranges[0]
            scene_end = _raw_scene_ranges[-1]
        else:
            scene_start = 1001
            scene_end = 1100

        preview_start = metadata_start or scene_start
        preview_end = metadata_end or scene_end
        self.preview_context.set_frame_range([preview_start, preview_end])

        preview_layout = QtWidgets.QHBoxLayout()
        self.bottom_layout.addLayout(preview_layout)

        preview_enabled_cb = QtWidgets.QCheckBox(text="Take Preview")
        preview_enabled_cb.setChecked(True)
        preview_layout.addWidget(preview_enabled_cb)

        preview_layout.addWidget(VerticalSeparator())

        camera_lbl = QtWidgets.QLabel("Camera: ")
        preview_layout.addWidget(camera_lbl)
        camera_combo = QtWidgets.QComboBox()
        cameras = list(scene_cameras.keys())
        camera_combo.addItems(cameras)
        # Try to get the camera other than [front, back, top, bottom, persp]
        # if there isn't any, select try to select persp.
        # if no persp, select the first camera
        default_camera = self.preview_context.get_default_camera(cameras)
        camera_combo.setCurrentText(default_camera)
        self.preview_context.set_camera(default_camera)

        preview_layout.addWidget(camera_combo)

        preview_layout.addWidget(VerticalSeparator())
        resolution_lbl = QtWidgets.QLabel("Resolution: ")
        preview_layout.addWidget(resolution_lbl)
        resolution_vc2 = Vector2Int("resolution", value=self.preview_context.resolution)
        preview_layout.addWidget(resolution_vc2)

        preview_layout.addWidget(VerticalSeparator())

        range_lbl = QtWidgets.QLabel("Range: ")
        preview_layout.addWidget(range_lbl)
        range_vc2 = Vector2Int("range", value=self.preview_context.frame_range)
        preview_layout.addWidget(range_vc2)

        preview_layout.addStretch()

        # SIGNALS

        preview_enabled_cb.stateChanged.connect(camera_combo.setEnabled)
        preview_enabled_cb.stateChanged.connect(resolution_vc2.setEnabled)
        preview_enabled_cb.stateChanged.connect(range_vc2.setEnabled)
        preview_enabled_cb.stateChanged.connect(self.preview_context.set_enabled)

        camera_combo.currentTextChanged.connect(self.preview_context.set_camera)
        resolution_vc2.com.valueChanged.connect(self.preview_context.set_resolution)
        range_vc2.com.valueChanged.connect(self.preview_context.set_frame_range)


    def _build_bottom(self):
        """Build the bottom section."""

        # management platform tasks
        self._management_widgets()

        # preview widgets
        self._preview_widgets()

        # notes layout
        notes_label = QtWidgets.QLabel("Notes:")
        self.bottom_layout.addWidget(notes_label)
        self.notes_text = QtWidgets.QTextEdit()

        # add a placeholder text
        self.notes_text.setPlaceholderText("Notes are mandatory for publishes.")
        self.bottom_layout.addWidget(self.notes_text)

        # buttons layout
        button_box = TikButtonBox()
        validate_pb = button_box.addButton(
            "Validate", QtWidgets.QDialogButtonBox.YesRole
        )
        validate_pb.setToolTip("Run all active and available validations checks.")
        publish_pb = button_box.addButton(
            "Publish", QtWidgets.QDialogButtonBox.AcceptRole
        )
        publish_pb.setEnabled(False)  # disable the publish button by default
        publish_pb.setToolTip(
            "Extract the elements and publish the scene. Notes are Mandatory."
        )
        button_box.addButton("Cancel", QtWidgets.QDialogButtonBox.RejectRole)
        self.bottom_layout.addWidget(button_box)

        def _toggle_publish_button():
            """Enable/Disable the publish button. According to the notes."""
            if self.notes_text.toPlainText():
                publish_pb.setEnabled(True)
            else:
                publish_pb.setEnabled(False)

        # SIGNALS
        self.notes_text.textChanged.connect(_toggle_publish_button)
        button_box.rejected.connect(self.reject)
        validate_pb.clicked.connect(self.validate_all)
        publish_pb.clicked.connect(self.publish)

    def validate_all(self):
        """Validate all the validators."""
        self.reset_validators()
        for validator_widget in self._validator_widgets:
            # if it is already validated or unchecked skip
            if (
                validator_widget.validator.state == "passed"
                or not validator_widget.checkbox.isChecked()
            ):
                continue
            validator_widget.validate()
            # keep updating the ui
            QtWidgets.QApplication.processEvents()

    def extract_all(self, callback_handler=None):
        """Extract all the extractors."""
        # single extractors are not saving the scene. Make sure the scene saved first
        self.project.publisher._dcc_handler.save_scene()
        for extractor_widget in self._extractor_widgets:
            if not extractor_widget.extract.enabled:
                continue
            if callback_handler:
                callback_handler.set_message(f"Extracting {extractor_widget.extract.name}...")
                callback_handler.display()
            self.project.publisher.extract_single(extractor_widget.extract)
            # update the message display
            extractor_widget.update_message_box()
            extractor_widget.set_state(extractor_widget.extract.state)
            if extractor_widget.extract.state == "failed":
                callback_handler.kill()
                q = self.feedback.pop_question(
                    title="Extraction Failed",
                    text=f"Extraction failed for: \n\n{extractor_widget.extract.name}\n\nDo you want to continue?",
                    buttons=["continue", "cancel"],
                )
                if q == "cancel":
                    self.project.publisher.discard()
                    QtWidgets.QApplication.processEvents()
                    return False
                if q == "continue":
                    continue
            QtWidgets.QApplication.processEvents()

        return True

    def reset_validators(self):
        """If the scene is modified it will reset all the validators."""
        if self.project.publisher._dcc_handler.is_modified():
            for validator_widget in self._validator_widgets:
                validator_widget.reset()
                validator_widget.update_state()

    def check_validation_state(self):
        """Check all validations and return current state."""
        passes = []
        warnings = []
        fails = []
        idle = []
        for validator_widget in self._validator_widgets:
            if validator_widget.validator.state != "passed":
                passes.append(validator_widget.name)
            if validator_widget.validator.state == "idle":
                idle.append(validator_widget.name)
            if validator_widget.validator.state == "failed":
                if validator_widget.validator.ignorable:
                    warnings.append(validator_widget.name)
                else:
                    fails.append(validator_widget.name)
        return passes, warnings, fails, idle

    def check_extraction_status(self):
        """Check all extractions and return current state."""
        unavailable = []
        for extractor_widget in self._extractor_widgets:
            if extractor_widget.extract.state == "unavailable":
                unavailable.append(extractor_widget.extract.name)
        return unavailable

    def publish(self):
        """Command to publish the scene."""
        self.publish_finished = False
        pop = WaitDialog(message="Publishing...", parent=self)
        pop.display()
        self.reset_validators()  # only resets if the scene is modified
        self.validate_all()
        # check the state of the validations
        passes, warnings, fails, idle = self.check_validation_state()
        # check for unavailable extractions
        unavailable_extractors = self.check_extraction_status()

        # if there are fails, pop up a dialog
        if fails:
            pop.kill()
            self.feedback.pop_info(
                title="Validation Failed",
                text=f"Validation failed for: \n\n{fails}\n\nPlease fix the validation issues before publishing.",
            )
            return
        # if there are warnings, pop up a dialog
        if warnings:
            pop.kill()
            q = self.feedback.pop_question(
                title="Validation Warnings",
                text=f"Validation warnings for: \n\n{warnings}\n\nDo you want IGNORE them and continue?",
                buttons=["continue", "cancel"],
            )
            if q == "cancel":
                return

        if unavailable_extractors:
            pop.kill()
            q = self.feedback.pop_question(
                title="Extraction Unavailable",
                text=f"Extraction unavailable for: \n\n{unavailable_extractors}\n\nDo you want to continue?",
                buttons=["continue", "cancel"],
            )
            if q == "cancel":
                return

        # reserve the slot
        pop.set_message("Reserving Slot...")
        pop.display()
        self.project.publisher.reserve()
        # extract the elements
        state = self.extract_all(callback_handler=pop)
        if not state:
            pop.kill()
            # user cancellation due to failed extracts
            self.project.publisher.discard()
            return

        # finalize publish
        management_task_id = None
        management_task_status = None
        if self.is_management_driven:
            # get the management task and status
            task_dict = self.management_tasks_combo.get_current_item()
            if task_dict:
                management_task_id = task_dict.get("id", None)
            management_task_status = self.management_status_combo.currentText()

        self.project.publisher.publish(
            notes=self.notes_text.toPlainText(),
            preview_context=self.preview_context,
            message_callback=pop.set_message,
            management_task_id=management_task_id,
            management_task_status_to=management_task_status,
        )
        warnings.extend(self.project.publisher.warnings)
        # prepare publish report and feedback
        pop.kill()
        self.publish_finished = True
        if warnings:
            msg = f"Publish finished with following warnings:\n\n{warnings}"
            # if there are warnings, lets not close the dialog. Let the user see the warnings
            self.feedback.pop_info(title="Publish Finished with Ignored Warnings", text=msg)
            return
        else:
            msg = f"Publish Successful"
            self.feedback.pop_info(title="Publish Successful", text=msg)
            self.close()
            self.deleteLater()
            return


class ValidateRow(QtWidgets.QHBoxLayout):
    """Custom Layout for validation rows."""

    def __init__(self, validator_object, toaster=None, *args, **kwargs):
        """Initialize the ValidateRow."""
        super(ValidateRow, self).__init__(*args, **kwargs)
        self.validator = validator_object
        self.name = self.validator.nice_name or self.validator.name
        self.build_widgets()
        self.update_state()

    def build_widgets(self):
        """Build the widgets."""
        # status icon
        # create a vertical line with color
        self.status_icon = QtWidgets.QFrame()
        # make it gray
        self.status_icon.setStyleSheet("background-color: gray;")
        # set the width to 10px
        self.status_icon.setFixedWidth(10)
        self.addWidget(self.status_icon)

        # checkbox
        self.checkbox = QtWidgets.QCheckBox()
        self.checkbox.setChecked(self.validator.checked_by_default)
        self.addWidget(self.checkbox)

        # button
        self.button = TikButton(text=self.name)
        # stretch it to the layout
        self.button.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        self.button.setFixedHeight(26)
        self.addWidget(self.button)

        # maintenance icons
        self.info_pb = TikIconButton(icon_name="info.png")
        self.info_pb.set_size(26)
        self.select_pb = TikIconButton(icon_name="select.png")
        self.select_pb.set_size(26)
        self.fix_pb = TikIconButton(icon_name="fix.png")
        self.fix_pb.set_size(26)
        self.addWidget(self.info_pb)
        self.addWidget(self.select_pb)
        self.addWidget(self.fix_pb)

        # SIGNALS
        self.checkbox.stateChanged.connect(self.update_state)
        self.button.clicked.connect(self.validate)
        self.info_pb.clicked.connect(self.pop_info)
        self.fix_pb.clicked.connect(self.fix)
        self.select_pb.clicked.connect(self.select)

    def validate(self):
        """Validate the validator."""
        start = time()
        LOG.info("validating %s...", self.button.text())
        self.validator.validate()
        self.update_state()
        end = time()
        LOG.info("took %s seconds", end-start)

    def pop_info(self):
        """Pop up an information dialog for informing the user what went wrong."""
        information = self.validator.fail_message
        if information:
            # create a mini dialog with non-editable text
            pop_info_dialog = QtWidgets.QDialog()
            pop_info_dialog.setWindowTitle(f"{self.validator.nice_name} Message")
            pop_info_dialog.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
            pop_info_dialog.setModal(True)
            pop_info_dialog.setMinimumWidth(300)
            pop_info_dialog.setMinimumHeight(200)
            pop_info_dialog.setLayout(QtWidgets.QVBoxLayout())
            text = QtWidgets.QTextEdit()
            text.setReadOnly(True)
            text.setText(information)
            pop_info_dialog.layout().addWidget(text)
            pop_info_dialog.exec_()
        else:
            return

    def fix(self):
        """Auto Fix the scene."""
        start = time()
        LOG.info("fixing %s...", self.button.text())
        self.validator.fix()
        self.validator.validate()
        end = time()
        if self.validator.state != "passed":
            # TODO: pop up a dialog to inform the user that the fix failed
            LOG.info("fix failed")
        self.update_state()


        LOG.info("took %s seconds", end - start)

    def select(self):
        """Select the objects related to the validator."""
        self.validator.select()
        self.update_state()

    def reset(self):
        """Reset the validator."""
        self.validator.reset()
        self.update_state()

    def update_state(self):
        """Update the availablity of the buttons."""

        _autofixable = self.validator.autofixable
        _ignorable = self.validator.ignorable
        _selectable = self.validator.selectable
        _state = self.validator.state

        # update the buttons
        if not _ignorable:
            self.checkbox.setCheckState(QtCore.Qt.Checked)
            self.checkbox.setEnabled(False)

        if self.checkbox.isChecked():
            self.button.setEnabled(True)
        else:
            self.status_icon.setStyleSheet("background-color: gray;")
            self.button.setEnabled(False)
            self.info_pb.setEnabled(False)
            self.select_pb.setEnabled(False)
            self.fix_pb.setEnabled(False)
            return

        if _state == "passed":
            self.status_icon.setStyleSheet("background-color: green;")
            self.info_pb.setEnabled(False)
            self.select_pb.setEnabled(False)
            self.fix_pb.setEnabled(False)

        elif _state == "idle":
            self.status_icon.setStyleSheet("background-color: gray;")
            self.info_pb.setEnabled(False)
            self.select_pb.setEnabled(False)
            self.fix_pb.setEnabled(False)

        else:
            _fail_colour = "yellow" if _ignorable else "red"
            self.status_icon.setStyleSheet(f"background-color: {_fail_colour};")
            if _autofixable:
                self.fix_pb.setEnabled(True)
            else:
                self.fix_pb.setEnabled(False)
            if _selectable:
                self.select_pb.setEnabled(True)
            else:
                self.select_pb.setEnabled(False)
            self.info_pb.setEnabled(True)


class ExtractRow(QtWidgets.QHBoxLayout):
    """Custom Layout for extract rows."""

    def __init__(self, extract_object, *args, **kwargs):
        """Initialize the ExtractRow."""
        super().__init__(*args, **kwargs)
        self.extract = extract_object
        self.status_icon = None
        self.label = None
        self.settings_btn = None
        self.settings_frame = None
        self.global_settings_data = None
        self.settings_data = None
        self.info = None

        self.build_widgets()

    def build_widgets(self):
        """Build the widgets."""
        # status icon
        # create a vertical line with color
        self.status_icon = QtWidgets.QFrame()
        # set the width to 10px
        self.status_icon.setFixedWidth(10)
        self.addWidget(self.status_icon)

        # main
        main_layout = QtWidgets.QVBoxLayout()
        self.addLayout(main_layout)
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setSpacing(0)
        main_layout.addLayout(header_layout)

        # add a checkbox if the extract is optional
        if self.extract.optional:
            self.checkbox = QtWidgets.QCheckBox()
            # make it to occupy minimum space
            self.checkbox.setFixedWidth(30)
            self.checkbox.setChecked(self.extract.enabled)
            header_layout.addWidget(self.checkbox)
            # SIGNALS
            self.checkbox.stateChanged.connect(self.toggle_enabled)

        self.collapsible_layout = CollapsibleLayout(
            text=self.extract.nice_name or self.extract.name
        )
        self.collapsible_layout.set_color(
            text_color=self.extract.color, border_color=self.extract.color
        )
        self.collapsible_layout.label.set_font_size(10, bold=True)
        header_layout.addLayout(self.collapsible_layout)

        if self.extract.global_settings.properties:
            # if there are global settings exposed for the extract draw them.
            global_settings_formlayout = SettingsLayout(
                self.extract.global_exposed_settings_ui, self.extract.global_settings
            )
            self.collapsible_layout.contents_layout.addLayout(global_settings_formlayout)
        _settings = self.extract.settings.get(self.extract.category, {})
        if _settings:
            _settings_ui = self.extract.exposed_settings_ui[self.extract.category]
            # get the settings from the extract
            settings_formlayout = SettingsLayout(_settings_ui, _settings)
            self.collapsible_layout.contents_layout.addLayout(settings_formlayout)
        if not self.extract.global_settings.properties and not _settings:
            self.collapsible_layout.expand_button.hide()

        # maintenance icons
        self.info = TikIconButton(icon_name=self.extract.name, circle=True)
        self.info.set_size(32)
        self.addWidget(self.info)

        # SIGNALS
        self.info.clicked.connect(self.pop_info)

        self.set_state(self.extract.state)
        self.update_message_box()
        self.toggle_enabled(self.extract.enabled)

    def update_message_box(self):
        """Update the info icons border color if there is a message to show."""
        if self.extract.message:
            self.info.set_color(border_color="red")
        else:
            self.info.set_color(border_color=self.extract.color)

    def pop_info(self):
        """Pops up an information dialog."""
        information = self.extract.message
        if information:
            # create a mini dialog with non-editable text
            pop_info_dialog = QtWidgets.QDialog()
            pop_info_dialog.setWindowTitle(f"{self.extract.nice_name} Information")
            pop_info_dialog.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
            pop_info_dialog.setModal(True)
            pop_info_dialog.setMinimumWidth(300)
            pop_info_dialog.setMinimumHeight(200)
            pop_info_dialog.setLayout(QtWidgets.QVBoxLayout())
            text = QtWidgets.QTextEdit()
            text.setReadOnly(True)
            text.setText(information)
            pop_info_dialog.layout().addWidget(text)
            pop_info_dialog.exec_()
        else:
            return

    def toggle_enabled(self, is_enabled):
        """Toggle the enabled state of the extract."""
        self.extract.enabled = is_enabled
        self.collapsible_layout.contents_widget.setEnabled(is_enabled)
        self.set_state(self.extract.state)
        self.info.setEnabled(is_enabled)

    def toggle_settings_visibility(self, state):
        """Toggle the visibility of the settings frame."""
        self.settings_frame.setVisible(state)

    def set_state(self, state):
        """Set the state of the extract."""
        if state == "success":
            self.status_icon.setStyleSheet("background-color: green;")
        elif state == "idle":
            self.status_icon.setStyleSheet("background-color: #FF8D1C;")
        elif state == "failed":
            self.status_icon.setStyleSheet("background-color: red;")
        elif state == "unavailable":
            self.status_icon.setStyleSheet("background-color: gray;")
        elif state == "disabled": # this is for optional extracts
            self.status_icon.setStyleSheet("background-color: gray;")
        else:
            pass
        return

class ManagementTasksComboBoxModel(QtCore.QAbstractListModel):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.items = items

    def rowCount(self, parent=None):
        return len(self.items)

    def get_display_name(self, item):
        """Get the display name of the item."""
        # This makes sure the display name becomes compatible for both
        # Shotgrid and Kitsu. If there are more management platforms
        # this method should be updated
        return item.get('content', '') or item.get('task_type_name', '')

    def get_status_name(self, item):
        """Get the status name of the item."""
        return item.get('sg_status_list', '') or item.get('task_status_name', '')

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self.items)):
            return None
        if role == QtCore.Qt.DisplayRole:
            # Display only the 'content' key's value
            return self.get_display_name(self.items[index.row()])
        return None

    def get_item(self, index):
        """Method to get the full dictionary item."""
        if 0 <= index < len(self.items):
            return self.items[index]
        return None

    def get_status(self, index):
        """Method to get the status of the item."""
        if 0 <= index < len(self.items):
            return self.get_status_name(self.items[index])
        return None

class ManagementTasksCombo(QtWidgets.QComboBox):
    """Custom ComboBox for Management Tasks."""
    def __init__(self, items, parent=None, default_item_name: str=None):
        super().__init__(parent)
        self.items = items
        self.model = ManagementTasksComboBoxModel(items)
        self.setModel(self.model)

        # if there is a default item defined, try to set it ONLY if exists in the items
        if default_item_name:
            self.set_item(default_item_name)

    def set_item(self, item_name):
        """Set the item by name."""
        for idx, item in enumerate(self.items or []):
            if self.model.get_display_name(item) == item_name:
                self.setCurrentIndex(idx)
                return

    def get_current_item(self):
        """Get the current selected item."""
        index = self.currentIndex()
        return self.model.get_item(index)

    def get_current_status(self):
        """Get the current selected status."""
        index = self.currentIndex()
        return self.model.get_status(index)



# test this dialog
if __name__ == "__main__":
    import sys
    import tik_manager4
    tik = tik_manager4.initialize("Standalone")

    app = QtWidgets.QApplication(sys.argv)

    dialog = PublishSceneDialog(
        tik.project
    )

    dialog.show()

    sys.exit(app.exec_())
