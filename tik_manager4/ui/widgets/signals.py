# pylint: disable=
"""Signal definitions for the TikManager4 UI."""
from tik_manager4.ui.Qt import QtCore


class ValueChangeObj(QtCore.QObject):
    """Simple QObject inheritance to pass the Signal and event to custom widgets"""

    valueChanged = QtCore.Signal(object)

    def __init__(self):
        super(ValueChangeObj, self).__init__()

    def valueChangeEvent(self, e):
        self.valueChanged.emit(e)


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
