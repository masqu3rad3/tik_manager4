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
        self.stateChanged.connect(self.com.valueChangeEvent)
        # self.stateChanged.connect(self.valueChangeEvent)
        self.disables = disables or []


class String(QtWidgets.QLineEdit):

    def __init__(self, name, object_name=None, value="", placeholder="", disables=None, **kwargs):
        super(String, self).__init__()
        self.com = ValueChangeStr()
        self.value = value
        self.setObjectName(object_name or name)
        self.setText(value)
        self.setPlaceholderText(placeholder)
        self.textEdited.connect(self.com.valueChangeEvent)
        self.disables = disables or []


class Combo(QtWidgets.QComboBox):

    def __init__(self, name, object_name=None, value=None, items=None, disables=None, **kwargs):
        super(Combo, self).__init__()
        self.com = ValueChangeStr()
        self.value = value
        self.setObjectName(object_name or name)
        self.addItems(items or [])
        self.setCurrentText(value)
        self.currentTextChanged.connect(self.com.valueChangeEvent)
        self.disables = disables or []


class SpinnerInt(QtWidgets.QSpinBox):

    def __init__(self, name, object_name=None, value=0, minimum=-99999, maximum=99999, disables=None, **kwargs):
        super(SpinnerInt, self).__init__()
        self.com = ValueChangeInt()
        self.value = value
        self.setObjectName(object_name or name)
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setValue(value)
        self.valueChanged.connect(self.com.valueChangeEvent)
        self.disables = disables or []

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

class Float(SpinnerFloat):
    def __init__(self, *args, **kwargs):
        super(Float, self).__init__(*args, **kwargs)
        self.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)

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
        # self.add_button = QtWidgets.QPushButton("Add")
        # self.add_button.clicked.connect(self.add_item)
        # self.remove_button = QtWidgets.QPushButton("Remove")
        # self.remove_button.clicked.connect(self.remove_item)
        # self.button_layout.addWidget(self.add_button)
        # self.button_layout.addWidget(self.remove_button)
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
        self.list.takeItem(self.list.currentRow())
        self.value.pop(self.list.currentRow())
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
        "list": List
    }

    def __init__(self, settings_obj, *args, **kwargs):
        super(SettingsLayout, self).__init__(*args, **kwargs)
        self.settings_data = settings_obj
        self.widgets = self.populate()
        self.signal_connections(self.widgets)

    def populate(self):
        """Creates the widgets"""
        _widgets = [] # flattened list of all widgets
        for name, properties in self.settings_data._currentValue.items():
            _display_name = properties.get("display_name", name)
            _label = QtWidgets.QLabel(text=_display_name)
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
                    _widget.com.valueChanged.connect(lambda x, n=name, k=key: self.settings_data.edit_sub_property([n, "value", k, "value"], x))
                    _widgets.append(_widget)
                self.addRow(_label, _layout)
            else:
                _widget_class = self.widget_dict.get(_type)
                if not _widget_class:
                    continue
                _widget = _widget_class(name, **properties)
                _widget.com.valueChanged.connect(lambda x, n=name: self.settings_data.edit_sub_property([n, "value"], x))
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
                widget.com.valueChanged.connect(lambda state, wgt=disable_widget, cnd=condition: self.__toggle_enabled(state, cnd, wgt))
                # widget.com.valueChanged.connect(lambda state, disable_widget, condition: self.__toggle_enabled(state, condition, disable_widget))
                self.__toggle_enabled(widget.value, condition, disable_widget)

    def __toggle_enabled(self, value, condition, widget):
        """Disables the widget if value equals to condition. Else enables"""
        if value == condition:
            widget.setEnabled(False)
        else:
            widget.setEnabled(True)

    def __find_widget(self, object_name, widget_list):
        """Finds the widget by given object name inside the widget list"""
        for widget in widget_list:
            if widget.objectName() == object_name:
                return widget
        return None


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
    setting_lay = SettingsLayout(test_settings)

    dialog.setLayout(setting_lay)
    dialog.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

