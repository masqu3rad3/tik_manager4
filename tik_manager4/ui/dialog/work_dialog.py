"""Dialogs for creating work files and versions of them."""

from tik_manager4.core.settings import Settings
from tik_manager4.ui.Qt import QtWidgets, QtCore
from tik_manager4.ui.widgets.common import HeaderLabel, ResolvedText
from tik_manager4.ui.dialog.feedback import Feedback
import tik_manager4.ui.layouts.settings_layout
from tik_manager4.ui.widgets.common import TikButtonBox


class NewWorkDialog(QtWidgets.QDialog):
    """Dialog for creating new work files."""
    def __init__(
        self,
        main_object,
        subproject=None,
        task=None,
        category=None,
        subproject_id=None,
        task_id=None,
        category_index=None,
        *args,
        **kwargs,
    ):
        super(NewWorkDialog, self).__init__(*args, **kwargs)

        self.feedback = Feedback(parent=self)
        self.main_object = main_object
        self.setWindowTitle("Create New Work File")

        # variables
        self.subproject = subproject
        self.task = task
        self.category = category

        self.header_layout = None
        self.left_layout = None
        self.right_layout = None
        self.buttons_layout = None

        self.resolved_path_lbl = None
        self.resolved_name_lbl = None

        # if no objects are given, try to resolve them from the given data
        if not any([subproject, task, category]):
            self.resolve_objects(subproject_id, task_id, category_index)

        self.category_index = category_index or self.main_object.user.last_category

        # create the main layout
        self.master_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.master_layout)

        self.build_layouts()

        self.primary_definition = self.define_primary_ui()
        self.primary_data = Settings()

        self.build_ui()

        self.update_labels(True)

        # self.resize(600, 350)
        # focus on notes widget
        self.notes_te.setFocus()

    def build_layouts(self):
        """Create the layouts and split the UI into left and right."""
        self.header_layout = QtWidgets.QVBoxLayout()
        self.master_layout.addLayout(self.header_layout)

        splitter = QtWidgets.QSplitter(self)
        splitter.setHandleWidth(10)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)

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

        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.master_layout.addLayout(self.buttons_layout)

    def build_ui(self):
        """Build the UI elements"""

        header = HeaderLabel("New Work")
        header.set_color("orange")
        self.header_layout.addWidget(header)
        self.resolved_path_lbl = ResolvedText("" * 30)
        self.resolved_path_lbl.set_color("gray")
        self.header_layout.addWidget(self.resolved_path_lbl)
        self.resolved_name_lbl = ResolvedText("")
        self.resolved_name_lbl.set_color("#FF8D1C")
        self.header_layout.addWidget(self.resolved_name_lbl)

        self.primary_content = tik_manager4.ui.layouts.settings_layout.SettingsLayout(
            self.primary_definition, self.primary_data, parent=self
        )
        self.left_layout.addLayout(self.primary_content)

        self.name_line_edit = self.primary_content.find("name")

        _browse_subproject_widget = self.primary_content.find("subproject")

        self.tasks_combo = self.primary_content.find("task")

        self.categories_combo = self.primary_content.find("category")

        _file_format = self.primary_content.find("file_format")

        # create a notes widget for the right side
        notes_lbl = QtWidgets.QLabel(text="Notes:")
        self.notes_te = QtWidgets.QPlainTextEdit()

        self.right_layout.addWidget(notes_lbl)
        self.right_layout.addWidget(self.notes_te)

        # create a the TikButtonBox
        button_box = TikButtonBox(parent=self)
        create_work_btn = button_box.addButton(
            "Create Work", QtWidgets.QDialogButtonBox.AcceptRole
        )
        _ = button_box.addButton("Cancel", QtWidgets.QDialogButtonBox.RejectRole)
        self.buttons_layout.addWidget(button_box)

        _browse_subproject_widget.sub.connect(self.refresh_subproject)
        self.tasks_combo.currentTextChanged.connect(self.set_task)
        self.categories_combo.currentTextChanged.connect(self.set_category)
        self.name_line_edit.validation_changed.connect(self.update_labels)
        _file_format.currentTextChanged.connect(self.update_labels)

        self.name_line_edit.add_connected_widget(create_work_btn)

        button_box.accepted.connect(self.on_create_work)
        button_box.rejected.connect(self.reject)

    def update_labels(self, validation_status):
        """Update the path and name labels."""
        _name = self.primary_content.settings_data.get_property("name")
        if not _name:
            self.resolved_name_lbl.setText("No Name Entered")
            # return
        elif not validation_status:
            self.resolved_name_lbl.setText("Invalid name")
            # return
        else:
            _file_format = self.primary_content.settings_data.get_property(
                "file_format"
            )
            constructed_name = f"{self.category.construct_name(_name)}{_file_format}"
            self.resolved_name_lbl.setText(constructed_name)

        if not self.category:
            self.resolved_path_lbl.setText("Path cannot be resolved")
        else:
            constructed_path = self.category.get_relative_work_path()
            self.resolved_path_lbl.setText(constructed_path)

    def resolve_objects(self, subproject_id=None, task_id=None, category_index=None):
        """Try to resolve the objects from the given data or last state."""

        subproject_id = subproject_id or self.main_object.user.last_subproject
        if subproject_id:
            _subproject = self.main_object.project.find_sub_by_id(subproject_id)
            if _subproject != 1:
                self.subproject = _subproject
                task_id = task_id or self.main_object.user.last_task
                if task_id:
                    _task = self.subproject.get_task_by_id(task_id)
                    if _task != -1:
                        self.task = _task
                        category_index = (
                            category_index or self.main_object.user.last_category or 0
                        )
                        _category_name = self.task.get_property("categories")[
                            category_index
                        ]
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
                "project_object": self.main_object.project,
                "value": sub_path,
                "tooltip": "Path of the sub-project",
            },
            "task": {
                "display_name": "Task",
                "type": "combo",
                "items": tasks,
                "value": task_name,
                "tooltip": "Name of the Task",
            },
            "category": {
                "display_name": "Category",
                "type": "combo",
                "items": categories,
                "value": category_name,
                "tooltip": "Category of the work file",
            },
            "name": {
                "display_name": "Name",
                "type": "validatedString",
                "value": "",
                "tooltip": "Name of the work file",
            },
            "file_format": {
                "display_name": "File Format",
                "type": "combo",
                "items": self.main_object.dcc.formats,
                "value": self.main_object.dcc.formats[0],
                "tooltip": "File format of the work file",
            },
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

        # reinitialize the primary UI but add the existing name and file format
        _name = self.primary_content.settings_data.get_property("name")
        _file_format = self.primary_content.settings_data.get_property("file_format")
        self.primary_content.settings_data.reset_settings()
        self.primary_content.settings_data.set_data(
            {"name": _name, "file_format": _file_format}
        )
        self.update_labels()

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
        if not task_name:
            return
        self.task = self.subproject.tasks[task_name]
        self.refresh_categories(self.task.categories)
        self.update_labels()
        return self.task

    def set_category(self, category_name):
        """Set the category from the index."""
        if not category_name:
            return
        self.category = self.task.categories[category_name]
        self.update_labels()
        return self.category

    def on_create_work(self):
        """Create the work file."""
        name = self.primary_data.get_property("name")
        file_format = self.primary_data.get_property("file_format")
        notes = self.notes_te.toPlainText()

        self.category.create_work(name, file_format=file_format, notes=notes)
        self.accept()


class NewVersionDialog(QtWidgets.QDialog):
    def __init__(self, work_object, ingest=False, *args, **kwargs):
        super(NewVersionDialog, self).__init__(*args, **kwargs)

        self.feedback = Feedback(parent=self)
        self.work_object = work_object

        self.ingest = ingest
        _title = "New Version" if not self.ingest else "Ingest Version"
        self.setWindowTitle(_title)

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
        self.master_layout.addWidget(header)

        path = self.work_object.path
        (
            _version_number,
            version_name,
            _thumbnail_name,
        ) = self.work_object.construct_names(self.work_object._dcc_handler.formats[0])

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
        self.notes_text.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum
        )

        self.master_layout.addWidget(notes_label)
        self.master_layout.addWidget(self.notes_text)

        # format
        self.format_combo = QtWidgets.QComboBox()
        self.format_combo.addItems(self.work_object._dcc_handler.formats)
        # align texts in combo to the right
        self.format_combo.setItemDelegate(QtWidgets.QStyledItemDelegate())
        # try to get the format from the last version and set it as current
        if self.work_object.versions:
            _format = self.work_object.versions[-1].get(
                "file_format", self.work_object._dcc_handler.formats[0]
            )
        else:
            _format = self.work_object._dcc_handler.formats[0]
        self.format_combo.setCurrentText(_format)
        self.on_format_changed(_format)  # initialize the name label with the format

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
        button_box.addButton(
            "Create New Version", QtWidgets.QDialogButtonBox.AcceptRole
        )
        button_box.addButton("Cancel", QtWidgets.QDialogButtonBox.RejectRole)
        self.master_layout.addWidget(button_box)

        # Signals
        button_box.accepted.connect(self.on_create_version)
        button_box.rejected.connect(self.reject)
        self.format_combo.currentTextChanged.connect(self.on_format_changed)

    def on_create_version(self):
        _version = self.work_object.new_version(
            self.format_combo.currentText(), self.notes_text.toPlainText()
        )
        if _version != -1:
            self.accept()
        else:
            self.feedback.pop_info(
                title="Error",
                text="Could not create version. Check the script editor for details.",
                critical=True,
            )
            self.reject()

    def on_format_changed(self, file_format):
        (
            _version_number,
            version_name,
            _thumbnail_name,
        ) = self.work_object.construct_names(file_format)
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
    dialog = NewWorkDialog(main_object=tik)
    _style_file = pick.style_file()
    dialog.setStyleSheet(str(_style_file.readAll(), "utf-8"))
    dialog.show()
    sys.exit(app.exec_())
