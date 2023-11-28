"""UI Layout for work and publish objects."""
from pathlib import Path

from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
from tik_manager4.core import filelog
from tik_manager4.ui import pick

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")


class TikVersionLayout(QtWidgets.QVBoxLayout):
    def __init__(self, *args, **kwargs):
        super(TikVersionLayout, self).__init__(*args, **kwargs)

        self.base = None  # this is work or publish object

        self.label = QtWidgets.QLabel("Versions")
        self.label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.addWidget(self.label)
        # create a separator label
        self.separator = QtWidgets.QLabel()
        self.separator.setFrameShape(QtWidgets.QFrame.HLine)
        self.separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.separator.setStyleSheet("background-color: rgb(255, 180, 60);")
        self.separator.setFixedHeight(1)
        self.addWidget(self.separator)

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

        self.show_preview_btn = QtWidgets.QPushButton()
        self.show_preview_btn.setText("Show Preview")
        self.show_preview_btn.setMinimumSize(QtCore.QSize(60, 30))
        version_layout.addWidget(self.show_preview_btn)

        element_layout = QtWidgets.QVBoxLayout()
        self.addLayout(element_layout)
        element_lbl = QtWidgets.QLabel("Element: ")
        element_lbl.setFont(QtGui.QFont("Arial", 10))
        element_layout.addWidget(element_lbl)
        self.element_combo = QtWidgets.QComboBox()
        element_layout.addWidget(self.element_combo)

        notes_layout = QtWidgets.QVBoxLayout()
        self.addLayout(notes_layout)
        notes_lbl = QtWidgets.QLabel("Notes: ")
        notes_lbl.setFont(QtGui.QFont("Arial", 10))
        self.notes_editor = QtWidgets.QPlainTextEdit()
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

        # SIGNALS
        self.version_combo.currentIndexChanged.connect(self.version_changed)

    def set_base(self, base):
        # self.clear()
        self.version_combo.blockSignals(True)
        if not base:
            self.version_combo.clear()
            self.element_combo.clear()
            self.notes_editor.clear()
            self.thumbnail.clear()
            return
        self.base = base
        # self.populate_versions(base._versions)
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

    def version_changed(self):
        """When the version dropdown is changed, update the notes and thumbnail."""
        version_number = int(self.version_combo.currentText())
        _index = self.version_combo.currentIndex()
        # check if the _index is the latest in combo box
        if _index == self.version_combo.count() - 1:
            self.version_combo.setProperty("preVersion", False)
        else:
            self.version_combo.setProperty("preVersion", True)
        self.version_combo.setStyleSheet("")

        _version = self.base.get_version(version_number)
        self.element_combo.clear()
        if self.base.object_type == "publish":
            self.element_combo.setEnabled(True)
            self.element_combo.addItems(_version.element_types)
        else:
            # disable
            self.element_combo.setEnabled(False)
        self.notes_editor.clear()
        self.thumbnail.clear()
        self.notes_editor.setPlainText(_version.get("notes"))
        _thumbnail_path = self.base.get_abs_database_path(_version.get("thumbnail", ""))
        if Path(_thumbnail_path).is_file():
            self.thumbnail.setPixmap(QtGui.QPixmap(_thumbnail_path))
        else:
            self.thumbnail.setPixmap(self.empty_pixmap)

    def set_version(self, combo_value):
        """Set the version dropdown to the given version value."""
        # check if the value exists in the version dropdown

        self.version_combo.setCurrentText(str(combo_value))

    def get_selected_version(self):
        """Return the current version."""
        version_number = int(self.version_combo.currentText())
        return version_number
        # Following returns the dictionary. We probably won't need it.

    def refresh(self):
        """Refresh the version dropdown."""
        if self.base:
            self.base.reload()
            self.populate_versions(self.base._versions)
        else:
            self.version_combo.clear()
            self.notes_editor.clear()
            self.thumbnail.clear()


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
