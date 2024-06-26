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
from tik_manager4.ui.Qt import QtWidgets, QtCore
from tik_manager4.ui.widgets.common import (
    TikLabel,
    TikLabelButton,
    HeaderLabel,
    ResolvedText,
    TikButtonBox,
    TikButton,
    TikIconButton,
    # ExpandableLayout,
)
from tik_manager4.ui.layouts.settings_layout import (
    SettingsLayout,
    convert_to_ui_definition,
)
from tik_manager4.ui.layouts.collapsible_layout import CollapsibleLayout
from tik_manager4.ui.dialog.feedback import Feedback
from tik_manager4.ui import pick

LOG = logging.getLogger(__name__)


class PublishSceneDialog(QtWidgets.QDialog):
    """Publishes the current scene."""

    def __init__(self, project_object, *args, **kwargs):
        """Initialize the PublishSceneDialog."""
        super(PublishSceneDialog, self).__init__(*args, **kwargs)

        # set style
        _style_file = pick.style_file()
        self.setStyleSheet(str(_style_file.readAll(), "utf-8"))

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

        # build the layouts
        self.build_ui()

        self.resize(1000, 600)

        self.horizontal_splitter.setSizes([500, 500])
        self.vertical_splitter.setSizes([800, 200])

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

    def _build_bottom(self):
        """Build the bottom section."""

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

    def extract_all(self):
        """Extract all the extractors."""
        # single extractors are not saving the scene. Make sure the scene saved first
        self.project.publisher._dcc_handler.save_scene()
        for extractor_widget in self._extractor_widgets:
            if not extractor_widget.extract.enabled:
                continue
            self.project.publisher.extract_single(extractor_widget.extract)
            extractor_widget.set_state(extractor_widget.extract.state)
            if extractor_widget.extract.state == "failed":
                q = self.feedback.pop_question(
                    title="Extraction Failed",
                    text=f"Extraction failed for: \n\n{extractor_widget.extract.name}\n\nDo you want to continue?",
                    buttons=["continue", "cancel"],
                )
                if q == "cancel":
                    self.project.publisher.discard()
                    # self.__init__(self.project)
                    return False
                    # raise Exception("Extraction Failed")
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
        self.reset_validators()  # only resets if the scene is modified
        self.validate_all()
        # check the state of the validations
        passes, warnings, fails, idle = self.check_validation_state()
        # check for unavailable extractions
        unavailable_extractors = self.check_extraction_status()

        # if there are fails, pop up a dialog
        if fails:
            self.feedback.pop_info(
                title="Validation Failed",
                text=f"Validation failed for: \n\n{fails}\n\nPlease fix the validation issues before publishing.",
            )
            return
        # if there are warnings, pop up a dialog
        if warnings:
            q = self.feedback.pop_question(
                title="Validation Warnings",
                text=f"Validation warnings for: \n\n{warnings}\n\nDo you want IGNORE them and continue?",
                buttons=["continue", "cancel"],
            )
            if q == "cancel":
                return

        if unavailable_extractors:
            q = self.feedback.pop_question(
                title="Extraction Unavailable",
                text=f"Extraction unavailable for: \n\n{unavailable_extractors}\n\nDo you want to continue?",
                buttons=["continue", "cancel"],
            )
            if q == "cancel":
                return

        # reserve the slot
        self.project.publisher.reserve()
        # extract the elements
        state = self.extract_all()
        if not state:
            # user cancellation due to failed extracts
            return

        # finalize publish
        self.project.publisher.publish(notes=self.notes_text.toPlainText())
        # prepare publish report and feedback
        if warnings:
            msg = f"Publish Successful with following warnings:\n\n{warnings}"
        else:
            msg = f"Publish Successful"
        self.feedback.pop_info(title="Publish Successful", text=msg)
        self.close()
        self.deleteLater()
        return


class ValidateRow(QtWidgets.QHBoxLayout):
    """Custom Layout for validation rows."""

    def __init__(self, validator_object, *args, **kwargs):
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
        LOG.info(f"validating {self.button.text()}...")
        self.validator.validate()
        self.update_state()
        end = time()
        LOG.info(f"took {end-start} seconds")

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
        LOG.info(f"fixing {self.button.text()}...")
        self.validator.fix()
        self.validator.validate()
        if self.validator.state != "passed":
            # TODO: dialog or some kind of feedback
            pass
        self.update_state()
        end = time()
        LOG.info(f"took {end - start} seconds")

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
            self.status_icon.setStyleSheet("background-color: {};".format(_fail_colour))
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
        super(ExtractRow, self).__init__(*args, **kwargs)
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


# test this dialog
if __name__ == "__main__":
    import sys
    import tik_manager4
    from tik_manager4.ui import pick

    tik = tik_manager4.initialize("Standalone")

    app = QtWidgets.QApplication(sys.argv)

    # _style_file = pick.style_file()
    # dialog = PublishSceneDialog(
    #     tik.project, styleSheet=str(_style_file.readAll(), "utf-8")
    # )
    dialog = PublishSceneDialog(
        tik.project
    )

    dialog.show()

    sys.exit(app.exec_())
