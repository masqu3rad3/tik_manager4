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

    # Function to show the dialog
    def show_dialog(self):
        self.show()
        QtWidgets.QApplication.processEvents()  # Ensure the UI updates immediately

    # Function to close the dialog
    def close_dialog(self):
        self.close()


# test the wait dialog
if __name__ == "__main__":
    import sys
    from time import sleep
    app = QtWidgets.QApplication(sys.argv)
    dialog = WaitDialog("Please wait...")
    dialog.show_dialog()
    # app.exec_()
    sleep(2)
    dialog.close_dialog()
    sys.exit()