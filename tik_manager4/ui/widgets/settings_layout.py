"""Settings Layout for auto-creating setting menus directly from Settings object"""

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
        print(e)
        self.valueChanged.emit(e)


class ValueChangeInt(QtCore.QObject):
    """Simple QObject inheritance to pass the Signal and event to custom widgets"""
    valueChanged = QtCore.Signal(int)

    def valueChangeEvent(self, e):
        print(e)

        self.valueChanged.emit(e)


class ValueChangeFloat(QtCore.QObject):
    """Simple QObject inheritance to pass the Signal and event to custom widgets"""
    valueChanged = QtCore.Signal(float)

    def valueChangeEvent(self, e):
        print(e)

        self.valueChanged.emit(e)


class ValueChangeBool(QtCore.QObject):
    """Simple QObject inheritance to pass the Signal and event to custom widgets"""
    valueChanged = QtCore.Signal(bool)

    def valueChangeEvent(self, e):
        print(e)

        self.valueChanged.emit(e)


# ######################### CUSTOM WIDGETS #######################################
class Boolean(QtWidgets.QCheckBox):
    com = ValueChangeBool()

    def __init__(self, name, object_name=None, value=False, disables=None, **kwargs):
        super(Boolean, self).__init__()
        self.value = value
        self.setObjectName(object_name or name)
        self.setChecked(value)
        self.stateChanged.connect(self.com.valueChangeEvent)
        self.disables = disables or []


class String(QtWidgets.QLineEdit):
    com = ValueChangeStr()

    def __init__(self, name, object_name=None, value="", placeholder="", disables=None, **kwargs):
        super(String, self).__init__()
        self.value = value
        self.setObjectName(object_name or name)
        self.setText(value)
        self.setPlaceholderText(placeholder)
        self.textEdited.connect(self.com.valueChangeEvent)
        self.disables = disables or []


class Combo(QtWidgets.QComboBox):
    com = ValueChangeInt()

    def __init__(self, name, object_name=None, value=0, items=None, disables=None, **kwargs):
        super(Combo, self).__init__()
        self.value = value
        self.setObjectName(object_name or name)
        self.addItems(items or [])
        self.setCurrentIndex(value)
        self.currentIndexChanged.connect(self.com.valueChangeEvent)
        self.disables = disables or []


class SpinnerInt(QtWidgets.QSpinBox):
    com = ValueChangeInt()

    def __init__(self, name, object_name=None, value=0, minimum=-99999, maximum=99999, disables=None, **kwargs):
        super(SpinnerInt, self).__init__()
        self.value = value
        self.setObjectName(object_name or name)
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setValue(value)
        self.valueChanged.connect(self.com.valueChangeEvent)
        self.disables = disables or []


class SpinnerFloat(QtWidgets.QDoubleSpinBox):
    com = ValueChangeFloat()

    def __init__(self, name, object_name=None, value=0, minimum=-99999.9, maximum=99999.9, disables=None, **kwargs):
        super(SpinnerFloat, self).__init__()
        self.value = value
        self.setObjectName(object_name or name)
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setValue(value)
        self.valueChanged.connect(self.com.valueChangeEvent)
        self.disables = disables or []

class SettingsLayout(QtWidgets.QFormLayout):
    """Visualizes and edits Setting objects in a vertical layout"""
    widget_dict = {
        "boolean": Boolean,
        "string": String,
        "combo": Combo,
        "spinnerInt": SpinnerInt,
        "spinnerFloat": SpinnerFloat
    }

    def __init__(self, settings_obj, *args, **kwargs):
        super(SettingsLayout, self).__init__(*args, **kwargs)
        self.settings_data = settings_obj
        self.widgets = self.populate()
        self.signal_connections(self.widgets)

    def populate(self):
        """Creates the widgets"""
        _widgets = []
        for name, properties in self.settings_data._currentValue.items():
            _label = QtWidgets.QLabel(text=name)
            _type = properties.get("type", None)
            if _type == "multi":
                multi_properties = properties.get("value", [])
                _layout = QtWidgets.QHBoxLayout()
                for each in multi_properties:
                    print(multi_properties)
                    _type = each.get("type", None)
                    _widget_class = self.widget_dict.get(_type)
                    if not _widget_class:
                        continue
                    _widget = _widget_class(name, **each)
                    _layout.addWidget(_widget)
                    _widget_class.com.valueChanged.connect(lambda x, n=name: self.settings_data.edit_property(n, x))
                    _widgets.append(_widget)
                self.addRow(_label, _layout)
            else:
                _widget_class = self.widget_dict.get(_type)
                if not _widget_class:
                    continue
                _widget = _widget_class(name, **properties)
                _widget_class.com.valueChanged.connect(lambda x, n=name: self.settings_data.edit_property(n, x))
                self.addRow(_label, _widget)
                _widgets.append(_widget)
            # elif isinstance(properties, list):
            #     _layout = QtWidgets.QHBoxLayout()
            #     for each in properties:
            #         _type = each.get("type", None)
            #         _widget_class = self.widget_dict.get(_type)
            #         if not _widget_class:
            #             continue
            #         _widget = _widget_class(name, **each)
            #         _layout.addWidget(_widget)
            #         _widget_class.com.valueChanged.connect(lambda x, n=name: self.settings_data.edit_property(n, x))
            #         _widgets.append(_widget)
            #     self.addRow(_label, _layout)

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
    test_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uiSettings_test.json")

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

