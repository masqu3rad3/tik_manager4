"""Dialog for ingesting bundled elements."""

import dataclasses
import logging

from tik_manager4.ui.Qt import QtWidgets, QtCore

from tik_manager4.ui.dialog.feedback import Feedback
from tik_manager4.ui.dialog.data_containers import MainLayout
from tik_manager4.ui.widgets.common import TikButtonBox

LOG = logging.getLogger(__name__)


@dataclasses.dataclass
class BundleIngestWidgets:
    """Widgets for the bundle ingest dialog."""

    ingest_as_bundle_rbtn: QtWidgets.QRadioButton = None
    ingest_pieces_rbtn: QtWidgets.QRadioButton = None
    bundle_ingestors_combo: QtWidgets.QComboBox = None
    scroll_area_widget: QtWidgets.QWidget = None
    row_widgets: list = None
    ingest_bundle_btn: QtWidgets.QPushButton = None
    cancel_btn: QtWidgets.QPushButton = None


class BundleIngestDialog(QtWidgets.QDialog):
    """Ingest Bundles."""

    def __init__(self, publish_obj, publish_version, element_type, parent=None):
        """Initialize."""
        super().__init__(parent=parent)
        self._publish_version = publish_version  # integer
        self.publish_obj = publish_obj
        self.publish_version_obj = self.publish_obj.get_version(publish_version)
        self.element_type = element_type
        self.setWindowTitle("Ingest Bundled Elements")
        self.feedback = Feedback(parent=self)

        self.ingest_mapping = {}

        self.widgets = BundleIngestWidgets()

        self.widgets.row_widgets = []

        self.layouts = MainLayout()
        self.build_layouts()

        self.build_widgets()
        self.build_buttons()

        # set the size
        self.resize(600, 400)

    def build_layouts(self):
        """Create the layouts."""
        self.layouts.master_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layouts.master_layout)
        self.layouts.header_layout = QtWidgets.QVBoxLayout()
        self.layouts.master_layout.addLayout(self.layouts.header_layout)
        self.layouts.body_layout = QtWidgets.QVBoxLayout()
        self.layouts.master_layout.addLayout(self.layouts.body_layout)
        # self.layouts.master_layout.addStretch()
        self.layouts.buttons_layout = QtWidgets.QHBoxLayout()
        self.layouts.master_layout.addLayout(self.layouts.buttons_layout)

    def build_widgets(self):
        """Build the bundle pieces."""
        element = self.publish_version_obj.get_element_by_type(self.element_type)
        if not element.get("bundled"):
            raise ValueError(
                "Element is not bundled. Bundle ingestion is not possible."
            )

        # create two radio buttons to select whether to ingest the whole bundle or individual pieces
        # create a radio button for the whole bundle
        # create a radio button for individual pieces
        # if the whole bundle is selected, disable the individual pieces
        # if individual pieces are selected, disable the whole bundle
        radio_button_sub_layout = QtWidgets.QHBoxLayout()
        self.layouts.header_layout.addLayout(radio_button_sub_layout)
        self.widgets.ingest_as_bundle_rbtn = QtWidgets.QRadioButton(
            "Ingest With Bundle Ingestor"
        )
        self.widgets.ingest_pieces_rbtn = QtWidgets.QRadioButton(
            "Ingest Individual Pieces"
        )
        self.widgets.ingest_pieces_rbtn.setChecked(True)
        radio_button_sub_layout.addWidget(self.widgets.ingest_as_bundle_rbtn)
        radio_button_sub_layout.addWidget(self.widgets.ingest_pieces_rbtn)
        radio_button_sub_layout.addStretch()

        bundle_match_id = element.get("bundle_match_id", 0)
        all_ingests = self.publish_obj._dcc_handler.ingests
        available_bundle_ingestors = self._resolve_available_ingests(bundle_match_id)

        bundle_ingestor_sub_layout = QtWidgets.QHBoxLayout()
        self.layouts.header_layout.addLayout(bundle_ingestor_sub_layout)
        bundle_ingestor_lbl = QtWidgets.QLabel("Available Bundle Ingestors: ")
        bundle_ingestor_sub_layout.addWidget(bundle_ingestor_lbl)
        self.widgets.bundle_ingestors_combo = QtWidgets.QComboBox()
        self.widgets.bundle_ingestors_combo.addItems(
            [ingestor.nice_name for ingestor in available_bundle_ingestors]
        )
        bundle_ingestor_sub_layout.addWidget(self.widgets.bundle_ingestors_combo)
        bundle_ingestor_sub_layout.addStretch()

        # create a scrollable area for the bundle pieces
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.layouts.body_layout.addWidget(scroll_area)
        self.widgets.scroll_area_widget = QtWidgets.QWidget()
        scroll_area.setWidget(self.widgets.scroll_area_widget)
        scroll_area_layout = QtWidgets.QVBoxLayout()
        self.widgets.scroll_area_widget.setLayout(scroll_area_layout)
        # scroll_area_widget.setEnabled(False)

        bundle_info = element.get("bundle_info", {})
        for name, bundle_piece in bundle_info.items():
            row = BundlePieceRow(name, bundle_piece, all_ingests)
            # self.layouts.body_layout.addWidget(row)
            scroll_area_layout.addWidget(row)
            self.widgets.row_widgets.append(row)

        scroll_area_layout.addStretch()

        # SIGNALS
        self.widgets.ingest_as_bundle_rbtn.toggled.connect(self.set_widget_states)

    def set_widget_states(self):
        """Set the widget states depending on the selected radio button."""
        whole_bundle = self.widgets.ingest_as_bundle_rbtn.isChecked()
        self.widgets.scroll_area_widget.setDisabled(whole_bundle)
        self.widgets.bundle_ingestors_combo.setEnabled(whole_bundle)

        # if the bundle_ingestor combo is

    # def get_available_bundle_ingestors(self, bundle_match_id):
    #     """Return the available bundle ingestors with a matching bundle_match_id."""
    #     available_bundle_ingestors = []
    #     for ingestor in self.publish_version_obj._dcc_handler.ingests.values():
    #         if ingestor.bundle and ingestor.bundle_match_id == bundle_match_id:
    #             available_bundle_ingestors.append(ingestor)
    #     return available_bundle_ingestors

    def _resolve_available_ingests(self, bundle_match_id):
        """Resolve the available ingestors for the given extension."""
        self.ingest_mapping = {}
        # go through all the ingests and check if the version extension is supported
        available_bundle_ingestors = []
        for ingestor in self.publish_obj._dcc_handler.ingests.values():
            if ingestor.bundle and ingestor.bundle_match_id == bundle_match_id:
                self.ingest_mapping[ingestor.nice_name] = ingestor
                available_bundle_ingestors.append(ingestor)
        return available_bundle_ingestors

    def build_buttons(self):
        """Create the button box."""
        button_box = TikButtonBox()
        self.widgets.ingest_bundle_btn = button_box.addButton(
            "Ingest Bundle", QtWidgets.QDialogButtonBox.AcceptRole
        )
        self.widgets.cancel_btn = button_box.addButton(
            "Cancel", QtWidgets.QDialogButtonBox.RejectRole
        )
        self.layouts.buttons_layout.addWidget(button_box)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

    def accept(self):
        """Accept the dialog."""
        # get the ingestors for the selected rows
        if self.widgets.ingest_as_bundle_rbtn.isChecked():
            ingestor_name = self.widgets.bundle_ingestors_combo.currentText()
            if not ingestor_name:
                self.feedback.pop_info(
                    title="Error",
                    text="There are no compatible bundle ingestors available.",
                    critical=True,
                )
                return
            ingestor = self.ingest_mapping[ingestor_name]
            self.publish_obj.import_version(self._publish_version, element_type=self.element_type, ingestor=ingestor)
        else:
            for row in self.widgets.row_widgets:
                if row.is_active():
                    ingestor = row.active_ingestor()
                    if row.get_active_action() == "Import":
                        self.publish_obj.import_bundle_piece(
                            self._publish_version,
                            self.element_type,
                            row.name,
                            ingestor.name,
                            sequential=row.bundle_info.get("sequential", False),
                        )
        self.feedback.pop_info(title="Success", text="Elements ingested successfully.")
        super().accept()


class BundlePieceRow(QtWidgets.QFrame):
    """Row for bundle piece."""

    def __init__(self, name, bundle_piece, all_ingests):
        super().__init__()
        # bundle piece is a dict with keys: extension, path, sequential
        self.name = name
        self.bundle_info = bundle_piece
        self._all_ingests = all_ingests

        # class variables
        # class variables
        self.ingest_mapping = {}

        # access widgets
        self._checkbox = None
        self._ingestor_dropdown = None
        self._action_dropdown = None

        # create a horizontal layout
        self.horizontal_layout = QtWidgets.QHBoxLayout()
        # self.horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.horizontal_layout)

        self.populate()

        # make the frame sunken
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)

    def is_active(self):
        """Check if the row is active and enabled."""
        return self._checkbox.isChecked() and self.isEnabled()

    def get_active_action(self):
        """Return the active action."""
        return self._action_dropdown.currentText()

    def active_ingestor(self):
        """Return the active ingestor."""
        key = self._ingestor_dropdown.currentText()
        if not key:
            return None
        return self.ingest_mapping[self._ingestor_dropdown.currentText()]

    def populate(self):
        """Populate some test widgets."""

        # create a label
        label = QtWidgets.QLabel(self.name)
        self.horizontal_layout.addWidget(label)

        # add a stretch
        self.horizontal_layout.addStretch()

        # create a dropdown with available ingestors for the extension
        self._ingestor_dropdown = QtWidgets.QComboBox()
        available_ingests = self._resolve_available_ingests(
            self.bundle_info["extension"]
        )
        self._ingestor_dropdown.addItems(available_ingests)
        self.horizontal_layout.addWidget(self._ingestor_dropdown)

        # create another dropdown for the desired action
        self._action_dropdown = QtWidgets.QComboBox()
        # self._action_dropdown.addItems(["Create", "Update"])
        self.horizontal_layout.addWidget(self._action_dropdown)

        # create a checkbox
        self._checkbox = QtWidgets.QCheckBox()
        self._checkbox.setChecked(True)
        self.horizontal_layout.addWidget(self._checkbox)

        # if there are no available ingests, disable the whole row
        self.setEnabled(bool(available_ingests))

        # SIGNALS
        self._ingestor_dropdown.currentIndexChanged.connect(self.update_actions)
        self.update_actions()

    def update_actions(self):
        """Update the actions dropbox based on the ingestor."""
        self._action_dropdown.clear()
        key = self._ingestor_dropdown.currentText()
        if not key:
            return
        ingestor = self.ingest_mapping[self._ingestor_dropdown.currentText()]
        available_actions = self._resolve_available_actions(ingestor)
        self._action_dropdown.addItems(available_actions)

    def _resolve_available_actions(self, ingestor):
        """Resolve the available actions for the given ingestor."""
        actions = []
        if ingestor.importable:
            actions.append("Import")
        if ingestor.referencable:
            actions.append("Reference")
        return actions

    def _resolve_available_ingests(self, version_extension):
        """Resolve the available ingestors for the given extension."""
        self.ingest_mapping = {}
        # go through all the ingests and check if the version extension is supported
        available_ingests = []
        for ingest_name, ingestor_obj in self._all_ingests.items():
            if version_extension in ingestor_obj.valid_extensions:
                # self.ingest_mapping[ingestor_obj.nice_name] = ingest_name
                self.ingest_mapping[ingestor_obj.nice_name] = ingestor_obj
                available_ingests.append(ingestor_obj.nice_name)
        return available_ingests


# test the dialog
if __name__ == "__main__":
    from tik_manager4.ui import pick

    _style_file = pick.style_file()
    app = QtWidgets.QApplication([])
    dialog = BundleIngestDialog()
    dialog.setStyleSheet(str(_style_file.readAll(), "utf-8"))
    dialog.show()
    app.exec_()
