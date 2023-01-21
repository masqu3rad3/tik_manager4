"""Dialog for new subproject creation."""
import sys
from tik_manager4.core.settings import Settings
from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
from tik_manager4.ui import utils
from tik_manager4.ui.dialog import feedback
from tik_manager4.ui.widgets.settings_layout import SettingsLayout

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

        # TODO resolution fallback need to be implemented and not hard coded
        _resolution = self._parent_sub.metadata.get_value("resolution", [1920, 1080])

        # TODO settings data will be flat and will be created from the _ui_definition.
        # TODO This means everything under 'multi' type keys will moved into same level
        # TODO We need to make sure that the sub-keys under 'value' in 'multi' type are unique
        _ui_definition = {
            "name":
               {
                   "display_name": "Name :",
                   "type": "validatedString",
                   "value": "",
               },
            "path":
               {
                   "display_name": "Path :",
                   "type": "string",
                   "value": self._parent_sub.path,
               },
            "resolution_override":
                {
                    "display_name": "Override Resolution :",
                    "type": "multi",
                    "value": {
                        "overrideResolution": {
                            "type": "boolean",
                            "value": False,
                            "disables": [[False, "resolutionX"], [False, "resolutionY"]]
                        },
                        "resolutionX": {
                            "type": "spinnerInt",
                            "value": _resolution[0],
                        },
                        "resolutionY": {
                            "type": "spinnerInt",
                            "value": _resolution[1],
                        }
                    }
                },
            "fps_override":
                {
                    "display_name": "FPS Override :",
                    "type": "multi",
                    "value": {
                        "overrideFPS": {
                            "type": "boolean",
                            "value": False,
                            "disables": [[False, "fps"]]
                        },
                        "fps": {
                            "type": "spinnerInt",
                            "object_name": "fps",
                            "value": self._parent_sub.metadata.get_value("fps", 24),
                        }
                    }
                },
            "mode_override":
                {
                    "display_name": "Mode Override :",
                    "type": "multi",
                    "value": {
                        "overrideMode": {
                            "type": "boolean",
                            "value": False,
                            "disables": [[False, "mode"]]
                        },
                        "mode": {
                            "type": "combo",
                            "object_name": "mode",
                            "items": ["", "asset", "shot"],
                            "value": self._parent_sub.metadata.get_value("mode") or "",
                        }
                    }
                }
        }

        return _ui_definition

    # def define_initial_settings_data(self):
    #     """Create a flat dictionary by grabbing the values from the ui_definition."""
    #
    #     _settings_data = Settings()
    #     for _key, _value in self.ui_definition.items():
    #         _settings_data.set_value(_key, _value["value"])



        # self.ui_definition.add_property("name", {
        #     "display_name": "Name :",
        #     "type": "validatedString",
        #     "value": "",
        # })
        # self.ui_definition.add_property("path", {
        #     "display_name": "Path :",
        #     "type": "string",
        #     "value": self._parent_sub.path,
        # })


        # _resolution = self._parent_sub.metadata.get_value("resolution", [1920, 1080])
        # self.ui_definition.add_property("resolution_override", {
        #     "display_name": "Override Resolution :",
        #     "type": "multi",
        #     "value": {
        #         "override": {
        #             "type": "boolean",
        #             "value": False,
        #             "disables": [[False, "resolutionX"], [False, "resolutionY"]]
        #         },
        #         "resolutionX": {
        #             "type": "spinnerInt",
        #             "value": _resolution[0],
        #         },
        #         "resolutionY": {
        #             "type": "spinnerInt",
        #             "value": _resolution[1],
        #         }
        #     }
        # })
        # self.ui_definition.add_property("fps_override", {
        #     "display_name": "FPS Override :",
        #     "type": "multi",
        #     "value": {
        #         "override": {
        #             "type": "boolean",
        #             "value": False,
        #             "disables": [[False, "fps"]]
        #         },
        #         "fps": {
        #             "type": "spinnerInt",
        #             "object_name": "fps",
        #             "value": self._parent_sub.metadata.get_value("fps", 24),
        #         }
        #     }
        # })
        # self.ui_definition.add_property("mode_override", {
        #     "display_name": "Mode Override :",
        #     "type": "multi",
        #     "value": {
        #         "override": {
        #             "type": "boolean",
        #             "value": False,
        #             "disables": [[False, "mode"]]
        #         },
        #         "mode": {
        #             "type": "combo",
        #             "object_name": "mode",
        #             "items": ["", "asset", "shot"],
        #             "value": self._parent_sub.metadata.get_value("mode") or "",
        #         }
        #     }
        # })

    def _init_ui(self):

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
        name = self.settings_data.get_property("name")
        path = self.settings_data.get_property("path")

        resolution_override = self.settings_data.get_property("overrideResolution")
        if resolution_override:
            _resolution_x = self.settings_data.get_property("resolutionX")
            _resolution_y = self.settings_data.get_property("resolutionY")
            resolution = [_resolution_x, _resolution_y]
        else:
            resolution = None

        fps_override = self.settings_data.get_property("overrideFPS")
        if fps_override:
            fps = self.settings_data.get_property("fps")
        else:
            fps = None

        mode_override = self.settings_data.get_property("overrideMode")
        if mode_override:
            mode = self.settings_data.get_property("mode")
        else:
            mode = None

        sub = self.tik_project.create_sub_project(name, parent_path=path, resolution=resolution, fps=fps, mode=mode)
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