"""Dialog for new subproject creation."""
import sys
from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.ui.dialog import feedback

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

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
        self._init_ui()

        self._new_subproject = None

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


        self.resolution_lbl = QtWidgets.QLabel("Resolution: ")
        self.resolution_hlay = QtWidgets.QHBoxLayout()
        self.resolution_x_sp = QtWidgets.QSpinBox()
        self.resolution_y_sp = QtWidgets.QSpinBox()
        self.resolution_hlay.addWidget(self.resolution_x_sp)
        self.resolution_hlay.addWidget(self.resolution_y_sp)
        self.resolution_x_sp.setRange(1, 99999)
        self.resolution_y_sp.setRange(1, 99999)
        self.resolution_x_sp.setValue(self._parent_sub.resolution[0])
        self.resolution_y_sp.setValue(self._parent_sub.resolution[1])
        self.resolution_x_sp.setFixedWidth(100)
        self.resolution_y_sp.setFixedWidth(100)
        self.resolution_x_sp.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.resolution_y_sp.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.form_layout.addRow(self.resolution_lbl, self.resolution_hlay)

        self.fps_lbl = QtWidgets.QLabel("FPS: ")
        self.fps_sp = QtWidgets.QSpinBox()
        self.fps_sp.setValue(self._parent_sub.fps)
        self.fps_sp.setRange(1, 99999)
        self.fps_sp.setFixedWidth(100)
        self.fps_sp.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.form_layout.addRow(self.fps_lbl, self.fps_sp)

        self.mode_lbl = QtWidgets.QLabel("Mode: ")
        self.mode_cb = QtWidgets.QComboBox()
        self.mode_cb.addItems(["None", "Asset", "Shot"])
        # select the mode of the parent subproject
        if self._parent_sub.mode.lower() == "asset":
            self.mode_cb.setCurrentIndex(1)
        elif self._parent_sub.mode.lower() == "shot":
            self.mode_cb.setCurrentIndex(2)
        else:
            self.mode_cb.setCurrentIndex(0)
        self.form_layout.addRow(self.mode_lbl, self.mode_cb)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.create_button = QtWidgets.QPushButton("Create")
        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addWidget(self.create_button)
        self.main_layout.addLayout(self.button_layout)

        self.cancel_button.clicked.connect(self.close)
        self.create_button.clicked.connect(self.create_subproject)

    def create_subproject(self):
        name = self.name_le.text()
        path = self.path_le.text()
        resolution = [self.resolution_x_sp.value(), self.resolution_y_sp.value()]
        fps = self.fps_sp.value()
        mode = self.mode_cb.currentText()
        sub = self.tik_project.create_sub_project(str(name), parent_path=path, resolution=resolution, fps=fps, mode=mode)

        if sub != -1:
            self._new_subproject = sub
            self.accept()
        else:
            msg, title = self.tik_project.log.get_last_message()
            self._feedback.pop_info(title, msg, critical=True)

    def get_created_subproject(self):
        return self._new_subproject