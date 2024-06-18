"""Settings Layout for auto-creating setting menus directly from Settings object.

Supported types:
    - boolean => QCheckBox
    - string => QLineEdit
    - spinnerInt => QSpinBox
    - spinnerFloat => QDoubleSpinBox
    - combo => QComboBox


"""
import re
from pathlib import Path
from tik_manager4.core.settings import Settings

from tik_manager4.ui.widgets import value_widgets
from tik_manager4.ui.widgets.category_list import CategoryList

import tik_manager4.ui.widgets.browser
import tik_manager4.ui.widgets.path_browser
from tik_manager4.ui.widgets.validated_string import ValidatedString
from tik_manager4.ui.Qt import QtWidgets, QtCore


def get_nice_name(input_str):
    """Convert camel case or snake case to nice name."""
    # Use regular expression to split the string at camel case boundaries
    words = re.findall(r"[A-Z][a-z]*|[a-z]+", input_str)
    # Capitalize the first letter of each word and join them with a space
    nice_name = " ".join(word.capitalize() for word in words)
    return nice_name
def guess_data_type(data, enums=None):
    """Guess the type of the data to be used as ui definition."""
    if enums:
        return "combo"
    if isinstance(data, bool):
        return "boolean"
    elif isinstance(data, str):
        if Path(data).exists() and data != "":
            return "pathBrowser"
        return "string"
    elif isinstance(data, int):
        return "integer"
    elif isinstance(data, float):
        return "float"
    elif isinstance(data, dict):
        return "multi"
    elif isinstance(data, (list, tuple)):
        if all(isinstance(item, int) for item in data) and len(data) == 2:
            return "vector2Int"
        # if ANY floats, it is a vector2Float
        elif any(isinstance(item, float) for item in data) and len(data) == 2:
            return "vector2Float"
        elif all(isinstance(item, int) for item in data) and len(data) == 3:
            return "vector3Int"
        # if ANY floats, it is a vector3Float
        elif any(isinstance(item, float) for item in data) and len(data) == 3:
            return "vector3Float"
        else:
            return "combo"
    else:
        return None
def convert_to_ui_definition(settings_data):
    """Converts the settings data to ui definition.

    Args:
        settings_data (Settings or dict): Settings object or dictionary data
        override_data (dict, optional): Override the settings data with this dictionary. Defaults to None.
    """
    if isinstance(settings_data, Settings):
        source_dict = settings_data.get_data()
    else:
        source_dict = settings_data

    ui_definition = {}
    for key, data in source_dict.items():
        # guess the type of the data
        data_type = guess_data_type(data)
        ui_definition[key] = {
            "display_name": get_nice_name(key),
            "tooltip": "",
            "type": data_type,
            "value": "",
            "disables": [],
        }
        if data_type == "multi":
            value = convert_to_ui_definition(data)
        elif data_type == "combo":
            value = data[0]
            ui_definition[key]["items"] = data
        else:
            value = data
        ui_definition[key]["value"] = value
    return ui_definition

class SettingsLayout(QtWidgets.QFormLayout):
    """Visualizes and edits Setting objects in a vertical layout"""
    modified = QtCore.Signal(bool)

    widget_dict = {
        "boolean": value_widgets.Boolean,
        "string": value_widgets.String,
        "combo": value_widgets.Combo,
        "integer": value_widgets.Integer,
        "float": value_widgets.Float,
        "spinnerInt": value_widgets.SpinnerInt,
        "spinnerFloat": value_widgets.SpinnerFloat,
        "list": value_widgets.List,
        "dropList": value_widgets.DropList,
        "categoryList": CategoryList,
        "validatedString": ValidatedString,
        "vector2Int": value_widgets.Vector2Int,
        "vector2Float": value_widgets.Vector2Float,
        "vector3Int": value_widgets.Vector3Int,
        "vector3Float": value_widgets.Vector3Float,
        "pathBrowser": tik_manager4.ui.widgets.path_browser.PathBrowser,
        "fileBrowser": tik_manager4.ui.widgets.path_browser.FileBrowser,
        "subprojectBrowser": tik_manager4.ui.widgets.browser.SubprojectBrowser,
    }

    def __init__(self, ui_definition, settings_data=None, *args, **kwargs):
        super(SettingsLayout, self).__init__()
        self.ui_definition = None
        self.settings_data = None
        self.widgets = None
        self.initialize(ui_definition, settings_data)

    def initialize(self, ui_definition, data):
        self.ui_definition = ui_definition
        self.settings_data = data or Settings()
        self.validate_settings_data()
        self.widgets = self.populate()
        self.signal_connections(self.widgets)

    def validate_settings_data(self):
        """Make sure all the keys are already present in settings data and all
        value keys are unique.
        """
        for key, data in self.ui_definition.items():
            if data["type"] == "multi":
                for sub_key, sub_data in data["value"].items():
                    self.settings_data.add_property(
                        sub_key, sub_data["value"], force=False
                    )
            else:
                self.settings_data.add_property(
                    key, data["value"], force=False
                )  # do not force the value to be set

    def populate(self):
        """Create the widgets."""
        _widgets = []  # flattened list of all widgets
        for name, properties in self.ui_definition.items():
            _display_name = properties.pop("display_name", name)
            _label = QtWidgets.QLabel(text=_display_name)
            _tooltip = properties.pop("tooltip", "")
            _label.setToolTip(_tooltip)
            _type = properties.pop("type", None)
            if _type == "multi":
                multi_properties = properties.get("value", {})
                _layout = QtWidgets.QHBoxLayout()
                _layout.setContentsMargins(0, 0, 0, 0)
                # align the contents to the left
                _layout.setAlignment(QtCore.Qt.AlignLeft)
                for key, data in multi_properties.items():
                    _type = data.get("type", None)
                    _widget_class = self.widget_dict.get(_type)
                    if not _widget_class:
                        continue
                    _widget = _widget_class(key, **data)
                    _layout.addWidget(_widget)
                    _widget.com.valueChanged.connect(lambda x, k=key: self._setting_data_modified(k, x))
                    _widgets.append(_widget)
                self.addRow(_label, _layout)
            elif _type == "group":
                # if it is a group, add a new row as a separator with the name
                _group_label = QtWidgets.QLabel(text=_display_name)
                _group_label.setStyleSheet("font-weight: bold;")

                group_properties = properties.get("value", {})
                _layout = QtWidgets.QVBoxLayout()
                _layout.setContentsMargins(0, 0, 0, 0)
                # align the contents to the left
                _layout.setAlignment(QtCore.Qt.AlignLeft)
                for key, data in group_properties.items():
                    _type = data.get("type", None)
                    _widget_class = self.widget_dict.get(_type)
                    if not _widget_class:
                        continue
                    sub_label = data.get("display_name", None)
                    if _label:
                        sub_label = QtWidgets.QLabel(text=sub_label)
                        _layout.addWidget(sub_label)
                    _widget = _widget_class(key, **data)
                    _layout.addWidget(_widget)
                    _widget.com.valueChanged.connect(lambda x, k=key: self._setting_data_modified(k, x))
                    _widgets.append(_widget)
                self.addRow(_label, _layout)
            else:
                _widget_class = self.widget_dict.get(_type)
                if not _widget_class:
                    continue
                _widget = _widget_class(name, **properties)
                _widget.com.valueChanged.connect(lambda x, n=name: self._setting_data_modified(n, x))
                self.addRow(_label, _widget)
                _widgets.append(_widget)
            _widget.label = _label

        return _widgets

    def _setting_data_modified(self, key, value):
        self.settings_data.edit_property(key, value)
        self.modified.emit(True)

    def signal_connections(self, widget_list):
        """Create the enable/disable logic between widgets. This needs to be done
        after population.
        """
        for widget in widget_list:
            # get the disable list
            for disable_data in widget.disables:
                # find the target widget / 2nd item in data list is the target
                # Example data: [false, "testString"]
                disable_widget = self.__find_widget(disable_data[1], widget_list)
                condition = disable_data[0]

                if not disable_widget:
                    continue
                widget.com.valueChanged.connect(
                    lambda st, w=disable_widget, c=condition: self.__toggle_enabled(
                        st, c, w
                    )
                )
                self.__toggle_enabled(widget.value, condition, disable_widget)

    @staticmethod
    def __toggle_enabled(value, condition, widget):
        """Disables the widget if value equals to condition. Else enables"""
        if value == condition:
            widget.setEnabled(False)
        else:
            widget.setEnabled(True)

    @staticmethod
    def __find_widget(object_name, widget_list):
        """Find the widget by given object name inside the widget list"""
        for widget in widget_list:
            if widget.objectName() == object_name:
                return widget
        return None

    def find(self, object_name):
        """Find the widget by given object name inside the widget list"""
        return self.__find_widget(object_name, self.widgets)

    def clear(self, keep_settings=False):
        """Clear the layout"""
        self._clear_layout(self)
        if not keep_settings:
            self.settings_data.reset_settings()

    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())

# test the layout
def main():
    import sys
    import os
    app = QtWidgets.QApplication(sys.argv)
    test_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uiSettings_testA.json")

    test_settings = Settings(test_file)
    dialog = QtWidgets.QDialog()
    setting_lay = SettingsLayout(test_settings.get_data())

    dialog.setLayout(setting_lay)
    dialog.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

