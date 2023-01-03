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


        self.populate_settings()
        self._init_ui()

        self._new_task = None

    def populate_settings(self):
        """Populate settings."""

        # _mode = self._parent_sub.mode or ""
        _mode = self._parent_sub.metadata.get_value("mode", "")
        if _mode.lower() == "asset":
            _default_categories = self.tik_project.guard.asset_categories
        elif _mode.lower() == "shot":
            _default_categories = self.tik_project.guard.shot_categories
        else:
            _default_categories = self.tik_project.guard.null_categories

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
        self.settings.add_property("categories", {
            "display_name": "Categories :",
            "type": "list",
            "value": _default_categories
        })

    def _init_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.settings_layout = SettingsLayout(self.settings, parent=self)
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
            # path=self.settings.get_property("path")["value"],
            categories=self.settings.get_property("categories")["value"],
            parent_uid=self._parent_sub.id,
        )
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
