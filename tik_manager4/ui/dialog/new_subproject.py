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
        self.settings = Settings()
        self.setWindowTitle("New Subproject")
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setFixedSize(600, 400)
        self.setModal(True)
        self.populate_settings()
        self._init_ui()

        self._new_subproject = None

    def populate_settings(self):
        self.settings.add_property("name", {
            "display_name": "Name :",
            "type": "string",
            "value": "",
        })
        self.settings.add_property("path", {
            "display_name": "Path :",
            "type": "string",
            "value": self._parent_sub.path,
        })
        self.settings.add_property("resolution_override", {
            "display_name": "Override Resolution :",
            "type": "multi",
            "value": {
                "override": {
                    "type": "boolean",
                    "value": False,
                    "disables": [[False, "resolutionX"], [False, "resolutionY"]]
                },
                "resolutionX": {
                    "type": "spinnerInt",
                    "value": self._parent_sub.resolution[0],
                },
                "resolutionY": {
                    "type": "spinnerInt",
                    "value": self._parent_sub.resolution[1],
                }
            }
        })
        self.settings.add_property("fps_override", {
            "display_name": "FPS Override :",
            "type": "multi",
            "value": {
                "override": {
                    "type": "boolean",
                    "value": False,
                    "disables": [[False, "fps"]]
                },
                "fps": {
                    "type": "spinnerInt",
                    "object_name": "fps",
                    "value": self._parent_sub.fps,
                }
            }
        })
        self.settings.add_property("mode_override", {
            "display_name": "Mode Override :",
            "type": "multi",
            "value": {
                "override": {
                    "type": "boolean",
                    "value": False,
                    "disables": [[False, "mode"]]
                },
                "mode": {
                    "type": "combo",
                    "object_name": "mode",
                    "items": ["", "asset", "shot"],
                    "value": self._parent_sub.mode,
                }
            }
        })

    def _init_ui(self):

        self.main_layout = QtWidgets.QVBoxLayout(self)

        self.settings_layout = SettingsLayout(self.settings, parent=self)
        self.main_layout.addLayout(self.settings_layout)

        # create a button box
        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.main_layout.addWidget(self.button_box)

        # SIGNALS
        self.button_box.accepted.connect(self.create_subproject)
        self.button_box.rejected.connect(self.reject)

    def create_subproject(self):
        name = self.settings.get_property("name")["value"]
        path = self.settings.get_property("path")["value"]

        resolution_override = self.settings.get_sub_property(["resolution_override", "value", "override", "value"])
        if resolution_override:
            _resolution_x = self.settings.get_sub_property(["resolution_override", "value", "resolutionX", "value"])
            _resolution_y = self.settings.get_sub_property(["resolution_override", "value", "resolutionY", "value"])
            resolution = [_resolution_x, _resolution_y]
        else:
            resolution = None

        fps_override = self.settings.get_sub_property(["fps_override", "value", "override", "value"])
        if fps_override:
            fps = self.settings.get_sub_property(["fps_override", "value", "fps", "value"])
        else:
            fps = None

        mode_override = self.settings.get_sub_property(["mode_override", "value", "override", "value"])
        if mode_override:
            mode = self.settings.get_sub_property(["mode_override", "value", "mode", "value"])
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
    tik.user.set("Admin", "1234")
    tik.project.set(test_project_path)
    dialog = NewSubproject(tik.project)
    dialog.show()
    app.exec_()

    sys.exit(app.exec_())