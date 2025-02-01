from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
from tik_manager4.ui.widgets.common import TikButton
from tik_manager4.ui import pick

def launch_interrupt(parent=None):
    """Launch the support splash screen"""
    splash = SupportSplashScreen(parent=parent)
    splash.exec_()
    return splash

def launch_support(parent=None):
    """Launch the support dialog"""
    support = SupportDialog(parent=parent)
    support.show()
    return support

class SupportSplashScreen(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(SupportSplashScreen, self).__init__(parent)
        self.setWindowTitle("Support Tik Manager")
        self.setModal(True)
        _style_file = pick.style_file()
        self.setStyleSheet("background-color: #222; color: #EEE; border-radius: 10px;")

        # Layouts
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Header
        title_label = QtWidgets.QLabel("Sorry for the Interruption")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #FE7E00;")
        main_layout.addWidget(title_label)

        # Sub Header
        sub_label = QtWidgets.QLabel("We know pop-ups are annoying!")
        sub_label.setAlignment(QtCore.Qt.AlignCenter)
        sub_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(sub_label)

        # Message
        message_label = QtWidgets.QLabel(
            "<p>So we’ll keep this short—just like the time between your last save and that unexpected crash.</p>"
            "<p>Tik Manager is free and open-source, and we want to keep it that way! If you find it useful, consider supporting its development. No pressure, but even a small contribution helps keep things running smoothly (and buys us more coffee ☕).</p>"
        )
        message_label.setWordWrap(True)
        message_label.setAlignment(QtCore.Qt.AlignCenter)
        message_label.setStyleSheet("font-size: 14px;")
        main_layout.addWidget(message_label)

        # Checkbox
        self.dont_show_again_cb = QtWidgets.QCheckBox("Spare me from pop-ups (until the next update)")
        self.dont_show_again_cb.setChecked(True)
        self.dont_show_again_cb.setStyleSheet("font-size: 13px;")
        main_layout.addWidget(self.dont_show_again_cb)

        # Buttons
        button_layout = SupportButtonsLayout()

        main_layout.addLayout(button_layout)
        self.resize(350, 300)

        # SIGNALS
        button_layout.github_button.clicked.connect(self.close)
        button_layout.paypal_button.clicked.connect(self.close)
        button_layout.patreon_button.clicked.connect(self.close)
        button_layout.dismiss_button.clicked.connect(self.close)


class SupportButtonsLayout(QtWidgets.QVBoxLayout):
    def __init__(self, parent=None):
        super(SupportButtonsLayout, self).__init__(parent)

        self.github_button = TikButton(background_color="#101010", text_color="white")
        self.github_button.setIcon(pick.icon("github"))
        self.github_button.setText("& GitHub Sponsors")

        self.paypal_button = TikButton(background_color="#002991", text_color="white")
        self.paypal_button.setIcon(pick.icon("paypal"))
        self.paypal_button.setText("& PayPal Donate")

        self.patreon_button = TikButton(background_color="#ff424d", text_color="white")
        self.patreon_button.setIcon(pick.icon("patreon"))
        self.patreon_button.setText("& Become a Patron")

        self.dismiss_button = TikButton(text="Nah, I Like Free Stuff")

        self.addWidget(self.github_button)
        self.addWidget(self.paypal_button)
        self.addWidget(self.patreon_button)
        self.addWidget(self.dismiss_button)

        # SIGNALS
        self.github_button.clicked.connect(
            lambda: self.open_link("https://github.com/sponsors/masqu3rad3"))
        self.paypal_button.clicked.connect(lambda: self.open_link(
            "https://www.paypal.com/donate/?hosted_button_id=75BHWFSZVPAHU"))
        self.patreon_button.clicked.connect(
            lambda: self.open_link("https://www.patreon.com/join/tikworks"))

    def open_link(self, url):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))


class SupportDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(SupportDialog, self).__init__(parent)
        self.setWindowTitle("Support Tik Manager")
        self.setModal(True)
        self.setStyleSheet("background-color: #222; color: #EEE; border-radius: 10px;")

        # Layouts
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Header
        title_label = QtWidgets.QLabel("Keep Tik Manager Running!")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #FE7E00;")
        main_layout.addWidget(title_label)

        # Message
        message_label = QtWidgets.QLabel(
            "<p>We love making Tik Manager free and open-source, and we want to keep it that way! "
            "If Tik Manager has made your life easier, consider supporting its development.</p>"
            "<p>No obligations—just good karma and maybe fewer unexpected crashes. 😉</p>"
        )
        message_label.setWordWrap(True)
        message_label.setAlignment(QtCore.Qt.AlignCenter)
        message_label.setStyleSheet("font-size: 14px;")
        main_layout.addWidget(message_label)

        # Buttons
        button_layout = SupportButtonsLayout()
        main_layout.addLayout(button_layout)

        # SIGNALS
        button_layout.dismiss_button.setText("Maybe Later")
        button_layout.github_button.clicked.connect(self.close)
        button_layout.paypal_button.clicked.connect(self.close)
        button_layout.patreon_button.clicked.connect(self.close)
        button_layout.dismiss_button.clicked.connect(self.close)

        self.resize(350, 250)

# Example usage:
if __name__ == "__main__":
    import sys

    # app = QtWidgets.QApplication(sys.argv)
    # splash = SupportSplashScreen()
    # splash.exec_()

    app = QtWidgets.QApplication(sys.argv)
    support_dialog = SupportDialog()
    support_dialog.exec_()