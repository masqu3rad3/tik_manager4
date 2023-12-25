"""Dialog for settings."""

from pathlib import Path
import logging

from tik_manager4.core import settings
from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
from tik_manager4.ui.widgets import value_widgets
from tik_manager4.ui.widgets.switch_tree import SwitchTreeWidget, SwitchTreeItem
from tik_manager4.ui.widgets.common import (
    TikLabel,
    TikLabelButton,
    HeaderLabel,
    ResolvedText,
    TikButtonBox,
    TikButton,
    TikIconButton,
    VerticalSeparator
)
from tik_manager4.ui.layouts.settings_layout import (
    SettingsLayout,
    convert_to_ui_definition,
    guess_data_type,
)
from tik_manager4.ui.dialog.feedback import Feedback

LOG = logging.getLogger(__name__)


class SettingsDialog(QtWidgets.QDialog):
    """Settings dialog."""

    def __init__(self, main_object, *args, **kwargs):
        super(SettingsDialog, self).__init__(*args, **kwargs)

        self.main_object = main_object

        self.settings_list = []  # list of settings objects

        self.setWindowTitle("Settings")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        # variables
        self.splitter = None
        self.left_vlay = None
        self.right_contents_lay = None
        self.button_box_lay = None
        self.menu_tree_widget = None
        self._validations_and_extracts = (
            None  # for caching the validations and extracts
        )
        self._setting_widgets = []

        # Execution
        self.build_layouts()
        self.build_static_widgets()
        self.create_content()
        # self.create_widgets()

        self.resize(960, 630)

        self.splitter.setSizes([250, 750])

    def build_layouts(self):
        """Build layouts."""

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.splitter = QtWidgets.QSplitter(self)

        left_widget = QtWidgets.QWidget(self.splitter)
        self.left_vlay = QtWidgets.QVBoxLayout(left_widget)
        self.left_vlay.setContentsMargins(0, 0, 0, 0)

        right_widget = QtWidgets.QWidget(self.splitter)
        self.right_vlayout = QtWidgets.QVBoxLayout(right_widget)
        self.right_vlayout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(self.splitter)

        self.button_box_lay = QtWidgets.QHBoxLayout()
        main_layout.addLayout(self.button_box_lay)

    def build_static_widgets(self):
        """Build static widgets."""
        # self.menu_tree_widget = QtWidgets.QTreeWidget()
        self.menu_tree_widget = SwitchTreeWidget()
        self.menu_tree_widget.setRootIsDecorated(True)
        self.menu_tree_widget.setHeaderHidden(True)
        self.menu_tree_widget.header().setVisible(False)
        self.left_vlay.addWidget(self.menu_tree_widget)

        tik_button_box = TikButtonBox(parent=self)
        self.button_box_lay.addWidget(tik_button_box)
        self.apply_button = tik_button_box.addButton("Apply", tik_button_box.ApplyRole)
        self.apply_button.setEnabled(False)
        cancel_button = tik_button_box.addButton("Cancel", tik_button_box.RejectRole)
        ok_button = tik_button_box.addButton("Ok", tik_button_box.AcceptRole)

        # SIGNALS
        self.apply_button.clicked.connect(self.apply_settings)
        cancel_button.clicked.connect(self.close)
        ok_button.clicked.connect(lambda: self.apply_settings(close_dialog=True))

        self.button_box_lay.addWidget(tik_button_box)

    def create_content(self):
        """Create the content."""
        self.menu_tree_widget.clear()
        self._user_settings()
        self._project_settings()
        self._common_settings()

        self.__create_content_links()

    def _user_settings(self):
        """Create the user settings."""
        # create the menu items
        self.user_widget_item = SwitchTreeItem(["User"])
        self.menu_tree_widget.addTopLevelItem(self.user_widget_item)

        # create sub-branches

    def _project_settings(self):
        """Create the project settings."""
        # create the menu items
        self.project_widget_item = SwitchTreeItem(["Project"])
        self.menu_tree_widget.addTopLevelItem(self.project_widget_item)

        # create sub-branches
        preview_settings = SwitchTreeItem(["Preview Settings"])
        self.project_widget_item.addChild(preview_settings)
        preview_settings.content = self.preview_settings_content()

        category_definitions = SwitchTreeItem(["Category Definitions"])
        self.project_widget_item.addChild(category_definitions)
        category_definitions.content = self.project_category_definitions_content()

        metadata = SwitchTreeItem(["Metadata"])
        self.project_widget_item.addChild(metadata)
        metadata.content = self.metadata_content()

        # self.__project_settings_contents()

    def _common_settings(self):
        """Create the common settings."""
        # create the menu items
        common_widget_item = SwitchTreeItem(["Common"])
        self.menu_tree_widget.addTopLevelItem(common_widget_item)

        # create sub-branches
        category_definitions = QtWidgets.QTreeWidgetItem(
            ["Category Definitions (Common)"]
        )
        common_widget_item.addChild(category_definitions)
        category_definitions.content = self.common_category_definitions_content()

        metadata = QtWidgets.QTreeWidgetItem(["Metadata (Common)"])
        common_widget_item.addChild(metadata)
        metadata.content = self.common_metadata_content()


    def __create_content_links(self):
        """Create content widgets for all top level items."""
        # collect all root items
        _root_items = [
            self.menu_tree_widget.topLevelItem(x)
            for x in range(self.menu_tree_widget.topLevelItemCount())
        ]

        for _root_item in _root_items:
            # create a content widget
            _content_widget = QtWidgets.QWidget()
            _content_widget.setVisible(False)
            _content_layout = QtWidgets.QVBoxLayout(_content_widget)

            # get all children of the root item
            _children = [_root_item.child(x) for x in range(_root_item.childCount())]
            for _child in _children:
                # create a QCommandLinkButton for each child
                _button = QtWidgets.QCommandLinkButton(_child.text(0))
                _button.clicked.connect(
                    lambda _, x=_child: self.menu_tree_widget.setCurrentItem(x)
                )
                _content_layout.addWidget(_button)

            _content_layout.addStretch()

            self.right_vlayout.addWidget(_content_widget)

            # add it to the item
            _root_item.content = _content_widget

    def _gather_validations_and_extracts(self):
        """Collect the available validations and extracts."""
        if self._validations_and_extracts:
            return self._validations_and_extracts
        # we cannot simply rely on the collected validators and extractors due to it will
        # differ from Dcc to Dcc. So we need to collect them from the directories.
        # This method is not the best way to do it but it is the most reliable way.
        validations = []
        extracts = []
        # get the location of the file
        _file_path = Path(__file__)
        # go to the tik_manager4 installation folder from  /tik_manager4/ui/dialog/settings_dialog.py
        _tik_manager4_path = _file_path.parents[2]
        # DCC folder
        _dcc_folder = _tik_manager4_path / "dcc"
        # collect all 'extract' and 'validate' folders under _dcc_folder recursively
        _extract_folders = list(_dcc_folder.glob("**/extract"))
        _validate_folders = list(_dcc_folder.glob("**/validate"))
        # Path(_search_dir).rglob("**/*.twork")

        # collect all extractors
        for _extract_folder in _extract_folders:
            extracts = list(
                {
                    x.stem
                    for x in _extract_folder.glob("*.py")
                    if not x.stem.startswith("_")
                }
            )

        for _validate_folder in _validate_folders:
            validations = list(
                {
                    x.stem
                    for x in _validate_folder.glob("*.py")
                    if not x.stem.startswith("_")
                }
            )
        self._validations_and_extracts = {
            "validations": validations,
            "extracts": extracts,
        }
        return self._validations_and_extracts

    def preview_settings_content(self):
        """Create the content for preview settings."""
        LOG.warning("Preview settings are not implemented yet.")
        return QtWidgets.QWidget()

    def project_category_definitions_content(self):
        """Create the project category definitions."""

        settings_data = self.main_object.project.guard.category_definitions
        availability_dict = self._gather_validations_and_extracts()
        self.settings_list.append(settings_data)

        project_category_definitions_widget = CategoryDefinitions(
            settings_data,
            availability_dict,
            title="Category Definitions (Project)",
            parent=self,
        )

        # hide by default
        project_category_definitions_widget.setVisible(False)
        self.right_vlayout.addWidget(project_category_definitions_widget)

        # SIGNALS
        project_category_definitions_widget.modified.connect(self.check_changes)
        return project_category_definitions_widget

    def metadata_content(self):
        """Create the metadata content."""
        settings_data = self.main_object.project.metadata_definitions
        # add it to the global settings list so it can be checked globally.
        self.settings_list.append(settings_data)

        metadata_widget = MetadataDefinitions(
            settings_data, title="Metadata Definitions", parent=self
        )
        metadata_widget.setVisible(False)
        self.right_vlayout.addWidget(metadata_widget)

        # SIGNALS
        metadata_widget.modified.connect(self.check_changes)
        return metadata_widget

    def common_metadata_content(self):
        """Create the common metadata content."""
        settings_data = self.main_object.user.commons.metadata
        # add it to the global settings list so it can be checked globally.
        self.settings_list.append(settings_data)

        common_metadata_widget = MetadataDefinitions(
            settings_data, title="Metadata Definitions (Common)", parent=self
        )
        common_metadata_widget.setVisible(False)
        self.right_vlayout.addWidget(common_metadata_widget)

        # SIGNALS
        common_metadata_widget.modified.connect(self.check_changes)
        return common_metadata_widget

    def common_category_definitions_content(self):
        """Create the common category definitions."""
        settings_data = self.main_object.user.commons.category_definitions
        availability_dict = self._gather_validations_and_extracts()
        self.settings_list.append(settings_data)

        common_category_definitions_widget = CategoryDefinitions(
            settings_data,
            availability_dict,
            title="Category Definitions (Common)",
            parent=self,
        )
        # self.right_contents_lay.addWidget(common_category_definitions_widget)
        common_category_definitions_widget.setVisible(False)
        self.right_vlayout.addWidget(common_category_definitions_widget)

        # SIGNALS
        common_category_definitions_widget.modified.connect(self.check_changes)
        return common_category_definitions_widget

    def apply_settings(self, close_dialog=False):
        """Apply the settings."""
        for settings_object in self.settings_list:
            settings_object.apply_settings()
            self.check_changes()
        if close_dialog:
            self.close()

    def check_changes(self):
        """Check if there are changes in the settings and enable the apply button."""

        for settings_object in self.settings_list:
            if settings_object.is_settings_changed():
                self.apply_button.setEnabled(True)
                return
        self.apply_button.setEnabled(False)


class CategoryDefinitions(QtWidgets.QWidget):
    """Widget for category definitions."""

    modified = QtCore.Signal(bool)

    def __init__(self, settings_data, availability_dict, title="", *args, **kwargs):
        super(CategoryDefinitions, self).__init__(*args, **kwargs)
        self.availability_dict = availability_dict
        self._definitions_layout = QtWidgets.QVBoxLayout(self)

        header_layout = QtWidgets.QVBoxLayout()
        header_layout.setSpacing(13)
        self._definitions_layout.addLayout(header_layout)

        # add the title
        title_label = HeaderLabel(title)
        header_layout.addWidget(title_label)

        # add a label to show the path of the settings file
        path_label = ResolvedText(settings_data.settings_file)
        header_layout.addWidget(path_label)

        header_layout.addWidget(VerticalSeparator(color=(255, 141, 28),height=1))

        # make a scroll area for the category definitions
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area_contents_widget = QtWidgets.QWidget()
        scroll_area_contents_widget.setGeometry(QtCore.QRect(0, 0, 104, 345))
        scroll_area.setWidget(scroll_area_contents_widget)
        self._definitions_layout.addWidget(scroll_area)
        self.scroll_layout = QtWidgets.QVBoxLayout(scroll_area_contents_widget)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)

        for category_key, data in settings_data.properties.items():
            self.add_category_definition(category_key, data)

        # add a separator line
        self._definitions_layout.addWidget(VerticalSeparator(color=(255, 141, 28),height=1))

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 5)
        self._definitions_layout.addLayout(button_layout)
        add_button = TikButton("Add New Definition", parent=self)
        add_button.set_color(background_color="#405040")
        button_layout.addWidget(add_button)

    def add_dialog(self):
        """Dialog to add a new category definition."""
        pass

    def _add_item(self, model, list_data, list_type):
        """Pops up a mini dialog to add the item to the list view."""
        # Make a dialog with a listwidget to select the ifem(s) to add
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Add Item")
        dialog_layout = QtWidgets.QVBoxLayout(dialog)
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
            dialog.accept()

        # if user clicks ok return the selected items
        button_box.accepted.connect(add)
        # button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        button_layout.addWidget(button_box)
        dialog_layout.addLayout(button_layout)
        dialog.show()

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

    def _reorder_items(self, validations_model, list_data):
        """Update the model with re-ordered items."""
        for idx, item in enumerate(validations_model.stringList()):
            list_data[idx] = item
        self.modified.emit(True)

    def delete_category_definition(self, name, data):
        """Removes the category definition from the layout and tags it as archived."""
        # delete the definition group object
        definition_group = self.findChild(QtWidgets.QGroupBox, f"{name}_group")
        definition_group.deleteLater()
        # delete the definition from the settings
        data["archived"] = True
        self.modified.emit(True)

    def add_category_definition(self, name, data):
        """Adds a new category definition to the layout."""

        if data.get("archived"):
            return

        definition_group = QtWidgets.QGroupBox(name)
        definition_group.setObjectName(f"{name}_group")
        #
        # make it bold and bigger
        title_font = definition_group.font()
        old_size = title_font.pointSize()
        title_font.setBold(True)
        title_font.setPointSize(12)
        definition_group.setFont(title_font)

        # intermediate widget to break the font inheritance
        intermediate_layout = QtWidgets.QVBoxLayout(definition_group)
        definition_group.setLayout(intermediate_layout)
        intermediate_widget = QtWidgets.QWidget(definition_group)
        intermediate_layout.addWidget(intermediate_widget)
        content_font = intermediate_widget.font()
        content_font.setPointSize(old_size)
        content_font.setBold(False)
        intermediate_widget.setFont(content_font)

        # self._definitions_layout.addWidget(definition_group)
        self.scroll_layout.addWidget(definition_group)
        # make it flat
        definition_group.setFlat(True)
        _group_layout = QtWidgets.QFormLayout()
        # definition_group.setLayout(_group_layout)
        intermediate_widget.setLayout(_group_layout)

        # add the name
        type_label = QtWidgets.QLabel("Type: ")
        type_combo = QtWidgets.QComboBox(self)
        type_combo.addItems(["asset", "shot", ""])

        # set the value by string
        type_combo.setCurrentText(data["type"])
        _group_layout.addRow(type_label, type_combo)

        # add the validations
        _validations_layout = QtWidgets.QHBoxLayout()
        validations_label = QtWidgets.QLabel("Validations: ")
        # create a standard model to hold and manipulate the data
        # validations_model = QtCore.QStringListModel()
        validations_model = ReorderListModel()
        validations_model.setStringList(data["validations"])
        validations_list = QtWidgets.QListView()
        # validations_list = ReorderListView()
        validations_list.setModel(validations_model)
        # # make the items in the list change order by drag and drop
        validations_list.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        # make it multi selection
        validations_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        _validations_layout.addWidget(validations_list)
        # add the buttons
        _validations_buttons_layout = QtWidgets.QVBoxLayout()
        _validations_layout.addLayout(_validations_buttons_layout)
        add_validation_button = TikIconButton(
            icon_name="plus", size=32, background_color="#405040", parent=self
        )
        _validations_buttons_layout.addWidget(add_validation_button)
        remove_validation_button = TikIconButton(
            icon_name="minus", size=32, parent=self, background_color="#504040"
        )

        _validations_buttons_layout.addWidget(remove_validation_button)

        _group_layout.addRow(validations_label, _validations_layout)

        # add extracts
        _extracts_layout = QtWidgets.QHBoxLayout()
        extracts_label = QtWidgets.QLabel("Extracts: ")
        # create a standard model to hold and manipulate the data
        extracts_model = QtCore.QStringListModel()
        extracts_model.setStringList(data["extracts"])
        extracts_list = QtWidgets.QListView()
        extracts_list.setModel(extracts_model)
        extracts_list.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

        _extracts_layout.addWidget(extracts_list)
        # add the buttons
        _extracts_buttons_layout = QtWidgets.QVBoxLayout()
        _extracts_layout.addLayout(_extracts_buttons_layout)
        add_extract_button = TikIconButton(
            icon_name="plus", size=32, background_color="#405040", parent=self
        )
        _extracts_buttons_layout.addWidget(add_extract_button)
        remove_extract_button = TikIconButton(
            icon_name="minus", size=32, parent=self, background_color="#504040"
        )
        _extracts_buttons_layout.addWidget(remove_extract_button)

        _group_layout.addRow(extracts_label, _extracts_layout)

        # add the delete button
        delete_button = TikButton("Delete Definition", parent=self)
        delete_button.set_color(background_color="#504040")
        intermediate_layout.addWidget(delete_button)

        # SIGNALS
        type_combo.currentTextChanged.connect(lambda text: data.update({"type": text}))
        # also emit the modified signal
        type_combo.currentTextChanged.connect(lambda text: self.modified.emit(True))
        # add_validation_button.clicked.connect(test_print)
        # When the user drops the item, update the underlying data
        validations_list.model().rowsMoved.connect(
            lambda _: self._reorder_items(validations_model, data["validations"])
        )
        remove_validation_button.clicked.connect(
            lambda: self._remove_item(
                validations_model, validations_list, data["validations"]
            )
        )
        add_validation_button.clicked.connect(
            lambda: self._add_item(
                validations_model, data["validations"], "validations"
            )
        )
        # add_extract_button.clicked.connect(test_print)
        extracts_list.model().rowsMoved.connect(
            lambda _: self._reorder_items(extracts_model, data["extracts"])
        )
        remove_extract_button.clicked.connect(
            lambda: self._remove_item(extracts_model, extracts_list, data["extracts"])
        )
        add_extract_button.clicked.connect(
            lambda: self._add_item(extracts_model, data["extracts"], "extracts")
        )

        delete_button.clicked.connect(
            lambda: self.delete_category_definition(name, data)
        )

        return definition_group


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

    def __init__(self, settings_data, title="", *args, **kwargs):
        super(MetadataDefinitions, self).__init__(*args, **kwargs)

        # variables
        self.title = title
        self.settings_data = settings_data

        self.build_layouts()
        self.build_static_widgets()
        self.build_value_widgets()

        self.splitter.setSizes([500, 500])

    def build_layouts(self):
        """Build the layouts."""
        main_layout = QtWidgets.QVBoxLayout(self)
        self.header_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(self.header_layout)

        self.splitter = QtWidgets.QSplitter(self)

        left_widget = QtWidgets.QWidget(self.splitter)
        self.left_vlay = QtWidgets.QVBoxLayout(left_widget)
        self.left_vlay.setContentsMargins(0, 0, 0, 0)

        right_widget = QtWidgets.QWidget(self.splitter)
        self.right_vlay = QtWidgets.QVBoxLayout(right_widget)
        self.right_vlay.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(self.splitter)

    def build_static_widgets(self):
        title_label = HeaderLabel(self.title)
        title_label.setMaximumHeight(30)
        self.header_layout.addWidget(title_label)

        # add a label to show the path of the settings file
        path_label = ResolvedText(self.settings_data.settings_file)
        path_label.setMaximumHeight(30)
        self.header_layout.addWidget(path_label)

        self.header_layout.addWidget(VerticalSeparator(color=(255, 141, 28),height=1))

        self.switch_tree_widget = SwitchTreeWidget()
        self.switch_tree_widget.setRootIsDecorated(False)
        self.switch_tree_widget.setHeaderHidden(True)
        self.switch_tree_widget.header().setVisible(False)
        self.left_vlay.addWidget(self.switch_tree_widget)

        # add 'add' and 'remove' buttons in a horizontal layout
        add_remove_buttons_layout = QtWidgets.QHBoxLayout()
        self.left_vlay.addLayout(add_remove_buttons_layout)
        add_metadata_button = TikButton(text="Add New Metadata", parent=self)
        add_remove_buttons_layout.addWidget(add_metadata_button)
        remove_metadata_button = TikButton(text="Delete Metadata", parent=self)
        add_remove_buttons_layout.addWidget(remove_metadata_button)

        # SIGNALS
        add_metadata_button.clicked.connect(self.add_metadata)
        remove_metadata_button.clicked.connect(self.remove_metadata)

    def add_metadata(self):
        """Pop up a dialog to add a new metadata."""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Add Metadata")
        dialog_layout = QtWidgets.QVBoxLayout(dialog)
        dialog.setLayout(dialog_layout)
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
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        # show the dialog
        dialog.show()
        # if user accepts the dialog, add the metadata
        if dialog.exec_():
            name = name_line_edit.text()
            data_type = type_combo.currentText()
            default_data = self._prepare_default_data(data_type)
            self.settings_data.add_property(name, default_data)
            self._add_value_widget(name, data=default_data)
            # emit the modified signal
            self.modified.emit(True)

    def _prepare_default_data(self, data_type):
        """Convenience method to prepare the default data for the given data type."""
        default_data = {}
        default_data["default"] = ""
        default_data["type"] = data_type
        if data_type == "boolean":
            default_data["default"]: bool = False
        elif data_type == "string":
            default_data["default"]: str =  ""
        elif data_type == "integer":
            default_data["default"]: int = 0
        elif data_type == "float":
            default_data["default"]: float = 0.0
        elif data_type == "vector2Int":
            default_data["default"]: list = [0, 0]
        elif data_type == "vector2Float":
            default_data["default"]: list = [0.0, 0.0]
        elif data_type == "vector3Int":
            default_data["default"]: list = [0, 0, 0]
        elif data_type == "vector3Float":
            default_data["default"]: list = [0.0, 0.0, 0.0]
        elif data_type == "combo":
            default_data["default"]: str = ""
        else:
            default_data["default"]: str = ""

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
        self.right_vlay.removeWidget(widget_item.content)
        widget_item.content = None

    def _add_value_widget(self, name, data):
        """Adds a new value widget to the layout."""
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

        # type label. We don't want to make it editable. Easier to delete the metadata and add a new one.
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
        self.right_vlay.addWidget(content_widget)
        widget_item.content = content_widget

    def build_value_widgets(self):
        """Build the widgets."""

        _valid_types = list(self.value_widgets.keys())
        for metadata_key, data in self.settings_data.properties.items():
            self._add_value_widget(metadata_key, data)
            # first create the widget item
            # widget_item = SwitchTreeItem([metadata_key])
            # self.switch_tree_widget.addTopLevelItem(widget_item)
            #
            # # create the content widget
            # content_widget = QtWidgets.QWidget()
            # content_layout = QtWidgets.QVBoxLayout()
            # # content_layout.setContentsMargins(0, 0, 0, 0)
            # # content_layout.setSpacing(0)
            # content_widget.setLayout(content_layout)
            #
            # # guess the data type from its default value
            # # if there is an enum list, that means it is a combo box
            # data_type = data.get("type", guess_data_type(data["default"]))
            #
            # # type combo
            # form_layout = QtWidgets.QFormLayout()
            # content_layout.addLayout(form_layout)
            #
            # type_label = QtWidgets.QLabel("Type: ")
            # type_combo = value_widgets.Combo(name="type", value=data_type, items=_valid_types)
            # form_layout.addRow(type_label, type_combo)
            # type_combo.currentTextChanged.connect(lambda text: data.update({"type": text}))
            # type_combo.currentTextChanged.connect(lambda text: self.modified.emit(True))
            #
            # # default value
            # default_value_label = QtWidgets.QLabel("Default Value: ")
            # default_value_widget = self.value_widgets[data_type](name="default_value", value=data["default"])
            # form_layout.addRow(default_value_label, default_value_widget)
            # default_value_widget.com.valueChanged.connect(lambda value: data.update({"default": value}))
            # default_value_widget.com.valueChanged.connect(lambda value: self.modified.emit(True))
            #
            # # create an additional list widget for combo items
            # if data_type == "combo":
            #     combo_items_label = QtWidgets.QLabel("Combo Items: ")
            #     combo_items_widget = value_widgets.List(name="enum", value=data["enum"])
            #     form_layout.addRow(combo_items_label, combo_items_widget)
            #     combo_items_widget.com.valueChanged.connect(lambda value: data.update({"enum": value}))
            #     combo_items_widget.com.valueChanged.connect(lambda value: self.modified.emit(True))
            #
            # content_widget.setVisible(False)
            # self.right_vlay.addWidget(content_widget)
            # widget_item.content = content_widget


class ReorderListModel(QtCore.QStringListModel):
    """Custom QStringListModel that disables the overwrite when reordering items by drag and drop."""

    def __init__(self, strings=None, parent=None):
        super().__init__(parent)
        if strings is not None:
            self.setStringList(strings)

    def flags(self, index):
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


# test the dialog
if __name__ == "__main__":
    import sys
    import tik_manager4
    from tik_manager4.ui import pick

    app = QtWidgets.QApplication(sys.argv)

    tik = tik_manager4.initialize("Standalone")
    _style_file = pick.style_file()

    dialog = SettingsDialog(tik, styleSheet=str(_style_file.readAll(), "utf-8"))
    # dialog = SettingsDialog(tik)
    dialog.show()
    sys.exit(app.exec_())
