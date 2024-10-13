from tik_manager4.ui.Qt import QtWidgets, QtCore
from tik_manager4.ui.widgets.common import (
    TikButton,
    StyleFrame,
    TikLabel,
    TikIconButton,
)


class CollapsibleLayout(QtWidgets.QVBoxLayout):
    """Header bar widget especially for expandable layouts."""

    expand_toggled = QtCore.Signal(bool)

    background_color = "#404040"
    text_color = "#b1b1b1"
    border_color = "#1e1e1e"

    style_sheet = """
QFrame
{
    background-color: #404040;
    border-width: 1px;
    border-color: #1e1e1e;
    border-style: solid;
    padding: 5px;
    border-radius: 14px;
}
QLabel
{
background-color: #404040;
border-width: 0px;
padding: 5px;
border-radius: 14px;
}
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
"""

    def __init__(self, text="", expanded=False, parent=None):
        super().__init__(parent)

        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)

        self.frame = StyleFrame()
        self.addWidget(self.frame)
        self.frame.setMaximumHeight(40)
        self.frame.setContentsMargins(0, 0, 0, 0)
        self.frame.setGeometry(QtCore.QRect(220, 160, 291, 81))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setStyleSheet(self.style_sheet)

        self.vertical_layout = QtWidgets.QVBoxLayout(self.frame)
        # reset margins
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.vertical_layout.setSpacing(0)
        self.horizontal_layout = QtWidgets.QHBoxLayout()
        # reset margins
        self.horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self.horizontal_layout.setSpacing(0)

        self.expand_button = TikIconButton(icon_name="arrow_right", size=22)
        self.horizontal_layout.addWidget(self.expand_button)

        self.label = TikLabel()
        self.label.setText(text)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.horizontal_layout.addWidget(self.label)

        self.vertical_layout.addLayout(self.horizontal_layout)

        self.contents_widget = QtWidgets.QWidget()
        self.contents_layout = QtWidgets.QVBoxLayout()
        self.addWidget(self.contents_widget)
        self.contents_widget.setLayout(self.contents_layout)
        self.contents_widget.setVisible(False)

        self._expanded = expanded
        if self._expanded:
            self.expand()
        else:
            self.collapse()

        # SIGNALS
        self.expand_button.clicked.connect(self.toggle)

    def toggle(self):
        """Toggle the layout."""
        if self._expanded:
            self.collapse()
        else:
            self.expand()

    def expand(self):
        """Expand the layout."""
        self.expand_button.set_icon("arrow_down")
        self.contents_widget.setVisible(True)
        self._expanded = True
        self.expand_toggled.emit(self._expanded)

    def collapse(self):
        """Collapse the layout."""
        self.expand_button.set_icon("arrow_right")
        self.contents_widget.setVisible(False)
        self._expanded = False
        self.expand_toggled.emit(self._expanded)

    def set_hidden(self, state=True):
        self.expand_button.setHidden(state)
        self.contents_widget.setHidden(state)

    def set_color(self, text_color=None, background_color=None, border_color=None):

        color, background_color, border_color = [
            "rgb({}, {}, {})".format(*var) if isinstance(var, (tuple, list)) else var
            for var in [text_color, background_color, border_color]
        ]

        text_color = text_color or self.text_color
        border_color = border_color or self.border_color
        background_color = background_color or self.background_color

        color_style = f"""
        QFrame
        {{
        background-color: {background_color};
        border-color: {border_color};
        }}
        QLabel
        {{
        color: {text_color};
        }}
        QPushButton
        {{
        color: {text_color};
        background-color: {background_color};
        border-color: {border_color};
        }}"""

        self.frame._append_style(color_style)
        self.expand_button._append_style(color_style)
        self.label._append_style(color_style)


#
# class CollapsibleLayout(QtWidgets.QVBoxLayout):
#     """A Layout which can expand and collapse its children."""
#
#     def __init__(self, title="", expanded=False, parent=None):
#         super(CollapsibleLayout, self).__init__()
#         if parent:
#             self.setLayout(parent)
#
#         # create a button to expand and collapse the layout
#         self._title = title
#         self._button = TikButton()
#         self.addWidget(self._button)
#         self._button.setText("+ {}".format(self._title))
#         # increase the button height to 30px
#         self._button.setMinimumHeight(25)
#         # set the button to flat with borders
#         # make button look like a label with borders
#         self._button.setFlat(True)
#         self._button.setStyleSheet(
#             "QPushButton {border: 1px solid #d9d9d9; border-radius: 5px;}"
#         )
#
#         self.contents_widget = QtWidgets.QWidget()
#         self.contents_layout = QtWidgets.QVBoxLayout()
#         self.addWidget(self.contents_widget)
#         self.contents_widget.setLayout(self.contents_layout)
#         self._expanded = expanded
#         if self._expanded:
#             self.expand()
#         else:
#             self.collapse()
#         self._button.clicked.connect(self.toggle)
#
#     def set_hidden(self, state=True):
#         self._button.setHidden(state)
#         self.contents_widget.setHidden(state)
#
#     def toggle(self):
#         """Toggle the layout."""
#         if self._expanded:
#             self.collapse()
#         else:
#             self.expand()
#
#     def expand(self):
#         """Expand the layout."""
#         self._button.setText("- {}".format(self._title))
#         self.contents_widget.setVisible(True)
#         self._expanded = True
#
#     def collapse(self):
#         """Collapse the layout."""
#         self._button.setText("+ {}".format(self._title))
#         self.contents_widget.setVisible(False)
#         self._expanded = False
#
#     def clear(self):
#         # hide and delete contents widget
#         self.contents_widget.setVisible(False)
#         self.contents_widget.deleteLater()
#         # create new contents widget
#         self.contents_widget = QtWidgets.QWidget()
#         self.addWidget(self.contents_widget)
