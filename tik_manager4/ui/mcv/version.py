"""UI Layout for work and publish objects."""
import os.path

from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
from tik_manager4.core import filelog
from tik_manager4.ui import pick
from tik_manager4.ui.dialog.feedback import Feedback

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")


class TikVersionLayout(QtWidgets.QVBoxLayout):
    def __init__(self, *args, **kwargs):
        super(TikVersionLayout, self).__init__(*args, **kwargs)

        self.base = None  # this is work or publish object

        version_layout = QtWidgets.QHBoxLayout()
        self.addLayout(version_layout)
        version_lbl = QtWidgets.QLabel("Version:")
        self.version_dropdown = QtWidgets.QComboBox()
        version_layout.addWidget(version_lbl)
        version_layout.addWidget(self.version_dropdown)

        notes_layout = QtWidgets.QVBoxLayout()
        self.addLayout(notes_layout)
        notes_lbl = QtWidgets.QLabel("Notes:")
        self.notes_editor = QtWidgets.QPlainTextEdit()
        notes_layout.addWidget(notes_lbl)
        notes_layout.addWidget(self.notes_editor)

        self.thumbnail = ImageWidget()
        self.empty_pixmap = pick.image("empty_thumbnail.png")
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
        self.version_dropdown.currentIndexChanged.connect(self.version_changed)

    def set_base(self, base):
        # self.clear()
        self.version_dropdown.blockSignals(True)
        if not base:
            self.version_dropdown.clear()
            self.notes_editor.clear()
            self.thumbnail.clear()
            return
        self.base = base
        self.populate_versions(base._versions)

        self.version_dropdown.blockSignals(False)
    # def clear(self):
    #     self.version_dropdown.clear()
    #     self.notes_editor.clear()
    #     self.thumbnail.clear()
    def populate_versions(self, versions):
        """Populate the version dropdown with the versions from the base object."""
        self.version_dropdown.blockSignals(True)
        self.version_dropdown.clear()
        for version in versions:
            # add the version number to the dropdown. Version number is integer, convert it to string
            self.version_dropdown.addItem(str(version.get("version_number")))
        # alyways select the last version
        self.version_dropdown.setCurrentIndex(self.version_dropdown.count() - 1)

        # get the current selected version name from the version_dropdown
        self.version_changed()

        # version_number = int(self.version_dropdown.currentText())
        # self.populate_details(version_number)
        # print(version_name)
        self.version_dropdown.blockSignals(False)

    # def populate_details(self, version_number):
    #     """Populate the version details."""
    #     # find the version from the version name
    #     _version = self.base.get_version(version_number)
    #     self.notes_editor.clear()
    #     self.thumbnail.clear()
    #     self.notes_editor.setPlainText(_version.get("notes"))
    #     self.thumbnail.setPixmap(QtGui.QPixmap(_version.get("thumbnail_path")))

    def version_changed(self):
        # print("version changed")
        # print(self.version_dropdown.currentText())
        version_number = int(self.version_dropdown.currentText())
        _version = self.base.get_version(version_number)
        self.notes_editor.clear()
        self.thumbnail.clear()
        self.notes_editor.setPlainText(_version.get("notes"))
        _thumbnail_path = self.base.get_abs_database_path(_version.get("thumbnail", ""))
        if os.path.isfile(_thumbnail_path):
            self.thumbnail.setPixmap(QtGui.QPixmap(_thumbnail_path))
        else:
            self.thumbnail.setPixmap(self.empty_pixmap)

class ImageWidget(QtWidgets.QLabel):
    """Custom class for thumbnail section. Keeps the aspect ratio when resized."""

    def __init__(self, parent=None):
        super(ImageWidget, self).__init__()
        self.aspectRatio = 1.78
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        size_policy.setHeightForWidth(True)
        self.setSizePolicy(size_policy)

    def resizeEvent(self, r):
        h = self.width()
        self.setMinimumHeight(int(h / self.aspectRatio))
        self.setMaximumHeight(int(h / self.aspectRatio))
