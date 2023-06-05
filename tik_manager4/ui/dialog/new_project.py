"""Dialog for creating a new project"""

import os

# from tik_manager4.core.settings import Settings
from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.ui.dialog.new_subproject import EditSubprojectDialog, FilteredData
import tik_manager4.ui.layouts.settings_layout


class NewProjectDialog(EditSubprojectDialog):
    """Dialog for creating a new project"""

    def __init__(self, main_object, *args, **kwargs):
        self.main_object = main_object
        self.structure_list = list(self.main_object.user.commons.structures.properties.values())
        super(NewProjectDialog, self).__init__(main_object.project, *args, **kwargs)

        self.structure_data = None

        self.setWindowTitle("Create New Project")
        self.setMinimumSize(800, 150)
        self.primary_layout.set_hidden(False)
        self.tertiary_layout.set_hidden(True)

    def _get_metadata_override(self, key):
        """Override the function to return always False."""
        return False

    def define_primary_ui(self):
        """Define the primary UI."""
        _structure_names = [x["name"] for x in self.structure_list]
        _primary_ui = {
            "project_root":
                {
                    "display_name": "Projects Root :",
                    "type": "pathBrowser",
                    # "type": "subprojectBrowser",
                    "project_object": self.tik_project,
                    "value": os.path.dirname(self.tik_project.absolute_path),
                    "tooltip": "Root for the projects",
                },
            "project_name": {
                   "display_name": "Project Name :",
                   "type": "validatedString",
                   "value": "",
                   "tooltip": "Name of the Project",
                },
            "structure_template": {
                "display_name": "Template :",
                "type": "combo",
                "items": _structure_names,
                "value": "Empty Project",
                "tooltip": "Pick a template to start with"
                }
        }
        return _primary_ui

    def define_other_ui(self, structure_template=None):
        """Define the secondary UI."""
        _secondary_ui = {}
        _tertiary_ui = {}

        # The next part of metadata is for displaying and overriding
        # the existing metadata keys in the stream
        for key, data in self.metadata_definitions.properties.items():
            _value_type, _default_value, _enum = self._get_metadata_type(data)
            if _default_value is None:
                raise ValueError("No default value defined for metadata {}".format(key))
            _check = False
            if structure_template:
                # print(structure_template)
                _structure_value = structure_template.get(key, None)
                if _structure_value is not None:
                    _default_value = _structure_value
                    _check = True
                    # print(_default_value, _check)

            _secondary_ui[key] = {
                "display_name": "{} :".format(key),
                "type": "multi",
                "tooltip": "New {}".format(key),
                "value": {
                    "__new_{}".format(key): {
                        "type": "boolean",
                        "value": _check,
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

    # def on_structure_template_changed(self, index):
    #     """Override the function to update the metadata."""
    #
    #     # find the structure template in self.structure_dictionary by name
    #     self.structure_data = self.structure_list[index]
    #     # from pprint import pprint
    #     # pprint(self.secondary_data.properties)
    #     # _temp = self.secondary_data.properties.copy()
    #     # self.secondary_content.clear(keep_settings=True)
    #     self.secondary_content.clear()
    #     self.secondary_ui = {}
    #     # print(self.structure_data)
    #     # self.secondary_data.properties.update(self.structure_data)
    #     self.secondary_ui, _ = self.define_other_ui(self.structure_data)
    #     # self.secondary_content.__init__(self.secondary_ui, self.secondary_data)
    #     self.secondary_content.ui_definition = self.secondary_ui
    #
    #     # self.secondary_content.settings_data = _temp
    #
    #     self.secondary_content.widgets = self.secondary_content.populate()
    #     self.secondary_content.signal_connections(self.secondary_content.widgets)
    #
    #     # self.secondary_data.set_data(_temp)
    #     # self.secondary_data = self.secondary_content.settings_data

    def on_structure_template_changed(self, index):
        """Override the function to update the metadata."""

        # find the structure template in self.structure_dictionary by name
        self.structure_data = self.structure_list[index]
        # from pprint import pprint
        # pprint(self.secondary_data.properties)
        # _temp = self.secondary_data.properties.copy()
        # self.secondary_content.clear(keep_settings=True)
        # self.secondary_content.clear()
        # self.secondary_ui = {}
        # print(self.structure_data)
        # self.secondary_data.properties.update(self.structure_data)
        self.secondary_ui, _ = self.define_other_ui(self.structure_data)
        self.secondary_content.__init__(self.secondary_ui, self.secondary_data)
        # self.secondary_content.ui_definition = self.secondary_ui

        # self.secondary_content.settings_data = _temp

        # self.secondary_content.widgets = self.secondary_content.populate()

        # self.secondary_data.set_data(_temp)
        # self.secondary_data = self.secondary_content.settings_data


    def build_ui(self):
        """Initialize the UI."""
        super(NewProjectDialog, self).build_ui()

        # create a button box
        # get the name ValidatedString widget and connect it to the ok button
        _name_line_edit = self.primary_content.find("project_name")
        _name_line_edit.add_connected_widget(self.button_box.button(QtWidgets.QDialogButtonBox.Ok))
        # _browse_widget = self.primary_content.find("parent_path")
        template_widget = self.primary_content.find("structure_template")

        template_widget.currentIndexChanged.connect(self.on_structure_template_changed)

        # run it once to update the secondary ui
        self.on_structure_template_changed(template_widget.currentIndex())

    def _execute(self):
        # build a new kwargs dictionary by filtering the settings_data
        path = os.path.join(self.primary_data.get_property("project_root"), self.primary_data.get_property("project_name"))

        # get the primary data
        filtered_data = FilteredData(
            structure_data=self.structure_data,
            set_after_creation=True
        )

        # filtered_data.update_overridden_data(self.secondary_data)
        filtered_data.update_new_data(self.secondary_data)
        # print("-" * 80)
        # print("-" * 80)
        # pprint(filtered_data)

        # from pprint import pprint
        # pprint(self.primary_data._currentValue)
        # print("path", path)

        self.main_object.create_project(path, **filtered_data)
        # print(self.main_object.project.absolute_path)
        # close the dialog
        self.close()


# Test the dialog
if __name__ == "__main__":
    import sys
    import tik_manager4
    from tik_manager4.ui import pick
    app = QtWidgets.QApplication(sys.argv)
    tik = tik_manager4.initialize("Standalone")
    tik.user.set("Admin", "1234")

    dialog = NewProjectDialog(tik)
    _style_file = pick.style_file()
    dialog.setStyleSheet(str(_style_file.readAll(), 'utf-8'))
    dialog.show()
    sys.exit(app.exec_())