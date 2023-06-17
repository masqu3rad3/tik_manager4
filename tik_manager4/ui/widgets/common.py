"""Common usage basic widgets."""

from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui

FONT = QtGui.QFont("Arial", 10)

class TikButton(QtWidgets.QPushButton):
    """Unified button class for the whole app."""

    def __init__(self, *args, **kwargs):
        super(TikButton, self).__init__(*args, **kwargs)
        # make sure the button has a font defined for different OS scales
        self.setFont(FONT)
        # set color
        # self.setStyleSheet("background-color: rgb(50, 50, 50); color: rgb(0, 200, 200);")


class TikButtonBox(QtWidgets.QDialogButtonBox):
    """Unified button box class for the whole app."""

    def __init__(self, *args, **kwargs):
        super(TikButtonBox, self).__init__(*args, **kwargs)
        self.setFont(FONT)
        # self.setStyleSheet("background-color: rgb(50, 50, 50); color: rgb(0, 200, 200);")
        # for button in self.buttons():
        #     self.modifyButton(button)

    # def event(self, event):
    #     if event.type() == QtCore.QEvent.ChildAdded:
    #         child = event.child()
    #         self.modifyButton(child)
    #     return super(TikButtonBox, self).event(event)
    #
    # def modifyButton(self, button):
    #     button.setFont(QtGui.QFont("Arial", 10))
    #     button.setStyleSheet("background-color: rgb(50, 50, 50); color: rgb(0, 200, 200);")


class TikMessageBox(QtWidgets.QMessageBox):
    def __init__(self, *args, **kwargs):
        super(TikMessageBox, self).__init__(*args, **kwargs)
        self.setFont(FONT)
        # self.setStyleSheet("background-color: rgb(50, 50, 50); color: rgb(0, 200, 200);")