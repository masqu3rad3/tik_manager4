"""Dialog for settings."""

from pathlib import Path
import logging

from tik_manager4.core import settings
from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
from tik_manager4.ui.widgets import value_widgets
from tik_manager4.ui.widgets.common import (
    TikLabel,
    TikLabelButton,
    HeaderLabel,
    ResolvedText,
    TikButtonBox,
    TikButton,
    TikIconButton,
)
from tik_manager4.ui.layouts.settings_layout import (
    SettingsLayout,
    convert_to_ui_definition,
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

        self.build_layouts()
        self.create_widgets()

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
        # right_scroll_area = QtWidgets.QScrollArea(right_widget)
        # right_scroll_area.setWidgetResizable(True)
        # right_scroll_area_contents_widget = QtWidgets.QWidget()
        # right_scroll_area_contents_widget.setGeometry(QtCore.QRect(0, 0, 104, 345))

        # self.right_contents_lay = QtWidgets.QVBoxLayout(
        #     right_scroll_area_contents_widget
        # )

        # right_scroll_area.setWidget(right_scroll_area_contents_widget)
        # self.right_vlayout.addWidget(right_scroll_area)

        main_layout.addWidget(self.splitter)

        self.button_box_lay = QtWidgets.QHBoxLayout()
        main_layout.addLayout(self.button_box_lay)

    def create_setting_categories(self):
        """Create the setting categories."""
        self.menu_tree_widget = QtWidgets.QTreeWidget()
        self.menu_tree_widget.setRootIsDecorated(True)
        self.menu_tree_widget.setHeaderHidden(True)
        self.menu_tree_widget.header().setVisible(False)
        self.left_vlay.addWidget(self.menu_tree_widget)

        # first create the Top Level categories which are 'User', 'Project' and 'Common'.
        self.menu_tree_widget.clear()
        user_widget_item = QtWidgets.QTreeWidgetItem(["User"])
        self.menu_tree_widget.addTopLevelItem(user_widget_item)
        project_widget_item = QtWidgets.QTreeWidgetItem(["Project"])
        self.menu_tree_widget.addTopLevelItem(project_widget_item)
        common_widget_item = QtWidgets.QTreeWidgetItem(["Common"])
        self.menu_tree_widget.addTopLevelItem(common_widget_item)

        # sub-categories for 'User'

        # sub-categories for 'Project'
        project_category_definitions = QtWidgets.QTreeWidgetItem(
            ["Category Definitions"]
        )
        project_widget_item.addChild(project_category_definitions)
        # self.create_project_category_definitions()

        # sub-categories for 'Common'

    def _gather_validations_and_extracts(self):
        """Collect the available validations and extracts."""

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

        return {"validations": validations, "extracts": extracts}

    def create_widgets(self):
        """Create widgets."""

        # left menu
        self.create_setting_categories()

        # right contents

        # TEMPORARY
        temp_path = "D:\\dev\\tik_manager4\\tik_manager4\\defaults\\temp_category_definitions.json"
        settings_data = settings.Settings(temp_path)
        availability_dict = self._gather_validations_and_extracts()
        self.settings_list.append(settings_data)

        project_category_definitions_widget = CategoryDefinitions(
            settings_data, availability_dict
        )
        # self.right_contents_lay.addWidget(project_category_definitions_widget)
        self.right_vlayout.addWidget(project_category_definitions_widget)

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

        project_category_definitions_widget.modified.connect(self.check_changes)

        self.button_box_lay.addWidget(tik_button_box)

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

    def __init__(self, settings_data, availability_dict, title="TEST", *args, **kwargs):
        super(CategoryDefinitions, self).__init__(*args, **kwargs)
        self.availability_dict = availability_dict
        self._definitions_layout = QtWidgets.QVBoxLayout(self)

        # add the title
        title_label = HeaderLabel(title)
        self._definitions_layout.addWidget(title_label)

        add_button = TikButton("Add New Definition", parent=self)
        add_button.set_color(background_color="#405040")
        self._definitions_layout.addWidget(add_button)

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
        add_validation_button = TikIconButton(icon_name="plus", size=32, background_color="#405040", parent=self)
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
        add_extract_button = TikIconButton(icon_name="plus", size=32, background_color="#405040", parent=self)
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
    dialog.show()
    sys.exit(app.exec_())
