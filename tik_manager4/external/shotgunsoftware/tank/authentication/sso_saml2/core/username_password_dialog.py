# Copyright (c) 2017 Autodesk.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.
"""
Module to support Web login via a web browser and automated session renewal.
"""

from __future__ import print_function

# pylint: disable=import-error
from ...ui.qt_abstraction import QtCore, QtGui

# No point in proceeding if QtGui is None.
if QtGui is None:
    raise ImportError("Unable to import QtGui")


class UsernamePasswordDialog(QtGui.QDialog):
    """Simple dialog to request a username and password from the user."""

    def __init__(self, window_title=None, message=None):
        super(UsernamePasswordDialog, self).__init__()

        if window_title is None:
            window_title = "Please enter your credentials"
        if message is None:
            message = ""
        self.setWindowTitle(window_title)

        # For now we fix the GUI size.
        self.setMinimumWidth(420)
        self.setMinimumHeight(120)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        # set up the layout
        form_grid_layout = QtGui.QGridLayout(self)

        # initialize the username combo box so that it is editable
        self._edit_username = QtGui.QLineEdit(self)
        self._edit_username.setPlaceholderText("Domain\\Username or email address")

        # initialize the password field so that it does not echo characters
        self._edit_password = QtGui.QLineEdit(self)
        self._edit_password.setEchoMode(QtGui.QLineEdit.Password)
        self._edit_password.setPlaceholderText("Password")

        # initialize the labels
        label_message = QtGui.QLabel(self)
        label_message.setText(message)
        label_message.setWordWrap(True)

        # initialize buttons
        buttons = QtGui.QDialogButtonBox(self)
        buttons.addButton(QtGui.QDialogButtonBox.Ok)
        buttons.addButton(QtGui.QDialogButtonBox.Cancel)
        buttons.button(QtGui.QDialogButtonBox.Ok).setText("Login")
        buttons.button(QtGui.QDialogButtonBox.Cancel).setText("Cancel")

        # place components into the dialog
        form_grid_layout.addWidget(label_message, 0, 0)
        form_grid_layout.addWidget(self._edit_username, 1, 0)
        form_grid_layout.addWidget(self._edit_password, 2, 0)
        form_grid_layout.setRowMinimumHeight(3, 20)
        form_grid_layout.addWidget(buttons, 4, 0)

        self.setLayout(form_grid_layout)

        buttons.button(QtGui.QDialogButtonBox.Ok).clicked.connect(
            self._on_enter_credentials
        )
        buttons.button(QtGui.QDialogButtonBox.Cancel).clicked.connect(self.close)

        # On Qt4, this sets the look-and-feel to that of the toolkit.
        self.setStyleSheet(
            """QWidget
            {
                background-color:  rgb(36, 39, 42);
                color: rgb(192, 193, 195);
                selection-background-color: rgb(168, 123, 43);
                selection-color: rgb(230, 230, 230);
                font-size: 11px;
                color: rgb(192, 192, 192);
            }
            QPushButton
            {
                background-color: transparent;
                border-radius: 2px;
                padding: 8px;
                padding-left: 15px;
                padding-right: 15px;
            }
            QPushButton:default
            {
                color: rgb(248, 248, 248);
                background-color: rgb(35, 165, 225);
            }
            """
        )

    @property
    def username(self):
        """Getter for username."""
        return self._edit_username.text()

    @username.setter
    def username(self, username):
        """Setter for username."""
        self._edit_username.setText(username)

    @property
    def password(self):
        """Getter for password."""
        return self._edit_password.text()

    @password.setter
    def password(self, password):
        """Setter for password."""
        self._edit_password.setText(password)

    def _on_enter_credentials(self):
        """Callback when clicking Ok."""
        if self._edit_username.text() == "":
            self._edit_username.setFocus()
            return

        if self._edit_password.text() == "":
            self._edit_password.setFocus()
            return

        self.accept()


def main():
    """Simple test"""
    _ = QtGui.QApplication([])
    window_title = "A title"
    message = "A message"
    login_dialog = UsernamePasswordDialog(window_title=window_title, message=message)
    login_dialog.username = "TheUsername"
    login_dialog.password = "ThePassword"
    if login_dialog.exec_():
        print("Username: %s" % login_dialog.username)
        print("Password: %s" % login_dialog.password)
    else:
        print("Canceled the operation")


if __name__ == "__main__":
    main()
