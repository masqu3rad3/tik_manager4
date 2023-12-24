"""Dialog for new subproject creation."""
from tik_manager4.core.settings import Settings
from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.ui.dialog.feedback import Feedback
from tik_manager4.ui.widgets.common import TikButtonBox

import tik_manager4.ui.layouts.settings_layout
from tik_manager4.ui.layouts.collapsible_layout import CollapsibleLayout


class EditSubprojectDialog(QtWidgets.QDialog):
    def __init__(self, project_object, parent_sub=None, parent=None, *args, **kwargs):
        super(EditSubprojectDialog, self).__init__(parent=parent, *args, **kwargs)
        self.feedback = Feedback(parent=self)
        self.tik_project = project_object
        self._parent_sub = parent_sub or project_object
        print(self._parent_sub.metadata.keys())
        print(self._parent_sub.id)
        print(self._parent_sub.name)
        print(self._parent_sub.path)
        print("-------------------\n")


        self.parent = parent

        self.setWindowTitle("Edit Subproject")
        self.setModal(True)

        self.metadata_definitions = self.tik_project.metadata_definitions

        self.primary_definition = self.define_primary_ui()
        self.secondary_definition, self.tertiary_definition = self.define_other_ui()

        self.primary_data = Settings()
        self.secondary_data = Settings()
        self.tertiary_data = Settings()

        self.primary_layout = None
        self.secondary_layout = None
        self.tertiary_layout = None

        self.primary_content = None
        self.secondary_content = None
        self.tertiary_content = None

        self._new_subproject = None
        self.button_box = None
        self.button_box_layout = None  # an empty layout to hold the button box

        self.build_ui()

        self.resize(400, 600)

        # print(self.secondary_data.properties)

    def build_ui(self):
        """Initialize the UI."""
        # create a scroll area
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

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(scroll_area)

        scroll_layout = QtWidgets.QVBoxLayout(contents_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        # create a collapsible widget for each section
        self.primary_layout = CollapsibleLayout("Main Properties", expanded=True)
        scroll_layout.addLayout(self.primary_layout)
        self.secondary_layout = CollapsibleLayout("Inherited Properties", expanded=True)
        scroll_layout.addLayout(self.secondary_layout)
        self.tertiary_layout = CollapsibleLayout("New Properties", expanded=False)
        scroll_layout.addLayout(self.tertiary_layout)

        scroll_layout.addStretch()

        self.primary_content = tik_manager4.ui.layouts.settings_layout.SettingsLayout(
            self.primary_definition, self.primary_data, parent=self
        )
        self.primary_layout.contents_layout.addLayout(self.primary_content)
        # print("before", self.secondary_data.properties)
        # print(self.secondary_definition)
        self.secondary_content = tik_manager4.ui.layouts.settings_layout.SettingsLayout(
            self.secondary_definition, self.secondary_data, parent=self
        )
        # print("after", self.secondary_data.properties)
        # print(self.secondary_definition)
        self.secondary_definition
        self.secondary_layout.contents_layout.addLayout(self.secondary_content)
        self.tertiary_content = tik_manager4.ui.layouts.settings_layout.SettingsLayout(
            self.tertiary_definition, self.tertiary_data, parent=self
        )
        self.tertiary_layout.contents_layout.addLayout(self.tertiary_content)

        # create a button box
        self.button_box_layout = QtWidgets.QHBoxLayout()
        self.button_box = TikButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        main_layout.addLayout(self.button_box_layout)
        self.button_box_layout.addWidget(self.button_box)
        # SIGNALS
        self.button_box.accepted.connect(self._execute)
        self.button_box.rejected.connect(self.reject)

        self.primary_layout.set_hidden(True)

    def define_primary_ui(self):
        return {}

    def get_metadata_value(self, key):
        """Convenient method to get the metadata value."""
        return self._parent_sub.metadata.get_value(key, None)

    def _get_metadata_override(self, key):
        """Convenient method to get the metadata override."""
        return self._parent_sub.metadata.is_overridden(key)

    def _get_metadata_type(self, data):
        """Get the correct SettingsLayout type for the metadata value."""
        default_value = data.get("default", None)
        enum = data.get("enum", [])
        if enum:
            return "combo", default_value, enum
        elif isinstance(default_value, int):
            return "spinnerInt", default_value, enum
        elif isinstance(default_value, float):
            return "spinnerFloat", default_value, enum
        elif isinstance(default_value, str):
            return "string", default_value, enum
        elif isinstance(default_value, list):
            # currently only lists with floats or ints are supported
            # Also the list length is limited with 3 items (vector3)
            if 2 > len(default_value) > 3:
                raise ValueError("List length is limited to 2 or 3 items")
            for item in default_value:
                if not isinstance(item, (float, int)):
                    raise ValueError("List items must be float or int")
            # if any of the items is float, the value type is float
            if any([isinstance(item, float) for item in default_value]):
                _value_suffix = "Float"
            else:
                _value_suffix = "Int"
            return (
                "vector{0}{1}".format(len(default_value), _value_suffix),
                default_value,
                enum,
            )
        else:
            raise ValueError(
                "Unsupported metadata type: {}".format(type(default_value))
            )

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

            if key in self._parent_sub.metadata.keys():
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

    def _execute(self):
        # build a new kwargs dictionary by filtering the settings_data

        # get the primary data
        filtered_data = FilteredData(
            uid=self._parent_sub.id,
            name=self._parent_sub.name,
        )

        filtered_data.update_overridden_data(self.secondary_data)
        filtered_data.update_new_data(self.tertiary_data)

        sub = self.tik_project.edit_sub_project(**filtered_data)
        if sub != -1:
            self._new_subproject = self._parent_sub
            self.accept()
        else:
            msg, title = self.tik_project.log.get_last_message()
            self.feedback.pop_info(title, msg, critical=True)


class NewSubprojectDialog(EditSubprojectDialog):
    def __init__(self, *args, **kwargs):
        """
        Dialog for new subproject creation.

        """
        super(NewSubprojectDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle("New Subproject")

    def define_primary_ui(self):
        """Define the primary UI."""
        _primary_ui = {
            "name": {
                "display_name": "Name :",
                "type": "validatedString",
                # "type": "string",
                "value": "",
                "tooltip": "Name of the subproject",
            },
            "parent_path": {
                "display_name": "Parent :",
                # "type": "pathBrowser",
                "type": "subprojectBrowser",
                "project_object": self.tik_project,
                "value": self._parent_sub.path,
                "tooltip": "Path of the sub-project",
            },
        }
        return _primary_ui

    def reinitilize_other_ui(self, new_parent_sub):
        """Reinitialize the secondary and tertiary UIs."""
        self._parent_sub = new_parent_sub
        self.secondary_content.clear()
        self.tertiary_content.clear()
        self.secondary_content.deleteLater()
        self.tertiary_content.deleteLater()

        self.secondary_definition, self.tertiary_definition = self.define_other_ui()
        self.secondary_content = None
        self.tertiary_content = None

        self.secondary_content = tik_manager4.ui.layouts.settings_layout.SettingsLayout(
            self.secondary_definition, self.secondary_data, parent=self
        )
        self.secondary_layout.contents_layout.addLayout(self.secondary_content)
        self.tertiary_content = tik_manager4.ui.layouts.settings_layout.SettingsLayout(
            self.tertiary_definition, self.tertiary_data, parent=self
        )
        self.tertiary_layout.contents_layout.addLayout(self.tertiary_content)

    def _get_metadata_override(self, key):
        """Override the function to return always False."""
        return False

    def build_ui(self):
        """Initialize the UI."""
        super(NewSubprojectDialog, self).build_ui()

        # create a button box
        # get the name ValidatedString widget and connect it to the ok button
        _name_line_edit = self.primary_content.find("name")
        _name_line_edit.add_connected_widget(
            self.button_box.button(QtWidgets.QDialogButtonBox.Ok)
        )
        _browse_widget = self.primary_content.find("parent_path")
        _browse_widget.sub.connect(lambda x: self.reinitilize_other_ui(x))

        self.primary_layout.set_hidden(False)

    def _execute(self):
        # build a new kwargs dictionary by filtering the settings_data

        # get the primary data
        filtered_data = FilteredData(
            name=self.primary_data.get_property("name"),
            parent_path=self.primary_data.get_property("parent_path"),
        )

        filtered_data.update_overridden_data(self.secondary_data)
        filtered_data.update_new_data(self.tertiary_data)

        sub = self.tik_project.create_sub_project(**filtered_data)
        if sub != -1:
            self._new_subproject = sub
            self.accept()
        else:
            msg, title = self.tik_project.log.get_last_message()
            self.feedback.pop_info(title, msg, critical=True)

    def get_created_subproject(self):
        return self._new_subproject


class FilteredData(dict):
    def __init__(self, **kwargs):
        super(FilteredData, self).__init__()
        self.update(kwargs)

    def update_overridden_data(self, settings_data):
        for key, value in settings_data.get_data().items():
            # if it starts __override, skip
            if key.startswith("__override"):
                continue
            # if the key has a __override key, check if it is True
            _override_key = "__override_{}".format(key)
            if _override_key not in list(settings_data.get_data().keys()):
                self[key] = value
            else:
                if settings_data.get_property(_override_key):
                    print(key, value)
                    self[key] = value

    def update_new_data(self, settings_data):
        for key, value in settings_data.get_data().items():
            if key.startswith("__new"):
                continue
            # if the new checked box is checked, add the key to the filtered_data
            _new_key = "__new_{}".format(key)
            if settings_data.get_property(_new_key):
                self[key] = value
