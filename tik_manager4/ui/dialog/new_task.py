"""Dialog for new subproject creation."""
import sys
from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.ui.dialog import feedback

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

class NewTask(QtWidgets.QDialog):
    def __init__(self, project_object, parent_sub=None, parent=None, *args, **kwargs):
        """
        Dialog for new subproject creation.

        """
        super(NewTask, self).__init__(parent=parent, *args, **kwargs)
        self.tik_project = project_object
        self._parent_sub = parent_sub or project_object
        self.parent = parent
        self._feedback = feedback.Feedback(parent=self)
        self.setWindowTitle("New Task")
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setFixedSize(600, 400)
        self.setModal(True)
        self._init_ui()

        self._new_task = None

    def _init_ui(self):

        self.main_layout = QtWidgets.QVBoxLayout(self)

        self.form_layout = QtWidgets.QFormLayout()
        self.main_layout.addLayout(self.form_layout)

        self.name_lbl = QtWidgets.QLabel("Name: ")
        self.name_le = QtWidgets.QLineEdit()
        self.form_layout.addRow(self.name_lbl, self.name_le)

        self.path_lbl = QtWidgets.QLabel("Path: ")
        self.path_le = QtWidgets.QLineEdit()
        self.path_le.setText(self._parent_sub.path)
        self.form_layout.addRow(self.path_lbl, self.path_le)

        # categories
        self.categories_lbl = QtWidgets.QLabel("Categories: ")

        print(self._parent_sub.name)
        print(self._parent_sub.mode)
        if self._parent_sub:
            _mode = self._parent_sub.mode
            if _mode.lower() == "asset":
                _default_categories = self.tik_project.guard.asset_categories
            elif _mode.lower() == "shot":
                _default_categories = self.tik_project.guard.shot_categories
            else:
                _default_categories = self.tik_project.guard.null_categories
        else:
            _default_categories = self.tik_project.guard.null_categories

        self.categories_lay = QtWidgets.QHBoxLayout()
        self.categories_list = QtWidgets.QListWidget()
        self.categories_list.addItems(_default_categories)
        self.categories_lay.addWidget(self.categories_list)

        self.categories_buttons_lay = QtWidgets.QVBoxLayout()
        self.categories_lay.addLayout(self.categories_buttons_lay)
        self.add_category_btn = QtWidgets.QPushButton("Add")
        self.remove_category_btn = QtWidgets.QPushButton("Remove")
        self.move_category_up_btn = QtWidgets.QPushButton("Up")
        self.move_category_down_btn = QtWidgets.QPushButton("Down")
        self.categories_buttons_lay.addWidget(self.add_category_btn)
        self.categories_buttons_lay.addWidget(self.remove_category_btn)
        self.categories_buttons_lay.addWidget(self.move_category_up_btn)
        self.categories_buttons_lay.addWidget(self.move_category_down_btn)

        self.form_layout.addRow(self.categories_lbl, self.categories_lay)

    #     self.resolution_lbl = QtWidgets.QLabel("Resolution: ")
    #     self.resolution_hlay = QtWidgets.QHBoxLayout()
    #     self.resolution_x_sp = QtWidgets.QSpinBox()
    #     self.resolution_y_sp = QtWidgets.QSpinBox()
    #     self.resolution_hlay.addWidget(self.resolution_x_sp)
    #     self.resolution_hlay.addWidget(self.resolution_y_sp)
    #     self.resolution_x_sp.setRange(1, 99999)
    #     self.resolution_y_sp.setRange(1, 99999)
    #     self.resolution_x_sp.setValue(self._parent_sub.resolution[0])
    #     self.resolution_y_sp.setValue(self._parent_sub.resolution[1])
    #     self.resolution_x_sp.setFixedWidth(100)
    #     self.resolution_y_sp.setFixedWidth(100)
    #     self.resolution_x_sp.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
    #     self.resolution_y_sp.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
    #     self.form_layout.addRow(self.resolution_lbl, self.resolution_hlay)
    #
    #     self.fps_lbl = QtWidgets.QLabel("FPS: ")
    #     self.fps_sp = QtWidgets.QSpinBox()
    #     self.fps_sp.setValue(self._parent_sub.fps)
    #     self.fps_sp.setRange(1, 99999)
    #     self.fps_sp.setFixedWidth(100)
    #     self.fps_sp.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
    #     self.form_layout.addRow(self.fps_lbl, self.fps_sp)
    #
    #     self.mode_lbl = QtWidgets.QLabel("Mode: ")
    #     self.mode_cb = QtWidgets.QComboBox()
    #     self.mode_cb.addItems(["None", "Asset", "Shot"])
    #     # select the mode of the parent subproject
    #     if self._parent_sub.mode.lower() == "asset":
    #         self.mode_cb.setCurrentIndex(1)
    #     elif self._parent_sub.mode.lower() == "shot":
    #         self.mode_cb.setCurrentIndex(2)
    #     else:
    #         self.mode_cb.setCurrentIndex(0)
    #     self.form_layout.addRow(self.mode_lbl, self.mode_cb)
    #
    #     self.button_layout = QtWidgets.QHBoxLayout()
    #     self.cancel_button = QtWidgets.QPushButton("Cancel")
    #     self.create_button = QtWidgets.QPushButton("Create")
    #     self.button_layout.addWidget(self.cancel_button)
    #     self.button_layout.addWidget(self.create_button)
    #     self.main_layout.addLayout(self.button_layout)
    #
    #     self.cancel_button.clicked.connect(self.close)
    #     self.create_button.clicked.connect(self.create_subproject)
    #
    # def create_subproject(self):
    #     name = self.name_le.text()
    #     path = self.path_le.text()
    #     resolution = [self.resolution_x_sp.value(), self.resolution_y_sp.value()]
    #     fps = self.fps_sp.value()
    #     mode = self.mode_cb.currentText()
    #     sub = self.tik_project.create_sub_project(str(name), parent_path=path, resolution=resolution, fps=fps, mode=mode)
    #
    #     if sub != -1:
    #         self._new_subproject = sub
    #         self.accept()
    #     else:
    #         msg, title = self.tik_project.log.get_last_message()
    #         self._feedback.pop_info(title, msg, critical=True)
    #
    # def get_created_subproject(self):
    #     return self._new_subproject

