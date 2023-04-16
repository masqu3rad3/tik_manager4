"""Dialog for setting and authorizing the user"""
from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
from tik_manager4.ui.dialog.feedback import Feedback

class LoginDialog(QtWidgets.QDialog):
    """Dialog for setting and authorizing the user"""

    def __init__(self, main_object, selected_user=None, *args, **kwargs):
        self.main_object = main_object
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
        self._users_combo.addItems(self.main_object.user.commons.users.keys)
        # if the selected user is not None and among the users, select it
        if selected_user and selected_user in self.main_object.user.commons.users.keys:
            self._users_combo.setCurrentText(selected_user)

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
        self.button_box = QtWidgets.QDialogButtonBox()
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

        main_layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self.on_accept)
        self.button_box.rejected.connect(self.reject)

        # self._user_name_le.textChanged.connect(self._on_user_name_changed)
        # self._user_password_le.textChanged.connect(self._on_user_password_changed)

        # self._user_name_le.setText(self.main_object.user.name)
        # self._user_password_le.setText(self.main_object.user.password)

        # self._user_name_le.setReadOnly(True)



        # _user_name_layout = QtWidgets.QHBoxLayout()
        # _user_name_layout.addWidget(_user_name_lbl)
        # _user_name_layout.addWidget(self._users_combo)
        #
        # _user_password_layout = QtWidgets.QHBoxLayout()
        # _user_password_layout.addWidget(_user_password_lbl)
        # _user_password_layout.addWidget(self._user_password_le)
        #
        # _button_layout = QtWidgets.QHBoxLayout()
        # _button_layout.addStretch(1)
        # _button_layout.setContentsMargins(0, 0, 0, 0)
        # _button_layout.setSpacing(0)
        #
        # _ok_btn = QtWidgets.QPushButton()
        # _ok_btn.setText("OK")
        # _ok_btn.clicked.connect(self.accept)
        # _cancel_btn = QtWidgets.QPushButton()
        # _cancel_btn.setText("Cancel")
        # _cancel_btn.clicked.connect(self.reject)
        #
        # _button_layout.addWidget(_ok_btn)
        # _button_layout.addWidget(_cancel_btn)
        #
        # main_layout = QtWidgets.QVBoxLayout()
        # main_layout.addLayout(_user_name_layout)
        # main_layout.addLayout(_user_password_layout)
        # main_layout.addLayout(_button_layout)

    def on_accept(self):
        """Accept the dialog"""
        _user = self._users_combo.currentText()
        _password = self._user_password_le.text()
        _remember = self._remember_cb.isChecked()
        # TODO: _remember NEEDS TO CHECK double-hashes for 'some' security
        state, msg = self.main_object.user.set(_user, _password, save_to_db=_remember)
        print("state", state)
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

# Test the dialog
if __name__ == "__main__":
    import sys
    import tik_manager4
    from tik_manager4.ui import pick
    app = QtWidgets.QApplication(sys.argv)
    tik = tik_manager4.initialize("Standalone")
    dialog = LoginDialog(tik)
    _style_file = pick.style_file()
    dialog.setStyleSheet(str(_style_file.readAll(), 'utf-8'))
    dialog.show()
    sys.exit(app.exec_())