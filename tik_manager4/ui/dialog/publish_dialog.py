"""Dialogs for publishing files."""
from time import time
import logging
from tik_manager4.ui.Qt import QtWidgets, QtCore
from tik_manager4.core import settings
from tik_manager4.ui.widgets.common import TikLabel, TikLabelButton, HeaderLabel, ResolvedText, TikButtonBox, TikButton, TikIconButton
from tik_manager4.ui.layouts.settings_layout import SettingsLayout, convert_to_ui_definition
from tik_manager4.ui.dialog.feedback import Feedback

LOG = logging.getLogger(__name__)

class PublishSceneDialog(QtWidgets.QDialog):
    """Publishes the current scene."""
    def __init__(self, project_object, *args, **kwargs):
        """Initialize the PublishSceneDialog."""
        super(PublishSceneDialog, self).__init__(*args, **kwargs)

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

        # self.horizontal_splitter.setStretchFactor(0, 50)
        # self.horizontal_splitter.setStretchFactor(1, 50)
        # self.vertical_splitter.setStretchFactor(0, 70)
        # self.vertical_splitter.setStretchFactor(1, 30)

    def check_eligibility(self):
        """Checks if the current scene is eligible for publishing."""
        if not self.project.publisher._work_object:
            self.feedback.pop_info(title="Non-valid Scene",
                                   text="Current Scene does not belong to a 'Work'. It is required to save scenes as a 'Work' before publishing.")
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
        self.vertical_splitter.setProperty("horizontal", True) # the icon is horizontal shaped. IT IS NOT A BUG

        # make it non-collapsible
        self.vertical_splitter.setChildrenCollapsible(False)

        _body_layout_widget = QtWidgets.QWidget(self.vertical_splitter)
        body_layout = QtWidgets.QHBoxLayout(_body_layout_widget)
        body_layout.setContentsMargins(0, 0, 0, 0)
        self.horizontal_splitter = QtWidgets.QSplitter(_body_layout_widget)
        self.horizontal_splitter.setOrientation(QtCore.Qt.Horizontal)
        self.horizontal_splitter.setHandleWidth(5)
        self.horizontal_splitter.setProperty("vertical", True) # the icon is vertical shaped. IT IS NOT A BUG

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
        self.bottom_layout.addWidget(self.notes_text)

        # buttons layout
        button_box = TikButtonBox()
        validate_pb = button_box.addButton("Validate", QtWidgets.QDialogButtonBox.YesRole)
        validate_pb.setToolTip("Run all active and available validations checks.")
        publish_pb = button_box.addButton("Publish", QtWidgets.QDialogButtonBox.AcceptRole)
        publish_pb.setEnabled(False) # disable the publish button by default
        publish_pb.setToolTip("Extract the elements and publish the scene. Notes are Mandatory.")
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
            if validator_widget.validator.state == "passed" or not validator_widget.checkbox.isChecked():
                continue
            validator_widget.validate()
            # keep updating the ui
            QtWidgets.QApplication.processEvents()

    def extract_all(self):
        """Extract all the extractors."""
        # single extractors are not saving the scene. Make sure the scene saved first
        self.project.publisher._dcc_handler.save_scene()
        for extractor_widget in self._extractor_widgets:
            self.project.publisher.extract_single(extractor_widget.extract)
            extractor_widget.set_state(extractor_widget.extract.state)
            print("compare_pre", extractor_widget.extract.settings)
            if extractor_widget.settings_data:
                print("compare_pre_fr", extractor_widget.settings_data.get_property("frame_range"))
                print("compare_pre_fr", extractor_widget.settings_data.get_property("step"))
            if extractor_widget.extract.state == "failed":
                q = self.feedback.pop_question(title="Extraction Failed", text=f"Extraction failed for: \n\n{extractor_widget.extract.name}\n\nDo you want to continue?", buttons=["continue", "cancel"])
                if q == "cancel":
                    self.project.publisher.discard()
                    self.__init__()
                    raise Exception("Extraction Failed")
                if q == "continue":
                    continue
            QtWidgets.QApplication.processEvents()

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
        successes = []
        fails = []
        idle = []

        for extractor_widget in self._extractor_widgets:
            if extractor_widget.extract.state == "success":
                successes.append(extractor_widget.name)
            if extractor_widget.extract.state == "idle":
                idle.append(extractor_widget.name)
            if extractor_widget.extract.state == "failed":
                fails.append(extractor_widget.name)
        return successes, fails, idle


    def publish(self):
        """Command to publish the scene."""
        self.reset_validators() # only resets if the scene is modified
        self.validate_all()
        # check the state of the validations
        passes, warnings, fails, idle = self.check_validation_state()
        # if there are fails, pop up a dialog
        if fails:
            self.feedback.pop_info(title="Validation Failed", text=f"Validation failed for: \n\n{fails}\n\nPlease fix the validation issues before publishing.")
            return
        # if there are warnings, pop up a dialog
        if warnings:
            q = self.feedback.pop_question(title="Validation Warnings", text=f"Validation warnings for: \n\n{warnings}\n\nDo you want IGNORE them and continue?", buttons=["continue", "cancel"])
            if q == "cancel":
                return

        # reserve the slot
        self.project.publisher.reserve()
        # extract the elements
        self.extract_all()

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
        self.button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
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
        information = self.validator.info()
        # TODO: make this a dialog

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
        self.build_widgets()

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
        # self.checkbox = QtWidgets.QCheckBox()
        # self.addWidget(self.checkbox)

        # main
        main_layout = QtWidgets.QVBoxLayout()
        self.addLayout(main_layout)
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setSpacing(0)
        main_layout.addLayout(header_layout)

        self.settings_btn = TikLabelButton()
        self.settings_btn.setFixedSize(32, 32)
        self.settings_btn.set_color(self.extract.color)
        header_layout.addWidget(self.settings_btn)
        self.label = HeaderLabel(text=self.extract.nice_name or self.extract.name)
        header_layout.addWidget(self.label)
        self.label.set_color(self.extract.color)
        self.label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.label.setFixedHeight(32)

        settings_frame = QtWidgets.QFrame()
        settings_frame.hide()
        main_layout.addWidget(settings_frame)

        self.settings_data = self.extract.settings.get(self.extract.category, None)
        print("settings_data_compare1", self.settings_data)

        print("category", self.extract.category)
        print("extract.settings", self.extract.settings)
        # print("settings_data", settings_data)
        # import pdb
        # pdb.set_trace()
        if self.settings_data:
            print("frame_rangeeee")
            print(self.settings_data.get_property("frame_range"))
            settings_ui = convert_to_ui_definition(self.settings_data)
            # settings_data = settings.Settings()
            # settings_data.set_data(settings_ui)
            # settings_layout = SettingsLayout(settings_ui, settings_data)
            settings_layout = SettingsLayout(settings_ui, self.settings_data)
            settings_frame.setLayout(settings_layout)
            print("settings_data_compare2", self.settings_data)

        # maintenance icons
        self.info = TikIconButton(icon_name=self.extract.name, circle=True)
        self.info.set_size(32)
        self.addWidget(self.info)
        def toggle_settings_visibility(state):
            if state:
                settings_frame.show()
            else:
                settings_frame.hide()


        self.settings_btn.toggled.connect(toggle_settings_visibility)


    def set_state(self, state):
        """Set the state of the extract."""
        if state == "success":
            self.status_icon.setStyleSheet("background-color: green;")
        elif state == "idle":
            self.status_icon.setStyleSheet("background-color: gray;")
        elif state == "failed":
            self.status_icon.setStyleSheet("background-color: red;")
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

    _style_file = pick.style_file()
    dialog = PublishSceneDialog(tik.project, styleSheet=str(_style_file.readAll(), "utf-8"))


    dialog.show()

    sys.exit(app.exec_())