"""Dialogs for publishing files."""

from tik_manager4.ui.Qt import QtWidgets, QtCore
from tik_manager4.ui.widgets.common import HeaderLabel, ResolvedText, TikButtonBox, TikButton, TikIconButton

from tik_manager4.ui.dialog.feedback import Feedback


class PublishSceneDialog(QtWidgets.QDialog):
    """Publishes the current scene."""
    def __init__(self, project_object, *args, **kwargs):
        """Initialize the PublishSceneDialog."""
        super(PublishSceneDialog, self).__init__(*args, **kwargs)

        # instanciate the publisher class
        self.feedback = Feedback(parent=self)
        self.project = project_object
        self.project.publisher.resolve()

        # self.check_eligibility()



        self.setWindowTitle("Publish Scene")
        self.resize(800, 600)

        self.master_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.master_layout)

        self.header_layout = QtWidgets.QVBoxLayout()
        self.master_layout.addLayout(self.header_layout)

        self.body_layout = QtWidgets.QHBoxLayout()
        self.master_layout.addLayout(self.body_layout)

        # squish everything to the top
        self.master_layout.addStretch()

        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.master_layout.addLayout(self.buttons_layout)

        splitter = QtWidgets.QSplitter(self)
        splitter.setHandleWidth(3)

        self.body_layout.addWidget(splitter)
        splitter.setFrameShape(QtWidgets.QFrame.NoFrame)
        splitter.setOrientation(QtCore.Qt.Horizontal)

        # left body widget and layout
        left_body_widget = QtWidgets.QWidget(splitter)
        # self.left_body_widget.setMinimumSize(500, 500)
        left_body_widget.setMinimumHeight(500)
        self.left_body_layout = QtWidgets.QVBoxLayout(left_body_widget)
        self.left_body_layout.setContentsMargins(10, 2, 10, 10)

        self.left_body_header_layout = QtWidgets.QVBoxLayout()
        self.left_body_layout.addLayout(self.left_body_header_layout)

        # create a scroll area
        left_body_scroll_area = QtWidgets.QScrollArea()
        left_body_scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        left_body_scroll_area.setFrameShadow(QtWidgets.QFrame.Sunken)
        left_body_scroll_area.setWidgetResizable(True)

        self.left_body_scroll_area_widget_contents = QtWidgets.QWidget()
        # self.left_body_scroll_area_widget_contents.setSizePolicy(
        #     QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        # )

        self.left_body_scroll_area_v_lay = QtWidgets.QVBoxLayout(
            self.left_body_scroll_area_widget_contents
        )


        left_body_scroll_area.setWidget(self.left_body_scroll_area_widget_contents)
        self.left_body_layout.addWidget(left_body_scroll_area)


        # right body widget and layout
        right_body_widget = QtWidgets.QWidget(splitter)
        self.right_body_layout = QtWidgets.QVBoxLayout(right_body_widget)
        self.right_body_layout.setContentsMargins(10, 2, 10, 10)

        self.build_ui()
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
        header = HeaderLabel("Publish Scene")
        header.set_color("orange")
        self.header_layout.addWidget(header)

        # resolved path
        path = self.project.publisher.relative_scene_path or "Path Not Resolved"
        path_label = ResolvedText(path)
        self.header_layout.addWidget(path_label)
        path_label.set_color("gray")
        name = self.project.publisher.publish_name or "Name Not Resolved"
        name_label = ResolvedText(name)
        name_label.set_color("green")
        self.header_layout.addWidget(name_label)

        # -- TEST --
        # put some test buttons inside left and right body layouts
        # left body layout
        # validations label
        # validations_label = HeaderLabel("Validations")
        validations_label = QtWidgets.QLabel("Validations")
        # validations_label.set_color("orange")
        validations_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        # self.left_body_layout.addWidget(validations_label)
        self.left_body_header_layout.addWidget(validations_label)
        separator = QtWidgets.QLabel()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        separator.setStyleSheet("background-color: rgb(221, 160, 221);")
        separator.setFixedHeight(1)
        self.left_body_header_layout.addWidget(separator)

        # ADD VALIDATIONS HERE
        # -------------------
        for i in range(5):
            validate_row = ValidateRow()
            # self.left_body_layout.addLayout(validate_row)
            self.left_body_scroll_area_v_lay.addLayout(validate_row)
        # -------------------
        self.left_body_scroll_area_v_lay.addStretch()


        # left_body_header = TikButton("Left Body Header")
        # self.left_body_layout.addWidget(left_body_header)
        # right body layout
        right_body_header = TikButton("Right Body Header")
        self.right_body_layout.addWidget(right_body_header)

        # icon_button1 = TikIconButton(icon_name="info.png")
        # icon_button1.setFixedSize(30, 30)
        # icon_button2 = TikIconButton(icon_name="select.png")
        # icon_button2.setFixedSize(30, 30)
        # icon_button3 = TikIconButton(icon_name="fix.png")
        # icon_button3.setFixedSize(30, 30)
        # self.right_body_layout.addWidget(icon_button1)
        # self.right_body_layout.addWidget(icon_button2)
        # self.right_body_layout.addWidget(icon_button3)
        # -- TEST -- [END]



        # buttons layout
        # self.buttons_layout.addStretch()
        button_box = TikButtonBox()
        button_box.addButton("Validate", QtWidgets.QDialogButtonBox.YesRole)
        button_box.addButton("Publish", QtWidgets.QDialogButtonBox.AcceptRole)
        button_box.addButton("Cancel", QtWidgets.QDialogButtonBox.RejectRole)
        self.buttons_layout.addWidget(button_box)



class ValidateRow(QtWidgets.QHBoxLayout):
    """Custom Layout for validation rows."""
    def __init__(self, validator_object=None, *args, **kwargs):
        """Initialize the ValidateRow."""
        super(ValidateRow, self).__init__(*args, **kwargs)
        self.validator = validator_object
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
        self.checkbox = QtWidgets.QCheckBox()
        self.addWidget(self.checkbox)

        # button
        self.button = TikButton(text="TEST") # TODO: change this with self.validator.name
        # stretch it to the layout
        self.button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.button.setFixedHeight(22)
        self.addWidget(self.button)

        # maintenance icons
        self.info = TikIconButton(icon_name="info.png")
        self.select = TikIconButton(icon_name="select.png")
        self.fix = TikIconButton(icon_name="fix.png")
        self.addWidget(self.info)
        self.addWidget(self.select)
        self.addWidget(self.fix)





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