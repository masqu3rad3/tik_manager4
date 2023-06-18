"""Dialog for setting and authorizing the user"""
from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
from tik_manager4.ui.dialog.feedback import Feedback
from tik_manager4.ui.widgets.common import TikButtonBox
from tik_manager4.ui.widgets.validated_string import ValidatedString

class NewUserDialog(QtWidgets.QDialog):
    """Dialog for setting and authorizing the user"""
    def __init__(self, user_object, *args, **kwargs):
        super(NewUserDialog, self).__init__(*args, **kwargs)
        self.feedback = Feedback(parent=self)
        self.user_object = user_object

        self.setWindowTitle("Create New User")
        self.setMinimumSize(500, 150)

        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)

        # form layout
        self.form_layout = QtWidgets.QFormLayout()
        main_layout.addLayout(self.form_layout)

        _user_name_lbl = QtWidgets.QLabel()
        _user_name_lbl.setText("User Name:")
        self._user_name_le = ValidatedString(name="user_name", allow_spaces=True)
        self.form_layout.addRow(_user_name_lbl, self._user_name_le)

        _initials_lbl = QtWidgets.QLabel()
        _initials_lbl.setText("Initials:")
        self._initials_le = ValidatedString(name="initials")
        self.form_layout.addRow(_initials_lbl, self._initials_le)

        _permission_level_lbl = QtWidgets.QLabel()
        _permission_level_lbl.setText("Permission Level:")
        self._permission_level_combo = QtWidgets.QComboBox()
        self._permission_level_combo.addItems(["0", "1", "2", "3"])
        self._permission_level_combo.setCurrentText("2")
        self.form_layout.addRow(_permission_level_lbl, self._permission_level_combo)

        _user_password_lbl = QtWidgets.QLabel()
        _user_password_lbl.setText("Password :")
        self._user_password_le = ValidatedString(name="user_password", allow_special_characters=True)
        self._user_password_le.setEchoMode(QtWidgets.QLineEdit.Password)
        self.form_layout.addRow(_user_password_lbl, self._user_password_le)

        _user_password2_lbl = QtWidgets.QLabel()
        _user_password2_lbl.setText("Password Again :")
        self._user_password2_le = ValidatedString(name="user_password", allow_special_characters=True)
        self._user_password2_le.setEchoMode(QtWidgets.QLineEdit.Password)
        self.form_layout.addRow(_user_password2_lbl, self._user_password2_le)

        # _remember_lbl = QtWidgets.QLabel()
        # _remember_lbl.setToolTip("If checked, remember this user on this machine")
        # _remember_lbl.setText("Remember :")
        # self._remember_cb = QtWidgets.QCheckBox()
        # self._remember_cb.setChecked(True)
        # self.form_layout.addRow(_remember_lbl, self._remember_cb)

        # button box
        self.button_box = TikButtonBox()
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )

        self._user_name_le.set_connected_widgets(self.button_box.button(QtWidgets.QDialogButtonBox.Ok))
        self._initials_le.set_connected_widgets(self.button_box.button(QtWidgets.QDialogButtonBox.Ok))
        self._user_password_le.set_connected_widgets(self.button_box.button(QtWidgets.QDialogButtonBox.Ok))
        self._user_password2_le.set_connected_widgets(self.button_box.button(QtWidgets.QDialogButtonBox.Ok))

        self.button_box.accepted.connect(self._on_create_user)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

    def _on_create_user(self):
        if not self._check_passwords():
            return
        _name = self._user_name_le.text()
        _initials = self._initials_le.text()
        _password = self._user_password_le.text()
        _permission_level = self._permission_level_combo.currentText()
        state, msg = self.user_object.create_new_user(_name, _initials, _password, _permission_level)
        if state != 1:
            self.feedback.pop_info(title="User Creation Error", text=msg, critical=True)
            return
        else:
            self.accept()

    def _check_passwords(self):
        """Compare the passwords. Pop a user message if they don't match"""
        _password = self._user_password_le.text()
        _password2 = self._user_password2_le.text()
        if _password != _password2:
            self.feedback.pop_info(title="Paswords not matching", text="Passwords entered don't match", critical=True)
            # clear the passwords
            self._user_password_le.setText("")
            self._user_password2_le.setText("")
            return False
        return True

class LoginDialog(QtWidgets.QDialog):
    """Dialog for setting and authorizing the user"""

    def __init__(self, user_object, *args, **kwargs):
        self.user_object = user_object
        super(LoginDialog, self).__init__(*args, **kwargs)

        self.setWindowTitle("Set User")
        self.setMinimumSize(300, 150)

        self.feedback = Feedback(parent=self)

        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)

        # form layout
        self.form_layout = QtWidgets.QFormLayout()
        main_layout.addLayout(self.form_layout)

        _user_name_lbl = QtWidgets.QLabel()
        _user_name_lbl.setText("User :")
        self._users_combo = QtWidgets.QComboBox()
        self._users_combo.addItems(self.user_object.commons.users.keys)

        # get the activeUser
        # _active_user = self.user_object.bookmarks.get_property("activeUser")
        _active_user = self.user_object.get()
        # if the active user is in the list, select it
        if _active_user and _active_user in self.user_object.commons.users.keys:
            self._users_combo.setCurrentText(_active_user)

        _user_password_lbl = QtWidgets.QLabel()
        _user_password_lbl.setText("Password :")
        self._user_password_le = QtWidgets.QLineEdit()
        self._user_password_le.setEchoMode(QtWidgets.QLineEdit.Password)

        _remember_lbl = QtWidgets.QLabel()
        _remember_lbl.setToolTip("If checked, remember this user until logout")
        _remember_lbl.setText("Remember :")
        self._remember_cb = QtWidgets.QCheckBox()
        self._remember_cb.setChecked(True)

        self.form_layout.addRow(_user_name_lbl, self._users_combo)
        self.form_layout.addRow(_user_password_lbl, self._user_password_le)
        self.form_layout.addRow(_remember_lbl, self._remember_cb)

        # button box
        self.button_box = TikButtonBox()
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

        main_layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self.on_accept)
        self.button_box.rejected.connect(self.reject)

    def on_accept(self):
        """Accept the dialog"""
        _user = self._users_combo.currentText()
        _password = self._user_password_le.text()
        _remember = self._remember_cb.isChecked()
        # TODO: _remember NEEDS TO CHECK double-hashes for 'some' security
        state, msg = self.user_object.set(_user, _password, save_to_db=_remember, clear_db=not _remember)
        if state != -1:
            self.accept()
        else:
            self.feedback.pop_info(title="Error", text=msg, critical=True)

    def _on_user_name_changed(self, text):
        """Set the user name"""
        self._user_name = text

    def _on_user_password_changed(self, text):
        """Set the user"""
        pass
#
# # Test the dialog
# if __name__ == "__main__":
#     import sys
#     import tik_manager4
#     from tik_manager4.ui import pick
#     app = QtWidgets.QApplication(sys.argv)
#     tik = tik_manager4.initialize("Standalone")
#     dialog = LoginDialog(tik)
#     _style_file = pick.style_file()
#     dialog.setStyleSheet(str(_style_file.readAll(), 'utf-8'))
#     dialog.show()
#     sys.exit(app.exec_())

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
    dialog.setStyleSheet(str(_style_file.readAll(), 'utf-8'))
    dialog.show()
    sys.exit(app.exec_())