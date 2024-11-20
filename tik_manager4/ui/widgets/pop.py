"""Popup dialogs."""

from tik_manager4.ui.Qt import QtWidgets, QtCore

class WaitDialog(QtWidgets.QDialog):
    def __init__(self, message="Please wait...", parent=None):
        super(WaitDialog, self).__init__(parent)

        # Set up the dialog
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.setModal(True)  # Make it a modal dialog
        # self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        # self.setWindowOpacity(0.9)  # Set transparency

        # create a bold fond with 20pt size
        font = self.font()
        font.setPointSize(20)
        # font.setBold(True)

        # Create a label to show the message
        self.label = QtWidgets.QLabel(message)
        # self.label.setStyleSheet("font: 20pt; color: black; background-color: white;")
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        # Set up the layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

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