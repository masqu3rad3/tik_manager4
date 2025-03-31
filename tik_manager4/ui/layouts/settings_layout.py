"""Settings Layout for auto-creating setting menus directly from Settings object.

Supported types:
    - boolean => QCheckBox
    - string => QLineEdit
    - spinnerInt => QSpinBox
    - spinnerFloat => QDoubleSpinBox
    - combo => QComboBox


"""
from pathlib import Path
from tik_manager4.core.constants import DataTypes
from tik_manager4.core.settings import Settings
from tik_manager4.core.utils import get_nice_name

from tik_manager4.ui.widgets import value_widgets
from tik_manager4.ui.widgets.category_list import CategoryList

import tik_manager4.ui.widgets.browser
import tik_manager4.ui.widgets.path_browser
from tik_manager4.ui.widgets.validated_string import ValidatedString
from tik_manager4.ui.Qt import QtWidgets, QtCore


def guess_data_type(data, enums=None):
    """Guess the type of the data to be used as ui definition."""
    if enums:
        # return "combo"
        return DataTypes.COMBO.value
    if isinstance(data, bool):
        # return "boolean"
        return DataTypes.BOOLEAN.value
    elif isinstance(data, str):
        if Path(data).exists() and data != "":
            # return "pathBrowser"
            return DataTypes.PATHBROWSER.value
        # return "string"
        return DataTypes.STRING.value
    elif isinstance(data, int):
        # return "integer"
        return DataTypes.INTEGER.value
    elif isinstance(data, float):
        # return "float"
        return DataTypes.FLOAT.value
    elif isinstance(data, dict):
        # return "multi"
        return DataTypes.MULTI.value
    elif isinstance(data, (list, tuple)):
        if all(isinstance(item, int) for item in data) and len(data) == 2:
            # return "vector2Int"
            return DataTypes.VECTOR2INT.value
        # if ANY floats, it is a vector2Float
        elif any(isinstance(item, float) for item in data) and len(data) == 2:
            # return "vector2Float"
            return DataTypes.VECTOR2FLOAT.value
        elif all(isinstance(item, int) for item in data) and len(data) == 3:
            # return "vector3Int"
            return DataTypes.VECTOR3INT.value
        # if ANY floats, it is a vector3Float
        elif any(isinstance(item, float) for item in data) and len(data) == 3:
            # return "vector3Float"
            return DataTypes.VECTOR3FLOAT.value
        else:
            # return "combo"
            return DataTypes.COMBO.value
    else:
        return None
def convert_to_ui_definition(settings_data):
    """Converts the settings data to ui definition.

    Args:
        settings_data (Settings or dict): Settings object or dictionary data
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
        # if data_type == "multi":
        if data_type == DataTypes.MULTI.value:
            value = convert_to_ui_definition(data)
        # elif data_type == "combo":
        elif data_type == DataTypes.COMBO.value:
            value = data[0]
            ui_definition[key]["items"] = data
        else:
            value = data
        ui_definition[key]["value"] = value
    return ui_definition

def convert_to_settings_data(ui_definition):
    """Converts the ui definition to settings data.

    Args:
        ui_definition (dict): UI definition data
    """
    settings_data = {}

    for key, data in ui_definition.items():
        if data.get("value") is None:
            continue # skip if the keys without value. (like separators)
        # if data["type"] in ["separator", "info"]:
        if data["type"] in [DataTypes.SEPARATOR.value, DataTypes.INFO.value]:
            continue
        # if data["type"] == "multi":
        if data["type"] == DataTypes.MULTI.value:
            settings_data[key] = convert_to_settings_data(data["value"])
        # elif data["type"] == "group":
        elif data["type"] == DataTypes.COMBO.value:
            continue
        else:
            settings_data[key] = data["value"]
    return settings_data

class SettingsLayout(QtWidgets.QFormLayout):
    """Visualizes and edits Setting objects in a vertical layout"""
    modified = QtCore.Signal(bool)

    widget_dict = {
        DataTypes.BOOLEAN.value: value_widgets.Boolean,
        DataTypes.STRING.value: value_widgets.String,
        DataTypes.COMBO.value: value_widgets.Combo,
        DataTypes.INTEGER.value: value_widgets.Integer,
        DataTypes.FLOAT.value: value_widgets.Float,
        DataTypes.SPINNERINT.value: value_widgets.SpinnerInt,
        DataTypes.SPINNERFLOAT.value: value_widgets.SpinnerFloat,
        DataTypes.LIST.value: value_widgets.List,
        DataTypes.DROPLIST.value: value_widgets.DropList,
        DataTypes.CATEGORYLIST.value: CategoryList,
        DataTypes.VALIDATEDSTRING.value: ValidatedString,
        DataTypes.VECTOR2INT.value: value_widgets.Vector2Int,
        DataTypes.VECTOR2FLOAT.value: value_widgets.Vector2Float,
        DataTypes.VECTOR3INT.value: value_widgets.Vector3Int,
        DataTypes.VECTOR3FLOAT.value: value_widgets.Vector3Float,
        DataTypes.PATHBROWSER.value: tik_manager4.ui.widgets.path_browser.PathBrowser,
        DataTypes.FILEBROWSER.value: tik_manager4.ui.widgets.path_browser.FileBrowser,
        DataTypes.SUBPROJECTBROWSER.value: tik_manager4.ui.widgets.browser.SubprojectBrowser,
        DataTypes.BUTTON.value: value_widgets.Button,
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
            # if data["type"] == "multi":
            if data["type"] == DataTypes.MULTI.value:
                for sub_key, sub_data in data["value"].items():
                    self.settings_data.add_property(
                        sub_key, sub_data["value"], force=False
                    )
            elif data.get("value") is None:
                continue # skip if the keys without value. (like separators)
            # elif data["type"] in [DataTypes.SEPARATOR.value, DataTypes.INFO.value]:
            elif data["type"] not in DataTypes.get_storable_types():
                continue # info and separator types are not stored in settings data
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
            if _type == DataTypes.MULTI.value:
                multi_properties = properties.get("value", {})
                _layout = QtWidgets.QHBoxLayout()
                _layout.setContentsMargins(0, 0, 0, 0)
                # align the contents to the left
                _layout.setAlignment(QtCore.Qt.AlignLeft)
                for key, data in multi_properties.items():
                    _type = data.get("type", None)
                    _widget = self.__instanciate_widget(_type, key, data)
                    if not _widget:
                        continue
                    _layout.addWidget(_widget)
                    _widgets.append(_widget)
                    # _type = data.get("type", None)
                    # _widget_class = self.widget_dict.get(_type)
                    # if not _widget_class:
                    #     continue
                    # _widget = _widget_class(key, **data)
                    # _layout.addWidget(_widget)
                    # _widget.com.valueChanged.connect(lambda x, k=key: self._setting_data_modified(k, x))
                    # _widgets.append(_widget)
                self.addRow(_label, _layout)
            # elif _type == "group":
            elif _type == DataTypes.GROUP.value:
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
            elif _type in  [DataTypes.INFO.value, DataTypes.SEPARATOR.value]:
                # first add a blank line
                # if the type is separator, simply add a new row.
                _widget = QtWidgets.QLabel(text=properties.get("value", _display_name))
                # make it bold and larger
                _widget.setStyleSheet("font-weight: bold; font-size: 14px;")
                self.addRow(_label, _widget)
            else:
                _widget = self.__instanciate_widget(_type, name, properties)
                if not _widget:
                    continue
                # _widget_class = self.widget_dict.get(_type)
                # if not _widget_class:
                #     continue
                # # if the key is available in the settings data and if it has a value, use that one
                # if self.settings_data.get(name) is not None:
                #     properties["value"] = self.settings_data.get(name)
                # _widget = _widget_class(name, **properties)
                # _widget.com.valueChanged.connect(lambda x, n=name: self._setting_data_modified(n, x))
                self.addRow(_label, _widget)
                _widgets.append(_widget)
            _widget.label = _label

        return _widgets

    def __instanciate_widget(self, widget_type, key, data):
        widget_class = self.widget_dict.get(widget_type)
        if not widget_class:
            return None
        if self.settings_data.get(key) is not None:
            data["value"] = self.settings_data.get(key)
        widget = widget_class(key, **data)
        if widget_type in DataTypes.get_storable_types():
            widget.com.valueChanged.connect(lambda x, k=key: self._setting_data_modified(k, x))
        return widget

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
    from tik_manager4.ui import pick
    app = QtWidgets.QApplication(sys.argv)
    test_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uiSettings_testA.json")

    test_settings = Settings(test_file)
    _style_file = pick.style_file()
    dialog = QtWidgets.QDialog(styleSheet=str(_style_file.readAll(), "utf-8"))
    setting_lay = SettingsLayout(test_settings.get_data())

    dialog.setLayout(setting_lay)

    dialog.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

