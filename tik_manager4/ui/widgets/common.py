"""Common usage basic widgets."""

from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui

FONT = QtGui.QFont("Arial", 10)

BUTTON_STYLE = """
QPushButton
{
    color: #b1b1b1;
    background-color: #404040;
    border-width: 1px;
    border-color: #1e1e1e;
    border-style: solid;
    padding: 7px;
    font-size: 12x;
}

QPushButton:hover
{
    background-color: #505050;
    border: 1px solid #ff8d1c;
}

QPushButton:disabled {
    color: #505050;
    background-color: #303030;
    border: 1px solid #404040;
    border-width: 1px;
    border-color: #1e1e1e;
    border-style: solid;
    padding: 7px;
    font-size: 12x;
}

QPushButton:pressed {
  background-color: #ff8d1c;
  border: 1px solid #ff8d1c;
}
"""

class TikButton(QtWidgets.QPushButton):
    """Unified button class for the whole app."""

    def __init__(self, *args, **kwargs):
        super(TikButton, self).__init__(*args, **kwargs)
        # make sure the button has a font defined for different OS scales
        self.setFont(FONT)
        self.setStyleSheet(BUTTON_STYLE)
        # self.setMaximumHeight(30)

        # set color
        # self.setStyleSheet("background-color: rgb(50, 50, 50); color: rgb(0, 200, 200);")


class TikButtonBox(QtWidgets.QDialogButtonBox):
    """Unified button box class for the whole app."""

    def __init__(self, *args, **kwargs):
        super(TikButtonBox, self).__init__(*args, **kwargs)
        # self.setFont(FONT)
        # make the buttons bigger but use font scale not pixel size
        # self.setStyleSheet("color: #b1b1b1; background-color: #404040; border-width: 1px; border-color: #1e1e1e; border-style: solid; padding: 10px; font-size: 12px;")
        # self.setStyleSheet(BUTTON_STYLE)

        # self.setStyleSheet("background-color: rgb(50, 50, 50); color: rgb(0, 200, 200);")
        for button in self.buttons():
            self.modifyButton(button)

    def event(self, event):
        if event.type() == QtCore.QEvent.ChildAdded:
            child = event.child()
            self.modifyButton(child)
        return super(TikButtonBox, self).event(event)

    def modifyButton(self, button):
        # button.setFont(QtGui.QFont("Arial", 10))
        button.setFont(FONT)
        button.setMinimumWidth(100)
        # button.setStyleSheet("background-color: rgb(50, 50, 50); color: rgb(0, 200, 200);")
        button.setStyleSheet(BUTTON_STYLE)


class TikMessageBox(QtWidgets.QMessageBox):
    def __init__(self, *args, **kwargs):
        super(TikMessageBox, self).__init__(*args, **kwargs)
        self.setFont(FONT)
        # make the buttons bigger
        # self.setStyleSheet("background-color: rgb(50, 50, 50); color: rgb(0, 200, 200);")

class HeaderLabel(QtWidgets.QLabel):
    """Label with bold font and indent."""

    def __init__(self, *args, **kwargs):
        super(HeaderLabel, self).__init__(*args, **kwargs)
        self.setProperty("header", True)
        self.setIndent(10)
        self.setMinimumHeight(30)
        self.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))
        self.setFrameShape(QtWidgets.QFrame.Box)

        # center text
        self.setAlignment(QtCore.Qt.AlignCenter)

    def set_color(self, color):
        self.setStyleSheet("color: {};".format(color))

class ResolvedText(QtWidgets.QLabel):
    """Label for resolved paths, names etc."""
    def __init__(self, *args, **kwargs):
        super(ResolvedText, self).__init__(*args, **kwargs)
        self.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))

        # make is selectable
        self.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        # self.setFrameShape(QtWidgets.QFrame.Box)


    def set_color(self, color):
        self.setStyleSheet("color: {};".format(color))
        # box and sunken


