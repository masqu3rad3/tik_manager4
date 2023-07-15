"""Dialogs for creating work files and versions of them."""

from tik_manager4.core.settings import Settings
from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
from tik_manager4.ui.widgets.common import TikButtonBox, HeaderLabel, ResolvedText
from tik_manager4.ui.dialog.feedback import Feedback
import tik_manager4.ui.layouts.settings_layout
from tik_manager4.ui.widgets.common import TikButtonBox

class NewWorkDialog(QtWidgets.QDialog):
    def __init__(self, main_object, subproject=None, task=None, category=None, subproject_id=None, task_id=None, category_index=None, *args, **kwargs):
        super(NewWorkDialog, self).__init__(*args, **kwargs)

        self.feedback = Feedback(parent=self)
        self.tik = main_object

        self.subproject = subproject
        self.task = task
        self.category = category

        # if no objects are given, try to resolve them from the given data
        if not any([subproject, task, category]):
            self.resolve_objects(subproject_id, task_id, category_index)


        self.category_index = category_index or self.tik.user.last_category

        self.setWindowTitle("Create New Work File")
        self.resize(600, 350)

        # create the main layout
        self.master_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.master_layout)

        splitter = QtWidgets.QSplitter(self)
        splitter.setHandleWidth(3)

        self.master_layout.addWidget(splitter)
        splitter.setFrameShape(QtWidgets.QFrame.NoFrame)
        splitter.setOrientation(QtCore.Qt.Horizontal)

        # left widget and layout
        left_widget = QtWidgets.QWidget(splitter)
        self.left_layout = QtWidgets.QVBoxLayout(left_widget)
        self.left_layout.setContentsMargins(10, 2, 2, 10)

        # right widget and layout
        right_widget = QtWidgets.QWidget(splitter)
        self.right_layout = QtWidgets.QVBoxLayout(right_widget)
        self.right_layout.setContentsMargins(10, 2, 2, 10)

        self.primary_definition = self.define_primary_ui()
        self.primary_data = Settings()

        self.build_ui()

        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)

    def resolve_objects(self, subproject_id=None, task_id=None, category_index=None):
        """Try to resolve the objects from the given data or last state."""

        subproject_id = subproject_id or self.tik.user.last_subproject
        if subproject_id:
            _subproject = self.tik.project.find_sub_by_id(subproject_id)
            if _subproject != 1:
                self.subproject = _subproject
                task_id = task_id or self.tik.user.last_task
                if task_id:
                    _task = self.subproject.find_task_by_id(task_id)
                    if _task != -1:
                        self.task = _task
                        category_index = category_index or self.tik.user.last_category or 0
                        _category_name = self.task.get_property("categories")[category_index]
                        self.category = self.task.categories[_category_name]

    def define_primary_ui(self):
        """Define the primary UI elements with settings layout"""
        sub_path = self.subproject.path if self.subproject else ""
        tasks = list(self.subproject.tasks.keys()) if self.subproject else []
        task_name = self.task.name if self.task else ""
        categories = list(self.task.categories.keys()) if self.task else []
        category_name = self.category.name if self.category else ""
        _primary_ui = {
            "subproject": {
                "display_name": "Sub-project",
                "type": "subprojectBrowser",
                "project_object": self.tik.project,
                "value": sub_path,
                "tooltip": "Path of the sub-project"
            },
            "task": {
                "display_name": "Task",
                "type": "combo",
                "items": tasks,
                "value": task_name,
                "tooltip": "Name of the Task"
            },
            "category": {
                "display_name": "Category",
                "type": "combo",
                "items": categories,
                "value": category_name,
                "tooltip": "Category of the work file"
            },
            "name": {
                "display_name": "Name",
                "type": "validatedString",
                "value": "",
                "tooltip": "Name of the work file"
                },
            "file_format": {
                "display_name": "File Format",
                "type": "combo",
                "items": self.tik.dcc.formats,
                "value": self.tik.dcc.formats[0],
                "tooltip": "File format of the work file"
            }
        }

        return _primary_ui

    def refresh_subproject(self, subproject):
        """Refresh the subproject and below."""
        self.subproject = subproject
        self.tasks_combo.clear()
        self.categories_combo.clear()
        tasks = subproject.scan_tasks()
        if tasks:
            self.refresh_tasks(tasks)


    def refresh_tasks(self, tasks):
        """Refresh the task and below."""
        task_names = list(tasks.keys())
        task_names.sort()
        self.task = tasks[task_names[0]]
        categories = self.task.categories

        # block the signals
        self.tasks_combo.blockSignals(True)
        self.tasks_combo.clear()
        self.tasks_combo.addItems(task_names)
        self.tasks_combo.setCurrentIndex(0)
        self.tasks_combo.blockSignals(False)

        if categories:
            self.refresh_categories(categories)

    def refresh_categories(self, categories):
        """Refresh the categories."""

        category_names = self.task.get_property("categories")
        self.category = categories[category_names[0]]
        # block the signals
        self.categories_combo.blockSignals(True)
        self.categories_combo.clear()
        self.categories_combo.addItems(category_names)
        self.categories_combo.setCurrentIndex(0)
        self.categories_combo.blockSignals(False)

    def set_task(self, task_name):
        """Set the task from the index."""
        self.task = self.subproject.tasks[task_name]
        self.refresh_categories(self.task.categories)

    def set_category(self, category_name):
        """Set the category from the index."""
        self.category = self.task.categories[category_name]

    def on_create_work(self):
        """Create the work file."""
        name = self.primary_data.get_property("name")
        file_format = self.primary_data.get_property("file_format")
        notes = self.notes_te.toPlainText()
        # print(name, file_format, notes)
        self.category.create_work(name, file_format=file_format, notes=notes)
        self.accept()

    def build_ui(self):
        """Build the UI elements"""

        self.primary_content = tik_manager4.ui.layouts.settings_layout.SettingsLayout(self.primary_definition, self.primary_data, parent=self)
        self.left_layout.addLayout(self.primary_content)

        _name_line_edit = self.primary_content.find("name")

        _browse_subproject_widget = self.primary_content.find("subproject")
        _browse_subproject_widget.sub.connect(self.refresh_subproject)

        self.tasks_combo = self.primary_content.find("task")
        # self.tasks_combo.current.connect(self.populate_categories)
        self.tasks_combo.currentTextChanged.connect(self.set_task)

        self.categories_combo = self.primary_content.find("category")
        self.categories_combo.currentTextChanged.connect(self.set_category)

        # create a notes widget for the right side
        notes_lbl = QtWidgets.QLabel(text="Notes:")
        self.notes_te = QtWidgets.QPlainTextEdit()
        self.right_layout.addWidget(notes_lbl)
        self.right_layout.addWidget(self.notes_te)

        # create a the TikButtonBox
        button_box = TikButtonBox(parent=self)
        create_work_btn = button_box.addButton("Create Work", QtWidgets.QDialogButtonBox.AcceptRole)
        cancel_btn = button_box.addButton("Cancel", QtWidgets.QDialogButtonBox.RejectRole)
        self.master_layout.addWidget(button_box)

        _name_line_edit.add_connected_widget(create_work_btn)

        button_box.accepted.connect(self.on_create_work)
        button_box.rejected.connect(self.reject)










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
        if _version != -1:
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
    dialog = NewWorkDialog(main_object=tik)
    # dialog = NewVersionDialog(work_object=work)
    _style_file = pick.style_file()
    dialog.setStyleSheet(str(_style_file.readAll(), 'utf-8'))
    dialog.show()
    sys.exit(app.exec_())