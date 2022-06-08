"""Settings Layout for auto-creating setting menus directly from Settings object"""

import os
import sys
from tik_manager4.core.settings import Settings
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtSignal as Signal
# from tik_manager4.ui.Qt import QtWidgets, QtGui, QtCore

class Boolean(QtWidgets.QCheckBox):
    # valueChanged = Signal(str)

    def __init__(self, value=False, *args, **kwargs):
        super(Boolean, self).__init__()
        # super(Boolean, self).__init__()
        self.setChecked(value)
        # self.stateChanged.connect(self.valueChangeEvent)

    # def valueChangeEvent(self, e):
    #     self.valueChanged.emit(e)


class String(QtWidgets.QLineEdit):
    def __init__(self, value="", placeholder="", **kwargs):
        super(String, self).__init__()
        self.setText(value)
        self.setPlaceholderText(placeholder)


class Combo(QtWidgets.QComboBox):
    def __init__(self, value=0, items=None, **kwargs):
        super(Combo, self).__init__()
        self.addItems(items or [])
        self.setCurrentIndex(value)


class SpinnerInt(QtWidgets.QSpinBox):
    def __init__(self, value=0, minimum=-99999, maximum=99999, **kwargs):
        super(SpinnerInt, self).__init__()
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setValue(value)


class SpinnerFloat(QtWidgets.QDoubleSpinBox):
    def __init__(self, value=0, minimum=-99999.9, maximum=99999.9, **kwargs):
        super(SpinnerFloat, self).__init__()
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setValue(value)


class SettingsLayout(QtWidgets.QFormLayout):
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

        self.populate()


    def populate(self):
        for name, properties in self.settings_data._currentValue.items():
            _type = properties.get("type", None)
            _label = QtWidgets.QLabel(text=name)
            _widget_class = self.widget_dict.get(_type)
            if not _widget_class:
                continue
            self.addRow(_label, _widget_class(**properties))

            _widget_class.valueChanged.connect(lambda x: print(x))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    test_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uiSettings_test.json")

    test_settings = Settings(test_file)

    dialog = QtWidgets.QDialog()
    setting_lay = SettingsLayout(test_settings)
    # setting_lay.addRow(QtWidgets.QLabel("test"), QtWidgets.QLabel("ASDFASDF"))

    dialog.setLayout(setting_lay)
    dialog.show()
    sys.exit(app.exec_())
