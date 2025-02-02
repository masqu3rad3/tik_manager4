"""Popup dialogs."""

from tik_manager4.ui.Qt import QtWidgets, QtCore

class WaitDialog(QtWidgets.QDialog):
    def __init__(self, message="Please wait...", frameless=True, message_size=20, parent=None):
        super(WaitDialog, self).__init__(parent)

        # Set up the dialog
        if frameless:
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)

        self.setModal(True)  # Make it a modal dialog

        # Create a frame to hold the label
        self.frame = QtWidgets.QWidget()
        self.frame.setStyleSheet(
            "background-color: rgb(20, 20, 20); color: rgb(254, 126, 0); border-radius: 20px;"
        )

        # Create a label to show the message
        self.label = QtWidgets.QLabel(message)
        self.set_message_size(message_size)
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        # Set up the frame layout
        frame_layout = QtWidgets.QVBoxLayout()
        frame_layout.setContentsMargins(22, 22, 22, 22)
        frame_layout.addWidget(self.label)
        self.frame.setLayout(frame_layout)

        # Set up the dialog layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.frame)
        self.setLayout(layout)

        # make the dialog transparent
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # center the dialog

        # Store the initial position
        self.initial_position = self.pos()

    def set_message_size(self, size):
        font = self.font()
        font.setFamily("Roboto")
        font.setPointSize(size)
        self.label.setFont(font)

    def set_message(self, message):
        self.label.setText(message)
        self.label.adjustSize()  # Adjust the size of the label to fit the new message
        self.frame.adjustSize()  # Adjust the size of the frame to fit the new message
        self.adjustSize()  # Adjust the size of the dialog to fit the new message
        self.close()  # Close the dialog to update the message
        self.show()

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
    dialog = WaitDialog("Please wait...", message_size=30)
    dialog.display()
    sleep(1)
    dialog.set_message("Please wait...AAA")
    sleep(1)
    dialog.set_message("Please wait...AAAAAA")
    sleep(1)
    dialog.set_message("Please wait...AAAAAAAAA")
    sleep(1)

    # app.exec_()
    # sleep(1)
    # dialog.set_message("Still doing its thing. Wait a bit more")
    # sleep(1)
    # dialog.set_message("Almost there...Wait a bit more. Apologies for inconvenience.")
    # sleep(1)
    # dialog.set_message("Almost done")
    # sleep(1)
    dialog.kill()
    sys.exit()