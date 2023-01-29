"""Dialog for new subproject creation."""
import sys
from tik_manager4.core.settings import Settings
from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
from tik_manager4.ui import utils
from tik_manager4.ui.dialog import feedback
from tik_manager4.ui.widgets.settings_layout import SettingsLayout

from tik_manager4.objects import guard


# if __name__ == '__main__':
#     app = QtWidgets.QApplication(sys.argv)

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
        self.ui_definition = self.define_ui_dictionary()
        self._init_ui()

        self._new_subproject = None


    def define_ui_dictionary(self):

        # get the metadata definitions from the lobby
        metadata_definitions = guard.Guard.commons.metadata

        # Start creating the ui definition dictionary
        ui_definition = {
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

        for key, data in metadata_definitions.properties.items():
            if key in self._parent_sub.metadata.keys():
                # if the metadata already defined, create it with overrride option
                # _default_value = data.get("default", None)
                _default_value = self._parent_sub.metadata.get_value(key, None)
                _enum = data.get("enum", [])
                if _default_value is None:
                    raise ValueError("No default value defined for metadata {}".format(key))

                if isinstance(_default_value, int):
                    _value_type = "spinnerInt"
                elif isinstance(_default_value, float):
                    _value_type = "spinnerFloat"
                elif isinstance(_default_value, str):
                    _value_type = "string"

                if _enum:
                    _value_type = "combo"

                # if there is an enum value, it should be a combo box

                ui_definition["{}_override".format(key)] = {
                    "display_name": "Override {} :".format(key),
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


        # TODO resolution fallback need to be implemented and not hard coded
        # _resolution = self._parent_sub.metadata.get_value("resolution", [1920, 1080])

        # TODO settings data will be flat and will be created from the _ui_definition.
        # TODO This means everything under 'multi' type keys will moved into same level
        # _ui_definition = {
        #     "name":
        #        {
        #            "display_name": "Name :",
        #            "type": "validatedString",
        #            "value": "",
        #            "tooltip": "Name of the subproject",
        #        },
        #     "path":
        #        {
        #            "display_name": "Path :",
        #            "type": "string",
        #            "value": self._parent_sub.path,
        #            "tooltip": "Path of the subproject",
        #        },
        #     "resolution_override":
        #         {
        #             "display_name": "Override Resolution :",
        #             "type": "multi",
        #             "tooltip": "Override the resolution of the subproject. \
        #             If not checked, the resolution will be inherited from the parent.",
        #             "value": {
        #                 "overrideResolution": {
        #                     "type": "boolean",
        #                     "value": False,
        #                     "disables": [[False, "resolutionX"], [False, "resolutionY"]]
        #                 },
        #                 "resolutionX": {
        #                     "type": "spinnerInt",
        #                     "value": _resolution[0],
        #                 },
        #                 "resolutionY": {
        #                     "type": "spinnerInt",
        #                     "value": _resolution[1],
        #                 }
        #             }
        #         },
        #     "fps_override":
        #         {
        #             "display_name": "FPS Override :",
        #             "type": "multi",
        #             "tooltip": "Override the FPS of the subproject. \
        #             If not checked, the FPS will be inherited from the parent.",
        #             "value": {
        #                 "overrideFPS": {
        #                     "type": "boolean",
        #                     "value": False,
        #                     "disables": [[False, "fps"]]
        #                 },
        #                 "fps": {
        #                     "type": "spinnerInt",
        #                     "object_name": "fps",
        #                     "value": self._parent_sub.metadata.get_value("fps", 24),
        #                 }
        #             }
        #         },
        #     "mode_override":
        #         {
        #             "display_name": "Mode Override :",
        #             "type": "multi",
        #             "tooltip": "Override the mode of the subproject. \
        #             If not checked, the mode will be inherited from the parent.",
        #             "value": {
        #                 "overrideMode": {
        #                     "type": "boolean",
        #                     "value": False,
        #                     "disables": [[False, "mode"]]
        #                 },
        #                 "mode": {
        #                     "type": "combo",
        #                     "object_name": "mode",
        #                     "items": ["", "asset", "shot"],
        #                     "value": self._parent_sub.metadata.get_value("mode") or "",
        #                 }
        #             }
        #         }
        # }

        return ui_definition

    def _init_ui(self):
        """Initialize the UI."""
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.settings_data = Settings()
        self.settings_layout = SettingsLayout(self.ui_definition, self.settings_data, parent=self)
        self.main_layout.addLayout(self.settings_layout)
        # create a button box
        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        # get the name ValidatedString widget and connect it to the ok button
        _name_line_edit = self.settings_layout.find("name")
        _name_line_edit.add_connected_widget(self.button_box.button(QtWidgets.QDialogButtonBox.Ok))
        self.main_layout.addWidget(self.button_box)
        # SIGNALS
        self.button_box.accepted.connect(self.on_create_subproject)
        self.button_box.rejected.connect(self.reject)

    def on_create_subproject(self):
        # name = self.settings_data.get_property("name")
        # path = self.settings_data.get_property("path")

        # resolution_override = self.settings_data.get_property("overrideResolution")
        # if resolution_override:
        #     _resolution_x = self.settings_data.get_property("resolutionX")
        #     _resolution_y = self.settings_data.get_property("resolutionY")
        #     resolution = [_resolution_x, _resolution_y]
        # else:
        #     resolution = None
        #
        # fps_override = self.settings_data.get_property("overrideFPS")
        # if fps_override:
        #     fps = self.settings_data.get_property("fps")
        # else:
        #     fps = None
        #
        # mode_override = self.settings_data.get_property("overrideMode")
        # if mode_override:
        #     mode = self.settings_data.get_property("mode")
        # else:
        #     mode = None

        # build a new kwargs dictionary by filtering the settings_data
        filtered_data = {}
        for key, value in self.settings_data.get_data().items():
            print(self.settings_data.get_data().keys())
            # if it starts __override, skip
            if key.startswith("__override"):
                continue
            # if the key has a __override key, check if it is True
            _override_key = "__override_{}".format(key)
            # if the _override_key is in the settings_data and it is True, add the key to the filtered_data
            if _override_key not in list(self.settings_data.get_data().keys()):
                filtered_data[key] = value
            # if "__override_{}".format(key) in self.settings_data.keys():
            #     if self.settings_data.get_property("__override_{}".format(key)):
            #         filtered_data[key] = value
            else:
                if self.settings_data.get_property(_override_key):
                    filtered_data[key] = value

        # sub = self.tik_project.create_sub_project(name, parent_path=path, resolution=resolution, fps=fps, mode=mode)
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
    tik.user._set("Admin", "1234")
    tik.project._set(test_project_path)
    dialog = NewSubproject(tik.project)
    dialog.show()
    app.exec_()

    sys.exit(app.exec_())