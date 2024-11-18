"""Dialog for setting project."""

import os

from pathlib import Path
from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
from tik_manager4.ui.widgets import path_browser
from tik_manager4.ui.widgets.common import TikButton, TikButtonBox
from tik_manager4.ui.dialog.feedback import Feedback
from tik_manager4.ui.widgets.value_widgets import DropList
from tik_manager4.ui.dialog.subproject_dialog import EditSubprojectDialog, FilteredData
from tik_manager4.ui.mcv.management_mcv import SgProjectPickWidget
from tik_manager4.ui.widgets.pop import WaitDialog


class SetProjectDialog(QtWidgets.QDialog):
    def __init__(self, main_object, parent=None, *args, **kwargs):
        self.main_object = main_object
        super().__init__(parent=parent)
        self.feedback = Feedback(parent=self)
        self.setWindowTitle("Set Project")
        self.setModal(True)

        self.setMinimumSize(982, 450)
        self.setFocus()

        self.active_project = None
        self.build_ui()

        self.populate_bookmarks()

    def build_ui(self):
        """Build the UI."""
        main_layout = QtWidgets.QVBoxLayout(self)
        header_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(header_layout)
        split_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(split_layout)
        splitter = QtWidgets.QSplitter()
        # splitter.setHandleWidth(20)
        split_layout.addWidget(splitter)
        folders_tree_widget = QtWidgets.QWidget(splitter)
        folders_tree_layout = QtWidgets.QVBoxLayout(folders_tree_widget)
        folders_tree_layout.setContentsMargins(0, 0, 0, 0)
        bookmarks_widget = QtWidgets.QWidget(splitter)
        bookmarks_layout = QtWidgets.QVBoxLayout(bookmarks_widget)
        bookmarks_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(buttons_layout)

        look_in_lbl = QtWidgets.QLabel(text="Look in:")
        browser_wgt = path_browser.PathBrowser("lookIn")
        browser_wgt.widget.setText(self.main_object.project.folder)
        header_layout.addWidget(look_in_lbl)
        header_layout.addWidget(browser_wgt)

        recent_pb = TikButton(text="Recent")
        recent_pb.setToolTip("Recent projects")
        header_layout.addWidget(recent_pb)

        # projects side
        self.folders_tree = QtWidgets.QTreeView(
            splitter,
            minimumSize=QtCore.QSize(0, 0),
            dragEnabled=True,
            dragDropMode=QtWidgets.QAbstractItemView.DragOnly,
            selectionMode=QtWidgets.QAbstractItemView.SingleSelection,
            itemsExpandable=False,
            rootIsDecorated=False,
            sortingEnabled=True,
            frameShape=QtWidgets.QFrame.NoFrame,
        )
        folders_tree_layout.addWidget(self.folders_tree)
        directory_filter = QtWidgets.QLineEdit()
        directory_filter.setPlaceholderText("Filter")
        folders_tree_layout.addWidget(directory_filter)

        self.source_model = QtWidgets.QFileSystemModel()
        self.source_model.setNameFilterDisables(False)
        self.source_model.setNameFilters(["*"])
        self.source_model.setRootPath(self.main_object.project.folder)
        self.source_model.setFilter(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot)
        self.folders_tree.setModel(self.source_model)
        self.set_tree_root(self.main_object.project.folder)
        self.folders_tree.setColumnWidth(0, 400)
        self.folders_tree.setColumnWidth(1, 0)
        self.folders_tree.setColumnWidth(2, 0)
        selection_model = self.folders_tree.selectionModel()

        self.bookmarks_droplist = DropList(
            name="Bookmarks", buttons_position="down", buttons=["+", "-"]
        )
        plus_btn = self.bookmarks_droplist.buttons[0]
        minus_btn = self.bookmarks_droplist.buttons[1]
        bookmarks_layout.addWidget(self.bookmarks_droplist)

        # make the right side of the splitter stretchable
        splitter.setStretchFactor(0, 1)

        # buttons
        # create a button box as "set" and "cancel"
        button_box = TikButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons_layout.addWidget(button_box)

        # SIGNALS
        self.bookmarks_droplist.dropped.connect(self.on_drag_and_drop)
        plus_btn.clicked.connect(self.on_add_bookmark)
        minus_btn.clicked.connect(self.on_remove_bookmark)

        button_box.accepted.connect(self.set_and_close)
        button_box.rejected.connect(self.close)
        self.bookmarks_droplist.list.doubleClicked.connect(
            lambda: self.set_and_close()  # pylint: disable=unnecessary-lambda
        )  # lambda is needed to pass the argument
        selection_model.selectionChanged.connect(self.activate_folders)
        self.bookmarks_droplist.list.currentRowChanged.connect(self.activate_bookmarks)
        recent_pb.clicked.connect(self.recents_pop_menu)
        browser_wgt.com.valueChanged.connect(self.set_tree_root)

    def set_tree_root(self, root_path):
        """Set the root of the tree to the given path."""
        # set the root of the model to e
        self.folders_tree.setRootIndex(self.source_model.index(root_path))

    def recents_pop_menu(self):
        """Pop menu for recent projects."""
        recents_list = reversed(self.main_object.user.get_recent_projects())

        zort_menu = QtWidgets.QMenu(self)
        for p in recents_list:
            _temp_action = QtWidgets.QAction(p, self)
            zort_menu.addAction(_temp_action)
            _temp_action.triggered.connect(
                lambda _ignore=p, item=p: self.set_and_close(item)
            )

        return bool(zort_menu.exec_((QtGui.QCursor.pos())))

    def activate_folders(self):
        """Get the active project from folders tree and
        clear the bookmarks area selection.
        """
        index = self.folders_tree.currentIndex()
        self.active_project = os.path.normpath(
            self.folders_tree.model().filePath(index)
        )
        self.bookmarks_droplist.list.clearSelection()

    def activate_bookmarks(self, row):
        """Get the active project from bookmarks and clear the
        folders tree area selection."""
        if row != -1:
            self.active_project = self.main_object.user.get_project_bookmarks()[row]
            self.folders_tree.clearSelection()

    def set_and_close(self, project_path=None):
        """Set the active project and close the dialog."""
        project_to_set = project_path or self.active_project
        if not project_to_set:
            self.feedback.pop_info(
                title="Cannot set project",
                text="No project selected.\nPlease select a project from \
                the folders or bookmarks and press 'Set'",
            )
            return
        self.main_object.set_project(project_to_set)
        self.accept()
        # self.close()

    def on_add_bookmark(self):
        """Called when the add bookmark button is clicked."""
        idx = self.folders_tree.currentIndex()
        if idx.isValid():
            path = self.folders_tree.model().filePath(idx)
            self.main_object.user.add_project_bookmark(path)
            self.populate_bookmarks()

    def on_remove_bookmark(self):
        """Called when the remove bookmark button is clicked."""
        row = self.bookmarks_droplist.list.currentRow()
        if row != -1:
            p_path = self.main_object.user.get_project_bookmarks()[row]
            self.main_object.user.delete_project_bookmark(p_path)
            self.populate_bookmarks()

    def on_drag_and_drop(self, p_path):
        """Called when a path is dropped to the dialog."""
        norm_path = os.path.normpath(p_path)
        self.main_object.user.add_project_bookmark(norm_path)
        self.populate_bookmarks()

    def populate_bookmarks(self):
        """Populate the bookmarks list."""
        self.bookmarks_droplist.list.clear()
        self.bookmarks_droplist.list.addItems(self.main_object.user.bookmark_names)


class NewProjectDialog(EditSubprojectDialog):
    """Dialog for creating a new project"""

    feedback = Feedback()

    def __init__(self, main_object, *args, **kwargs):
        self.main_object = main_object
        self.structure_list = list(
            self.main_object.user.commons.structures.properties.values()
        )
        super().__init__(main_object.project, *args, **kwargs)
        self.structure_data = None
        self.set_after_create_cb = None

        self.setWindowTitle("Create New Project")
        self.setMinimumSize(300, 200)
        self.resize(600, 650)
        self.primary_layout.set_hidden(False)
        self.tertiary_layout.set_hidden(True)

        self.secondary_layout.label.setText("Root Properties")
        self.tertiary_layout.label.setHidden(True)

    def _get_metadata_override(self, key):
        """Override the function to return always False."""
        _key = key
        return False

    def define_primary_ui(self):
        """Define the primary UI."""
        _structure_names = [x["name"] for x in self.structure_list]
        _primary_ui = {
            "project_root": {
                "display_name": "Projects Root :",
                "type": "pathBrowser",
                # "type": "subprojectBrowser",
                "project_object": self.tik_project,
                "value": os.path.dirname(self.tik_project.absolute_path),
                "tooltip": "Root for the projects",
            },
            "project_name": {
                "display_name": "Project Name :",
                "type": "validatedString",
                "value": "",
                "tooltip": "Name of the Project",
            },
            "structure_template": {
                "display_name": "Template :",
                "type": "combo",
                "items": _structure_names,
                "value": "Empty Project",
                "tooltip": "Pick a template to start with",
            },
        }
        return _primary_ui

    def define_other_ui(self, structure_template=None):
        """Define the secondary UI."""
        _secondary_ui = {}
        _tertiary_ui = {}

        # The next part of metadata is for displaying and overriding
        # the existing metadata keys in the stream
        for key, data in self.metadata_definitions.properties.items():
            _value_type, _default_value, _enum = self._get_metadata_type(data)
            if _default_value is None:
                raise ValueError(f"No default value defined for metadata {key}")
            _check = False
            if structure_template:
                _structure_value = structure_template.get(key, None)
                if _structure_value is not None:
                    _default_value = _structure_value
                    _check = True

            _secondary_ui[key] = {
                "display_name": f"{key} :",
                "type": "multi",
                "tooltip": f"New {key}",
                "value": {
                    f"__new_{key}": {
                        "type": "boolean",
                        "value": _check,
                        "disables": [[False, key]],
                    },
                    key: {
                        "type": _value_type,
                        "value": _default_value,
                        "items": _enum,
                    },
                },
            }
        return _secondary_ui, _tertiary_ui

    def on_structure_template_changed(self, index):
        """Override the function to update the metadata."""
        # find the structure template in self.structure_dictionary by name
        self.structure_data = self.structure_list[index]
        self.secondary_ui, _ = self.define_other_ui(self.structure_data)
        self.secondary_content.clear()
        self.secondary_content.initialize(self.secondary_ui, self.secondary_data)

    def build_ui(self):
        """Initialize the UI."""
        super(NewProjectDialog, self).build_ui()

        # create a button box
        # get the name ValidatedString widget and connect it to the ok button
        _name_line_edit = self.primary_content.find("project_name")
        _name_line_edit.add_connected_widget(
            self.button_box.button(QtWidgets.QDialogButtonBox.Ok)
        )
        template_widget = self.primary_content.find("structure_template")

        template_widget.currentIndexChanged.connect(self.on_structure_template_changed)

        # run it once to update the secondary ui
        self.on_structure_template_changed(template_widget.currentIndex())

        # create a checkbox to switch to the new project after creation
        self.set_after_create_cb = QtWidgets.QCheckBox("Set After Creation")
        self.set_after_create_cb.setChecked(True)
        self.button_box_layout.addWidget(self.set_after_create_cb)

    def _execute(self):
        """Create the project."""
        # build a new kwargs dictionary by filtering the settings_data
        path = os.path.join(
            self.primary_data.get_property("project_root"),
            self.primary_data.get_property("project_name"),
        )

        # get the primary data
        filtered_data = FilteredData(
            structure_data=self.structure_data,
            set_after_creation=self.set_after_create_cb.isChecked(),
        )

        # filtered_data.update_overridden_data(self.secondary_data)
        filtered_data.update_new_data(self.secondary_data)

        self.main_object.create_project(path, **filtered_data)
        # close the dialog
        self.accept()


class CreateFromShotgridDialog(QtWidgets.QDialog):
    """Create a new project from the management system."""

    def __init__(self, management_handler, parent=None):
        super().__init__(parent=parent)
        all_widgets = QtWidgets.QApplication.allWidgets()
        for entry in all_widgets:
            try:
                if entry.objectName() == "CreateFromShotgridDialog":
                    entry.close()
                    entry.deleteLater()
            except (AttributeError, TypeError):
                pass

        self.tik = management_handler.tik_main
        self.feedback = Feedback(parent=self)
        self.handler = management_handler
        self.setWindowTitle("Create New Project from Shotgrid")
        self.setObjectName("CreateFromShotgridDialog")
        self.setModal(True)
        self.setMinimumSize(300, 200)
        self.resize(600, 650)

        self.master_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.master_layout)
        self.project_root_pathb = None
        self.set_project_cb = None
        self.sg_project_pick_widget = None
        self.build_ui()

    def build_ui(self):
        """Build the UI."""
        # path browser
        path_browser_layout = QtWidgets.QHBoxLayout()
        self.master_layout.addLayout(path_browser_layout)
        path_browser_lbl = QtWidgets.QLabel("Projects Root :")
        path_browser_layout.addWidget(path_browser_lbl)
        _value = Path(self.tik.project.absolute_path).parent.as_posix()
        self.project_root_pathb = path_browser.PathBrowser("project_root", value=_value)
        path_browser_layout.addWidget(self.project_root_pathb)

        self.sg_project_pick_widget = SgProjectPickWidget(self.handler, parent=self)
        self.master_layout.addWidget(self.sg_project_pick_widget)

        # create a button box as "create" and "cancel"
        button_box = TikButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )

        button_layout = QtWidgets.QHBoxLayout()
        self.master_layout.addLayout(button_layout)
        create_btn = button_box.button(QtWidgets.QDialogButtonBox.Ok)
        create_btn.setText("Create")
        button_layout.addWidget(button_box)

        self.set_project_cb = QtWidgets.QCheckBox("Set After Creation")
        self.set_project_cb.setChecked(True)
        button_layout.addWidget(self.set_project_cb)

        # SIGNALS
        button_box.accepted.connect(self.execute)
        button_box.rejected.connect(self.close)

    def execute(self):
        """Create the project."""
        project_root = self.project_root_pathb.widget.text()
        project_id = self.sg_project_pick_widget.get_selected_project_id()
        if project_id:
            self.wait_dialog = WaitDialog(
                message="Creating project from Shotgrid...",
                parent=self,
            )
            self.wait_dialog.show_dialog()

            ret = self.handler.create_from_project(
                project_root, project_id, set_project=self.set_project_cb.isChecked()
            )
            self.wait_dialog.close_dialog()
            if not ret:
                msg, _msg_type = self.tik.log.get_last_message()
                self.feedback.pop_info(
                    title="Error Creating Project", text=msg, critical=True
                )
                return
                # get the last log message from the logger
        else:
            self.feedback.pop_info(
                title="No Project Selected",
                text="Please select a project from the list.",
                critical=True
            )
            return
        self.accept()


# Test the set project dialog
if __name__ == "__main__":
    import sys
    import tik_manager4
    from tik_manager4.ui import pick
    from tik_manager4 import management

    app = QtWidgets.QApplication(sys.argv)
    tik = tik_manager4.initialize("Standalone")
    handler = management.platforms["shotgrid"](tik)
    # dialog = SetProjectDialog(tik)
    dialog = CreateFromShotgridDialog(handler)
    _style_file = pick.style_file()
    dialog.setStyleSheet(str(_style_file.readAll(), "utf-8"))
    dialog.show()
    sys.exit(app.exec_())
