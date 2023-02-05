from tik_manager4.ui.widgets.value_widgets import List
from tik_manager4.ui.Qt import QtWidgets


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