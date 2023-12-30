import re
from tik_manager4.ui.Qt import QtCore
from tik_manager4.ui.widgets.value_widgets import String


class ValidatedString(String):
    """A custom QLineEdit widget purposed for browsing subprojects"""

    validation_changed = QtCore.Signal(bool)

    def __init__(
        self,
        *args,
        connected_widgets=None,
        allow_spaces=False,
        allow_directory=False,
        allow_empty=False,
        allow_special_characters=False,
        **kwargs
    ):
        """Custom QLineEdit widget to validate entered values"""
        super(ValidatedString, self).__init__(*args, **kwargs)
        self.allow_spaces = allow_spaces
        self.allow_directory = allow_directory
        self.allow_empty = allow_empty
        self.allow_special_characters = allow_special_characters
        self.connected_widgets = connected_widgets or []
        self.default_stylesheet = self.styleSheet()
        if connected_widgets:
            self.set_connected_widgets(
                connected_widgets
            )  # validate and toggle connected widgets
        else:
            self._validate()  # just validate the value

    def set_connected_widgets(self, widgets):
        if not isinstance(widgets, (list, tuple)):
            self.connected_widgets = [widgets]
        else:
            self.connected_widgets = widgets
        self._validate()

    def add_connected_widget(self, widget):
        self.connected_widgets.append(widget)
        self._validate()

    def get_connected_widgets(self):
        return self._connected_widgets

    def keyPressEvent(self, *args, **kwargs):
        # supress the signals
        super(ValidatedString, self).keyPressEvent(*args, **kwargs)
        self._validate()

    def _validate(self):
        current_text = self.text()
        if not self.allow_empty and not current_text:
            self._fail()
            self.validation_changed.emit(False)
        elif not self.string_value(
            current_text,
            allow_spaces=self.allow_spaces,
            directory=self.allow_directory,
            allow_special=self.allow_special_characters,
        ):
            self._fail()
            self.validation_changed.emit(False)
        else:
            self.setStyleSheet(self.default_stylesheet)
            if self.connected_widgets:
                for wid in self.connected_widgets:
                    wid.setEnabled(True)
            self.validation_changed.emit(True)

    def _fail(self):
        """Disable the connected widgets and set the background color to red"""
        self.setStyleSheet("background-color: rgb(40,40,40); color: red")
        if self.connected_widgets:
            for wid in self.connected_widgets:
                wid.setEnabled(False)

    def _pass(self):
        """Enable the connected widgets and set the background color to the default"""
        self.setStyleSheet(self.default_stylesheet)
        if self.connected_widgets:
            for wid in self.connected_widgets:
                wid.setEnabled(True)

    @staticmethod
    def string_value(
        input_text, allow_spaces=False, directory=False, allow_special=False
    ):
        """Check the text for illegal characters."""
        _start = "^[:A-Za-z0-9"
        _end = "]*$"
        allow_spaces = " " if allow_spaces else ""
        directory = "/\\\\:" if directory or allow_special else ""
        specials = ".A_!\"#$%&'()*+,./:;<=>?@[\\]^_`{|}~-" if allow_special else ".A_-"
        pattern = "{0}{1}{2}{3}{4}".format(
            _start, allow_spaces, directory, specials, _end
        )

        if re.match(pattern, input_text):
            return True
        else:
            return False
