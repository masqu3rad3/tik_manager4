from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui


class SupportSplashScreen(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(SupportSplashScreen, self).__init__(parent)
        self.setWindowTitle("Support Tik Manager!")
        self.setModal(True)
        self.setStyleSheet("background-color: #222; color: #EEE; border-radius: 10px;")

        # Layouts
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Header
        title_label = QtWidgets.QLabel("🚀 Sorry for the Interruption")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: orange;")
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
        self.dont_show_again_checkbox = QtWidgets.QCheckBox("Don’t show this again")
        self.dont_show_again_checkbox.setChecked(True)
        self.dont_show_again_checkbox.setStyleSheet("font-size: 13px;")
        main_layout.addWidget(self.dont_show_again_checkbox)

        # Buttons
        button_layout = QtWidgets.QVBoxLayout()

        self.github_button = QtWidgets.QPushButton()
        self.github_button.setIcon(QtGui.QIcon("path/to/github_logo.png"))
        self.github_button.setText("GitHub Sponsors")
        self.github_button.setStyleSheet(
            "background-color: orange; color: black; font-weight: bold; padding: 5px; border-radius: 5px;"
        )
        self.github_button.clicked.connect(lambda: self.open_link("https://github.com/sponsors/masqu3rad3"))

        self.paypal_button = QtWidgets.QPushButton()
        self.paypal_button.setIcon(QtGui.QIcon("path/to/paypal_logo.png"))
        self.paypal_button.setText("PayPal Donate")
        self.paypal_button.setStyleSheet(
            "background-color: orange; color: black; font-weight: bold; padding: 5px; border-radius: 5px;"
        )
        self.paypal_button.clicked.connect(lambda: self.open_link("https://www.paypal.com/donate/?hosted_button_id=75BHWFSZVPAHU"))

        self.patreon_button = QtWidgets.QPushButton()
        self.patreon_button.setIcon(QtGui.QIcon("path/to/patreon_logo.png"))
        self.patreon_button.setText("Patreon")
        self.patreon_button.setStyleSheet(
            "background-color: orange; color: black; font-weight: bold; padding: 5px; border-radius: 5px;"
        )
        self.patreon_button.clicked.connect(lambda: self.open_link("https://www.patreon.com/join/tikworks"))

        self.dismiss_button = QtWidgets.QPushButton("Nah, I Like Free Stuff")
        self.dismiss_button.setStyleSheet(
            "background-color: #444; color: #EEE; padding: 5px; border-radius: 5px;"
        )
        self.dismiss_button.clicked.connect(self.close)

        button_layout.addWidget(self.github_button)
        button_layout.addWidget(self.paypal_button)
        button_layout.addWidget(self.patreon_button)
        button_layout.addWidget(self.dismiss_button)

        main_layout.addLayout(button_layout)

    def open_link(self, url):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))
        self.close()


# Example usage:
if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    splash = SupportSplashScreen()
    splash.exec_()