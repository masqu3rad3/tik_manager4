"""Common usage basic widgets."""
import math
import collections.abc
import re

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


class StyleEditor:
    """Convenience class to edit the style of a widget."""

    background_color = "#404040"
    text_color = "#b1b1b1"
    border_color = "#1e1e1e"

    def _update(self, old, new):
        for k, v in new.items():
            if isinstance(v, collections.abc.Mapping):
                old[k] = self._update(old.get(k, {}), v)
            else:
                old[k] = v
        return old

    def _append_style(self, new_style):
        """Append style to the current style sheet."""
        # if the style argument is not dictionary, convert it to dictionary
        if not isinstance(new_style, dict):
            new_style = self.stylesheet_to_dictionary(new_style)
        current_style_dict = self.stylesheet_to_dictionary(self.styleSheet())

        current_style_dict = self._update(current_style_dict, new_style)

        self.setStyleSheet(self.dictionary_to_stylesheet(current_style_dict))
        self.style().unpolish(self)
        self.style().polish(self)

    @staticmethod
    def stylesheet_to_dictionary(stylesheet):
        # Regular expression patterns for extracting style information
        selector_pattern = re.compile(
            r"(\w+(?:\s*:\s*\w+)?(?:\[[^\]]+\])?)\s*{([^}]*)}"
        )
        property_pattern = re.compile(r"\s*([^:]+)\s*:\s*([^;]+);")

        styles = {}
        for match in selector_pattern.finditer(stylesheet):
            selector = match.group(1)
            properties = {}
            for prop_match in property_pattern.finditer(match.group(2)):
                properties[prop_match.group(1)] = prop_match.group(2)
            styles[selector] = properties

        return styles

    @staticmethod
    def dictionary_to_stylesheet(styles):
        stylesheet = ""
        for selector, properties in styles.items():
            stylesheet += f"{selector} {{\n"
            for prop, value in properties.items():
                stylesheet += f"    {prop}: {value};\n"
            stylesheet += "}\n"

        return stylesheet


class ClickableFrame(QtWidgets.QFrame):
    """Clickable frame widget."""

    clicked = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def mousePressEvent(self, event):
        self.clicked.emit()
        return super().mousePressEvent(event)

class StyleFrame(ClickableFrame, StyleEditor):
    """Frame with custom styler."""

    pass


class TikButton(QtWidgets.QPushButton, StyleEditor):
    """Unified button class for the whole app."""

    def __init__(self,
        text="",
        font_size=10,
        text_color="#b1b1b1",
        border_color="#1e1e1e",
        background_color="#404040",
        *args,
        **kwargs,
    ):
        super().__init__()
        # make sure the button has a font defined for different OS scales
        self.setText(text)
        self.text_color = text_color
        self.border_color = border_color
        self.background_color = background_color
        self.set_font_size(font_size)
        self.setStyleSheet(BUTTON_STYLE)
        self.set_color(text_color, background_color, border_color)

    def set_font_size(self, font_size):
        self.setFont(QtGui.QFont(FONT, font_size))

    def set_color(self, text_color=None, background_color=None, border_color=None):

        color, background_color, border_color = [
            "rgb({}, {}, {})".format(*var) if isinstance(var, (tuple, list)) else var
            for var in [text_color, background_color, border_color]
        ]

        text_color = text_color or self.text_color
        background_color = background_color or self.background_color
        border_color = border_color or self.border_color

        color_style = f"""
        QPushButton
        {{
        color: {text_color};
        background-color: {background_color};
        border-color: {border_color};
        }}"""

        self._append_style(color_style)


class TikIconButton(TikButton):
    """Button specific for fixed sized icons."""

    def __init__(self, icon_name=None, circle=True, size=22, icon_size=None, **kwargs):
        super().__init__(**kwargs)
        self.radius = int(size * 0.5)
        self.circle = circle
        self.set_size(size)
        self._icon_size = icon_size

        if icon_name:
            self.set_icon(icon_name)

    def set_icon(self, icon_name):
        self.setIcon(pick.icon(icon_name))
        #double the size of the icon
        if self._icon_size:
            self.setIconSize(QtCore.QSize(self._icon_size, self._icon_size))

    def set_size(self, size):
        self.setFixedSize(size, size)
        self.radius = int(size * 0.5)
        if self.circle:
            borders_style = {
                "QPushButton": {"border-radius": f"{self.radius}"},
                "QPushButton:disabled": {"border-radius": f"{self.radius}"},
            }
        else:
            borders_style = {
                "QPushButton": {"border-radius": "4px"},
                "QPushButton:disabled": {"border-radius": "4px"},
            }
        self._append_style(borders_style)

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


class TikLabel(QtWidgets.QLabel, StyleEditor):
    """Unified label class for the whole app."""

    def __init__(self, *args, text="", font_size=10, color=(255, 255, 255), **kwargs):
        super(TikLabel, self).__init__(*args, **kwargs)
        self.color = color
        self.set_font_size(font_size)
        self.set_color(text_color=self.color, border_color=self.color)

    def set_font_size(self, font_size, bold=False):
        if bold:
            self.setFont(QtGui.QFont(FONT, font_size, QtGui.QFont.Bold))
        else:
            self.setFont(QtGui.QFont(FONT, font_size))

    def set_color(self, text_color=None, background_color=None, border_color=None):

        color, background_color, border_color = [
            "rgb({}, {}, {})".format(*var) if isinstance(var, (tuple, list)) else var
            for var in [text_color, background_color, border_color]
        ]

        text_color = text_color or self.text_color
        border_color = border_color or self.border_color

        color_style = f"""
        QLabel
        {{
        color: {text_color};
        border-color: {border_color};
        }}"""

        self._append_style(color_style)

    def set_text(self, text):
        self.setText(text)


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
        self.set_color(text_color=color, border_color=color)
        self.toggled.connect(self.set_state_text)

    # override the checked state
    def set_state_text(self, checked):
        if checked:
            self.setText(self.clicked_text)
        else:
            self.setText(self.normal_text)


class HeaderLabel(TikLabel):
    """Label with bold font and indent."""

    style_sheet = """
QLabel
{
    background-color: #404040;
    border-width: 1px;
    border-color: #1e1e1e;
    border-style: solid;
    padding: 5px;
    font-size: 12x;
    border-radius: 14px;
}
"""

    def __init__(self, *args, **kwargs):
        super(HeaderLabel, self).__init__(*args, **kwargs)
        self.setProperty("header", True)
        self.setIndent(10)
        self.setFixedHeight(30)
        self.setFrameShape(QtWidgets.QFrame.Box)
        # center text
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.color = (255, 0, 255)
        self.setStyleSheet(self.style_sheet)
        self.style().unpolish(self)
        self.style().polish(self)

    def set_font_size(self, font_size, bold=True):
        super(HeaderLabel, self).set_font_size(font_size, bold)


class ResolvedText(TikLabel):
    """Label for resolved paths, names etc."""

    def __init__(self, *args, **kwargs):
        super(ResolvedText, self).__init__(*args, **kwargs)
        # make is selectable
        self.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        # make is wrap
        self.setWordWrap(True)

    def set_font_size(self, font_size, bold=True):
        super(ResolvedText, self).set_font_size(font_size, bold)


class VerticalSeparator(QtWidgets.QLabel):
    """Simple horizontal separator."""

    def __init__(self, color=(100, 100, 100), height=25, width=20):
        super(VerticalSeparator, self).__init__()
        self._pixmap = QtGui.QPixmap(2, 100)
        self.set_color(color)
        self.setPixmap(self._pixmap)
        self.setFixedHeight(height)
        self.setFixedWidth(width)
        self.setAlignment(QtCore.Qt.AlignCenter)

    def set_color(self, color):
        self._pixmap.fill(QtGui.QColor(*color))


class HorizontalSeparator(QtWidgets.QLabel):
    """Simple vertical separator."""

    def __init__(self, color=(100, 100, 100), height=1, width=None):
        super(HorizontalSeparator, self).__init__()
        self.set_color(color)
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.setFixedHeight(height)
        if width:
            self.setFixedWidth(width)

    def set_color(self, color):
        if isinstance(color, (tuple, list)):
            color = f"rgb({color[0]}, {color[1]}, {color[2]});"
        self.setStyleSheet(f"background-color: {color};")
