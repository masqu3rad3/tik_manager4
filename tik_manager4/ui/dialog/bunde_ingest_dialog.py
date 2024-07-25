"""Dialog for ingesting bundled elements."""

import logging

from tik_manager4.ui.Qt import QtWidgets, QtCore

from tik_manager4.ui.dialog.feedback import Feedback
from tik_manager4.ui.dialog.data_containers import MainLayout

LOG = logging.getLogger(__name__)


class BundleIngestDialog(QtWidgets.QDialog):
    """Ingest Bundles."""

    def __init__(self):
        """Initialize."""
        super().__init__()

        self.setWindowTitle("Ingest Bundled Elements")

        self.layouts = MainLayout()
        self.layouts.master_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layouts.master_layout)

        ### TEST
        for i in range(5):
            test_piece = BundlePieceRow()
            self.layouts.master_layout.addWidget(test_piece)
            if i == 2:
                test_piece.checkbox.setChecked(True)
            if i == 3:
                test_piece.setEnabled(False)


class BundlePieceRow(QtWidgets.QFrame):
    """Row for bundle piece."""

    def __init__(self):
        super().__init__()

        # create a horizontal layout
        self.horizontal_layout = QtWidgets.QHBoxLayout()
        # self.horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.horizontal_layout)

        self.test()

        # make the frame sunken
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
    def test(self):
        """Populate some test widgets."""

        # create a label
        self.label = QtWidgets.QLabel("Test Test Test")
        self.horizontal_layout.addWidget(self.label)

        # add a stretch
        self.horizontal_layout.addStretch()

        # create a checkbox
        self.checkbox = QtWidgets.QCheckBox(text="muymuy")
        self.horizontal_layout.addWidget(self.checkbox)

        # create a button
        self.button = QtWidgets.QPushButton("press me")
        self.horizontal_layout.addWidget(self.button)


# test the dialog
if __name__ == "__main__":
    from tik_manager4.ui import pick

    _style_file = pick.style_file()
    app = QtWidgets.QApplication([])
    dialog = BundleIngestDialog()
    dialog.setStyleSheet(str(_style_file.readAll(), "utf-8"))
    dialog.show()
    app.exec_()
