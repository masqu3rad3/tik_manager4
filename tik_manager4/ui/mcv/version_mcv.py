"""UI Layout for work and publish objects."""
import tempfile
from pathlib import Path
from dataclasses import dataclass
from tik_manager4.core.constants import ObjectType
from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
from tik_manager4.ui.dialog.feedback import Feedback
from tik_manager4.ui.widgets.common import TikButton, HorizontalSeparator, TikIconButton
from tik_manager4.ui.widgets.screenshot import take_screen_area
from tik_manager4.ui.widgets.info import ImageWidget, NotesEditor
from tik_manager4.ui.dialog.bunde_ingest_dialog import BundleIngestDialog
from tik_manager4.core import filelog

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")

class VersionComboBoxModel(QtCore.QAbstractListModel):
    """Model for the version combo box."""

    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.items = items

    def rowCount(self, parent=None):
        """Return the number of items in the model."""
        _ = parent
        return len(self.items)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        """Return the data for the given index and role."""
        if not index.isValid() or not (0 <= index.row() < len(self.items)):
            return None
        if role == QtCore.Qt.DisplayRole:
            # Display only the 'content' key's value
            return self.items[index.row()].nice_name
        if role == QtCore.Qt.ForegroundRole:
            # Set color based on item state
            item = self.items[index.row()]
            return QtGui.QBrush(QtGui.QColor(item.get_display_color()))
        return None

    def get_item(self, index):
        """Method to get the full dictionary item."""
        if 0 <= index < len(self.items):
            return self.items[index]
        return None


class VersionComboBox(QtWidgets.QComboBox):
    """Custom combo box for version selection."""

    def __init__(self, items=None, parent=None):
        """Initialize the VersionComboBox."""
        super().__init__(parent)
        self.model = None
        if items:
            self.set_items(items)

    def set_items(self, items):
        """Set the items for the combo box."""
        self.model = VersionComboBoxModel(items)
        self.setModel(self.model)

    def get_item(self, index):
        """Get the item at the given index."""
        # print(self.model.get_item(index).publish_id)
        return self.model.get_item(index)

    def get_current_item(self):
        """Get the current selected item."""
        return self.model.get_item(self.currentIndex())

    def clear(self):
        """Clear the items from the combo box."""
        if self.model:
            self.model.items = []  # Clear the items in the model
            self.model.layoutChanged.emit()  # Notify views of the change
        super().clear()  # Clear any additional internal state in QComboBox

    def paintEvent(self, event):
        """Override paintEvent to apply the color of the selected item."""
        painter = QtGui.QPainter(self)
        rect = self.rect()

        # Draw the combo box frame
        opt = QtWidgets.QStyleOptionComboBox()
        self.initStyleOption(opt)
        self.style().drawComplexControl(QtWidgets.QStyle.CC_ComboBox, opt, painter, self)

        # Get the current item and its color
        current_index = self.currentIndex()
        if current_index >= 0 and self.model:
            item = self.model.get_item(current_index)
            if item:
                # Determine the color based on the item's state
                _color = item.get_display_color()
                if _color:
                    color = QtGui.QColor(_color)
                else:
                    color = self.palette().color(QtGui.QPalette.Text)

                # Draw the text with the appropriate color
                painter.setPen(color)
                text = item.nice_name
                text_rect = self.style().subControlRect(
                    QtWidgets.QStyle.CC_ComboBox, opt, QtWidgets.QStyle.SC_ComboBoxEditField, self
                )
                painter.drawText(text_rect, QtCore.Qt.AlignVCenter | QtCore.Qt.TextSingleLine, text)

        painter.end()


@dataclass
class HeaderWidgets:
    label: QtWidgets
    refresh_btn: TikIconButton


@dataclass
class VersionWidgets:
    border: QtWidgets.QWidget
    sync_btn: TikButton
    lbl: QtWidgets.QLabel
    combo: VersionComboBox
    promote_btn: TikIconButton
    preview_btn: TikIconButton
    owner_lbl: QtWidgets.QLabel


@dataclass
class ElementWidgets:
    element_lbl: QtWidgets.QLabel
    element_combo: QtWidgets.QComboBox
    element_view_btn: TikIconButton
    ingest_with_lbl: QtWidgets.QLabel
    ingest_with_combo: QtWidgets.QComboBox


@dataclass
class InfoWidgets:
    notes_lbl: QtWidgets.QLabel
    notes_editor: NotesEditor
    thumbnail: ImageWidget


@dataclass
class Buttons:
    import_btn: TikButton
    bundle_ingest_btn: TikButton
    load_btn: TikButton
    reference_btn: TikButton


class TikVersionLayout(QtWidgets.QVBoxLayout):
    """Layout for versioning work and publish objects."""

    element_view_event = QtCore.Signal(str, str)
    status_updated = QtCore.Signal(str, int)
    version_resurrected = QtCore.Signal()

    def __init__(self, project_object, *args, **kwargs):
        """Initialize the TikVersionLayout."""
        super().__init__()
        self._purgatory_mode = False
        self.project = project_object
        self.base = None
        self.parent = kwargs.get("parent")
        self.feedback = Feedback(parent=self.parent)
        self.app_instance = QtWidgets.QApplication.instance()

        self.ingest_mapping = {}  # mapping of ingestor nice name to ingestor name
        self.element_mapping = ({})  # mapping of element type nice name to element type name

        self.header = HeaderWidgets(
            label=QtWidgets.QLabel("Versions"),
            refresh_btn=TikIconButton(icon_name="refresh", circle=True, size=18, icon_size=14)
        )

        self.version = VersionWidgets(
            border=QtWidgets.QWidget(),
            sync_btn=TikButton(text="Sync"),
            lbl=QtWidgets.QLabel(text="Version: "),
            combo=VersionComboBox(),
            promote_btn=TikIconButton(icon_name="star.png", circle=False, size=30),
            preview_btn=TikIconButton(icon_name="player.png", circle=False, size=30),
            owner_lbl=QtWidgets.QLabel("Owner: ")
        )

        self.element = ElementWidgets(
            element_lbl=QtWidgets.QLabel("Element: "),
            element_combo=QtWidgets.QComboBox(),
            element_view_btn=TikIconButton(icon_name="view.png", circle=False, size=30),
            ingest_with_lbl=QtWidgets.QLabel("Ingest with: "),
            ingest_with_combo=QtWidgets.QComboBox()
        )

        self.info = InfoWidgets(
            notes_lbl=QtWidgets.QLabel("Notes: "),
            # notes_editor=QtWidgets.QPlainTextEdit(),
            notes_editor=NotesEditor(),
            thumbnail=ImageWidget()
        )

        self.buttons = Buttons(
            import_btn=TikButton("Import"),
            bundle_ingest_btn=TikButton("Bundle Ingest"),
            load_btn=TikButton("Load"),
            reference_btn=TikButton("Reference")
        )

        self.build_ui()
        self.connect_signals()

        self.set_base(self.base)

    def set_purgatory_mode(self, state):
        """Set the purgatory mode."""
        self.purgatory_mode = state

    @property
    def purgatory_mode(self):
        """Get the purgatory mode."""
        return self._purgatory_mode

    @purgatory_mode.setter
    def purgatory_mode(self, state):
        """Set the purgatory mode."""
        self._purgatory_mode = state
        self.refresh()

    def build_ui(self):
        """Setup the UI."""
        header_lay = QtWidgets.QHBoxLayout()
        header_lay.setContentsMargins(0, 0, 0, 0)
        self.addLayout(header_lay)
        self.header.label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_lay.addWidget(self.header.label)
        header_lay.addStretch()
        header_lay.addWidget(self.header.refresh_btn)
        self.addWidget(HorizontalSeparator(color=(255, 180, 60)))

        version_layout = QtWidgets.QHBoxLayout()
        self.version.border.setLayout(version_layout)
        self.addWidget(self.version.border)

        self.version.border.setObjectName("versionContainer")
        version_layout.addWidget(self.version.sync_btn)
        version_layout.addStretch()
        self.version.lbl.setFont(QtGui.QFont("Arial", 10))
        self.version.lbl.setMinimumSize = QtCore.QSize(10, 30)
        self.version.lbl.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        version_layout.addWidget(self.version.lbl)

        self.version.combo.setMinimumSize(QtCore.QSize(10, 30))
        version_layout.addWidget(self.version.combo)

        self.version.promote_btn.setMinimumSize(QtCore.QSize(30, 30))
        self.version.promote_btn.setEnabled(False)
        self.version.promote_btn.setHidden(True)
        self.version.promote_btn.setToolTip("Promote the selected publish version to Production.")
        version_layout.addWidget(self.version.promote_btn)

        self.version.preview_btn.setMinimumSize(QtCore.QSize(30, 30))
        self.version.preview_btn.setEnabled(False)
        version_layout.addWidget(self.version.preview_btn)

        user_layout = QtWidgets.QHBoxLayout()
        self.addLayout(user_layout)
        self.version.owner_lbl = QtWidgets.QLabel("Owner: ")
        self.version.owner_lbl.setFont(QtGui.QFont("Arial", 10))
        user_layout.addStretch()
        user_layout.addWidget(self.version.owner_lbl)

        element_layout = QtWidgets.QVBoxLayout()
        self.addLayout(element_layout)
        self.element.element_lbl.setFont(QtGui.QFont("Roboto", 10))
        element_layout.addWidget(self.element.element_lbl)
        element_hlay = QtWidgets.QHBoxLayout()
        self.element.element_view_btn.setMaximumWidth(30)
        element_hlay.addWidget(self.element.element_combo)
        element_hlay.addWidget(self.element.element_view_btn)
        element_layout.addLayout(element_hlay)

        self.element.ingest_with_lbl.setFont(QtGui.QFont("Arial", 10))
        element_layout.addWidget(self.element.ingest_with_lbl)
        element_layout.addWidget(self.element.ingest_with_combo)

        notes_layout = QtWidgets.QVBoxLayout()
        self.addLayout(notes_layout)
        self.info.notes_lbl.setFont(QtGui.QFont("Arial", 10))
        notes_layout.addWidget(self.info.notes_lbl)
        notes_layout.addWidget(self.info.notes_editor)

        self.info.thumbnail.setToolTip("Right Click for replace options")
        self.info.thumbnail.setMinimumSize(QtCore.QSize(55, 30))
        self.info.thumbnail.setFrameShape(QtWidgets.QFrame.Box)
        self.info.thumbnail.setScaledContents(True)
        self.info.thumbnail.setAlignment(QtCore.Qt.AlignCenter)
        self.addWidget(self.info.thumbnail)

        btn_layout = QtWidgets.QHBoxLayout()
        self.buttons.bundle_ingest_btn.setVisible(False)
        btn_layout.addWidget(self.buttons.import_btn)
        btn_layout.addWidget(self.buttons.bundle_ingest_btn)
        btn_layout.addWidget(self.buttons.load_btn)
        btn_layout.addWidget(self.buttons.reference_btn)
        self.addLayout(btn_layout)
        self.buttons.import_btn.setEnabled(False)
        self.buttons.load_btn.setEnabled(False)
        self.buttons.reference_btn.setEnabled(False)

    def connect_signals(self):
        """Connect the signals."""
        self.element.element_combo.currentTextChanged.connect(self.element_type_changed)
        self.version.combo.currentIndexChanged.connect(self.version_changed)
        self.buttons.import_btn.clicked.connect(self.on_import)
        self.buttons.load_btn.clicked.connect(self.on_load)
        self.buttons.reference_btn.clicked.connect(self.on_reference)
        self.buttons.bundle_ingest_btn.clicked.connect(self.on_bundle_ingest)
        self.version.combo.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.version.combo.customContextMenuRequested.connect(self.version_right_click_menu)
        self.info.thumbnail.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.info.thumbnail.customContextMenuRequested.connect(self.thumbnail_right_click_menu)
        self.element.element_view_btn.clicked.connect(self.on_element_view_event)
        self.header.refresh_btn.clicked.connect(self.refresh)
        self.version.sync_btn.clicked.connect(self.on_sync_to_origin)
        self.info.notes_editor.notes_updated.connect(self.__apply_to_base)
        self.version.promote_btn.clicked.connect(self.on_promote)

    def on_promote(self):
        """Execute the promote action."""
        if not self.base:
            self.feedback.pop_info(
                title="No publish version selected.",
                text="Please select a publish version to promote.",
                critical=True,
            )
            return

        if not self.base.object_type == ObjectType.PUBLISH:
            return

        _version = self.version.combo.get_current_item()
        # if the version is already promoted, ask the user if they want to force it again
        if _version.is_promoted():
            question = self.feedback.pop_question(
                title="Version already promoted",
                text="The selected version is already promoted.\n\nDo you want to force the promotion again?",
                buttons=["yes", "cancel"],
            )
            if question == "cancel":
                return

        _version.promote()
        # store the selected version in the combo box

        # refresh the version list
        _index = self.version.combo.currentIndex()
        self.populate_versions(self.base)
        self.version.combo.setCurrentIndex(_index)


    def on_sync_to_origin(self):
        """Sync the version to the origin."""
        if not self.base:
            self.feedback.pop_info(
                title="No work or publish selected.",
                text="Please select a work or publish to sync.",
                critical=True,
            )
            return
        _version = self.version.combo.get_current_item()
        if not _version:
            return
        are_you_sure = self.feedback.pop_question(
            title="Sync to origin",
            text="You are about to move the local version to the origin.\n\n"
            "This action cannot be undone.\n"
            "Do you want to continue?",
            buttons=["yes", "cancel"],
        )
        if are_you_sure == "cancel":
            return
        ret, msg = _version.sync()
        if not ret:
            self.feedback.pop_info(
                title="Sync failed",
                text="The sync operation failed.",
                details=str(msg),
                critical=True,
            )
            return
        # if this is a work version, the work object should be updated as well
        if _version.object_type == ObjectType.WORK_VERSION:
            self.__apply_to_base()

        self.toggle_sync_state(False)
        self.status_updated.emit("Synced to origin.", 5000)

    def on_import(self):
        """Import the current version."""
        if not self.base:
            self.feedback.pop_info(
                title="No work or publish selected.",
                text="Please select a work or publish to import.",
                critical=True,
            )
            return
        _version_number = self.get_selected_version_number()
        _element_type = self.get_selected_element_type()
        _ingestor = self.get_selected_ingestor()
        self.base.import_version(
            _version_number, element_type=_element_type, ingestor=_ingestor
        )

    def on_element_view_event(self):
        """Emit the selected element's path."""
        element_type = self.get_selected_element_type()
        if not element_type:
            return
        _version = self.version.combo.get_current_item()
        _element = _version.get_element_path(
            element_type, relative=False
        )
        if not _element:
            return
        self.element_view_event.emit(element_type, _element)

    def _load_pre_checks(self, work_obj):
        """Metadata and scene compare checks before loading."""
        # there are some conditions we may want to skip the checks

        if self.base.object_type == ObjectType.PUBLISH:
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
                buttons=["continue", "cancel"],
            )
            if question == "cancel":
                return False
        return True

    def __scene_modified_check(self):
        if self.base._dcc_handler.is_modified():
            question = "Current scene is modified. Do you want to save it?"
            state = self.feedback.pop_question(
                title="Save current scene?",
                text=question,
                buttons=["yes", "no", "cancel"],
            )
            if state == "cancel":
                return False
            if state == "yes":
                if self.base._dcc_handler.get_scene_file() == "":
                    _state = self.base._dcc_handler.save_prompt()
                    # if the save prompt is defined, it will do a recursive check.
                    # this is a safety procedure to prevent infinite recursion
                    # if the save prompts is not defined on a dcc.
                    # this is not working on NUKE at the moment.
                    if _state:
                        self.on_load()
                    return False
                self.base._dcc_handler.save_scene()
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

        if self.base.object_type == ObjectType.PUBLISH:
            work_obj = self.base.work_object
        else:
            work_obj = self.base

        if not self._load_pre_checks(work_obj):
            return

        _version_number = self.get_selected_version_number()
        # check if the current scene is modified.
        # if it is, ask if the user wants to save it
        if not self.__scene_modified_check():
            return

        read_only = False
        if self.base.object_type == ObjectType.PUBLISH:

            if self.base.dcc.lower() == self.base.guard.dcc.lower() and element_type.lower() == "source":
                question = f"Publish versions are protected. The file will be loaded and saved as a new WORK version immediately.\n\nDo you want to continue?"
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

        self.base.load_version(
            _version_number, force=True, element_type=element_type, read_only=read_only
        )

    def on_reference(self):
        """Reference the current version."""
        if not self.base:
            self.feedback.pop_info(
                title="No work or publish selected.",
                text="Please select a work or publish to reference.",
                critical=True,
            )
            return
        if self.base.object_type == ObjectType.WORK:
            state = self.feedback.pop_question(
                title="Referencing WORK version",
                text="WORK versions are not meant to be referenced as they are not protected.\n Do you want to continue?",
                buttons=["yes", "cancel"],
            )
            if state == "cancel":
                return

        _version = self.get_selected_version_number()
        _element_type = self.get_selected_element_type()
        _ingestor = self.get_selected_ingestor()
        self.base.reference_version(
            _version, element_type=_element_type, ingestor=_ingestor
        )

    def on_bundle_ingest(self):
        """Launch the bundle ingest dialog."""

        # testing
        publish_version_number = self.get_selected_version_number()
        element_type = self.get_selected_element_type()

        dialog = BundleIngestDialog(self.base, publish_version_number, element_type, parent=self.parent)
        dialog.show()

    def __load_btn_state(self, base, element_type):
        """Resolve the load button state."""

        # load button is enabled only if the base.dcc and base.guard.dcc are the same
        # it also requires the element_type to be source (in publish mode) or none (in work mode)
        if element_type == "source" or not element_type:
            self.buttons.load_btn.setEnabled(base.dcc == base.guard.dcc)
        else:
            _ingestor = self.get_selected_ingestor()
            if not _ingestor:
                self.buttons.load_btn.setEnabled(False)
                return
            dcc_extensions = base._dcc_handler.formats
            element_version_extension = self.__get_element_suffix(element_type)
            if element_version_extension in dcc_extensions:
                self.buttons.load_btn.setEnabled(True)
                return
            self.buttons.load_btn.setEnabled(False)

    def __import_and_reference_btn_states(self):
        """Resolve the import button state."""
        # if the ingest combo is empty, disable the import and reference buttons
        _ingestor = self.get_selected_ingestor()
        if not _ingestor:
            self.buttons.import_btn.setEnabled(False)
            self.buttons.reference_btn.setEnabled(False)
            return
        # finally, check the ingestors importable and referencable status
        _importable = self.base._dcc_handler.ingests[_ingestor].importable
        _referenceable = self.base._dcc_handler.ingests[_ingestor].referencable
        self.buttons.import_btn.setEnabled(_importable)
        self.buttons.reference_btn.setEnabled(_referenceable)
        return

    def button_states(self, base):
        """Toggle the buttons depending on the base status."""
        if not base:
            self.buttons.load_btn.setEnabled(False)
            self.buttons.import_btn.setEnabled(False)
            self.buttons.reference_btn.setEnabled(False)
            self.element.element_view_btn.setEnabled(False)
            return
        _element_type = self.get_selected_element_type()
        if _element_type:
            self.element.element_view_btn.setEnabled(True)
        _is_bundled = self.__is_element_bundled(_element_type)
        if _is_bundled:
            self.buttons.bundle_ingest_btn.setVisible(True)
            self.buttons.import_btn.setVisible(False)
            self.element.ingest_with_combo.setEnabled(False)
            return
        else:
            self.buttons.bundle_ingest_btn.setVisible(False)
            self.buttons.import_btn.setVisible(True)
            self.element.ingest_with_combo.setEnabled(True)
        self.__load_btn_state(base, _element_type)
        self.__import_and_reference_btn_states()

    def set_base(self, base):
        """Set the base object. This can be work or publish object."""
        self.version.combo.blockSignals(True)
        self.button_states(base)
        if not base:
            self.version.combo.clear()
            self.version.combo.setEnabled(False)
            self.element.element_combo.clear()
            self.element.element_view_btn.setEnabled(False)
            self.info.notes_editor.clear()
            self.info.notes_editor.setEnabled(False)
            self.info.thumbnail.clear()
            self.info.thumbnail.setEnabled(False)
            self.version.preview_btn.setEnabled(False)
            self.toggle_sync_state(False)
            return
        self.version.combo.setEnabled(True)
        self.info.notes_editor.setEnabled(True)
        self.info.thumbnail.setEnabled(True)
        self.version.preview_btn.setEnabled(True)
        self.base = base
        self.populate_versions(base)
        self.version.combo.blockSignals(False)

    # def populate_versions(self, versions):
    def populate_versions(self, base):
        """Populate the version dropdown with the versions from the base object."""
        versions = base.all_versions if self._purgatory_mode else base.versions
        self.version.combo.blockSignals(True)
        self.version.combo.clear()
        self.version.combo.set_items(versions)
        self.version.combo.setCurrentIndex(self.version.combo.count() - 1)

        # get the current selected version name from the version_dropdown
        self.version_changed()
        self.version.combo.blockSignals(False)

    def _resolve_available_ingests(self, version_extension):
        """Resolve the available ingestors for the given extension."""
        self.ingest_mapping = {}
        all_ingests = self.base._dcc_handler.ingests
        # go through all the ingests and check if the version extension is supported
        available_ingests = []
        for ingest_name, fn in all_ingests.items():
            if version_extension in fn.valid_extensions:
                self.ingest_mapping[fn.nice_name] = ingest_name
                available_ingests.append(fn.nice_name)
        return available_ingests

    def toggle_sync_state(self, state, critical=False):
        """Toggle the path warning."""
        # Apply a red border using a style sheet
        color = "red" if critical else "yellow"
        self.version.border.setStyleSheet(f"""
            #versionContainer {{
                border: {int(bool(state))}px solid {color};
            }}
        """)
        # polish the widget
        self.version.border.style().polish(self.version.border)
        self.version.sync_btn.setVisible(state)

    def version_changed(self):
        """When the version dropdown is changed, update the notes and thumbnail."""
        self.element.element_combo.blockSignals(True)
        self.element.ingest_with_combo.blockSignals(True)
        _version = self.version.combo.get_current_item()
        if not _version:
            return

        # set the state of the path warning
        state = False
        critical = False
        if _version.localized:
            state = True
            if not Path(_version.localized_path).exists():
                state = True
                critical = True
        self.toggle_sync_state(state=state, critical=critical)

        _index = self.version.combo.currentIndex()

        self.element.element_combo.clear()
        self.element_mapping.clear()
        if self.base.object_type == ObjectType.PUBLISH:
            self.version.promote_btn.setHidden(False)
            self.version.promote_btn.setEnabled(_version.can_promote())
            self.version.preview_btn.setEnabled(bool(_version.previews))
            self.element.element_combo.setEnabled(True)
            self.element.element_view_btn.setEnabled(True)
            self.element.ingest_with_combo.setEnabled(True)
            self.element_mapping = _version.element_mapping
            self.element.element_combo.addItems(list(self.element_mapping.keys()))
            # trigger the element type changed manually
            self.element_type_changed(self.element.element_combo.currentText())
            owner = _version.creator
        else:  # WORK
            self.version.promote_btn.setHidden(True)
            self.element.element_combo.setEnabled(False)
            self.element.element_view_btn.setEnabled(False)
            self.element.ingest_with_combo.setEnabled(False)
            # enable the show preview button if there are previews
            self.version.preview_btn.setEnabled(bool(_version.previews))
            owner = _version.user
        self.version.owner_lbl.setText(f"Owner: {owner}")
        self.info.thumbnail.clear()
        self.info.notes_editor.set_version(_version)
        _thumbnail_path = self.base.get_abs_database_path(_version.thumbnail)
        self.info.thumbnail.set_media(_thumbnail_path)
        self.element.element_combo.blockSignals(False)
        self.element.ingest_with_combo.blockSignals(False)

    def __is_element_bundled(self, element_type):
        """Check if the element type is bundled."""
        if not self.base or not element_type:
            return False
        _version = self.version.combo.get_current_item()
        return _version.is_element_bundled(element_type)

    def __get_element_suffix(self, element_type):
        """Find the extension for the given element type of selected version."""
        _version = self.version.combo.get_current_item()
        return _version.get_element_suffix(element_type)

    def element_type_changed(self, element_name):
        """Update the rest when element type is changed."""
        element_type = self.element_mapping.get(element_name, None)
        self.element.ingest_with_combo.clear()
        if not element_type:
            return
        element_version_extension = self.__get_element_suffix(element_type)
        _available_ingests = self._resolve_available_ingests(element_version_extension)
        # update the ingest with combo
        self.element.ingest_with_combo.addItems(_available_ingests)
        # if there is an ingestor with the same name as the element type, select it
        if element_type in _available_ingests:
            self.element.ingest_with_combo.setCurrentText(element_type)
        # update the buttons
        self.button_states(self.base)
        return

    def set_version(self, combo_value):
        """Set the version dropdown to the given version value."""
        # check if the value exists in the version dropdown

        self.version.combo.setCurrentText(str(combo_value))

    def get_selected_version_number(self):
        """Return the current version."""
        selected_version = self.version.combo.get_current_item()
        if not selected_version:
            return None
        return selected_version.version

    def get_selected_element_type(self):
        """Return the current element."""
        if self.element.element_combo.isEnabled():
            key = self.element.element_combo.currentText()
            return self.element_mapping.get(key, None)
        return None

    def get_selected_ingestor(self):
        """Return the selected ingestor."""
        if self.element.ingest_with_combo.isEnabled():
            key = self.element.ingest_with_combo.currentText()
            return self.ingest_mapping.get(key, None)
        else:
            return None

    def open_scene_folder(self):
        """Open the scene folder in the file manager."""
        if not self.base:
            return
        _version = self.version.combo.get_current_item()
        _version.show_project_folder()

    def open_database_folder(self):
        """Open the scene folder in the file manager."""
        if not self.base:
            return
        _version = self.version.combo.get_current_item()
        _version.show_database_folder()

    def delete_version(self):
        """Delete the selected Work or Publish version."""
        if not self.base:
            self.feedback.pop_info(
                title="No work or publish selected.",
                text="Please select a work or publish to delete.",
                critical=True,
            )
            return
        _version_obj = self.version.combo.get_current_item()
        state, msg = self.base.check_owner_permissions(_version_obj.version)
        if state != 1:
            self.feedback.pop_info(
                title="Permission Error",
                text=msg,
                critical=True,
            )
            return

        if self.base.object_type == ObjectType.WORK:
            _name = _version_obj.scene_path
            are_you_sure = self.feedback.pop_question(
                title="Delete Work Version",
                text="You are about to delete a work version:\n\n"
                f"{_name}\n\n"
                "This action cannot be undone.\n"
                "Do you want to continue?",
                buttons=["yes", "cancel"],
            )
            if are_you_sure == "cancel":
                return
        elif self.base.object_type == ObjectType.PUBLISH:
            _name = _version_obj.name
            are_you_sure = self.feedback.pop_question(
                title="Delete Publish Version",
                text="You are about to delete a PUBLISH version:\n\n"
                f"{_name}\n\n"
                "This action cannot be undone.\n"
                "Do you want to continue?",
                buttons=["yes", "cancel"],
            )
            if are_you_sure == "cancel":
                return

        state, msg = self.base.delete_version(_version_obj.version)
        if state == -1:
            self.feedback.pop_info(
                title="Delete Error",
                text=msg,
                critical=True,
            )
            return
        # self.populate_versions(self.base.versions)
        self.populate_versions(self.base)

    def refresh(self):
        """Refresh the version dropdown."""
        if self.base:
            self.base.reload()
            # self.populate_versions(self.base.versions)
            self.populate_versions(self.base)
        else:
            self.version.combo.clear()
            self.info.notes_editor.clear()
            self.info.thumbnail.clear()

    def on_replace_thumbnail(self, mode="view"):
        """Replace the thumbnail with the current view or external file."""
        if not self.base:
            return
        if not self.base.object_type == ObjectType.WORK:
            return
        version_number = self.get_selected_version_number()
        state, msg = self.base.check_owner_permissions(version_number)
        if state != 1:
            self.feedback.pop_info(
                title="Permission Error",
                text=msg,
                critical=True,
            )
            return
        if mode == "view":
            file_path = None
        elif mode == "screenshot":
            temp_file = (Path(tempfile.gettempdir()) /
                         "tik_manager_screenshot_temp.jpg").as_posix()

            window = self.app_instance.activeWindow()

            # hide window instance for a moment
            if hasattr(window, "hide"):
                window.hide()

            file_path = take_screen_area(temp_file)

            # bring back the window
            if hasattr(window, "show"):
                window.show()

        else:
            # get the project directory
            file_path = QtWidgets.QFileDialog.getOpenFileName(
                self.parent,
                "Open file",
                self.project.get_abs_project_path(),
                "Image files (*.jpg *.png *.gif *.webp)",
            )[0]

        if mode != "view" and not file_path:
            return

        self.base.replace_thumbnail(version_number, new_thumbnail_path=file_path)
        self.refresh()

    def thumbnail_right_click_menu(self, position):
        """Right click menu for the thumbnail."""
        if not self.base:
            return
        if not self.base.object_type == ObjectType.WORK:
            return

        _ = position

        right_click_menu = QtWidgets.QMenu()
        right_click_menu.setStyleSheet(self.parent.styleSheet())

        take_snapshot_action = QtWidgets.QAction(self.tr("Take screen snapshot"), self)
        right_click_menu.addAction(take_snapshot_action)
        replace_with_view_action = QtWidgets.QAction(
            self.tr("Replace with current view"), self
        )
        right_click_menu.addAction(replace_with_view_action)
        replace_with_file_action = QtWidgets.QAction("Replace with external file", self)
        right_click_menu.addAction(replace_with_file_action)
        take_snapshot_action.triggered.connect(
            lambda: self.on_replace_thumbnail(mode="screenshot")
        )
        replace_with_view_action.triggered.connect(
            lambda: self.on_replace_thumbnail(mode="view")
        )
        replace_with_file_action.triggered.connect(
            lambda: self.on_replace_thumbnail(mode="file")
        )

        right_click_menu.exec_((QtGui.QCursor.pos()))

    def version_right_click_menu(self, position):
        """Right click menu for the version dropdown."""

        _ = position  # stop the linter complaining
        right_click_menu = QtWidgets.QMenu()
        right_click_menu.setStyleSheet(self.parent.styleSheet())  # Add this line

        # get the current version object from the combo box

        if self.purgatory_mode:
            _version = self.version.combo.get_current_item()
            if _version.deleted:
                act_resurrect = right_click_menu.addAction(self.tr("Resurrect Version"))
                act_resurrect.triggered.connect(lambda _=None, x=_version: self.on_resurrect(_version))

        delete_version_action = QtWidgets.QAction(self.tr("Delete Version"), self)
        right_click_menu.addAction(delete_version_action)
        delete_version_action.triggered.connect(self.delete_version)

        right_click_menu.addSeparator()
        if self.base.object_type == ObjectType.WORK:
            publish_snapshot_act = right_click_menu.addAction(
                self.tr("Publish Snapshot")
            )
            publish_snapshot_act.triggered.connect(self.publish_snapshot)

        right_click_menu.addSeparator()
        open_scene_folder_action = right_click_menu.addAction(self.tr("Open Scene Folder"))
        open_database_folder_action = right_click_menu.addAction(self.tr("Open Database Folder"))
        open_scene_folder_action.triggered.connect(self.open_scene_folder)
        open_database_folder_action.triggered.connect(self.open_database_folder)

        right_click_menu.exec_((QtGui.QCursor.pos()))

    def on_resurrect(self, version_obj):
        """Resurrect the selected version."""
        state, msg = version_obj.resurrect()
        if not state:
            self.feedback.pop_info(
                title="Resurrect Error",
                text=msg,
                critical=True,
            )
            return
        self.version_resurrected.emit()
        self.refresh()
        return

    def publish_snapshot(self):
        """Publish a snapshot of the current work."""
        if not self.base.object_type == ObjectType.WORK:
            LOG.warning("Publish snapshot is only available for work objects.")
            return -1
        self.project.snapshot_publisher.work_object = self.base
        self.project.snapshot_publisher.work_version = self.get_selected_version_number()
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

    def __apply_to_base(self):
        """Apply the changes to the base object and persistent database."""
        # self.base._apply_versions()
        self.base.apply_settings(force=True)



