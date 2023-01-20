"""Dialog for new subproject creation."""
import sys
from tik_manager4.core.settings import Settings
from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.ui.dialog import feedback
from tik_manager4.ui.widgets.settings_layout import SettingsLayout

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

class NewTask(QtWidgets.QDialog):
    def __init__(self, project_object, parent_sub=None, parent=None, *args, **kwargs):
        """
        Dialog for new new task creation.

        """
        super(NewTask, self).__init__(parent=parent, *args, **kwargs)
        self.tik_project = project_object
        self._parent_sub = parent_sub or project_object
        self.parent = parent
        self._feedback = feedback.Feedback(parent=self)
        self.settings = Settings()
        self.setWindowTitle("New Task")
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setFixedSize(600, 400)
        self.setModal(True)

        self.categoty_type_dictionary = self._categorize_category_definitions()

        self.populate_settings()
        self._init_ui()

        self._new_task = None

    def _categorize_category_definitions(self):
        """Categorize category definitions."""
        _items  = self._parent_sub.guard.category_definitions.get_data().items()

        # seperate groups by type
        _groups = {}
        for key, val in _items:
            _type = val.get("type", "null")
            if _type not in _groups.keys():
                _groups[_type] = []
            _groups[_type].append(val)
        return _groups

    def _collect_category_display_names(self, category_definition_data, mode=None):
        """Collect category display names and return a dictionary.
        This essentially uses the display name as the key and category_definition key as the value.
        """
        _display_name_dict = {}
        for key, data in category_definition_data.items():
            if data.get("type", None) == mode:
                _display_name_dict[data["display_name"]] = key
        return _display_name_dict

    def filter_category_definitions(self, category_definition_data, mode=None):
        """Filter category definitions."""
        filtered_data = {}
        for key, data in category_definition_data.items():
            _type = data.get("type", None)
            _archived = data.get("archived", False)
            if _archived:
                continue
            if _type and _type != mode:
                continue
            filtered_data[key] = data
        return filtered_data
    def populate_settings(self):
        """Populate settings."""

        # _mode = self._parent_sub.mode or ""
        _mode = self._parent_sub.metadata.get_value("mode", "")
        # _default_categories = self._parent_sub.guard.category_definitions.get_data()
        _default_categories = self.filter_category_definitions(self._parent_sub.guard.category_definitions.get_data(), mode=_mode)

        # TODO: Instead of a simple string, make it a validated string which won't allow spaces and illegal characters
        self.settings.add_property("name", {
            "display_name": "Name :",
            "type": "string",
            "value": "",
            "tooltip": "Name of the new task.",
            # "disables": [["", "categories"]]
        })
        self.settings.add_property("path", {
            "display_name": "Path :",
            "type": "string",
            "value": self._parent_sub.path,
            "tooltip": "Path of the new task.",
        })
        self.settings.add_property("categories", {
            "display_name": "Categories :",
            "type": "categoryList",
            "value": list(_default_categories.keys()),
            "tooltip": "Categories of the new task.",
        })

    def _init_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.settings_layout = SettingsLayout(self.settings, parent=self)
        # TODO: Make it fool proof (i.e. disable the ok button if the name is empty)
        self.main_layout.addLayout(self.settings_layout)

        # create a button box
        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.main_layout.addWidget(self.button_box)

        # SIGNALS
        self.button_box.accepted.connect(self.on_create_task)
        self.button_box.rejected.connect(self.reject)

    def on_create_task(self):
        """Create task."""
        self._new_task = self.tik_project.create_task(
            name=self.settings.get_property("name")["value"],
            categories=self.settings.get_property("categories")["value"],
            parent_uid=self._parent_sub.id,
        )
        if self._new_task == -1:
            self._feedback.pop_info(title="Failed to create task.", text=self.tik_project.log.last_message, critical=True)
            return
        self.accept()
    def get_created_task(self):
        return self._new_task

    # def _init_ui(self):
    #
    #     self.main_layout = QtWidgets.QVBoxLayout(self)
    #
    #     self.form_layout = QtWidgets.QFormLayout()
    #     self.main_layout.addLayout(self.form_layout)
    #
    #     self.name_lbl = QtWidgets.QLabel("Name: ")
    #     self.name_le = QtWidgets.QLineEdit()
    #     self.form_layout.addRow(self.name_lbl, self.name_le)
    #
    #     self.path_lbl = QtWidgets.QLabel("Path: ")
    #     self.path_le = QtWidgets.QLineEdit()
    #     self.path_le.setText(self._parent_sub.path)
    #     self.form_layout.addRow(self.path_lbl, self.path_le)
    #
    #     # categories
    #     self.categories_lbl = QtWidgets.QLabel("Categories: ")
    #
    #     print(self._parent_sub.name)
    #     print(self._parent_sub.mode)
    #     if self._parent_sub:
    #         _mode = self._parent_sub.mode
    #         if _mode.lower() == "asset":
    #             _default_categories = self.tik_project.guard.asset_categories
    #         elif _mode.lower() == "shot":
    #             _default_categories = self.tik_project.guard.shot_categories
    #         else:
    #             _default_categories = self.tik_project.guard.null_categories
    #     else:
    #         _default_categories = self.tik_project.guard.null_categories
    #
    #     self.categories_lay = QtWidgets.QHBoxLayout()
    #     self.categories_list = QtWidgets.QListWidget()
    #     self.categories_list.addItems(_default_categories)
    #     self.categories_lay.addWidget(self.categories_list)
    #
    #     self.categories_buttons_lay = QtWidgets.QVBoxLayout()
    #     self.categories_lay.addLayout(self.categories_buttons_lay)
    #     self.add_category_btn = QtWidgets.QPushButton("Add")
    #     self.remove_category_btn = QtWidgets.QPushButton("Remove")
    #     self.move_category_up_btn = QtWidgets.QPushButton("Up")
    #     self.move_category_down_btn = QtWidgets.QPushButton("Down")
    #     self.categories_buttons_lay.addWidget(self.add_category_btn)
    #     self.categories_buttons_lay.addWidget(self.remove_category_btn)
    #     self.categories_buttons_lay.addWidget(self.move_category_up_btn)
    #     self.categories_buttons_lay.addWidget(self.move_category_down_btn)
    #
    #     self.form_layout.addRow(self.categories_lbl, self.categories_lay)
