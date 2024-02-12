# pylint: disable=import-error
"""Dialog for setting and authorizing the user"""

import dataclasses

from tik_manager4.ui.Qt import QtWidgets, QtCore
from tik_manager4.ui.dialog.data_containers import MainLayout
from tik_manager4.ui.dialog.feedback import Feedback
from tik_manager4.ui.widgets.common import HeaderLabel
from tik_manager4.ui.widgets.common import TikButtonBox
from tik_manager4.ui.widgets.validated_string import ValidatedString


@dataclasses.dataclass
class WidgetsData:
    """Data for the widgets"""
    user_name_le: ValidatedString = None
    initials_le: ValidatedString = None
    permission_level_combo: QtWidgets.QComboBox = None
    user_password_le: ValidatedString = None
    user_password2_le: ValidatedString = None
    users_combo: QtWidgets.QComboBox = None
    remember_cb: QtWidgets.QCheckBox = None


class NewUserDialog(QtWidgets.QDialog):
    """Dialog for setting and authorizing the user"""

    def __init__(self, user_object, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.feedback = Feedback(parent=self)
        self.user_object = user_object

        self.setWindowTitle("Create New User")
        self.setMinimumSize(400, 150)

        self.layouts = MainLayout()

        self.widgets = WidgetsData()

        self.build_ui()

    def build_ui(self):
        """Build the UI elements."""
        # layouts
        self.layouts.master_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layouts.master_layout)
        self.layouts.header_layout = QtWidgets.QVBoxLayout()
        self.layouts.master_layout.addLayout(self.layouts.header_layout)
        self.layouts.body_layout = QtWidgets.QVBoxLayout()
        self.layouts.master_layout.addLayout(self.layouts.body_layout)
        self.layouts.buttons_layout = QtWidgets.QHBoxLayout()
        self.layouts.master_layout.addLayout(self.layouts.buttons_layout)

        # form layout
        form_layout = QtWidgets.QFormLayout()
        self.layouts.body_layout.addLayout(form_layout)

        header = HeaderLabel("Add New User")
        header.set_color("orange")
        self.layouts.header_layout.addWidget(header)

        user_name_lbl = QtWidgets.QLabel()
        user_name_lbl.setText("User Name:")
        self.widgets.user_name_le = ValidatedString(name="user_name", allow_spaces=True)
        form_layout.addRow(user_name_lbl, self.widgets.user_name_le)

        initials_lbl = QtWidgets.QLabel()
        initials_lbl.setText("Initials:")
        self.widgets.initials_le = ValidatedString(name="initials")
        form_layout.addRow(initials_lbl, self.widgets.initials_le)

        permission_level_lbl = QtWidgets.QLabel()
        permission_level_lbl.setText("Permission Level:")
        self.widgets.permission_level_combo = QtWidgets.QComboBox()
        self.widgets.permission_level_combo.addItems(
            ["Observer", "Generic", "Experienced", "Admin"])
        self.widgets.permission_level_combo.setCurrentText("2")
        form_layout.addRow(permission_level_lbl, self.widgets.permission_level_combo)

        user_password_lbl = QtWidgets.QLabel()
        user_password_lbl.setText("Password :")
        self.widgets.user_password_le = ValidatedString(
            name="user_password", allow_special_characters=True
        )
        self.widgets.user_password_le.setEchoMode(QtWidgets.QLineEdit.Password)
        form_layout.addRow(user_password_lbl, self.widgets.user_password_le)

        user_password2_lbl = QtWidgets.QLabel()
        user_password2_lbl.setText("Password Again :")
        self.widgets.user_password2_le = ValidatedString(
            name="user_password", allow_special_characters=True
        )
        self.widgets.user_password2_le.setEchoMode(QtWidgets.QLineEdit.Password)
        form_layout.addRow(user_password2_lbl, self.widgets.user_password2_le)

        # button box
        button_box = TikButtonBox()
        button_box.setOrientation(QtCore.Qt.Horizontal)
        button_box.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )
        self.layouts.buttons_layout.addWidget(button_box)

        self.widgets.user_name_le.set_connected_widgets(
            button_box.button(QtWidgets.QDialogButtonBox.Ok)
        )
        self.widgets.initials_le.set_connected_widgets(
            button_box.button(QtWidgets.QDialogButtonBox.Ok)
        )
        self.widgets.user_password_le.set_connected_widgets(
            button_box.button(QtWidgets.QDialogButtonBox.Ok)
        )
        self.widgets.user_password2_le.set_connected_widgets(
            button_box.button(QtWidgets.QDialogButtonBox.Ok)
        )

        button_box.accepted.connect(self.on_create_user)
        button_box.rejected.connect(self.reject)

    def on_create_user(self):
        """Create the user."""
        if not self.check_passwords():
            return
        _name = self.widgets.user_name_le.text()
        _initials = self.widgets.initials_le.text()
        _password = self.widgets.user_password_le.text()
        # get the permission level. It is the index of the combo
        _permission_level = self.widgets.permission_level_combo.currentIndex()

        state, msg = self.user_object.create_new_user(
            _name, _initials, _password, _permission_level
        )
        if state != 1:
            self.feedback.pop_info(title="User Creation Error", text=msg, critical=True)
            return
        self.accept()

    def check_passwords(self):
        """Compare the passwords. Pop a user message if they don't match"""
        _password = self.widgets.user_password_le.text()
        _password2 = self.widgets.user_password2_le.text()
        if _password != _password2:
            self.feedback.pop_info(
                title="Paswords not matching",
                text="Passwords entered don't match",
                critical=True,
            )
            # clear the passwords
            self.widgets.user_password_le.setText("")
            self.widgets.user_password2_le.setText("")
            return False
        return True


class LoginDialog(QtWidgets.QDialog):
    """Dialog for setting and authorizing the user"""

    def __init__(self, user_object, *args, **kwargs):
        self.user_object = user_object
        super().__init__(*args, **kwargs)

        self.setWindowTitle("User Login")
        self.setMinimumSize(300, 150)

        self.feedback = Feedback(parent=self)

        self.widgets = WidgetsData()

        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)

        # form layout
        self.form_layout = QtWidgets.QFormLayout()
        main_layout.addLayout(self.form_layout)

        # button box
        self.button_box = TikButtonBox()
        self.button_box.setStandardButtons(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )

        main_layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self.on_accept)
        self.button_box.rejected.connect(self.reject)

        self.build_ui()

    def build_ui(self):
        """Build the UI elements."""
        user_name_lbl = QtWidgets.QLabel()
        user_name_lbl.setText("User :")
        self.widgets.users_combo = QtWidgets.QComboBox()
        self.widgets.users_combo.addItems(self.user_object.commons.users.keys)

        # get the activeUser
        active_user = self.user_object.get()
        # if the active user is in the list, select it
        if active_user and active_user in self.user_object.commons.users.keys:
            self.widgets.users_combo.setCurrentText(active_user)

        user_password_lbl = QtWidgets.QLabel()
        user_password_lbl.setText("Password :")
        self.widgets.user_password_le = QtWidgets.QLineEdit()
        self.widgets.user_password_le.setEchoMode(QtWidgets.QLineEdit.Password)

        remember_lbl = QtWidgets.QLabel()
        remember_lbl.setToolTip("If checked, remember this user until logout")
        remember_lbl.setText("Remember :")
        self.widgets.remember_cb = QtWidgets.QCheckBox()
        self.widgets.remember_cb.setChecked(True)

        self.form_layout.addRow(user_name_lbl, self.widgets.users_combo)
        self.form_layout.addRow(user_password_lbl, self.widgets.user_password_le)
        self.form_layout.addRow(remember_lbl, self.widgets.remember_cb)

    def on_accept(self):
        """Accept the dialog"""
        user = self.widgets.users_combo.currentText()
        password = self.widgets.user_password_le.text()
        remember = self.widgets.remember_cb.isChecked()
        state, msg = self.user_object.set(
            user, password, save_to_db=remember, clear_db=not remember
        )
        if state != -1:
            self.accept()
        else:
            self.feedback.pop_info(title="Error", text=msg, critical=True)


if __name__ == "__main__":
    import sys
    import tik_manager4
    from tik_manager4.ui import pick

    app = QtWidgets.QApplication(sys.argv)
    tik = tik_manager4.initialize("Standalone")
    # tik.user.set("Admin", "1234")
    # tik.user.set("Generic", "1234")
    dialog = NewUserDialog(tik.user)
    _style_file = pick.style_file()
    dialog.setStyleSheet(str(_style_file.readAll(), "utf-8"))
    dialog.show()
    sys.exit(app.exec_())
