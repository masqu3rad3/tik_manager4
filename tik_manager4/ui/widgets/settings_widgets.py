"""Convenince widgets for settings UI."""
from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
from tik_manager4.ui.widgets import value_widgets
from tik_manager4.ui.widgets.validated_string import ValidatedString
from tik_manager4.ui.dialog.feedback import Feedback
from tik_manager4.ui.dialog.data_containers import MainLayout
from tik_manager4.ui.widgets.common import (
    HeaderLabel,
    ResolvedText,
    TikButtonBox,
    TikButton,
    TikIconButton,
    HorizontalSeparator,
)

from tik_manager4.ui.layouts.settings_layout import (
guess_data_type
)

from tik_manager4.ui.dialog.user_dialog import NewUserDialog

from tik_manager4.ui.widgets.switch_tree import SwitchTreeWidget, SwitchTreeItem

class UsersDefinitions(QtWidgets.QWidget):
    """Widget for users definitions management."""

    value_widgets = {
        "combo": value_widgets.Combo,
        "string": value_widgets.String,
    }

    modified = QtCore.Signal(bool)

    def __init__(self, user_object, *args, title="", **kwargs):
        """Initiate the class."""
        super().__init__(*args, **kwargs)
        self.title = title
        self.user_object = user_object
        self.settings_data = user_object.commons.users
        self.feedback = Feedback(parent=self)
        self.layouts = MainLayout()
        self.switch_tree_widget = None
        self.build_layouts()
        self.build_static_widgets()
        self.build_value_widgets()
        self.layouts.splitter.setSizes([500, 500])

    def build_layouts(self):
        """Build the layouts."""
        self.layouts.master_layout = QtWidgets.QVBoxLayout(self)
        self.layouts.header_layout = QtWidgets.QVBoxLayout()
        self.layouts.master_layout.addLayout(self.layouts.header_layout)

        self.layouts.splitter = QtWidgets.QSplitter(self)

        left_widget = QtWidgets.QWidget(self.layouts.splitter)
        self.layouts.left_layout = QtWidgets.QVBoxLayout(left_widget)
        self.layouts.left_layout.setContentsMargins(0, 0, 0, 0)

        right_widget = QtWidgets.QWidget(self.layouts.splitter)
        self.layouts.right_layout = QtWidgets.QVBoxLayout(right_widget)
        self.layouts.right_layout.setContentsMargins(0, 0, 0, 0)

        self.layouts.master_layout.addWidget(self.layouts.splitter)

    def build_static_widgets(self):
        """Build static widgets."""
        title_label = HeaderLabel(self.title)
        self.layouts.header_layout.addWidget(title_label)

        # add a label to show the path of the settings file
        path_label = ResolvedText(self.settings_data.settings_file)
        path_label.setMaximumHeight(30)
        self.layouts.header_layout.addWidget(path_label)

        self.layouts.header_layout.addWidget(
            HorizontalSeparator(color=(255, 141, 28), height=1)
        )

        self.switch_tree_widget = SwitchTreeWidget()
        self.switch_tree_widget.setRootIsDecorated(False)
        self.switch_tree_widget.setHeaderHidden(True)
        self.switch_tree_widget.header().setVisible(False)
        self.layouts.left_layout.addWidget(self.switch_tree_widget)

        # add 'add' and 'remove' buttons in a horizontal layout
        add_remove_buttons_layout = QtWidgets.QHBoxLayout()
        self.layouts.left_layout.addLayout(add_remove_buttons_layout)
        add_metadata_button = TikButton(text="Add New User", parent=self)
        add_remove_buttons_layout.addWidget(add_metadata_button)
        remove_metadata_button = TikButton(text="Delete User", parent=self)
        add_remove_buttons_layout.addWidget(remove_metadata_button)

        # SIGNALS
        add_metadata_button.clicked.connect(self.add_user)
        remove_metadata_button.clicked.connect(self.remove_user)

    def reinit(self):
        """Reinitialize the widget."""
        self.switch_tree_widget.clear()
        self.build_value_widgets()

    def add_user(self):
        """Launch the add user dialog."""
        # refresh the switch tree widget
        dialog = NewUserDialog(self.user_object, parent=self)
        state = dialog.exec_()
        if state:
            self.reinit()

    def remove_user(self):
        """Remove the user from the database."""
        selected_item = self.switch_tree_widget.currentItem()
        if selected_item is None:
            return
        name = selected_item.text(0)
        are_you_sure = self.feedback.pop_question(
            title="Delete User",
            text=f"Are you sure you want to delete the user '{name}'? This action cannot be undone.",
            buttons=["yes", "cancel"],
        )
        if are_you_sure == "cancel":
            return

        result, msg = self.user_object.delete_user(name)
        if result == -1:
            self.feedback.pop_info(title="Cannot delete user", text=msg, critical=True)
            return
        self.reinit()

    def _delete_value_widget(self, widget_item):
        """Deletes the value widget and removes it from the layout."""
        widget_item.content.deleteLater()
        self.layouts.right_layout.removeWidget(widget_item.content)
        widget_item.content = None

    def _add_value_widget(self, name, data):
        """Add a new value widget to the layout."""
        # create the widget item
        widget_item = SwitchTreeItem([name])
        self.switch_tree_widget.addTopLevelItem(widget_item)

        # create the content widget
        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout()
        content_widget.setLayout(content_layout)

        form_layout = QtWidgets.QFormLayout()
        content_layout.addLayout(form_layout)
        # type label. We don't want to make it editable.
        # Easier to delete the metadata and add a new one.
        type_name = ResolvedText(data["initials"])
        form_layout.addRow("Initials: ", type_name)

        user_email = ValidatedString(name="user_email", value=data.get("email", ""), allow_special_characters=True)

        form_layout.addRow("Email: ", user_email)

        # Parse the value to the string
        permission_levels = ["Observer", "Generic", "Experienced", "Admin"]
        permission_as_string = permission_levels[data["permissionLevel"]]

        permission_widget = self.value_widgets["combo"](
            name="permissionLevel", value=permission_as_string, items=permission_levels
        )
        # if this is default Admin user, make it uneditable
        if name == "Admin":
            permission_widget.setEnabled(False)

        form_layout.addRow("Permission Level: ", permission_widget)
        permission_widget.currentIndexChanged.connect(
            lambda value: data.update({"permissionLevel": value})
        )
        permission_widget.com.valueChanged.connect(
            lambda value: self.modified.emit(True)
        )

        # user_email.com.valueChanged.connect(lambda value: self.modified.emit(True))
        user_email.textChanged.connect(lambda value: data.update({"email": value}))
        user_email.com.valueChanged.connect(lambda value: self.modified.emit(True))

        content_widget.setVisible(False)
        self.layouts.right_layout.addWidget(content_widget)
        widget_item.content = content_widget

    def build_value_widgets(self):
        """Build the widgets."""

        for metadata_key, data in self.settings_data.properties.items():
            self._add_value_widget(metadata_key, data)

class MetadataDefinitions(QtWidgets.QWidget):
    """Widget for metadata definitions management."""

    value_widgets = {
        "boolean": value_widgets.Boolean,
        "string": value_widgets.String,
        "integer": value_widgets.Integer,
        "float": value_widgets.Float,
        "vector2Int": value_widgets.Vector2Int,
        "vector2Float": value_widgets.Vector2Float,
        "vector3Int": value_widgets.Vector3Int,
        "vector3Float": value_widgets.Vector3Float,
        "combo": value_widgets.Combo,
    }

    modified = QtCore.Signal(bool)

    def __init__(self, settings_data, *args, title="", **kwargs):
        super().__init__(*args, **kwargs)

        # variables
        self.title = title
        self.settings_data = settings_data

        self.layouts = MainLayout()
        self.switch_tree_widget = None

        self.build_layouts()
        self.build_static_widgets()
        self.build_value_widgets()

        self.layouts.splitter.setSizes([500, 500])

    def build_layouts(self):
        """Build the layouts."""
        self.layouts.master_layout = QtWidgets.QVBoxLayout(self)
        self.layouts.header_layout = QtWidgets.QVBoxLayout()
        self.layouts.master_layout.addLayout(self.layouts.header_layout)

        self.layouts.splitter = QtWidgets.QSplitter(self)

        left_widget = QtWidgets.QWidget(self.layouts.splitter)
        self.layouts.left_layout = QtWidgets.QVBoxLayout(left_widget)
        self.layouts.left_layout.setContentsMargins(0, 0, 0, 0)

        right_widget = QtWidgets.QWidget(self.layouts.splitter)
        self.layouts.right_layout = QtWidgets.QVBoxLayout(right_widget)
        self.layouts.right_layout.setContentsMargins(0, 0, 0, 0)

        self.layouts.master_layout.addWidget(self.layouts.splitter)

    def build_static_widgets(self):
        """Build static widgets."""
        title_label = HeaderLabel(self.title)
        self.layouts.header_layout.addWidget(title_label)

        # add a label to show the path of the settings file
        path_label = ResolvedText(self.settings_data.settings_file)
        path_label.setMaximumHeight(30)
        self.layouts.header_layout.addWidget(path_label)

        self.layouts.header_layout.addWidget(
            HorizontalSeparator(color=(255, 141, 28), height=1)
        )

        self.switch_tree_widget = SwitchTreeWidget()
        self.switch_tree_widget.setRootIsDecorated(False)
        self.switch_tree_widget.setHeaderHidden(True)
        self.switch_tree_widget.header().setVisible(False)
        self.layouts.left_layout.addWidget(self.switch_tree_widget)

        # add 'add' and 'remove' buttons in a horizontal layout
        add_remove_buttons_layout = QtWidgets.QHBoxLayout()
        self.layouts.left_layout.addLayout(add_remove_buttons_layout)
        add_metadata_button = TikButton(text="Add New Metadata", parent=self)
        add_remove_buttons_layout.addWidget(add_metadata_button)
        remove_metadata_button = TikButton(text="Delete Metadata", parent=self)
        add_remove_buttons_layout.addWidget(remove_metadata_button)

        # SIGNALS
        add_metadata_button.clicked.connect(self.add_metadata)
        remove_metadata_button.clicked.connect(self.remove_metadata)

    def add_metadata(self):
        """Pop up a dialog to add a new metadata."""
        _dialog = QtWidgets.QDialog(self)
        _dialog.setWindowTitle("Add Metadata")
        dialog_layout = QtWidgets.QVBoxLayout(_dialog)
        _dialog.setLayout(dialog_layout)
        # create a combo box to select the type
        type_combo = QtWidgets.QComboBox(self)
        type_combo.addItems(list(self.value_widgets.keys()))
        dialog_layout.addWidget(type_combo)
        # create a line edit to enter the name
        name_line_edit = QtWidgets.QLineEdit(self)
        dialog_layout.addWidget(name_line_edit)
        # create a button box
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        dialog_layout.addWidget(button_box)
        # if user clicks ok return the selected items
        button_box.accepted.connect(_dialog.accept)
        button_box.rejected.connect(_dialog.reject)
        # show the dialog
        _dialog.show()
        # if user accepts the dialog, add the metadata
        if _dialog.exec_():
            name = name_line_edit.text()
            data_type = type_combo.currentText()
            default_data = self._prepare_default_data(data_type)
            self.settings_data.add_property(name, default_data)
            self._add_value_widget(name, data=default_data)
            # emit the modified signal
            self.modified.emit(True)

    @staticmethod
    def _prepare_default_data(data_type):
        """Convenience method to prepare the default data for the given data type."""

        if data_type == "boolean":
            _default_object_type: bool = False
        elif data_type == "string":
            _default_object_type: str = ""
        elif data_type == "integer":
            _default_object_type: int = 0
        elif data_type == "float":
            _default_object_type: float = 0.0
        elif data_type == "vector2Int":
            _default_object_type: list = [0, 0]
        elif data_type == "vector2Float":
            _default_object_type: list = [0.0, 0.0]
        elif data_type == "vector3Int":
            _default_object_type: list = [0, 0, 0]
        elif data_type == "vector3Float":
            _default_object_type: list = [0.0, 0.0, 0.0]
        elif data_type == "combo":
            _default_object_type: str = ""
        else:
            _default_object_type: str = ""
        default_data = {"default": _default_object_type, "type": data_type}
        # enum lists are only for combo boxes
        if data_type == "combo":
            default_data["enum"] = []
        return default_data

    def remove_metadata(self):
        """Removes the selected metadata from the layout."""
        # get the selected item
        selected_item = self.switch_tree_widget.currentItem()
        if selected_item is None:
            return
        # get the name of the metadata
        name = selected_item.text(0)
        # delete it from the tree widget
        self.switch_tree_widget.takeTopLevelItem(
            self.switch_tree_widget.indexOfTopLevelItem(selected_item)
        )
        # delete the value widget
        self._delete_value_widget(selected_item)
        # delete the metadata from the settings
        self.settings_data.delete_property(name)
        # emit the modified signal
        self.modified.emit(True)

    def _delete_value_widget(self, widget_item):
        """Deletes the value widget and removes it from the layout."""
        widget_item.content.deleteLater()
        self.layouts.right_layout.removeWidget(widget_item.content)
        widget_item.content = None

    def _add_value_widget(self, name, data):
        """Add a new value widget to the layout."""
        # create the widget item
        widget_item = SwitchTreeItem([name])
        self.switch_tree_widget.addTopLevelItem(widget_item)

        # create the content widget
        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout()
        content_widget.setLayout(content_layout)

        # guess the data type from its default value
        # if there is an enum list, that means it is a combo box
        data_type = data.get("type", guess_data_type(data["default"]))

        form_layout = QtWidgets.QFormLayout()
        content_layout.addLayout(form_layout)
        # type label. We don't want to make it editable.
        # Easier to delete the metadata and add a new one.
        type_label = QtWidgets.QLabel("Type: ")
        type_name = ResolvedText(data_type)
        form_layout.addRow(type_label, type_name)

        # default value
        default_value_label = QtWidgets.QLabel("Default Value: ")
        default_value_widget = self.value_widgets[data_type](
            name="default_value", value=data["default"]
        )
        form_layout.addRow(default_value_label, default_value_widget)
        default_value_widget.com.valueChanged.connect(
            lambda value: data.update({"default": value})
        )
        default_value_widget.com.valueChanged.connect(
            lambda value: self.modified.emit(True)
        )

        # create an additional list widget for combo items
        if data_type == "combo":
            combo_items_label = QtWidgets.QLabel("Combo Items: ")
            combo_items_widget = value_widgets.List(name="enum", value=data["enum"])
            default_value_widget.addItems(data["enum"])
            default_value_widget.setCurrentText(data["default"])
            form_layout.addRow(combo_items_label, combo_items_widget)
            combo_items_widget.com.valueChanged.connect(
                lambda value: data.update({"enum": value})
            )
            combo_items_widget.com.valueChanged.connect(
                lambda value: self.modified.emit(True)
            )

        content_widget.setVisible(False)
        self.layouts.right_layout.addWidget(content_widget)
        widget_item.content = content_widget

    def build_value_widgets(self):
        """Build the widgets."""

        for metadata_key, data in self.settings_data.properties.items():
            self._add_value_widget(metadata_key, data)

class CategoryDefinitions(QtWidgets.QWidget):
    """Widget for category definitions management."""

    modified = QtCore.Signal(bool)

    def __init__(self, settings_data, availability_dict, *args, title="", **kwargs):
        """Initiate the class."""
        super().__init__(*args, **kwargs)
        self.availability_dict = availability_dict

        self.title = title
        self.settings_data = settings_data

        self.layouts = MainLayout()

        self.switch_tree_widget = None

        self.build_layouts()
        self.build_static_widgets()
        self.build_value_widgets()

        self.layouts.splitter.setSizes([500, 500])

    def build_layouts(self):
        """Build the layouts."""
        self.layouts.master_layout = QtWidgets.QVBoxLayout(self)
        self.layouts.header_layout = QtWidgets.QVBoxLayout()
        self.layouts.master_layout.addLayout(self.layouts.header_layout)

        self.layouts.splitter = QtWidgets.QSplitter(self)

        left_widget = QtWidgets.QWidget(self.layouts.splitter)
        self.layouts.left_layout = QtWidgets.QVBoxLayout(left_widget)
        self.layouts.left_layout.setContentsMargins(0, 0, 0, 0)

        right_widget = QtWidgets.QWidget(self.layouts.splitter)
        self.layouts.right_layout = QtWidgets.QVBoxLayout(right_widget)
        self.layouts.right_layout.setContentsMargins(0, 0, 0, 0)

        self.layouts.master_layout.addWidget(self.layouts.splitter)

    def build_static_widgets(self):
        """Build static widgets."""
        title_label = HeaderLabel(self.title)
        # title_label.setMaximumHeight(30)
        self.layouts.header_layout.addWidget(title_label)

        # add a label to show the path of the settings file
        path_label = ResolvedText(self.settings_data.settings_file)
        path_label.setMaximumHeight(30)
        self.layouts.header_layout.addWidget(path_label)

        self.layouts.header_layout.addWidget(
            HorizontalSeparator(color=(255, 141, 28), height=1)
        )

        self.switch_tree_widget = SwitchTreeWidget()
        self.switch_tree_widget.setRootIsDecorated(False)
        self.switch_tree_widget.setHeaderHidden(True)
        self.switch_tree_widget.header().setVisible(False)
        self.layouts.left_layout.addWidget(self.switch_tree_widget)

        # add 'add' and 'remove' buttons in a horizontal layout
        add_remove_buttons_layout = QtWidgets.QHBoxLayout()
        self.layouts.left_layout.addLayout(add_remove_buttons_layout)
        add_category_pb = TikButton(text="Add New Category", parent=self)
        add_remove_buttons_layout.addWidget(add_category_pb)
        delete_category_pb = TikButton(text="Delete Category", parent=self)
        add_remove_buttons_layout.addWidget(delete_category_pb)

        # SIGNALS
        add_category_pb.clicked.connect(self.add_category)
        delete_category_pb.clicked.connect(self.delete_category)

    def add_category(self):
        """Pop up a dialog to add a new category."""

        def _add_category_item():
            name = name_line_edit.text()
            if name in self.settings_data.properties:
                if self.settings_data.get_property(name).get("archived", False):
                    self.settings_data.edit_sub_property((name, "archived"), False)
                    self._add_value_widget(
                        name, data=self.settings_data.get_property(name)
                    )
                    # emit the modified signal
                    self.modified.emit(True)
                    add_category_dialog.close()
                    return
                QtWidgets.QMessageBox.warning(
                    self,
                    "Warning",
                    f"Category with the name '{name}' already exists.",
                )
                return
            default_data = {
                "type": "",
                "validations": [],
                "extracts": [],
            }
            self.settings_data.add_property(name, default_data)
            self._add_value_widget(name, data=default_data)
            # emit the modified signal
            self.modified.emit(True)
            add_category_dialog.close()

        add_category_dialog = QtWidgets.QDialog(self)
        add_category_dialog.setWindowTitle("Add Category")
        dialog_layout = QtWidgets.QVBoxLayout(add_category_dialog)
        add_category_dialog.setLayout(dialog_layout)
        # create a line edit to enter the name
        horizontal_layout = QtWidgets.QHBoxLayout()
        dialog_layout.addLayout(horizontal_layout)
        name_label = QtWidgets.QLabel("Name: ")
        name_line_edit = ValidatedString("name")
        name_line_edit.allow_spaces = False
        name_line_edit.allow_special_characters = False
        name_line_edit.allow_empty = False
        horizontal_layout.addWidget(name_label)
        horizontal_layout.addWidget(name_line_edit)
        # create a button box
        button_box = TikButtonBox()
        add_category_pb = button_box.addButton(
            "Add", QtWidgets.QDialogButtonBox.AcceptRole
        )
        name_line_edit.set_connected_widgets(add_category_pb)
        _cancel_pb = button_box.addButton(
            "Cancel", QtWidgets.QDialogButtonBox.RejectRole
        )
        dialog_layout.addWidget(button_box)
        # if user clicks ok return the selected items
        # button_box.accepted.connect(add_category_dialog.accept)
        add_category_pb.clicked.connect(_add_category_item)
        button_box.rejected.connect(add_category_dialog.reject)
        # show the dialog
        add_category_dialog.show()

    def delete_category(self):
        """Removes the selected category from the layout."""
        # get the selected item
        selected_item = self.switch_tree_widget.currentItem()
        if selected_item is None:
            return
        # get the name of the metadata
        category_name = selected_item.text(0)
        # delete it from the tree widget
        self.switch_tree_widget.takeTopLevelItem(
            self.switch_tree_widget.indexOfTopLevelItem(selected_item)
        )
        # delete the value widget
        self._delete_value_widget(selected_item)
        # ARCHIVE the category in settings data
        self.settings_data.edit_sub_property((category_name, "archived"), True)
        # emit the modified signal
        self.modified.emit(True)

    def _delete_value_widget(self, widget_item):
        """Deletes the value widget and removes it from the layout."""
        widget_item.content.deleteLater()
        self.layouts.right_layout.removeWidget(widget_item.content)
        widget_item.content = None

    def _add_value_widget(self, name, data):
        """Adds a new value widget to the layout."""

        # if it is archived, skip it.
        if data.get("archived"):
            return

        widget_item = SwitchTreeItem([name])
        self.switch_tree_widget.addTopLevelItem(widget_item)

        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout()
        content_widget.setLayout(content_layout)

        form_layout = QtWidgets.QFormLayout()
        content_layout.addLayout(form_layout)

        # add type, validations and extracts
        self.__add_info(form_layout)
        self.__add_type(form_layout, data)
        self.__add_validations(form_layout, data)
        self.__add_extracts(form_layout, data)

        # link the content widget to the item for visibility switching
        content_widget.setVisible(False)
        self.layouts.right_layout.addWidget(content_widget)
        widget_item.content = content_widget

    def _remove_item(self, validations_model, validations_list, list_data):
        """Removes the selected item from the list view."""
        # validations_model.removeRow(validations_list.currentIndex().row())
        selected_index = validations_list.currentIndex().row()
        if selected_index == -1:
            return
        # sorting and reversing the indexes to avoid index errors
        for index in reversed(sorted(validations_list.selectedIndexes())):
            selected_index = index.row()
            # Remove the item from the underlying data
            list_data.pop(selected_index)
            # Update the model
            validations_model.removeRow(selected_index)
            self.modified.emit(True)

    def _add_item(self, model, list_data, list_type):
        """Pops up a mini dialog to add the item to the list view."""
        # Make a dialog with a listwidget to select the ifem(s) to add
        add_item_dialog = QtWidgets.QDialog(self)
        add_item_dialog.setWindowTitle("Add Item")
        dialog_layout = QtWidgets.QVBoxLayout(add_item_dialog)
        list_widget = QtWidgets.QListWidget()
        available_items = [
            x for x in self.availability_dict[list_type] if x not in list_data
        ]
        list_widget.addItems(available_items)
        # make it multi selection
        list_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        dialog_layout.addWidget(list_widget)
        button_layout = QtWidgets.QHBoxLayout()
        # create the buttons with button box
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )

        def add():
            for item in list_widget.selectedItems():
                model.insertRow(model.rowCount())
                model.setData(model.index(model.rowCount() - 1), item.text())
                list_data.append(item.text())
                self.modified.emit(True)
            add_item_dialog.accept()

        # if user clicks ok return the selected items
        button_box.accepted.connect(add)
        button_box.rejected.connect(add_item_dialog.reject)
        button_layout.addWidget(button_box)
        dialog_layout.addLayout(button_layout)
        add_item_dialog.show()

    def _reorder_items(self, validations_model, list_data):
        """Update the model with re-ordered items."""
        for idx, item in enumerate(validations_model.stringList()):
            list_data[idx] = item
        self.modified.emit(True)

    def build_value_widgets(self):
        """Build the widgets."""
        # _valid_types = list(self.value_widgets.keys())
        for metadata_key, data in self.settings_data.properties.items():
            self._add_value_widget(metadata_key, data)

    def __add_info(self, form_layout):
        """Add the info label."""

        info_label = QtWidgets.QLabel(
            "Validations and extracts available for lists are sourced from all DCC folders.\n" 
            "Therefore, some DCCs may not include certain items. "
            "Right-click items to see the DCC availability.\n"
        )
        # wrap the text
        info_label.setWordWrap(True)
        form_layout.addRow(info_label)

    def __add_type(self, form_layout, data):
        """Convenience method for adding a type widget."""
        type_label = QtWidgets.QLabel("Type: ")
        type_combo = value_widgets.Combo(name="type", value=data["type"])
        type_combo.setToolTip(
            "Type of the category. "
            "This value defines if the category belongs to an asset or shot mode. "
            "If left empty, it will be available in all modes."
        )
        type_combo.addItems(["asset", "shot", ""])
        type_combo.setCurrentText(data["type"])

        form_layout.addRow(type_label, type_combo)

        # SIGNALS
        type_combo.com.valueChanged.connect(lambda value: data.update({"type": value}))
        type_combo.com.valueChanged.connect(lambda value: self.modified.emit(True))

    def __add_validations(self, form_layout, data):
        """Convenience method for adding validations view."""
        validations_layout = QtWidgets.QHBoxLayout()
        validations_label = QtWidgets.QLabel("Validations: ")
        validations_list = ReorderListView(list_data=data["validations"], dcc_availability=self.availability_dict["dcc_validations"])

        validations_layout.addWidget(validations_list)
        # add the buttons
        validations_buttons_layout = QtWidgets.QVBoxLayout()
        validations_layout.addLayout(validations_buttons_layout)
        add_validation_button = TikIconButton(
            icon_name="plus", size=32, background_color="#405040", parent=self
        )
        validations_buttons_layout.addWidget(add_validation_button)
        remove_validation_button = TikIconButton(
            icon_name="minus", size=32, parent=self, background_color="#504040"
        )

        validations_buttons_layout.addWidget(remove_validation_button)

        form_layout.addRow(validations_label, validations_layout)

        # SIGNALS
        validations_list.model.rowsMoved.connect(
            lambda _: self._reorder_items(validations_list.model, data["validations"])
        )
        remove_validation_button.clicked.connect(
            lambda: self._remove_item(
                validations_list.model, validations_list, data["validations"]
            )
        )
        add_validation_button.clicked.connect(
            lambda: self._add_item(
                validations_list.model, data["validations"], "validations"
            )
        )

    def __add_extracts(self, form_layout, data):
        """Convenience method to add extracts view."""
        extracts_layout = QtWidgets.QHBoxLayout()
        extracts_label = QtWidgets.QLabel("Extracts: ")

        extracts_list = ReorderListView(list_data=data["extracts"], dcc_availability=self.availability_dict["dcc_extracts"])


        extracts_layout.addWidget(extracts_list)
        # add the buttons
        extracts_buttons_layout = QtWidgets.QVBoxLayout()
        extracts_layout.addLayout(extracts_buttons_layout)
        add_extract_button = TikIconButton(
            icon_name="plus", size=32, background_color="#405040", parent=self
        )
        extracts_buttons_layout.addWidget(add_extract_button)
        remove_extract_button = TikIconButton(
            icon_name="minus", size=32, parent=self, background_color="#504040"
        )
        extracts_buttons_layout.addWidget(remove_extract_button)

        form_layout.addRow(extracts_label, extracts_layout)

        # SIGNALS
        # extracts_list.model().rowsMoved.connect(
        extracts_list.model.rowsMoved.connect(
            lambda _: self._reorder_items(extracts_list.model, data["extracts"])
        )
        remove_extract_button.clicked.connect(
            lambda: self._remove_item(extracts_list.model, extracts_list, data["extracts"])
        )
        add_extract_button.clicked.connect(
            lambda: self._add_item(extracts_list.model, data["extracts"], "extracts")
        )

class ReorderListModel(QtCore.QStringListModel):
    """Custom QStringListModel that disables the overwrite
    when reordering items by drag and drop.
    """

    # pylint: disable=too-few-public-methods
    def __init__(self, strings=None, parent=None):
        super().__init__(parent)
        if strings is not None:
            self.setStringList(strings)

    def flags(self, index):
        """Override the flags method to disable the overwrite."""
        if index.isValid():
            return (
                QtCore.Qt.ItemIsSelectable
                | QtCore.Qt.ItemIsDragEnabled
                | QtCore.Qt.ItemIsEnabled
            )
        return (
            QtCore.Qt.ItemIsSelectable
            | QtCore.Qt.ItemIsDragEnabled
            | QtCore.Qt.ItemIsDropEnabled
            | QtCore.Qt.ItemIsEnabled
        )

    # show a custom hint when hovered over the item
    def data(self, index, role):
        """Override the data method to show a custom hint."""
        if role == QtCore.Qt.ToolTipRole:
            return f"Drag and drop to reorder the item."
        return super().data(index, role)

class ReorderListView(QtWidgets.QListView):
    """Custom QListView that disables the overwrite
    when reordering items by drag and drop.
    """

    def __init__(self, list_data = None, dcc_availability=None, parent=None):
        """Initialize the class.

        Args:
            list_data: List of strings to populate the list view.
            dcc_availability: Dictionary containing the availability of the
                items in the list for each DCC.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.model = ReorderListModel()
        if list_data:
            self.set_data(list_data)
        self.setModel(self.model)

        self.dcc_availability = dcc_availability or {}

        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.right_click_menu)

    def set_data(self, list_data):
        self.model.setStringList(list_data)
        # self.setModel(self.model)

    def right_click_menu(self, position):
        item = self.indexAt(position)
        if not item.isValid():
            return
        item_name = item.data()
        collected = [dcc for dcc, supported_items in
                     self.dcc_availability.items() if
                     item_name in supported_items]

        if not collected:
            return

        tooltip_text = "Available in:\n-------------\n" + "\n".join(collected)
        QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), tooltip_text)