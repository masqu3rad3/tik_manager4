"""Dialog for new subproject creation."""

import sys

from tik_manager4.objects.metadata import FilteredData
from tik_manager4.core.settings import Settings
from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.ui.dialog import feedback
from tik_manager4.ui.widgets.common import TikButtonBox
from tik_manager4.ui.layouts.collapsible_layout import CollapsibleLayout

import tik_manager4.ui.layouts.settings_layout

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)


class TaskDialog(QtWidgets.QDialog):
    """Shared dialog for task creation and editing."""

    def __init__(
        self,
        parent_sub,
        parent=None,
        management_locked=False,
    ):
        super(TaskDialog, self).__init__(parent=parent)

        if parent_sub and not isinstance(parent_sub, list):
            parent_sub = [parent_sub]
        self._parent_sub = parent_sub
        self.management_locked = management_locked
        self.metadata_definitions = self._parent_sub[0].guard.metadata_definitions
        self.inherited_metadata = self._parent_sub[0].metadata

        self.feedback = feedback.Feedback(parent=self)

        self.setMinimumSize(600, 400)
        self.setModal(True)

        self.category_type_dictionary = self._categorize_category_definitions()

        self.primary_data = Settings()
        self.secondary_data = Settings()
        self.tertiary_data = Settings()

        self.main_layout = QtWidgets.QVBoxLayout(self)

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
        global_modes = ["root", "null", "global", ""]
        filtered_data = {}
        for key, data in category_definition_data.items():
            _type = data.get("type", None)
            _archived = data.get("archived", False)
            if _archived:
                continue
            # if _type and _type != mode:
            if _type and _type != mode and mode not in global_modes:
                continue
            filtered_data[key] = data
        return filtered_data

    def define_primary_ui(self):
        """Populate settings."""

        # get the metadata from the last selected one
        _mode = self._parent_sub[-1].metadata.get_value("mode", "")
        all_categories = self._parent_sub[-1].guard.category_definitions.get_data()
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

    def get_metadata_value(self, key):
        """Convenient method to get the metadata value."""
        return self._parent_sub[0].metadata.get_value(key, None)

    def _get_metadata_override(self, key):
        """Convenience method to get the metadata override."""
        return self._parent_sub[0].metadata.is_overridden(key)

    def _get_metadata_type(self, data):
        """Get the correct SettingsLayout type for the metadata value."""
        default_value = data.get("default", None)
        enums = data.get("enum", [])
        data_type = tik_manager4.ui.layouts.settings_layout.guess_data_type(
            default_value, enums
        )
        if not data_type:
            raise ValueError(
                "Unsupported metadata type: {}".format(type(default_value))
            )
        return data_type, default_value, enums

    def define_other_ui(self):
        """Define the secondary UI."""
        _secondary_ui = {}
        _tertiary_ui = {}
        # The next part of metadata is for displaying and overriding
        # the existing metadata keys in the stream
        for key, data in self.metadata_definitions.properties.items():
            _value_type, _default_value, _enum = self._get_metadata_type(data)
            # _default_value = self.get_metadata_value(key) or data.get("default", None)
            _default_value = self.get_metadata_value(key) or _default_value
            if _default_value is None:
                raise ValueError("No default value defined for metadata {}".format(key))

            if key in self.inherited_metadata.keys():
                # if the metadata already defined, create it with override option
                _secondary_ui["{}_override".format(key)] = {
                    "display_name": "{} (Override):".format(key),
                    "type": "multi",
                    "tooltip": "Override {}".format(key),
                    "value": {
                        "__override_{}".format(key): {
                            "type": "boolean",
                            "value": self._get_metadata_override(key),
                            "disables": [[False, key]],
                        },
                        key: {
                            "type": _value_type,
                            "value": _default_value,
                            "items": _enum,
                        },
                    },
                }
            else:
                # if the metadata is not defined, create it with new option
                _tertiary_ui[key] = {
                    "display_name": "{} :".format(key),
                    "type": "multi",
                    "tooltip": "New {}".format(key),
                    "value": {
                        "__new_{}".format(key): {
                            "type": "boolean",
                            "value": False,
                            "disables": [[False, key]],
                        },
                        key: {
                            "type": _value_type,
                            "value": _default_value,
                            "items": _enum,
                        },
                    },
                }

        return _secondary_ui, _tertiary_ui

    def _init_ui(self):
        """Initialize UI."""
        primary_definition = self.define_primary_ui()
        secondary_definition, tertiary_definition = self.define_other_ui()

        self.settings_layout = tik_manager4.ui.layouts.settings_layout.SettingsLayout(
            primary_definition, self.primary_data, parent=self
        )
        self.main_layout.addLayout(self.settings_layout)

        # create a metadata layout which has a scroll area
        metadata_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addLayout(metadata_layout)

        scroll_area = QtWidgets.QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll_area.setFrameShadow(QtWidgets.QFrame.Plain)
        scroll_area.setLineWidth(0)
        scroll_area.setMidLineWidth(0)
        scroll_area.setContentsMargins(0, 0, 0, 0)

        # creata a widget for contents
        contents_widget = QtWidgets.QWidget()
        contents_widget.setContentsMargins(0, 0, 0, 0)

        scroll_area.setWidget(contents_widget)

        metadata_layout.addWidget(scroll_area)
        scroll_layout = QtWidgets.QVBoxLayout(contents_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        self.secondary_layout = CollapsibleLayout("Inherited Properties", expanded=True)
        # self.secondary_layout.contents_widget.setEnabled(not self.management_locked)
        scroll_layout.addLayout(self.secondary_layout)
        self.tertiary_layout = CollapsibleLayout("New Properties", expanded=False)
        scroll_layout.addLayout(self.tertiary_layout)

        secondary_content = tik_manager4.ui.layouts.settings_layout.SettingsLayout(
            secondary_definition, self.secondary_data, parent=self
        )
        self.secondary_layout.contents_layout.addLayout(secondary_content)
        tertiary_content = tik_manager4.ui.layouts.settings_layout.SettingsLayout(
            tertiary_definition, self.tertiary_data, parent=self
        )
        self.tertiary_layout.contents_layout.addLayout(tertiary_content)

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
        self.button_box.accepted.connect(self.execute)
        self.button_box.rejected.connect(self.reject)

    def execute(self):
        pass


class NewTask(TaskDialog):
    def __init__(self, project_object, parent_sub=None, parent=None, *args, **kwargs):
        super(NewTask, self).__init__(parent_sub, parent=parent, *args, **kwargs)
        self.setWindowTitle("New Task")
        self.tik_project = project_object

        self._new_tasks = []

        self._init_ui()

    def execute(self):
        """Create Task(s)."""

        filtered_data = FilteredData()
        filtered_data.update_overridden_data(self.secondary_data)
        filtered_data.update_new_data(self.tertiary_data)

        for sub in self._parent_sub:
            _new_task = self.tik_project.create_task(
                name=self.primary_data.get_property("name"),
                categories=self.primary_data.get_property("categories"),
                parent_uid=sub.id,
                metadata_overrides=filtered_data,
            )
            if _new_task == -1:
                self.feedback.pop_info(
                    title="Failed to create task.",
                    text=self.tik_project.log.last_message,
                    critical=True,
                )
                return
            self._new_tasks.append(_new_task)
            self.accept()

    def get_created_task(self):
        return self._new_tasks

    def _get_metadata_override(self, key):
        """Override the function to return always False."""
        return False


class EditTask(TaskDialog):
    """Dialog for task editing."""

    def __init__(self, task_object, parent_sub=None, parent=None, management_locked=False, *args, **kwargs):
        self.task_object = task_object
        super(EditTask, self).__init__(
            parent_sub=parent_sub, parent=parent, management_locked=management_locked, *args, **kwargs
        )
        self.setWindowTitle("Edit Task")
        self.inherited_metadata = self.task_object.metadata

        self._init_ui()

    def define_primary_ui(self):
        """Populate settings."""

        _mode = self.task_object.metadata.get_value("mode", "")
        all_categories = self.task_object.guard.category_definitions.get_data()
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
                "value": self._parent_sub[0].path,
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

    def get_metadata_value(self, key):
        """Convenient method to get the metadata value."""
        return self.task_object.metadata.get_value(key, None)

    def _get_metadata_override(self, key):
        """Convenience method to get the metadata override."""
        return self.task_object.metadata.is_overridden(key)

    def execute(self):
        """Edit task."""
        filtered_data = FilteredData()
        filtered_data.update_overridden_data(self.secondary_data)
        filtered_data.update_new_data(self.tertiary_data)
        _name = self.primary_data.get_property("name")
        self.task_object.edit(
            name=_name,
            categories=self.primary_data.get_property("categories"),
            metadata_overrides=filtered_data,
        )
        self.accept()
