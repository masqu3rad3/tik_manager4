"""Dialogs for creating work files and versions of them."""

from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
from tik_manager4.ui.widgets.common import TikButtonBox, HeaderLabel, ResolvedText
from tik_manager4.ui.dialog.feedback import Feedback

class NewWorkDialog(QtWidgets.QDialog):
    def __init__(self, category_object, *args, **kwargs):
        super(NewWorkDialog, self).__init__(*args, **kwargs)

        self.feedback = Feedback(parent=self)
        category_object = category_object

        self.setWindowTitle("Create New Work File")


        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.create_widgets()
        self.create_layout()
        self.create_connections()


class NewVersionDialog(QtWidgets.QDialog):
    def __init__(self, work_object, ingest=False, *args, **kwargs):
        super(NewVersionDialog, self).__init__(*args, **kwargs)

        self.feedback = Feedback(parent=self)
        self.work_object = work_object

        self.ingest = ingest
        _title = "New Version" if not self.ingest else "Ingest Version"
        self.setWindowTitle(_title)
        # self.setMinimumSize(500, 150)
        # self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.master_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.master_layout)

        self.build_ui()
        # resize the dialog slightly bigger than actually is
        size_hint = self.sizeHint()
        self.resize(QtCore.QSize(size_hint.width() + 10, 300))

    def build_ui(self):

        header = HeaderLabel(self.windowTitle())
        _color = "orange" if not self.ingest else "pink"
        header.set_color(_color)
        # header.set_color("rgb(255, 255, 255)")
        self.master_layout.addWidget(header)

        path = self.work_object.path
        _version_number, version_name, _thumbnail_name = self.work_object.construct_names(self.work_object._dcc_handler.formats[0])

        path_label = ResolvedText(path)
        path_label.set_color("gray")
        self.name_label = ResolvedText(version_name)
        self.name_label.set_color("rgb(0, 150, 200)")

        self.master_layout.addWidget(path_label)
        self.master_layout.addWidget(self.name_label)

        notes_label = QtWidgets.QLabel("Notes: ")
        self.notes_text = QtWidgets.QPlainTextEdit()
        self.notes_text.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.notes_text.setMinimumHeight(50)
        # make its initial size not bigger than the minimum size
        self.notes_text.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

        self.master_layout.addWidget(notes_label)
        self.master_layout.addWidget(self.notes_text)
        # self.master_layout.addStretch(0)

        # format
        self.format_combo = QtWidgets.QComboBox()
        self.format_combo.addItems(self.work_object._dcc_handler.formats)
        # align texts in combo to the right
        self.format_combo.setItemDelegate(QtWidgets.QStyledItemDelegate())
        self.master_layout.addWidget(self.format_combo)

        # add a separator before buttons
        separator = QtWidgets.QLabel()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        # separator.setStyleSheet("background-color: rgb(174, 215, 91);")
        separator.setFixedHeight(10)
        self.master_layout.addWidget(separator)

        # buttons
        button_box = TikButtonBox()
        button_box.addButton("Create New Version", QtWidgets.QDialogButtonBox.AcceptRole)
        button_box.addButton("Cancel", QtWidgets.QDialogButtonBox.RejectRole)
        self.master_layout.addWidget(button_box)

        # Signals
        button_box.accepted.connect(self.on_create_version)
        self.format_combo.currentTextChanged.connect(self.on_format_changed)

    def on_create_version(self):
        _version = self.work_object.new_version(self.format_combo.currentText(), self.notes_text.toPlainText())
        if _version:
            self.accept()
        else:
            self.feedback.pop_info(title="Error", text="Could not create version. Check the script editor for details.", critical=True)
            self.reject()

    def on_format_changed(self, file_format):
        _version_number, version_name, _thumbnail_name = self.work_object.construct_names(file_format)
        self.name_label.setText(version_name)


# test this dialog
if __name__ == "__main__":
    import sys
    import tik_manager4
    from tik_manager4.ui import pick
    app = QtWidgets.QApplication(sys.argv)
    tik = tik_manager4.initialize("Standalone")
    tik.user.set("Admin", "1234")
    # tik.user.set("Generic", "1234")
    sub = tik.project.find_sub_by_path("Assets/Characters/Soldier")
    sub.scan_tasks()
    task = sub.tasks.get("bizarro")
    category = task.categories.get("Model")
    works = category.scan_works()
    work = list(works.values())[0]
    print(work)
    dialog = NewVersionDialog(work_object=work)
    _style_file = pick.style_file()
    dialog.setStyleSheet(str(_style_file.readAll(), 'utf-8'))
    dialog.show()
    sys.exit(app.exec_())