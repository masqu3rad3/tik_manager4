"""Common usage basic widgets."""

from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
from tik_manager4.ui import pick

FONT = QtGui.QFont("Arial", 10)

BUTTON_STYLE = """
QPushButton
{
    color: #b1b1b1;
    background-color: #404040;
    border-width: 1px;
    border-color: #1e1e1e;
    border-style: solid;
    padding: 5px;
    font-size: 12x;
    border-radius: 4px;
}

QPushButton:hover
{
    background-color: #505050;
    border: 1px solid #ff8d1c;
}

QPushButton:hover[circle=true]
{
    background-color: #505050;
    border: 2px solid #ff8d1c;
}

QPushButton:disabled {
    color: #505050;
    background-color: #303030;
    border: 1px solid #404040;
    border-width: 1px;
    border-color: #1e1e1e;
    border-style: solid;
    padding: 5px;
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

class TikIconButton(QtWidgets.QPushButton):
    """Button specific for uniform sized icons."""
    style_sheet = """QPushButton[circle=true]
    {{
        color: #b1b1b1;
        background-color: #404040;
        padding: 7px;
        font-size: 12x;
        border-radius: {0};
        border : 2px solid black;
    }}"""
    def __init__(self, icon_name=None, circle=True, *args, **kwargs):
        super(TikIconButton, self).__init__(*args, **kwargs)
        self.setFont(FONT)
        self.setStyleSheet(BUTTON_STYLE)
        self.circle = circle
        self.setFixedSize(22, 22)
        self.setIconSize(QtCore.QSize(12, 12))
        if icon_name:
            self.set_icon(icon_name)
        # self.setIconSize(QtCore.QSize(20, 20))
        # self.setStyleSheet(BUTTON_STYLE)

    # def set_size(self, size):
    #     self.resize(size, size)
    #     self.setIconSize(QtCore.QSize(size-10, size-10))
    #     self.setStyleSheet(BUTTON_STYLE)
    def set_icon(self, icon_name):
        self.setIcon(pick.icon(icon_name))
        # get the current height of the button
        # size = self.width() * 0.6
        # self.setIconSize(QtCore.QSize(size, size))

    def resizeEvent(self, _resize_event):
        height = self.width()
        self.setMinimumHeight(int(height))
        self.setMaximumHeight(int(height))
        _radius = int(height/2)
        if self.circle:
            self.setProperty("circle", True)
            self.setStyleSheet(self.styleSheet() + self.style_sheet.format(_radius))
        else:
            self.setProperty("circle", False)
            # self.setStyleSheet(self.styleSheet()+(f"border-radius : 0px; border : 2px solid black"))
        self.style().unpolish(self)
        self.style().polish(self)
        # size = self.width() * 0.6

        # align the icon to center


class TikButtonBox(QtWidgets.QDialogButtonBox):
    """Unified button box class for the whole app."""

    def __init__(self, *args, **kwargs):
        super(TikButtonBox, self).__init__(*args, **kwargs)
        for button in self.buttons():
            self.modifyButton(button)

    def event(self, event):
        if event.type() == QtCore.QEvent.ChildAdded:
            child = event.child()
            self.modifyButton(child)
        return super(TikButtonBox, self).event(event)

    def modifyButton(self, button):
        button.setFont(FONT)
        button.setMinimumWidth(100)
        button.setStyleSheet(BUTTON_STYLE)


class TikMessageBox(QtWidgets.QMessageBox):
    def __init__(self, *args, **kwargs):
        super(TikMessageBox, self).__init__(*args, **kwargs)
        self.setFont(FONT)


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

    def set_color(self, color):
        self.setStyleSheet("color: {};".format(color))
