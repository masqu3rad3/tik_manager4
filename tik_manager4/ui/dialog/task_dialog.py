"""Dialog for new subproject creation."""
import sys
from tik_manager4.core.settings import Settings
from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.ui.dialog import feedback
from tik_manager4.ui.widgets.common import TikButtonBox

# from tik_manager4.ui.layouts.settings_layout import SettingsLayout
import tik_manager4.ui.layouts.settings_layout

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)


class EditTask(QtWidgets.QDialog):
    def __init__(self, task_object, parent_sub=None, parent=None, *args, **kwargs):
        """Dialog for task editing."""
        super(EditTask, self).__init__(parent=parent, *args, **kwargs)
        self.task_object = task_object
        self.feedback = feedback.Feedback(parent=self)

        # if parent_sub and not isinstance(parent_sub, list):
        #     parent_sub = [parent_sub]

        self._parent_sub = parent_sub or task_object.parent_sub
        self.parent = parent
        self.setWindowTitle("Edit Task")
        self.setFixedSize(600, 400)
        self.setModal(True)

        self.category_type_dictionary = self._categorize_category_definitions()

        self.ui_definition = self.define_ui_dictionary()
        self._init_ui()

        self._new_task = None

    def _categorize_category_definitions(self):
        """Categorize category definitions."""
        _items = self._parent_sub.guard.category_definitions.get_data().items()
        # separate groups by type
        _groups = {}
        for key, val in _items:
            _type = val.get("type", "null")
            if _type not in _groups.keys():
                _groups[_type] = []
            _groups[_type].append(val)
        return _groups

    @staticmethod
    def _collect_category_display_names(category_definition_data, mode=None):
        """Collect category display names and return a dictionary.
        This essentially uses the display name as the key and category_definition key
        as the value.
        """
        _display_name_dict = {}
        for key, data in category_definition_data.items():
            if data.get("type", None) == mode:
                _display_name_dict[data["display_name"]] = key
        return _display_name_dict

    @staticmethod
    def filter_category_definitions(category_definition_data, mode=None):
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

    def define_ui_dictionary(self):
        """Populate settings."""

        _mode = self._parent_sub.metadata.get_value("mode", "")
        all_categories = self._parent_sub.guard.category_definitions.get_data()
        if _mode == "":
            _default_categories = all_categories
        else:
            _default_categories = self.filter_category_definitions(
                all_categories, mode=_mode
            )

        _ui_definition = {
            "name": {
                "display_name": "Name :",
                "type": "validatedString",
                "value": self.task_object.name,
                "tooltip": "Name of the new task.",
                "readOnly": True,
            },
            "path": {
                "display_name": "Path :",
                "type": "string",
                "value": self._parent_sub.path,
                "tooltip": "Path of the new task.",
                "readOnly": True,
            },
            "categories": {
                "display_name": "Categories :",
                "type": "categoryList",
                "value": list(self.task_object.categories.keys()),
                "category_list": _default_categories,
                "tooltip": "Categories of the new task.",
            },
        }

        return _ui_definition

    def _init_ui(self):
        """Initialize UI."""
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.settings_data = Settings()
        self.settings_layout = tik_manager4.ui.layouts.settings_layout.SettingsLayout(
            self.ui_definition, self.settings_data, parent=self
        )
        self.main_layout.addLayout(self.settings_layout)
        # create a button box
        self.button_box = TikButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        # get the name ValidatedString widget and connect it to the ok button
        _name_line_edit = self.settings_layout.find("name")
        _name_line_edit.add_connected_widget(
            self.button_box.button(QtWidgets.QDialogButtonBox.Ok)
        )
        self.main_layout.addWidget(self.button_box)

        # if multi subs, disable path
        # if len(self._parent_sub) > 1:
        #     _path_line_edit = self.settings_layout.find("path")
        #     _path_line_edit.setHidden(True)

        # SIGNALS
        self.button_box.accepted.connect(self.on_edit_task)
        self.button_box.rejected.connect(self.reject)

    def on_edit_task(self):
        """Create task."""
        _name = self.settings_data.get_property("name")
        self.task_object.edit(
            name=_name, categories=self.settings_data.get_property("categories")
        )
        self.accept()


class NewTask(QtWidgets.QDialog):
    def __init__(self, project_object, parent_sub=None, parent=None, *args, **kwargs):
        """
        Dialog for new task creation.

        """
        super(NewTask, self).__init__(parent=parent, *args, **kwargs)
        self.tik_project = project_object
        self.feedback = feedback.Feedback()

        if parent_sub and not isinstance(parent_sub, list):
            parent_sub = [parent_sub]

        self._parent_sub = parent_sub or project_object
        # self._multi_parent_subs = multi_subs
        self.parent = parent
        self.setWindowTitle("New Task")
        self.setFixedSize(600, 400)
        self.setModal(True)

        self.category_type_dictionary = self._categorize_category_definitions()

        self.ui_definition = self.define_ui_dictionary()
        self._init_ui()

        self._new_tasks = []

    def _categorize_category_definitions(self):
        """Categorize category definitions."""
        _items = self._parent_sub[-1].guard.category_definitions.get_data().items()
        # separate groups by type
        _groups = {}
        for key, val in _items:
            _type = val.get("type", "null")
            if _type not in _groups.keys():
                _groups[_type] = []
            _groups[_type].append(val)
        return _groups

    @staticmethod
    def _collect_category_display_names(category_definition_data, mode=None):
        """Collect category display names and return a dictionary.
        This essentially uses the display name as the key and category_definition key
        as the value.
        """
        _display_name_dict = {}
        for key, data in category_definition_data.items():
            if data.get("type", None) == mode:
                _display_name_dict[data["display_name"]] = key
        return _display_name_dict

    @staticmethod
    def filter_category_definitions(category_definition_data, mode=None):
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

    def define_ui_dictionary(self):
        """Populate settings."""

        # get the metadata from the last selected one
        _mode = self._parent_sub[-1].metadata.get_value("mode", "")
        all_categories = self._parent_sub[-1].guard.category_definitions.get_data()
        print("DEBUG")
        print(all_categories)
        print(_mode)
        if _mode == "" or _mode == "root" or _mode == "null" or _mode == "global":
            _default_categories = all_categories
        else:
            _default_categories = self.filter_category_definitions(
                all_categories, mode=_mode
            )

        _ui_definition = {
            "name": {
                "display_name": "Name :",
                "type": "validatedString",
                "value": "",
                "tooltip": "Name of the new task.",
            },
            "path": {
                "display_name": "Path :",
                "type": "string",
                "value": self._parent_sub[-1].path,
                "tooltip": "Path of the new task.",
                "readOnly": True,
            },
            "categories": {
                "display_name": "Categories :",
                "type": "categoryList",
                "value": list(_default_categories.keys()),
                "tooltip": "Categories of the new task.",
            },
        }

        return _ui_definition

    def _init_ui(self):
        """Initialize UI."""
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.settings_data = Settings()
        self.settings_layout = tik_manager4.ui.layouts.settings_layout.SettingsLayout(
            self.ui_definition, self.settings_data, parent=self
        )
        self.main_layout.addLayout(self.settings_layout)
        # create a button box
        self.button_box = TikButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        # get the name ValidatedString widget and connect it to the ok button
        _name_line_edit = self.settings_layout.find("name")
        _name_line_edit.add_connected_widget(
            self.button_box.button(QtWidgets.QDialogButtonBox.Ok)
        )
        self.main_layout.addWidget(self.button_box)

        # if multi subs, disable path
        if len(self._parent_sub) > 1:
            _path_line_edit = self.settings_layout.find("path")
            _path_line_edit.setEnabled(False)
            self.setWindowTitle("New Task (Multiple Selection)")

        # SIGNALS
        self.button_box.accepted.connect(self.on_create_task)
        self.button_box.rejected.connect(self.reject)

    def on_create_task(self):
        """Create task."""

        for sub in self._parent_sub:
            _new_task = self.tik_project.create_task(
                name=self.settings_data.get_property("name"),
                categories=self.settings_data.get_property("categories"),
                parent_uid=sub.id,
            )
            if _new_task == -1:
                self.feedback.pop_info(
                    title="Failed to create task.",
                    text=self.tik_project.LOG.last_message,
                    critical=True,
                )
                return
            self._new_tasks.append(_new_task)
            self.accept()

        #
        # self._new_task = self.tik_project.create_task(
        #     name=self.settings_data.get_property("name"),
        #     categories=self.settings_data.get_property("categories"),
        #     parent_uid=self._parent_sub.id,
        # )
        # if self._new_task == -1:
        #     self.feedback.pop_info(
        #         title="Failed to create task.",
        #         text=self.tik_project.log.last_message,
        #         critical=True,
        #     )
        #     return
        # self.accept()

    def get_created_task(self):
        return self._new_tasks
