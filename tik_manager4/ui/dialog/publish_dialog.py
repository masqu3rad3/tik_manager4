"""Dialogs for publishing files."""
from time import time
import logging
from tik_manager4.ui.Qt import QtWidgets, QtCore
from tik_manager4.ui.widgets.common import TikLabel, HeaderLabel, ResolvedText, TikButtonBox, TikButton, TikIconButton

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


        self.master_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.master_layout)

        self.header_layout = QtWidgets.QVBoxLayout()
        self.header_layout.setContentsMargins(0, 10, 0, 0)
        self.master_layout.addLayout(self.header_layout)

        self.body_layout = QtWidgets.QHBoxLayout()
        self.master_layout.addLayout(self.body_layout)

        # squish everything to the top
        self.master_layout.addStretch()

        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.master_layout.addLayout(self.buttons_layout)

        splitter = QtWidgets.QSplitter(self)
        splitter.setHandleWidth(5)

        self.body_layout.addWidget(splitter)
        splitter.setFrameShape(QtWidgets.QFrame.NoFrame)
        splitter.setOrientation(QtCore.Qt.Horizontal)

        # left body widget and layout
        left_body_widget = QtWidgets.QWidget(splitter)
        left_body_widget.setMinimumHeight(500)
        left_body_layout = QtWidgets.QVBoxLayout(left_body_widget)

        self.left_body_header_layout = QtWidgets.QVBoxLayout()
        left_body_layout.addLayout(self.left_body_header_layout)

        # create a scroll area
        left_body_scroll_area = QtWidgets.QScrollArea(splitter)
        left_body_scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        left_body_scroll_area.setFrameShadow(QtWidgets.QFrame.Sunken)
        left_body_scroll_area.setWidgetResizable(True)

        left_body_scroll_area_widget_contents = QtWidgets.QWidget()

        self.left_body_scroll_area_v_lay = QtWidgets.QVBoxLayout(
            left_body_scroll_area_widget_contents
        )


        left_body_scroll_area.setWidget(left_body_scroll_area_widget_contents)
        left_body_layout.addWidget(left_body_scroll_area)


        # right body widget and layout
        right_body_widget = QtWidgets.QWidget(splitter)
        right_body_widget.setMinimumHeight(500)
        right_body_layout = QtWidgets.QVBoxLayout(right_body_widget)

        self.right_body_header_layout = QtWidgets.QVBoxLayout()
        right_body_layout.addLayout(self.right_body_header_layout)

        # create a scroll area
        right_body_scroll_area = QtWidgets.QScrollArea(splitter)
        right_body_scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        right_body_scroll_area.setFrameShadow(QtWidgets.QFrame.Sunken)
        right_body_scroll_area.setWidgetResizable(True)

        right_body_scroll_area_widget_contents = QtWidgets.QWidget()

        self.right_body_scroll_area_v_lay = QtWidgets.QVBoxLayout(
            right_body_scroll_area_widget_contents
        )

        right_body_scroll_area.setWidget(right_body_scroll_area_widget_contents)
        right_body_layout.addWidget(right_body_scroll_area)

        # self.right_body_layout = QtWidgets.QVBoxLayout(right_body_widget)
        # self.right_body_layout.setContentsMargins(10, 2, 10, 10)

        self.build_ui()

        self.resize(800, 600)

        splitter.setSizes([600, 400])



    def check_eligibility(self):
        """Checks if the current scene is eligible for publishing."""
        if not self.project.publisher._work_object:
            self.feedback.pop_info(title="Non-valid Scene", text="Current Scene does not belong to a 'Work'. It is required to save scenes as a 'Work' before publishing.")
            # destroy the dialog. make it dispappear
            self.close()
            self.deleteLater()
            # raise Exception("Current Scene does not belong to a 'Work'. It is required to save scenes as a 'Work' before publishing.")
            return

    def build_ui(self):

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

        validations_label = QtWidgets.QLabel("Validations")
        validations_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.left_body_header_layout.addWidget(validations_label)
        separator = QtWidgets.QLabel()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        separator.setStyleSheet("background-color: rgb(221, 160, 221);")
        separator.setFixedHeight(1)
        self.left_body_header_layout.addWidget(separator)

        # ADD VALIDATIONS HERE
        # -------------------
        for validator_name, validator in self.project.publisher.validators.items():
            validate_row = ValidateRow(validator_object=validator)
            self.left_body_scroll_area_v_lay.addLayout(validate_row)
            self._validator_widgets.append(validate_row)
        # -------------------
        self.left_body_scroll_area_v_lay.addStretch()

        # right body layout
        extracts_label = QtWidgets.QLabel("Extracts")
        extracts_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.right_body_header_layout.addWidget(extracts_label)
        separator = QtWidgets.QLabel()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        separator.setStyleSheet("background-color: rgb(221, 160, 221);")
        separator.setFixedHeight(1)
        self.right_body_header_layout.addWidget(separator)

        # ADD EXTRACTS HERE
        # -------------------
        for extractor_name, extractor in self.project.publisher.extractors.items():
            extract_row = ExtractRow(extract_object=extractor)
            self.right_body_scroll_area_v_lay.addLayout(extract_row)
            self._extractor_widgets.append(extract_row)
        # -------------------
        self.right_body_scroll_area_v_lay.addStretch()

        # buttons layout
        button_box = TikButtonBox()
        validate_pb = button_box.addButton("Validate", QtWidgets.QDialogButtonBox.YesRole)
        publish_pb = button_box.addButton("Publish", QtWidgets.QDialogButtonBox.AcceptRole)
        button_box.addButton("Cancel", QtWidgets.QDialogButtonBox.RejectRole)
        self.buttons_layout.addWidget(button_box)

        # SIGNALS
        button_box.rejected.connect(self.reject)
        validate_pb.clicked.connect(self.validate_all)
        # # connect the publish button to publish the scene
        # publish_button = button_box.button("Publish")
        # publish_button.clicked.connect(self.publish)
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
        self.project.publisher.extract()
        # finalize publish
        self.project.publisher.publish()
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

        # button
        self.label = HeaderLabel(text=self.extract.nice_name or self.extract.name)
        self.label.set_color(self.extract.color)
        # stretch it to the layout
        self.label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.label.setFixedHeight(32)
        self.addWidget(self.label)

        # maintenance icons
        self.info = TikIconButton(icon_name=self.extract.name, circle=True)
        self.info.set_size(32)
        self.addWidget(self.info)






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