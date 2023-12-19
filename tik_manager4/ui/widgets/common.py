"""Common usage basic widgets."""
import math

from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
from tik_manager4.ui import pick

FONT = "Arial"

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
    def __init__(self, *args, font_size=10, **kwargs):
        super(TikButton, self).__init__(*args, **kwargs)
        # make sure the button has a font defined for different OS scales
        self.set_font_size(font_size)
        self.setStyleSheet(BUTTON_STYLE)

    def set_font_size(self, font_size):
        self.setFont(QtGui.QFont(FONT, font_size))

class TikIconButton(QtWidgets.QPushButton):
    """Button specific for fixed sized icons."""
    style_sheet = """QPushButton[circle=true]
    {{
        color: #b1b1b1;
        background-color: #404040;
        border-radius: {0};
        border-style: solid;
        border-color: green;
        border-width: 1px;
    }}
    
    QPushButton:disabled[circle=true] {{
        color: #101010;
        background-color: #101010;
        border-radius: {0};
        border-style: solid;
        border-color: black;
        border-width: 1px;
    }}
    
    """
    def __init__(self, icon_name=None, circle=True, size=22, *args, **kwargs):
        super(TikIconButton, self).__init__(*args, **kwargs)
        self.setStyleSheet(BUTTON_STYLE)
        self.circle = circle
        self.set_size(size)

        if icon_name:
            self.set_icon(icon_name)

    def set_icon(self, icon_name):
        self.setIcon(pick.icon(icon_name))

    def set_size(self, size):
        self.setFixedSize(size, size)
        _radius = int(size * 0.5)
        if self.circle:
            self.setProperty("circle", True)
            self.setStyleSheet(self.styleSheet() + self.style_sheet.format(_radius))
            circle_icon_size = int(self.square_to_circle_multiplier(size) * size)
            self.setIconSize(QtCore.QSize(circle_icon_size, circle_icon_size))
        else:
            self.setProperty("circle", False)
            self.setFixedSize(size, size)
            self.setIconSize(QtCore.QSize(size, size))
        self.style().unpolish(self)
        self.style().polish(self)

    @staticmethod
    def square_to_circle_multiplier(side_length):
        diagonal = math.sqrt(2) * side_length
        radius = diagonal * 0.5
        multiplier = radius / side_length
        return multiplier


class TikButtonBox(QtWidgets.QDialogButtonBox):
    """Unified button box class for the whole app."""

    def __init__(self, *args, font_size=10, **kwargs):
        super(TikButtonBox, self).__init__(*args, **kwargs)
        self.font_size = font_size
        for button in self.buttons():
            self.modifyButton(button)

    def set_font_size(self, font_size):
        self.font_size = font_size
        for button in self.buttons():
            self.modifyButton(button)

    def event(self, event):
        if event.type() == QtCore.QEvent.ChildAdded:
            child = event.child()
            self.modifyButton(child)
        return super(TikButtonBox, self).event(event)

    def modifyButton(self, button):
        button.setFont(QtGui.QFont(FONT, self.font_size))
        button.setMinimumWidth(100)
        button.setStyleSheet(BUTTON_STYLE)


class TikMessageBox(QtWidgets.QMessageBox):
    def __init__(self, *args, font_size=10, **kwargs):
        super(TikMessageBox, self).__init__(*args, **kwargs)
        self.set_font_size(font_size)

    def set_font_size(self, font_size):
        self.setFont(QtGui.QFont(FONT, font_size))

class TikLabel(QtWidgets.QLabel):
    """Unified label class for the whole app."""

    def __init__(self, *args, font_size=10, color=(255, 255, 255), **kwargs):
        super(TikLabel, self).__init__(*args, **kwargs)
        self.set_font_size(font_size)
        self.set_color(color)

    def set_font_size(self, font_size):
        self.setFont(QtGui.QFont(FONT, font_size))

    def set_color(self, color):
        if isinstance(color, (tuple, list)):
            color = "rgb({},{},{})".format(color[0], color[1], color[2])
        self.setStyleSheet("color: {};".format(color))

class TikLabelButton(TikButton):
    """Customize the button to be used next to the header."""
    style_sheet = """
    QPushButton
    {{
        color: {0};
        background-color: #404040;
        border-width: 1px;
        border-color: {0};
        border-style: solid;
        padding: 5px;
        font-size: 12x;
        border-radius: 0px;
    }}"""
    def __init__(self, *args, color=(255, 255, 255), **kwargs):
        super(TikLabelButton, self).__init__(*args, **kwargs)
        self.normal_text = kwargs.get("text", ">")
        self.clicked_text = "˅"
        self.setText(self.normal_text)
        # make the button checkable
        self.setCheckable(True)
        self.setProperty("label", True)
        self.set_color(color)
        self.toggled.connect(self.set_state_text)

    # override the checked state
    def set_state_text(self, checked):
        if checked:
            self.setText(self.clicked_text)
        else:
            self.setText(self.normal_text)

    def set_color(self, color):
        if isinstance(color, (tuple, list)):
            color = "rgb({},{},{})".format(color[0], color[1], color[2])
        self.setStyleSheet(self.styleSheet() + self.style_sheet.format(color))
        self.style().unpolish(self)
        self.style().polish(self)


class HeaderLabel(TikLabel):
    """Label with bold font and indent."""

    def __init__(self, *args, **kwargs):
        super(HeaderLabel, self).__init__(*args, **kwargs)
        self.setProperty("header", True)
        self.setIndent(10)
        self.setMinimumHeight(30)
        self.setFrameShape(QtWidgets.QFrame.Box)
        # center text
        self.setAlignment(QtCore.Qt.AlignCenter)
    def set_font_size(self, font_size):
        self.setFont(QtGui.QFont(FONT, font_size, QtGui.QFont.Bold))


    

# class HeaderLabel(QtWidgets.QLabel):
#     """Label with bold font and indent."""
#
#     def __init__(self, *args, font_size=10, color=(255, 255, 255), **kwargs):
#         super(HeaderLabel, self).__init__(*args, **kwargs)
#         self.setProperty("header", True)
#         self.setIndent(10)
#         self.setMinimumHeight(30)
#         self.set_font_size(font_size)
#         self.setFrameShape(QtWidgets.QFrame.Box)
#         self.set_color(color)
#         # center text
#         self.setAlignment(QtCore.Qt.AlignCenter)
#
#     def set_font_size(self, font_size):
#         self.setFont(QtGui.QFont(FONT, font_size, QtGui.QFont.Bold))
#
#     def set_color(self, color):
#         if isinstance(color, (tuple, list)):
#             color = "rgb({},{},{})".format(color[0], color[1], color[2])
#         self.setStyleSheet("color: {};".format(color))

class ResolvedText(TikLabel):
    """Label for resolved paths, names etc."""

    def __init__(self, *args, **kwargs):
        super(ResolvedText, self).__init__(*args, **kwargs)
        # make is selectable
        self.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        
    def set_font_size(self, font_size):
        self.setFont(QtGui.QFont(FONT, font_size, QtGui.QFont.Bold))

# class ResolvedText(QtWidgets.QLabel):
#     """Label for resolved paths, names etc."""
#
#     def __init__(self, *args, font_size=10, **kwargs):
#         super(ResolvedText, self).__init__(*args, **kwargs)
#         self.set_font_size(font_size)
#         # make is selectable
#         self.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
#     def set_font_size(self, font_size):
#         self.setFont(QtGui.QFont(FONT, font_size, QtGui.QFont.Bold))
#
#     def set_color(self, color):
#         if isinstance(color, (tuple, list)):
#             color = "rgb({},{},{})".format(color[0], color[1], color[2])
#         self.setStyleSheet("color: {};".format(color))
