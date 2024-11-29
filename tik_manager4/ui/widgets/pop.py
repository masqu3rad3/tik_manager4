"""Popup dialogs."""

from tik_manager4.ui.Qt import QtWidgets, QtCore

class WaitDialog(QtWidgets.QDialog):
    def __init__(self, message="Please wait...", frameless=True, message_size=20, parent=None):
        super(WaitDialog, self).__init__(parent)

        # Set up the dialog
        if frameless:
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)

        self.setModal(True)  # Make it a modal dialog

        # Create a label to show the message
        self.label = QtWidgets.QLabel(message)
        self.set_message_size(message_size)
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        # Set up the layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def set_message_size(self, size):
        font = self.font()
        font.setPointSize(size)
        self.label.setFont(font)

    def set_message(self, message):
        self.label.setText(message)
        QtWidgets.QApplication.processEvents()  # Ensure the UI updates immediately

    # Function to show the dialog
    def display(self, message=None):
        if message:
            self.set_message(message)
        self.show()
        QtWidgets.QApplication.processEvents()  # Ensure the UI updates immediately

    # Function to close the dialog
    def kill(self):
        self.close()


# test the wait dialog
if __name__ == "__main__":
    import sys
    from time import sleep
    app = QtWidgets.QApplication(sys.argv)
    dialog = WaitDialog("Please wait...")
    dialog.display()
    # app.exec_()
    sleep(2)
    dialog.kill()
    sys.exit()