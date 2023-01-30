"""Settings Layout for auto-creating setting menus directly from Settings object.

Supported types:
    - boolean => QCheckBox
    - string => QLineEdit
    - spinnerInt => QSpinBox
    - spinnerFloat => QDoubleSpinBox
    - combo => QComboBox


"""

import os
import sys
from tik_manager4.core.settings import Settings
# from PyQt5 import QtWidgets, QtGui, QtCore
#
import re
from tik_manager4.ui.Qt import QtWidgets, QtGui, QtCore


# Signal - Slot requires QObject inheritance
class ValueChangeStr(QtCore.QObject):
    """Simple QObject inheritance to pass the Signal and event to custom widgets"""
    valueChanged = QtCore.Signal(str)

    def __init__(self):
        super(ValueChangeStr, self).__init__()

    def valueChangeEvent(self, e):
        self.valueChanged.emit(e)


class ValueChangeInt(QtCore.QObject):
    """Simple QObject inheritance to pass the Signal and event to custom widgets"""
    valueChanged = QtCore.Signal(int)

    def valueChangeEvent(self, e):
        self.valueChanged.emit(e)


class ValueChangeFloat(QtCore.QObject):
    """Simple QObject inheritance to pass the Signal and event to custom widgets"""
    valueChanged = QtCore.Signal(float)

    def valueChangeEvent(self, e):
        self.valueChanged.emit(e)


class ValueChangeBool(QtCore.QObject):
    """Simple QObject inheritance to pass the Signal and event to custom widgets"""
    valueChanged = QtCore.Signal(bool)

    def valueChangeEvent(self, e):
        self.valueChanged.emit(e)


class ValueChangeList(QtCore.QObject):
    """Simple QObject inheritance to pass the Signal and event to custom widgets"""
    valueChanged = QtCore.Signal(list)

    def valueChangeEvent(self, e):
        self.valueChanged.emit(e)


# ######################### CUSTOM WIDGETS #######################################
class Boolean(QtWidgets.QCheckBox):

    def __init__(self, name, object_name=None, value=False, disables=None, **kwargs):
        super(Boolean, self).__init__()
        self.com = ValueChangeBool()
        self.value = value
        self.setObjectName(object_name or name)
        self.setChecked(value)
        self.stateChanged.connect(self.value_change_event)
        self.disables = disables or []

    def value_change_event(self, e):
        self.value = e
        self.com.valueChangeEvent(e)


class String(QtWidgets.QLineEdit):

    def __init__(self, name, object_name=None, value="", placeholder="", disables=None, **kwargs):
        super(String, self).__init__()
        self.com = ValueChangeStr()
        self.value = value
        self.setObjectName(object_name or name)
        self.setText(value)
        self.setPlaceholderText(placeholder)
        self.textEdited.connect(self.value_change_event)
        self.disables = disables or []

    def value_change_event(self, e):
        self.value = e
        self.com.valueChangeEvent(e)


class Combo(QtWidgets.QComboBox):

    def __init__(self, name, object_name=None, value=None, items=None, disables=None, **kwargs):
        super(Combo, self).__init__()
        self.com = ValueChangeStr()
        self.value = value
        self.setObjectName(object_name or name)
        self.addItems(items or [])
        self.setCurrentText(value)
        self.currentTextChanged.connect(self.value_change_event)
        self.disables = disables or []

    def value_change_event(self, e):
        self.value = e
        self.com.valueChangeEvent(e)


class SpinnerInt(QtWidgets.QSpinBox):

    def __init__(self, name, object_name=None, value=0, minimum=-99999, maximum=99999, disables=None, **kwargs):
        super(SpinnerInt, self).__init__()
        self.com = ValueChangeInt()
        self.value = value
        self.setObjectName(object_name or name)
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setValue(value)
        # self.valueChanged.connect(self.com.valueChangeEvent)
        self.valueChanged.connect(self.value_change_event)
        self.disables = disables or []

    def value_change_event(self, e):
        self.value = e
        self.com.valueChangeEvent(e)


class Integer(SpinnerInt):

    def __init__(self, *args, **kwargs):
        super(Integer, self).__init__(*args, **kwargs)
        self.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)


class SpinnerFloat(QtWidgets.QDoubleSpinBox):

    def __init__(self, name, object_name=None, value=0, minimum=-99999.9, maximum=99999.9, disables=None, **kwargs):
        super(SpinnerFloat, self).__init__()
        self.com = ValueChangeFloat()
        self.value = value
        self.setObjectName(object_name or name)
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setValue(value)
        self.valueChanged.connect(self.com.valueChangeEvent)
        self.disables = disables or []

    def value_change_event(self, e):
        self.value = e
        self.com.valueChangeEvent(e)


class Float(SpinnerFloat):
    def __init__(self, *args, **kwargs):
        super(Float, self).__init__(*args, **kwargs)
        self.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)


class _Vector(QtWidgets.QWidget):
    """Convenient class for other vector widget classes"""
    def __init__(self, name, object_name=None, value=None, minimum=None, maximum=None, disables=None, **kwargs):
        super(_Vector, self).__init__()
        self.com = ValueChangeList()
        self.value = value
        self.setObjectName(object_name or name)
        # self.valueChanged.connect(self.com.valueChangeEvent)
        self.disables = disables or []

        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)


class Vector2Float(_Vector):
    def __init__(self, *args, **kwargs):
        super(Vector2Float, self).__init__(*args, **kwargs)
        self.x = Float("x", value=self.value[0])
        self.y = Float("y", value=self.value[1])
        self.layout.addWidget(self.x)
        self.layout.addWidget(self.y)
        self.x.valueChanged.connect(self.value_change_event)
        self.y.valueChanged.connect(self.value_change_event)
        self.layout.addStretch()

    def value_change_event(self, e):
        self.value = [self.x.value, self.y.value]
        self.com.valueChangeEvent(self.value)


class Vector3Float(_Vector):
    def __init__(self, *args, **kwargs):
        super(Vector3Float, self).__init__(*args, **kwargs)
        self.x = Float("x", value=self.value[0])
        self.y = Float("y", value=self.value[1])
        self.z = Float("z", value=self.value[2])
        self.layout.addWidget(self.x)
        self.layout.addWidget(self.y)
        self.layout.addWidget(self.z)
        self.x.valueChanged.connect(self.value_change_event)
        self.y.valueChanged.connect(self.value_change_event)
        self.z.valueChanged.connect(self.value_change_event)
        self.layout.addStretch()

    def value_change_event(self, e):
        self.value = [self.x.value, self.y.value, self.z.value]
        self.com.valueChangeEvent(self.value)


class Vector2Int(_Vector):
    def __init__(self, *args, **kwargs):
        super(Vector2Int, self).__init__(*args, **kwargs)
        self.x = Integer("x", value=self.value[0])
        self.y = Integer("y", value=self.value[1])
        self.layout.addWidget(self.x)
        self.layout.addWidget(self.y)
        self.x.valueChanged.connect(self.value_change_event)
        self.y.valueChanged.connect(self.value_change_event)
        self.layout.addStretch()

    def value_change_event(self, e):
        self.value = [self.x.value, self.y.value]
        self.com.valueChangeEvent(self.value)


class Vector3Int(_Vector):
    def __init__(self, *args, **kwargs):
        super(Vector3Int, self).__init__(*args, **kwargs)
        self.x = Integer("x", value=self.value[0])
        self.y = Integer("y", value=self.value[1])
        self.z = Integer("z", value=self.value[2])
        self.layout.addWidget(self.x)
        self.layout.addWidget(self.y)
        self.layout.addWidget(self.z)
        self.x.valueChanged.connect(self.valueChangeEvent)
        self.y.valueChanged.connect(self.valueChangeEvent)
        self.z.valueChanged.connect(self.valueChangeEvent)
        self.layout.addStretch()

    def valueChangeEvent(self, e):
        self.value = [self.x.value, self.y.value, self.z.value]
        self.com.valueChangeEvent(self.value)

# class Vector2Int(QtWidgets.QWidget):
#     """A Class to draw 2D integer vectors"""
#     def __init__(self, name, object_name=None, value=None, minimum=-99999, maximum=99999, disables=None, **kwargs):
#         super(Vector2Int, self).__init__()
#         self.com = ValueChangeList()
#         self.value = value
#         self.setObjectName(object_name or name)
#         self.disables = disables or []
#         self.setLayout(QtWidgets.QHBoxLayout())
#         self.layout().setContentsMargins(0, 0, 0, 0)
#         # self.layout().setSpacing(0)
#         self.x = Integer("x", value=value[0], minimum=minimum, maximum=maximum)
#         self.y = Integer("y", value=value[1], minimum=minimum, maximum=maximum)
#         self.x.setMinimum(minimum)
#         self.y.setMaximum(maximum)
#         self.x.setValue(value[0])
#         self.y.setValue(value[1])
#
#         self.layout().addWidget(self.x)
#         self.layout().addWidget(self.y)
#         self.layout().addStretch()
#         self.x.valueChanged.connect(self.valueChangeEvent)
#         self.y.valueChanged.connect(self.valueChangeEvent)
#
#     def valueChangeEvent(self, e):
#         self.com.valueChangeEvent([self.x.value, self.y.value])


class List(QtWidgets.QWidget):
    """Customized List widget with buttons to manage the list"""

    def __init__(self, name, object_name=None, value=None, disables=None, **kwargs):
        super(List, self).__init__()
        self.com = ValueChangeList()
        self.value = value or []
        self.setObjectName(object_name or name)
        self.disables = disables or []
        self.layout = QtWidgets.QHBoxLayout(self)
        self.list = QtWidgets.QListWidget()
        self.button_layout = QtWidgets.QVBoxLayout()
        self.button_names = kwargs.get("buttons", ["Add", "Remove", "Up", "Down"])
        self.buttons = []
        self._create_buttons()
        self.build()

    def build(self):
        self.list.addItems(self.value)
        self.list.itemChanged.connect(self.com.valueChangeEvent)
        self.layout.addWidget(self.list)
        self.layout.addLayout(self.button_layout)

    def get_button(self, name):
        """Return the button widget with the given name"""
        return self.buttons[self.button_names.index(name)]

    def _create_buttons(self):
        for button in self.button_names:
            _button = QtWidgets.QPushButton(button)
            _button.setObjectName(button)
            self.button_layout.addWidget(_button)
            self.buttons.append(_button)
            # handle the predefined functions
            if button == "Add":
                _button.clicked.connect(self.add_item)
            elif button == "Remove":
                _button.clicked.connect(self.remove_item)
            elif button == "Up":
                _button.clicked.connect(self.up_item)
            elif button == "Down":
                _button.clicked.connect(self.down_item)
            else:
                # now handle the buttons with custom functions
                # TODO add the custom functions
                pass

    def add_item(self):
        # create a mini dialog to define the item name
        item_name, ok = QtWidgets.QInputDialog.getText(self, "Add Item", "Item Name")
        if ok:
            # if the item is already in the list, do nothing
            if item_name in self.value:
                return
            self.list.addItem(item_name)
            self.value.append(item_name)
            self.com.valueChangeEvent(self.value)

    def remove_item(self):
        """Remove the selected item from the list and from the self.value"""
        item = self.list.currentItem()
        if item:
            self.list.takeItem(self.list.row(item))
            self.value.remove(item.text())
            self.com.valueChangeEvent(self.value)

    def up_item(self):
        """Move the selected item up in the list of items."""
        current_row = self.list.currentRow()
        if current_row > 0:
            item = self.list.takeItem(current_row)
            self.list.insertItem(current_row - 1, item)
            self.list.setCurrentRow(current_row - 1)
            self.value.insert(current_row - 1, self.value.pop(current_row))
            self.com.valueChangeEvent(self.value)

    def down_item(self):
        """Move the selected item down in the list of items."""
        current_row = self.list.currentRow()
        if current_row < self.list.count() - 1:
            item = self.list.takeItem(current_row)
            self.list.insertItem(current_row + 1, item)
            self.list.setCurrentRow(current_row + 1)
            self.value.insert(current_row + 1, self.value.pop(current_row))
            self.com.valueChangeEvent(self.value)


class CategoryList(List):
    """A special list widget purposed for category selection"""

    def __init__(self, name, object_name=None, value=None, disables=None, category_list=None, **kwargs):
        super(CategoryList, self).__init__(name, object_name, value, disables, **kwargs)
        self.category_list = category_list or list(self.value)

    def add_item(self):
        """Add a new item from the category list"""
        # Make a dialog with a combo box to select the item from the category list
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Add Item")
        dialog_layout = QtWidgets.QVBoxLayout(dialog)
        combo = QtWidgets.QComboBox()
        combo.addItems(self.category_list)
        dialog_layout.addWidget(combo)
        button_layout = QtWidgets.QHBoxLayout()
        # create the buttons with button box
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        button_layout.addWidget(button_box)
        dialog_layout.addLayout(button_layout)

        if dialog.exec_():
            # if the item is already in the list, do nothing
            if combo.currentText() in self.value:
                return
            self.list.addItem(combo.currentText())
            self.value.append(combo.currentText())
            self.com.valueChangeEvent(self.value)


class ValidatedString(String):
    def __init__(self, *args, connected_widgets=None, allow_spaces=False, allow_directory=False, allow_empty=False, **kwargs):
        """Custom QLineEdit widget to validate entered values"""
        super(ValidatedString, self).__init__(*args, **kwargs)
        self.allow_spaces = allow_spaces
        self.allow_directory = allow_directory
        self.allow_empty = allow_empty
        self.connected_widgets = connected_widgets or []
        self.default_stylesheet = self.styleSheet()
        if connected_widgets:
            self.set_connected_widgets(connected_widgets) # validate and toggle connected widgets
        else:
            self._validate() # just validate the value

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
        super(ValidatedString, self).keyPressEvent(*args, **kwargs)
        self._validate()

    def _validate(self):
        current_text = self.text()
        if not self.allow_empty and not current_text:
            self._fail()
        elif not self.string_value(current_text, allow_spaces=self.allow_spaces, directory=self.allow_directory):
            self._fail()
        else:
            self.setStyleSheet(self.default_stylesheet)
            if self.connected_widgets:
                for wid in self.connected_widgets:
                    wid.setEnabled(True)

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
    def string_value(input_text, allow_spaces=False, directory=False):
        """Check the text for illegal characters."""
        allow_spaces = " " if allow_spaces else ""
        directory = "/\\\\:" if directory else ""

        pattern = r'^[:A-Za-z0-9%s%s.A_-]*$' % (directory, allow_spaces)

        if re.match(pattern, input_text):
            return True
        else:
            return False


class SettingsLayout(QtWidgets.QFormLayout):
    """Visualizes and edits Setting objects in a vertical layout"""
    widget_dict = {
        "boolean": Boolean,
        "string": String,
        "combo": Combo,
        "integer": Integer,
        "float": Float,
        "spinnerInt": SpinnerInt,
        "spinnerFloat": SpinnerFloat,
        "list": List,
        "categoryList": CategoryList,
        "validatedString": ValidatedString,
        "vector2Int": Vector2Int,
        "vector2Float": Vector2Float,
        "vector3Int": Vector3Int,
        "vector3Float": Vector3Float
    }

    def __init__(self, ui_definition, settings_data=None, *args, **kwargs):
        super(SettingsLayout, self).__init__(*args, **kwargs)
        self.ui_definition = ui_definition
        # TODO validate settings data type
        self.settings_data = settings_data or Settings()
        self.validate_settings_data()
        self.widgets = self.populate()
        self.signal_connections(self.widgets)

    def validate_settings_data(self):
        """Make sure all the keys are already present in settings data and all value keys are unique."""
        for key, data in self.ui_definition.items():
            if data["type"] == "multi":
                for sub_key, sub_data in data["value"].items():
                    self.settings_data.add_property(sub_key, sub_data["value"], force=False)
            else:
                self.settings_data.add_property(key, data["value"], force=False) # do not force the value to be set

    def populate(self):
        """Create the widgets."""
        _widgets = []  # flattened list of all widgets
        for name, properties in self.ui_definition.items():
            _display_name = properties.get("display_name", name)
            _label = QtWidgets.QLabel(text=_display_name)
            _tooltip = properties.get("tooltip", "")
            _label.setToolTip(_tooltip)
            _type = properties.get("type", None)
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
                    _widget.com.valueChanged.connect(
                        # lambda x, n=name, k=key: self.ui_definition.edit_sub_property([n, "value", k, "value"], x))
                        lambda x, n=name, k=key: self.settings_data.edit_property(k, x)
                    )
                    _widgets.append(_widget)
                self.addRow(_label, _layout)
            else:
                _widget_class = self.widget_dict.get(_type)
                if not _widget_class:
                    continue
                _widget = _widget_class(name, **properties)
                _widget.com.valueChanged.connect(
                    # lambda x, n=name: self.ui_definition.edit_sub_property([n, "value"], x)
                    lambda x, n=name: self.settings_data.edit_property(n, x)
                )
                self.addRow(_label, _widget)
                _widgets.append(_widget)

        return _widgets


    def signal_connections(self, widget_list):
        """Creates the enable/disable logic between widgets. This needs to be done after population"""
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
                    lambda state, wgt=disable_widget, cnd=condition: self.__toggle_enabled(state, cnd, wgt))
                # widget.com.valueChanged.connect(lambda state, disable_widget, condition: self.__toggle_enabled(state, condition, disable_widget))
                self.__toggle_enabled(widget.value, condition, disable_widget)

    def __toggle_enabled(self, value, condition, widget):
        """Disables the widget if value equals to condition. Else enables"""
        if value == condition:
            widget.setEnabled(False)
        else:
            widget.setEnabled(True)

    def __find_widget(self, object_name, widget_list):
        """Find the widget by given object name inside the widget list"""
        for widget in widget_list:
            if widget.objectName() == object_name:
                return widget
        return None

    def find(self, object_name):
        """Find the widget by given object name inside the widget list"""
        return self.__find_widget(object_name, self.widgets)

def main():
    app = QtWidgets.QApplication(sys.argv)
    test_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uiSettings_testA.json")

    test_settings = Settings(test_file)
    # test_settings = Settings()
    # test_check = {
    #     "type": "boolean",
    #     "value": True,
    #     "disables": []
    # }
    # test_settings.add_property("testCheck", test_check)

    dialog = QtWidgets.QDialog()
    setting_lay = SettingsLayout(test_settings.get_data())
    # setting_lay.addRow(QtWidgets.QLabel("test"), QtWidgets.QLabel("ASDFASDF"))

    dialog.setLayout(setting_lay)
    dialog.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
    # app = QtWidgets.QApplication(sys.argv)
    # test_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uiSettings_test.json")
    #
    # test_settings = Settings(test_file)
    #
    # dialog = QtWidgets.QDialog()
    # setting_lay = SettingsLayout(test_settings)
    # # setting_lay.addRow(QtWidgets.QLabel("test"), QtWidgets.QLabel("ASDFASDF"))
    #
    # dialog.setLayout(setting_lay)
    # dialog.show()
    # sys.exit(app.exec_())

