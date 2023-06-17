"""Collection of simple value widgets."""

from tik_manager4.ui.Qt import QtWidgets, QtCore
from tik_manager4.ui.widgets.common import TikButton

from tik_manager4.ui.widgets import signals



class Boolean(QtWidgets.QCheckBox):
    def __init__(self, name, object_name=None, value=False, disables=None, **kwargs):
        super(Boolean, self).__init__()
        self.com = signals.ValueChangeBool()
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
        self.com = signals.ValueChangeStr()
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
        self.com = signals.ValueChangeStr()
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
        self.com = signals.ValueChangeInt()
        self.value = value
        self.setObjectName(object_name or name)
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setValue(value)
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
        self.com = signals.ValueChangeFloat()
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
        self.com = signals.ValueChangeList()
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
        self.x.valueChanged.connect(self.value_change_event)
        self.y.valueChanged.connect(self.value_change_event)
        self.z.valueChanged.connect(self.value_change_event)
        self.layout.addStretch()

    def value_change_event(self, e):
        self.value = [self.x.value, self.y.value, self.z.value]
        self.com.valueChangeEvent(self.value)


class List(QtWidgets.QWidget):
    """Customized List widget with buttons to manage the list"""

    def __init__(self, name=None, object_name=None, value=None, disables=None, buttons_position="side", **kwargs):
        super(List, self).__init__()
        self.com = signals.ValueChangeList()
        self.value = value or []
        self.setObjectName(object_name or name)
        self.disables = disables or []

        self.master_layout = QtWidgets.QVBoxLayout(self)
        if name:
            self.label = QtWidgets.QLabel(name)
            self.master_layout.addWidget(self.label)
        self.master_layout.addWidget(self.label)
        self.layout = QtWidgets.QHBoxLayout() if buttons_position == "side" else QtWidgets.QVBoxLayout()
        self.master_layout.addLayout(self.layout)
        # self.layout = QtWidgets.QHBoxLayout(self) if buttons_position == "side" else QtWidgets.QVBoxLayout(self)
        self.list = QtWidgets.QListWidget()
        self.button_layout = QtWidgets.QVBoxLayout() if buttons_position == "side" else QtWidgets.QHBoxLayout()
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
            _button = TikButton(button)
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


class DropList(List):
    """Custom List Widget which accepts drops"""
    dropped = QtCore.Signal(str)

    def __init__(self, parent=None, **kwargs):
        super(DropList, self).__init__(parent=parent, **kwargs)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('text/uri-list'):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('text/uri-list'):
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        # rawPath = event.mimeData().data('text/uri-list').__str__()
        rawPath = event.mimeData().text()
        path = rawPath.replace("file:///", "").splitlines()[0]
        # path = path.replace("\\r\\n'", "")
        self.dropped.emit(path)
