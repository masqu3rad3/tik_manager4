"""Dialogs for creating work files and versions of them."""

from pathlib import Path
import dataclasses

from tik_manager4.core.settings import Settings
from tik_manager4.ui.Qt import QtWidgets, QtCore
from tik_manager4.ui.dialog.data_containers import MainLayout
from tik_manager4.ui.widgets.common import HeaderLabel, ResolvedText
from tik_manager4.ui.dialog.feedback import Feedback
import tik_manager4.ui.layouts.settings_layout
from tik_manager4.ui.widgets.common import TikButtonBox


@dataclasses.dataclass
class WidgetsData:
    """Data for the widgets"""

    header_lbl: QtWidgets.QLabel = None
    resolved_path_lbl: ResolvedText = None
    resolved_name_lbl: ResolvedText = None
    name_le: QtWidgets.QLineEdit = None
    subproject_widget: QtWidgets.QWidget = None
    tasks_combo: QtWidgets.QComboBox = None
    categories_combo: QtWidgets.QComboBox = None
    notes_lbl: QtWidgets.QLabel = None
    notes_te: QtWidgets.QPlainTextEdit = None
    create_btn: QtWidgets.QPushButton = None
    cancel_btn: QtWidgets.QPushButton = None


class NewWorkDialog(QtWidgets.QDialog):
    """Dialog for creating new work files."""

    def __init__(
        self,
        main_object,
        subproject=None,
        task_object=None,
        category_object=None,
        subproject_id=None,
        task_id=None,
        category_index=None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.feedback = Feedback(parent=self)
        self.main_object = main_object
        self.setWindowTitle("Create New Work File")

        # variables
        self.subproject = subproject
        self.task = task_object
        self.category = category_object

        # layouts
        self.layouts = MainLayout()
        self.widgets = WidgetsData()

        # if no objects are given, try to resolve them from the given data
        if not any([subproject, task_object, category_object]):
            self.resolve_objects(subproject_id, task_id, category_index)

        self.category_index = category_index or self.main_object.user.last_category

        # create the main layout

        self.build_layouts()

        self.primary_definition = self.define_primary_ui()
        self.primary_data = Settings()
        self.primary_content = None

        self.build_ui()

        self.update_labels(True)

        # focus on notes widget
        self.widgets.notes_te.setFocus()

    def build_layouts(self):
        """Create the layouts and split the UI into left and right."""
        self.layouts.master_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layouts.master_layout)
        self.layouts.header_layout = QtWidgets.QVBoxLayout()
        self.layouts.master_layout.addLayout(self.layouts.header_layout)

        self.layouts.splitter = QtWidgets.QSplitter(self)
        self.layouts.splitter.setHandleWidth(10)
        self.layouts.splitter.setCollapsible(0, False)
        self.layouts.splitter.setCollapsible(1, False)

        self.layouts.master_layout.addWidget(self.layouts.splitter)
        self.layouts.splitter.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.layouts.splitter.setOrientation(QtCore.Qt.Horizontal)

        # left widget and layout
        left_widget = QtWidgets.QWidget(self.layouts.splitter)
        self.layouts.left_layout = QtWidgets.QVBoxLayout(left_widget)
        self.layouts.left_layout.setContentsMargins(10, 2, 2, 10)

        # right widget and layout
        right_widget = QtWidgets.QWidget(self.layouts.splitter)
        self.layouts.right_layout = QtWidgets.QVBoxLayout(right_widget)
        self.layouts.right_layout.setContentsMargins(10, 2, 2, 10)

        self.layouts.buttons_layout = QtWidgets.QHBoxLayout()
        self.layouts.master_layout.addLayout(self.layouts.buttons_layout)

    def build_ui(self):
        """Build the UI elements"""

        self.widgets.header_lbl = HeaderLabel("New Work")
        self.widgets.header_lbl.set_color("orange")
        self.layouts.header_layout.addWidget(self.widgets.header_lbl)
        self.widgets.resolved_path_lbl = ResolvedText("" * 30)
        self.widgets.resolved_path_lbl.set_color("gray")
        self.layouts.header_layout.addWidget(self.widgets.resolved_path_lbl)
        self.widgets.resolved_name_lbl = ResolvedText("")
        self.widgets.resolved_name_lbl.set_color("#FF8D1C")
        self.layouts.header_layout.addWidget(self.widgets.resolved_name_lbl)

        self.primary_content = tik_manager4.ui.layouts.settings_layout.SettingsLayout(
            self.primary_definition, self.primary_data, parent=self
        )
        self.layouts.left_layout.addLayout(self.primary_content)
        self.widgets.name_le = self.primary_content.find("name")
        self.widgets.subproject_widget = self.primary_content.find("subproject")
        self.widgets.tasks_combo = self.primary_content.find("task")
        self.widgets.categories_combo = self.primary_content.find("category")
        file_format_combo = self.primary_content.find("file_format")
        # allow empty for the name widget.
        self.widgets.name_le.allow_empty = True

        # create a notes widget for the right side
        self.widgets.notes_lbl = QtWidgets.QLabel(text="Notes:")
        self.widgets.notes_te = QtWidgets.QPlainTextEdit()

        self.layouts.right_layout.addWidget(self.widgets.notes_lbl)
        self.layouts.right_layout.addWidget(self.widgets.notes_te)

        # create a the TikButtonBox
        button_box = TikButtonBox(parent=self)
        self.widgets.create_btn = button_box.addButton(
            "Create Work", QtWidgets.QDialogButtonBox.AcceptRole
        )
        self.widgets.cancel_btn = button_box.addButton(
            "Cancel", QtWidgets.QDialogButtonBox.RejectRole
        )
        self.layouts.buttons_layout.addWidget(button_box)

        self.widgets.subproject_widget.sub.connect(self.refresh_subproject)
        self.widgets.tasks_combo.currentTextChanged.connect(self.set_task)
        self.widgets.categories_combo.currentTextChanged.connect(self.set_category)
        self.widgets.name_le.validation_changed.connect(self.update_labels)
        file_format_combo.currentTextChanged.connect(self.update_labels)

        self.widgets.name_le.add_connected_widget(self.widgets.create_btn)

        button_box.accepted.connect(self.on_create_work)
        button_box.rejected.connect(self.reject)

    def update_labels(self, validation_status):
        """Update the path and name labels."""
        _name = self.primary_content.settings_data.get_property("name")
        _file_format = self.primary_content.settings_data.get_property("file_format")
        if not self.category:
            self.widgets.resolved_path_lbl.setText("Path cannot be resolved")
            self.widgets.resolved_name_lbl.setText("Name cannot be resolved")
            return

        _name = self.primary_content.settings_data.get_property("name")
        if not validation_status:
            self.widgets.resolved_name_lbl.setText("Invalid name")
        else:
            constructed_name = f"{self.category.construct_name(_name)}{_file_format}"
            self.widgets.resolved_name_lbl.setText(constructed_name)

        constructed_path = self.category.get_relative_work_path()
        self.widgets.resolved_path_lbl.setText(constructed_path)

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
                "display_name": "Label",
                "type": "validatedString",
                "value": "",
                "tooltip": "Name of the work file that will be added as a label tag.",
                "placeholder": "(Optional)",
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
        self.widgets.tasks_combo.clear()
        self.widgets.categories_combo.clear()
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
        self.update_labels(True)

    def refresh_tasks(self, tasks):
        """Refresh the task and below."""
        task_names = list(tasks.keys())
        task_names.sort()
        self.task = tasks[task_names[0]]
        categories = self.task.categories

        # block the signals
        self.widgets.tasks_combo.blockSignals(True)
        self.widgets.tasks_combo.clear()
        self.widgets.tasks_combo.addItems(task_names)
        self.widgets.tasks_combo.setCurrentIndex(0)
        self.widgets.tasks_combo.blockSignals(False)

        if categories:
            self.refresh_categories(categories)

    def refresh_categories(self, categories):
        """Refresh the categories."""

        category_names = self.task.get_property("categories")
        self.category = categories[category_names[0]]
        # block the signals
        self.widgets.categories_combo.blockSignals(True)
        self.widgets.categories_combo.clear()
        self.widgets.categories_combo.addItems(category_names)
        self.widgets.categories_combo.setCurrentIndex(0)
        self.widgets.categories_combo.blockSignals(False)

    def set_task(self, task_name):
        """Set the task from the index."""
        if not task_name:
            return
        self.task = self.subproject.tasks[task_name]
        self.refresh_categories(self.task.categories)
        self.update_labels(True)
        return self.task

    def set_category(self, category_name):
        """Set the category from the index."""
        if not category_name:
            return
        self.category = self.task.categories[category_name]
        self.update_labels(True)
        return self.category

    def on_create_work(self):
        """Create the work file."""
        name = self.primary_data.get_property("name")
        file_format = self.primary_data.get_property("file_format")
        notes = self.widgets.notes_te.toPlainText()

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
            _format = self.work_object.versions[-1].file_format or self.work_object._dcc_handler.formats[0]
            # _format = self.work_object.versions[-1].get(
            #     "file_format", self.work_object._dcc_handler.formats[0]
            # )
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


class WorkFromTemplateDialog(NewWorkDialog):
    """Dialog to create a work file from a template file."""

    def __init__(self, main_object, template_names=None, *args, **kwargs):
        self.template_names = template_names
        super().__init__(main_object, *args, **kwargs)
        self.setWindowTitle("Create Work From Template")
        self.widgets.header_lbl.setText("Create Work From Template")
        self.widgets.header_lbl.set_color("green")

        # hide the file_format widget
        self.file_format_widget = self.primary_content.find("file_format")
        self.file_format_widget.hide()
        self.file_format_widget.label.hide()

    def define_primary_ui(self):

        # available_templates = self.main_object.get_template_names()

        _primary_ui = {
            "template": {
                "display_name": "Template",
                "type": "combo",
                "items": self.template_names,
                "value": self.template_names[0],
                "tooltip": "Template file to create the work from",
            }
        }
        _orig_dict = super().define_primary_ui()
        _primary_ui.update(_orig_dict)
        return _primary_ui

    def on_create_work(self):
        """Create the work file."""
        template_name = self.primary_data.get_property("template")
        name = self.primary_data.get_property("name")
        notes = self.widgets.notes_te.toPlainText()
        #
        # resolve the template file.
        dcc_name, template_path = self.main_object.get_template_path_by_name(
            template_name
        )
        self.category.create_work_from_template(
            name, template_path, dcc=dcc_name, ignore_checks=True, notes=notes
        )
        self.accept()


class SaveAnyFileDialog(NewWorkDialog):
    """Dialog to save any file or folder to the tik manager 4 project."""

    def __init__(self, main_object, file_or_folder_path=None, *args, **kwargs):
        self._file_or_folder_path = file_or_folder_path
        super().__init__(main_object, *args, **kwargs)

        if not file_or_folder_path:
            raise ValueError("file_or_folder_path is not given.")

        self.setWindowTitle("Save Any File or Folder")
        self.widgets.header_lbl.setText("Save Any File or Folder")
        self.widgets.header_lbl.set_color("magenta")

        self.file_or_folder_path_lbl = ResolvedText(f"Saving: {file_or_folder_path}")
        self.file_or_folder_path_lbl.set_color("magenta")
        self.layouts.header_layout.insertWidget(1, self.file_or_folder_path_lbl)

        # find the file_format widget and its label and hide them
        self.file_format_widget = self.primary_content.find("file_format")
        self.file_format_widget.hide()
        self.file_format_widget.label.hide()

        self.resize(500, 300)
        self.layouts.splitter.setSizes([200, 150])

    def on_create_work(self):
        """Create the work file."""
        name = self.primary_data.get_property("name")
        override_dcc = self.primary_data.get_property("override_dcc")
        notes = self.widgets.notes_te.toPlainText()
        #
        self.category.create_work_from_path(
            name, self._file_or_folder_path, override_dcc=override_dcc, ignore_checks=True, notes=notes
        )
        self.accept()

    def __get_matching_dccs(self, suffix):
        """Get the matching DCCs for the given suffix."""
        for dcc_name, extensions in self.main_object.all_dcc_extensions.items():
            if suffix in extensions:
                yield dcc_name

    def define_primary_ui(self):
        _primary_ui = super().define_primary_ui()
        # override the format with the defined file paths extension
        _path_obj = Path(self._file_or_folder_path)
        stem = _path_obj.stem
        # replace all non-alphanumeric characters with underscores
        _name = "".join([x if x.isalnum() else "_" for x in stem])
        # get the matching extensions
        matching_dccs = list(self.__get_matching_dccs(_path_obj.suffix))
        matching_dccs.append("standalone")

        update_dict = {
            "override_dcc": {
                "display_name": "DCC override",
                "type": "combo",
                "items": matching_dccs,
                "value": matching_dccs[0],
                "tooltip": "DCC to use for the work file",
            },
            "name": {
                "display_name": "Name",
                "type": "validatedString",
                "value": _name,
                "tooltip": "Name of the work file",
            },
            "file_format": {
                "display_name": "File Format",
                "type": "combo",
                "items": [_path_obj.suffix],
                "value": _path_obj.suffix,
            },
        }
        _primary_ui.update(update_dict)
        return _primary_ui


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
