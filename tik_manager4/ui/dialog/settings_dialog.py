"""Dialog for settings."""

import logging

from tik_manager4.core import settings
from tik_manager4.ui.Qt import QtWidgets, QtCore
from tik_manager4.ui.widgets.common import TikLabel, TikLabelButton, HeaderLabel, ResolvedText, TikButtonBox, TikButton, TikIconButton
from tik_manager4.ui.layouts.settings_layout import SettingsLayout, convert_to_ui_definition
from tik_manager4.ui.dialog.feedback import Feedback

LOG = logging.getLogger(__name__)

class SettingsDialog(QtWidgets.QDialog):
    """Settings dialog."""

    def __init__(self):
        super(SettingsDialog, self).__init__()

        self.setWindowTitle("Settings")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        self.splitter = QtWidgets.QSplitter(self)

        self.left_widget = QtWidgets.QWidget(self.splitter)
        self.left_verticalLayout = QtWidgets.QVBoxLayout(self.left_widget)
        self.left_verticalLayout.setContentsMargins(0, 0, 0, 0)

        self.treeWidget = QtWidgets.QTreeWidget(self.left_widget)
        self.treeWidget.setRootIsDecorated(True)
        self.treeWidget.setHeaderHidden(True)
        self.treeWidget.header().setVisible(False)
        self.left_verticalLayout.addWidget(self.treeWidget)

        self.right_widget = QtWidgets.QWidget(self.splitter)
        self.right_verticalLayout = QtWidgets.QVBoxLayout(self.right_widget)
        self.right_verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.right_scrollArea = QtWidgets.QScrollArea(self.right_widget)
        self.right_scrollArea.setWidgetResizable(True)
        self.right_scrollAreaWidgetContents = QtWidgets.QWidget()
        self.right_scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 104, 345))

        self.right_contents_layout = QtWidgets.QVBoxLayout(self.right_scrollAreaWidgetContents)
        self.formLayout = QtWidgets.QFormLayout()
        self.right_contents_layout.addLayout(self.formLayout)

        self.right_scrollArea.setWidget(self.right_scrollAreaWidgetContents)
        self.right_verticalLayout.addWidget(self.right_scrollArea)

        self.main_layout.addWidget(self.splitter)

        self.buttonBox_layout = QtWidgets.QHBoxLayout()
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox_layout.addWidget(self.buttonBox)
        self.main_layout.addLayout(self.buttonBox_layout)

        self.resize(960, 630)


# test the dialog
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    dialog = SettingsDialog()
    dialog.show()
    sys.exit(app.exec_())