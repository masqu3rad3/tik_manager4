"""UI Layout for work and publish objects."""
from pathlib import Path

from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
from tik_manager4.ui.dialog.feedback import Feedback
from tik_manager4.ui.widgets.common import TikButton, VerticalSeparator
from tik_manager4.core import filelog
from tik_manager4.ui import pick

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")


class TikVersionLayout(QtWidgets.QVBoxLayout):
    """Layout for versioning work and publish objects."""
    def __init__(self, project_object, *args, **kwargs):
        """Initialize the TikVersionLayout."""
        super().__init__()
        self.project = project_object
        self.base = None  # this is work or publish object
        # get the parent widget
        self.parent = kwargs.get("parent")
        self.feedback = Feedback(parent=kwargs.get("parent"))

        self.label = QtWidgets.QLabel("Versions")
        self.label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.addWidget(self.label)
        self.addWidget(VerticalSeparator(color=(255, 180, 60)))

        version_layout = QtWidgets.QHBoxLayout()
        self.addLayout(version_layout)
        version_lbl = QtWidgets.QLabel(text="Version: ")
        # set the font size to 10
        version_lbl.setFont(QtGui.QFont("Arial", 10))
        version_lbl.setMinimumSize = QtCore.QSize(60, 30)
        version_lbl.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        version_layout.addWidget(version_lbl)

        self.version_combo = QtWidgets.QComboBox()
        self.version_combo.setMinimumSize(QtCore.QSize(60, 30))
        version_layout.addWidget(self.version_combo)

        self.show_preview_btn = TikButton()
        self.show_preview_btn.setText("Show Preview")
        self.show_preview_btn.setMinimumSize(QtCore.QSize(60, 30))
        self.show_preview_btn.setEnabled(False)
        version_layout.addWidget(self.show_preview_btn)

        element_layout = QtWidgets.QVBoxLayout()
        self.addLayout(element_layout)
        element_lbl = QtWidgets.QLabel("Element: ")
        element_lbl.setFont(QtGui.QFont("Arial", 10))
        element_layout.addWidget(element_lbl)
        self.element_combo = QtWidgets.QComboBox()
        element_layout.addWidget(self.element_combo)

        ingest_with_lbl = QtWidgets.QLabel("Ingest with: ")
        ingest_with_lbl.setFont(QtGui.QFont("Arial", 10))
        self.ingest_with_combo = QtWidgets.QComboBox()
        element_layout.addWidget(ingest_with_lbl)
        element_layout.addWidget(self.ingest_with_combo)

        notes_layout = QtWidgets.QVBoxLayout()
        self.addLayout(notes_layout)
        notes_lbl = QtWidgets.QLabel("Notes: ")
        notes_lbl.setFont(QtGui.QFont("Arial", 10))
        self.notes_editor = QtWidgets.QPlainTextEdit()
        self.notes_editor.setReadOnly(True)
        notes_layout.addWidget(notes_lbl)
        notes_layout.addWidget(self.notes_editor)

        self.thumbnail = ImageWidget()
        self.empty_pixmap = pick.pixmap("empty_thumbnail.png")
        # self.empty_pixmap = QtGui.QPixmap(":/images/CSS/rc/empty_thumbnail.png")
        self.thumbnail.setToolTip("Right Click for replace options")
        self.thumbnail.setProperty("image", True)
        self.thumbnail.setPixmap(self.empty_pixmap)

        self.thumbnail.setMinimumSize(QtCore.QSize(221, 124))
        self.thumbnail.setFrameShape(QtWidgets.QFrame.Box)
        self.thumbnail.setScaledContents(True)
        self.thumbnail.setAlignment(QtCore.Qt.AlignCenter)
        self.addWidget(self.thumbnail)

        # # buttons
        self.btn_layout = QtWidgets.QHBoxLayout()
        self.import_btn = TikButton("Import")
        self.load_btn = TikButton("Load")
        self.reference_btn = TikButton("Reference")
        self.btn_layout.addWidget(self.import_btn)
        self.btn_layout.addWidget(self.load_btn)
        self.btn_layout.addWidget(self.reference_btn)
        self.addLayout(self.btn_layout)
        self.import_btn.setEnabled(False)
        self.load_btn.setEnabled(False)
        self.reference_btn.setEnabled(False)

        self.ingest_mapping = {} # mapping of ingestor nice name to ingestor name
        self.element_mapping = {} # mapping of element type nice name to element type name

        # SIGNALS
        self.element_combo.currentTextChanged.connect(self.element_type_changed)
        self.version_combo.currentIndexChanged.connect(self.version_changed)
        self.import_btn.clicked.connect(self.on_import)
        self.load_btn.clicked.connect(self.on_load)
        self.reference_btn.clicked.connect(self.on_reference)

        self.version_combo.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.version_combo.customContextMenuRequested.connect(self.right_click_menu)

    def on_import(self):
        """Import the current version."""
        if not self.base:
            self.feedback.pop_info(
                title="No work or publish selected.",
                text="Please select a work or publish to import.",
                critical=True,
            )
            return
        _version = self.get_selected_version()
        _element_type = self.get_selected_element_type()
        _ingestor = self.get_selected_ingestor()
        self.base.import_version(
            _version, element_type=_element_type, ingestor=_ingestor
        )

    def _load_pre_checks(self, work_obj):
        """Metadata and scene compare checks before loading."""
        # there are some conditions we may want to skip the checks

        if self.base.object_type == "publish":
            element_type = self.get_selected_element_type()
            ingestor = self.get_selected_ingestor()
            # only check if both ingest and element types are "source"
            if all([element_type, ingestor]):
                if element_type != "source" or ingestor != "source":
                    return True


        if work_obj.dcc.lower() != work_obj.guard.dcc.lower():
            self.feedback.pop_info(
                title="DCC mismatch",
                text=f"{work_obj.dcc} scenes cannot loaded into {work_obj.guard.dcc}.",
                critical=True,
            )
            return False
        dcc_version_mismatch = work_obj.check_dcc_version_mismatch()
        if dcc_version_mismatch:
            question = self.feedback.pop_question(
                title="DCC version mismatch",
                text="The current DCC version does not match the version of the work or metadata definition.\n\n"
                f"Current DCC version: {dcc_version_mismatch[1]}\n"
                f"Defined DCC version: {dcc_version_mismatch[0]}\n\n"
                "Do you want to continue loading?",
                buttons=["continue", "cancel"]
            )
            if question == "cancel":
                return False
        return True

    def on_load(self):
        """Load the current version."""
        if not self.base:
            self.feedback.pop_info(
                title="No work or publish selected.",
                text="Please select a work or publish to load.",
                critical=True,
            )
            return

        element_type = self.get_selected_element_type()
        # ingestor = self.get_selected_ingestor()

        if self.base.object_type == "publish":
            work_obj = self.base.work_object
        else:
            work_obj = self.base

        if not self._load_pre_checks(work_obj):
            return

        _version = self.get_selected_version()
        # check if the current scene is modified.
        # if it is, ask if the user wants to save it
        if self.base._dcc_handler.is_modified():
            question = "Current scene is modified. Do you want to save it?"
            state = self.feedback.pop_question(
                title="Save current scene?",
                text=question,
                buttons=["yes", "no", "cancel"],
            )
            if state == "cancel":
                return
            if state == "yes":
                if self.base._dcc_handler.get_scene_file() == "":
                    _state = self.base._dcc_handler.save_prompt()
                    # if the save prompt is defined, it will do a recursive check.
                    # this is a safety procedure to prevent infinite recursion
                    # if the save prompts is not defined on a dcc.
                    # this is not working on NUKE at the moment.
                    if _state:
                        self.on_load()
                    return
                self.base._dcc_handler.save_scene()

        read_only = False
        if self.base.object_type == "publish":

            if self.base.dcc.lower() == self.base.guard.dcc.lower():
                question = "Publish versions are protected. The file will be loaded and saved as a new WORK version immediately.\n Do you want to continue?"
                state = self.feedback.pop_question(
                    title="Load publish version?",
                    text=question,
                    buttons=["yes", "cancel"],
                )
                if state == "cancel":
                    return
            else:
                question = f"Publish versions are protected. Do you want to continue with read-only mode?"
                state = self.feedback.pop_question(
                    title="Load publish version?",
                    text=question,
                    buttons=["yes", "cancel"],
                )
                if state == "cancel":
                    return
                else:
                    read_only = True

        self.base.load_version(_version, force=True, element_type=element_type, read_only=read_only)

    def on_reference(self):
        """Reference the current version."""
        if not self.base:
            self.feedback.pop_info(
                title="No work or publish selected.",
                text="Please select a work or publish to reference.",
                critical=True,
            )
            return
        if self.base.object_type == "work":
            state = self.feedback.pop_question(
                title="Referencing WORK version",
                text="WORK versions are not meant to be referenced as they are not protected.\n Do you want to continue?",
                buttons=["yes", "cancel"],
            )
            if state == "cancel":
                return

        _version = self.get_selected_version()
        # if self.base.object_type == "publish":
        _element_type = self.get_selected_element_type()
        _ingestor = self.get_selected_ingestor()
        self.base.reference_version(
            _version, element_type=_element_type, ingestor=_ingestor
        )

    def __load_btn_state(self, base, element_type):
        """Resolve the load button state."""

        # load button is enabled only if the base.dcc and base.guard.dcc are the same
        # it also requires the element_type to be source (in publish mode) or none (in work mode)
        if element_type == "source" or not element_type:
            self.load_btn.setEnabled(base.dcc == base.guard.dcc)
        else:
            _ingestor = self.get_selected_ingestor()
            if not _ingestor:
                self.load_btn.setEnabled(False)
                return
            dcc_extensions = base._dcc_handler.formats
            element_version_extension = self.__get_element_suffix(element_type)
            if element_version_extension in dcc_extensions:
                self.load_btn.setEnabled(True)
                return
            self.load_btn.setEnabled(False)

    def __import_and_reference_btn_states(self, base, element_type):
        """Resolve the import button state."""

        # if element_type == "source" or not element_type:
        #     self.import_btn.setEnabled(base.dcc == base.guard.dcc)
        #     self.reference_btn.setEnabled(base.dcc == base.guard.dcc)
        #     return

        # if the ingest combo is empty, disable the import and reference buttons
        _ingestor = self.get_selected_ingestor()
        if not _ingestor:
            self.import_btn.setEnabled(False)
            self.reference_btn.setEnabled(False)
            return
        # finally, check the ingestors importable and referencable status
        _importable = self.base._dcc_handler.ingests[_ingestor].importable
        _referenceable = self.base._dcc_handler.ingests[_ingestor].referencable
        self.import_btn.setEnabled(_importable)
        self.reference_btn.setEnabled(_referenceable)
        return

    def button_states(self, base):
        """Toggle the buttons depending on the base status."""
        if not base:
            self.load_btn.setEnabled(False)
            self.import_btn.setEnabled(False)
            self.reference_btn.setEnabled(False)
            return
        _element_type = self.get_selected_element_type()
        self.__load_btn_state(base, _element_type)
        self.__import_and_reference_btn_states(base, _element_type)

    def set_base(self, base):
        """Set the base object. This can be work or publish object."""
        self.version_combo.blockSignals(True)
        self.button_states(base)
        if not base:
            self.version_combo.clear()
            self.element_combo.clear()
            self.notes_editor.clear()
            self.thumbnail.clear()
            return
        self.base = base
        self.populate_versions(base.versions)
        self.version_combo.blockSignals(False)

    def populate_versions(self, versions):
        """Populate the version dropdown with the versions from the base object."""
        self.version_combo.blockSignals(True)
        self.version_combo.clear()
        for version in versions:
            # add the version number to the dropdown.
            # Version number is integer, convert it to string
            self.version_combo.addItem(str(version.get("version_number")))
        # alyways select the last version
        self.version_combo.setCurrentIndex(self.version_combo.count() - 1)

        # get the current selected version name from the version_dropdown
        self.version_changed()
        self.version_combo.blockSignals(False)

    def _resolve_available_ingests(self, version_extension):
        """Resolve the available ingestors for the given extension."""
        self.ingest_mapping = {}
        all_ingests = self.base._dcc_handler.ingests
        # go through all the ingests and check if the version extension is supported
        available_ingests = []
        for ingest_name, fn in all_ingests.items():
            if version_extension in fn.valid_extensions:
                # available_ingests.append(ingest_name)
                self.ingest_mapping[fn.nice_name] = ingest_name
                available_ingests.append(fn.nice_name)
        return available_ingests

    def version_changed(self):
        """When the version dropdown is changed, update the notes and thumbnail."""
        self.element_combo.blockSignals(True)
        self.ingest_with_combo.blockSignals(True)
        version_text = self.version_combo.currentText()
        if not version_text:
            return
        version_number = int(version_text)
        _index = self.version_combo.currentIndex()
        # check if the _index is the latest in combo box
        if _index == self.version_combo.count() - 1:
            self.version_combo.setProperty("preVersion", False)
        else:
            self.version_combo.setProperty("preVersion", True)
        self.version_combo.setStyleSheet("")

        _version = self.base.get_version(version_number)
        self.element_combo.clear()
        self.element_mapping.clear()
        if self.base.object_type == "publish":
            self.show_preview_btn.setEnabled(False)
            self.element_combo.setEnabled(True)
            self.ingest_with_combo.setEnabled(True)
            self.element_mapping = _version.element_mapping
            # self.element_combo.addItems(_version.element_types)
            self.element_combo.addItems(list(self.element_mapping.keys()))
            # trigger the element type changed manually
            self.element_type_changed(self.element_combo.currentText())
        else:  # WORK
            # disable
            self.element_combo.setEnabled(False)
            self.ingest_with_combo.setEnabled(False)
            # enable the show preview button if there are previews
            self.show_preview_btn.setEnabled(bool(_version.get("previews")))
        self.notes_editor.clear()
        self.thumbnail.clear()
        self.notes_editor.setPlainText(_version.get("notes"))
        _thumbnail_path = self.base.get_abs_database_path(_version.get("thumbnail", ""))
        if Path(_thumbnail_path).is_file():
            self.thumbnail.setPixmap(QtGui.QPixmap(_thumbnail_path))
        else:
            self.thumbnail.setPixmap(self.empty_pixmap)
        self.element_combo.blockSignals(False)
        self.ingest_with_combo.blockSignals(False)

    def __get_element_suffix(self, element_type):
        """Find the extension for the given element type of selected version."""
        _version_number = self.get_selected_version()
        _version_object = self.base.get_version(_version_number)
        return _version_object.get_element_suffix(element_type)

    def element_type_changed(self, element_name):
        """Update the rest when element type is changed."""
        element_type = self.element_mapping.get(element_name, None)
        self.ingest_with_combo.clear()
        if not element_type:
            return
        element_version_extension = self.__get_element_suffix(element_type)
        _available_ingests = self._resolve_available_ingests(element_version_extension)
        # update the ingest with combo
        self.ingest_with_combo.addItems(_available_ingests)
        # if there is an ingestor with the same name as the element type, select it
        if element_type in _available_ingests:
            self.ingest_with_combo.setCurrentText(element_type)

        # update the buttons
        self.button_states(self.base)
        return

    def set_version(self, combo_value):
        """Set the version dropdown to the given version value."""
        # check if the value exists in the version dropdown

        self.version_combo.setCurrentText(str(combo_value))

    def get_selected_version(self):
        """Return the current version."""
        selected_version_as_str = self.version_combo.currentText()
        if not selected_version_as_str:
            return None
        version_number = int(selected_version_as_str)
        return version_number
        # Following returns the dictionary. We probably won't need it.

    def get_selected_element_type(self):
        """Return the current element."""
        if self.element_combo.isEnabled():
            # return self.element_combo.currentText()
            key = self.element_combo.currentText()
            return self.element_mapping.get(key, None)
        else:
            return None

    def get_selected_ingestor(self):
        """Return the selected ingestor."""
        if self.ingest_with_combo.isEnabled():
            # return self.ingest_with_combo.currentText()
            key = self.ingest_with_combo.currentText()
            return self.ingest_mapping.get(key, None)
        else:
            return None

    def delete_version(self):
        """Delete the selected Work or Publish version."""
        if not self.base:
            self.feedback.pop_info(
                title="No work or publish selected.",
                text="Please select a work or publish to delete.",
                critical=True,
            )
            return
        _version = self.get_selected_version()

        state, msg = self.base.check_delete_version_permissions(_version)
        if state != 1:
            self.feedback.pop_info(
                title="Permission Error",
                text=msg,
                critical=True,
            )
            return

        if self.base.object_type == "work":
            _name = self.base.get_version(_version).get("scene_path", "")
            are_you_sure = self.feedback.pop_question(
                title="Delete Work Version",
                text="You are about to delete a work version:\n\n"
                     f"{_name}\n\n"
                     "This action cannot be undone.\n"
                     "Do you want to continue?",
                buttons=["yes", "cancel"]
                )
            if are_you_sure == "cancel":
                return
        elif self.base.object_type == "publish":
            _name = self.base.get_version(_version).get("name", "")
            are_you_sure = self.feedback.pop_question(
                title="Delete Publish Version",
                text="You are about to delete a PUBLISH version:\n\n"
                     f"{_name}\n\n"
                     "This action cannot be undone.\n"
                     "Do you want to continue?",
                buttons=["yes", "cancel"]
                )
            if are_you_sure == "cancel":
                return

        self.base.delete_version(_version)
        # repopulate the combo box
        self.populate_versions(self.base.versions)

    def refresh(self):
        """Refresh the version dropdown."""
        if self.base:
            self.base.reload()
            self.populate_versions(self.base.versions)
        else:
            self.version_combo.clear()
            self.notes_editor.clear()
            self.thumbnail.clear()

    def right_click_menu(self, position):
        """Right click menu for the version dropdown."""

        right_click_menu = QtWidgets.QMenu()
        right_click_menu.setStyleSheet(self.parent.styleSheet())  # Add this line

        delete_version_action = QtWidgets.QAction(self.tr("Delete Version"), self)
        right_click_menu.addAction(delete_version_action)
        delete_version_action.triggered.connect(self.delete_version)

        right_click_menu.addSeparator()
        if self.base.object_type == "work":
            publish_snapshot_act = right_click_menu.addAction(
                self.tr("Publish Snapshot")
            )
            publish_snapshot_act.triggered.connect(
                self.publish_snapshot
            )

        right_click_menu.exec_((QtGui.QCursor.pos()))

    def publish_snapshot(self):
        """Publish a snapshot of the current work."""
        if not self.base.object_type == "work":
            LOG.warning("Publish snapshot is only available for work objects.")
            return -1
        self.project.snapshot_publisher.work_object = self.base
        self.project.snapshot_publisher.work_version = self.get_selected_version()
        self.project.snapshot_publisher.resolve()
        self.project.snapshot_publisher.reserve()
        self.project.snapshot_publisher.extract()
        published_object = self.project.snapshot_publisher.publish()
        if published_object:
            self.feedback.pop_info(
                title="Snapshot Published",
                text=f"Snapshot published.\nName: {published_object.name}\nPath: {published_object.path}",
                critical=False,
            )

# class ComboItem(str):
#     """Custom class for combo box items."""
#     def __init__(self, *_args):
#         super().__init__()
#         self.data=None


# class ComboItem:
#     """Custom class for combo box items."""
#
#     def __init__(self, nice_name, value=None):
#         self.nice_name = nice_name
#         self.value = value
#
#     def __str__(self):
#         return self.nice_name
#
#     def __repr__(self):
#         return self.nice_name


class ImageWidget(QtWidgets.QLabel):
    """Custom class for thumbnail section. Keeps the aspect ratio when resized."""

    def __init__(self, parent=None):
        super(ImageWidget, self).__init__()
        self.aspectRatio = 1.78
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        size_policy.setHeightForWidth(True)
        self.setSizePolicy(size_policy)

    def resizeEvent(self, _resize_event):
        height = self.width()
        self.setMinimumHeight(int(height / self.aspectRatio))
        self.setMaximumHeight(int(height / self.aspectRatio))
