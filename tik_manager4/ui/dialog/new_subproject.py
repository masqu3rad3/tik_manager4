"""Dialog for new subproject creation."""
from tik_manager4.core.settings import Settings
from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.ui.dialog import feedback
from tik_manager4.ui.layouts.settings_layout import SettingsLayout
from tik_manager4.ui.layouts.collapsible_layout import CollapsibleLayout

from tik_manager4.objects import guard


class NewSubproject(QtWidgets.QDialog):
    def __init__(self, project_object, parent_sub=None, parent=None, *args, **kwargs):
        """
        Dialog for new subproject creation.

        """
        super(NewSubproject, self).__init__(parent=parent, *args, **kwargs)
        self.tik_project = project_object
        self._parent_sub = parent_sub or project_object
        self.parent = parent
        self._feedback = feedback.Feedback(parent=self)
        self.setWindowTitle("New Subproject")
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setFixedSize(600, 400)
        self.setModal(True)

        self.metadata_definitions = guard.Guard.commons.metadata

        self.primary_definition = self.define_primary_ui()
        self.secondary_definition, self.tertiary_definition = self.define_other_ui()

        self.primary_data = Settings()
        self.secondary_data = Settings()
        self.tertiary_data = Settings()

        self.build_ui()

        self._new_subproject = None

    def define_primary_ui(self):
        """Define the primary UI."""
        _primary_ui = {
            "name": {
                   "display_name": "Name :",
                   "type": "validatedString",
                   "value": "",
                   "tooltip": "Name of the subproject",
               },
            "parent_path":
               {
                   "display_name": "Path :",
                   "type": "string",
                   "value": self._parent_sub.path,
                   "tooltip": "Path of the subproject",
               }
        }
        return _primary_ui

    def define_other_ui(self):
        """Define the secondary UI."""
        _secondary_ui = {}
        _tertiary_ui = {}
        # The next part of metadata is for displaying and overriding
        # the existing metadata keys in the stream
        for key, data in self.metadata_definitions.properties.items():
            _default_value = self._parent_sub.metadata.get_value(key, None) or data.get("default", None)
            _enum = data.get("enum", [])
            if _default_value is None:
                raise ValueError("No default value defined for metadata {}".format(key))

            # define what widget to use to display and manipulate the metadata
            # if there is an enum value, it is always a combo box
            if _enum:
                _value_type = "combo"
            else:
                if isinstance(_default_value, int):
                    _value_type = "spinnerInt"
                elif isinstance(_default_value, float):
                    _value_type = "spinnerFloat"
                elif isinstance(_default_value, str):
                    _value_type = "string"
                elif isinstance(_default_value, list):
                    # currently only lists with floats or ints are supported
                    # Also the list lenght is limited with 3 items (vector3)
                    if 2 > len(_default_value) > 3:
                        raise ValueError("List lenght is limited to 2 or 3 items")
                    for item in _default_value:
                        if not isinstance(item, (float, int)):
                            raise ValueError("List items must be float or int")
                    # if any of the items is float, the value type is float
                    if any([isinstance(item, float) for item in _default_value]):
                        _value_suffix = "Float"
                    else:
                        _value_suffix = "Int"
                    _value_type = "vector{0}{1}".format(len(_default_value), _value_suffix)
                else:
                    raise ValueError("Unknown type for metadata {}".format(key))

            if key in self._parent_sub.metadata.keys():
                # if the metadata already defined, create it with override option
                _secondary_ui["{}_override".format(key)] = {
                    "display_name": "{} (Override):".format(key),
                    "type": "multi",
                    "tooltip": "Override {}".format(key),
                    "value": {
                        "__override_{}".format(key): {
                            "type": "boolean",
                            "value": False,
                            "disables": [[False, key]]
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
                            "disables": [[False, key]]
                        },
                        key: {
                            "type": _value_type,
                            "value": _default_value,
                            "items": _enum,
                        },
                    },
                }

        return _secondary_ui, _tertiary_ui

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
        # main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        # self.main_layout.addWidget(self.scroll_area)

        scroll_layout = QtWidgets.QVBoxLayout(contents_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        # create a collapsible widget for each section
        primary_layout = CollapsibleLayout("Main Properties", expanded=True)
        scroll_layout.addLayout(primary_layout)
        secondary_layout = CollapsibleLayout("Inherited Properties", expanded=True)
        scroll_layout.addLayout(secondary_layout)
        tertiary_layout = CollapsibleLayout("New Properties", expanded=False)
        scroll_layout.addLayout(tertiary_layout)

        scroll_layout.addStretch()

        primary_content = SettingsLayout(self.primary_definition, self.primary_data, parent=self)
        primary_layout.contents_layout.addLayout(primary_content)
        secondary_content = SettingsLayout(self.secondary_definition, self.secondary_data, parent=self)
        secondary_layout.contents_layout.addLayout(secondary_content)
        tertiary_content = SettingsLayout(self.tertiary_definition, self.tertiary_data, parent=self)
        tertiary_layout.contents_layout.addLayout(tertiary_content)
        # create a button box
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        # get the name ValidatedString widget and connect it to the ok button
        _name_line_edit = primary_content.find("name")
        _name_line_edit.add_connected_widget(button_box.button(QtWidgets.QDialogButtonBox.Ok))
        main_layout.addWidget(button_box)
        # SIGNALS
        button_box.accepted.connect(self.on_create_subproject)
        button_box.rejected.connect(self.reject)

    def on_create_subproject(self):
        # build a new kwargs dictionary by filtering the settings_data
        filtered_data = {
            "name": self.primary_data.get_property("name"),
            "parent_path": self.primary_data.get_property("parent_path"),
                         }
        for key, value in self.secondary_data.get_data().items():
            # if it starts __override, skip
            if key.startswith("__override"):
                continue
            # if the key has a __override key, check if it is True
            _override_key = "__override_{}".format(key)
            # if the _override_key is in the settings_data and it is True, add the key to the filtered_data
            if _override_key not in list(self.secondary_data.get_data().keys()):
                filtered_data[key] = value
            else:
                if self.secondary_data.get_property(_override_key):
                    filtered_data[key] = value
        for key, value in self.tertiary_data.get_data().items():
            if key.startswith("__new"):
                continue
            # if the new checked box is checked, add the key to the filtered_data
            _new_key = "__new_{}".format(key)
            if self.tertiary_data.get_property(_new_key):
                filtered_data[key] = value

        sub = self.tik_project.create_sub_project(**filtered_data)
        if sub != -1:
            self._new_subproject = sub
            self.accept()
        else:
            msg, title = self.tik_project.log.get_last_message()
            self._feedback.pop_info(title, msg, critical=True)

    def get_created_subproject(self):
        return self._new_subproject


# test new subproject dialog
if __name__ == "__main__":
    import sys
    import os
    import tik_manager4

    app = QtWidgets.QApplication(sys.argv)

    test_project_path = os.path.join(os.path.expanduser("~"), "t4_test_manual_DO_NOT_USE")
    tik = tik_manager4.initialize("Standalone")
    tik.user.set("Admin", "1234")
    tik.set_project(test_project_path)
    dialog = NewSubproject(tik.project)
    dialog.show()
    app.exec_()

    sys.exit(app.exec_())