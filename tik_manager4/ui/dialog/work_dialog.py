"""Dialogs for creating work files and versions of them."""

from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui

class NewWorkDialog(QtWidgets.QDialog):
    def __init__(self):
        super(NewWorkDialog, self).__init__()
        self.setWindowTitle("New Work File")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.create_widgets()
        self.create_layout()
        self.create_connections()