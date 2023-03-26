"""UI Layout for work and publish objects."""

from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
from tik_manager4.core import filelog
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
        self.addWidget(self.thumbnail)

        # SIGNALS
        self.version_dropdown.currentIndexChanged.connect(self.version_changed)

    def set_base(self, base):
        self.clear()
        if not base:
            # only clear
            return
        self.base = base
        self.populate_versions(base._versions)

    def clear(self):
        self.version_dropdown.clear()
        self.notes_editor.clear()
        self.thumbnail.clear()
    def populate_versions(self, versions):
        """Populate the version dropdown with the versions from the base object."""
        for version in versions:
            # add the version number to the dropdown. Version number is integer, convert it to string
            self.version_dropdown.addItem(str(version.get("version_number")))
            # add the notes to the notes editor
            # self.notes_editor.appendPlainText(version.get("notes"))
            self.notes_editor.setPlainText(version.get("notes"))
            # add the thumbnail to the thumbnail widget
            self.thumbnail.setPixmap(QtGui.QPixmap(version.get("thumbnail_path")))
        # alyways select the last version
        self.version_dropdown.setCurrentIndex(self.version_dropdown.count() - 1)

    def version_changed(self):
        pass

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
