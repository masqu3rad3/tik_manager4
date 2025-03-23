"""Custom widgets for setting / displaying users"""

from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.ui.dialog.user_dialog import LoginDialog
from tik_manager4.ui.widgets.common import TikButton, ResolvedText

class TikUserWidget(QtWidgets.QWidget):
    """Widget for displaying user information"""

    def __init__(self, user_obj, parent=None):
        super().__init__()
        self.parent = parent
        self.user_obj = user_obj

        self.layout = TikUserLayout(user_obj, parent=parent)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

    def refresh(self):
        """Refresh the user name"""
        self.layout.refresh()

    def on_set_user(self):
        """Set the user"""
        self.layout.on_set_user()

class TikUserLayout(QtWidgets.QHBoxLayout):
    """Layout for displaying user information"""

    def __init__(self, user_obj, parent=None):
        super().__init__()
        self.parent = parent
        self.user_obj = user_obj

        _user_lbl = QtWidgets.QLabel()
        _user_lbl.setMaximumHeight(30)
        _user_lbl.setText("User: ")
        self.addWidget(_user_lbl)

        self.user_name_lbl = ResolvedText(self.user_obj.get())
        self.user_name_lbl.setMaximumHeight(30)
        self.addWidget(self.user_name_lbl)

        self.set_user_btn = TikButton()
        self.set_user_btn.setMaximumHeight(30)
        self.set_user_btn.setText("Login")
        self.set_user_btn.setToolTip("Opens up User Login Dialog")
        self.addWidget(self.set_user_btn)

        # SIGNALS
        self.set_user_btn.clicked.connect(self.on_set_user)
        self.refresh()

    def refresh(self):
        """Refresh the user name"""
        self.user_name_lbl.setText(self.user_obj.get())

    def on_set_user(self):
        """Set the user to display"""
        # get the parent dialog
        dialog = LoginDialog(self.user_obj, parent=self.parent or self.set_user_btn.window())
        state = dialog.exec_()
        if state == 1:
            self.refresh()
