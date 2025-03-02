"""Custom class for thumbnail section. Keeps the aspect ratio when resized."""
from pathlib import Path

from tik_manager4.core.constants import ObjectType
from tik_manager4.ui.Qt import QtWidgets, QtGui, QtCore
from tik_manager4.ui.widgets.common import TikButtonBox
from tik_manager4.ui import pick

class ImageWidget(QtWidgets.QLabel):
    """Custom class for thumbnail section. Keeps the aspect ratio when resized."""

    def __init__(self):
        super().__init__()
        self.aspect_ratio = 1.78
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        size_policy.setHeightForWidth(True)
        self.setSizePolicy(size_policy)
        self.setProperty("image", True)

        self.is_movie = False
        self.q_media = None

    def set_media(self, media_path):
        """Set the media to the widget."""
        if not Path(media_path).exists():
            self.q_media = pick.pixmap("empty_thumbnail.png")
            self.setPixmap(self.q_media)
            self.is_movie = False
            return
        if Path(media_path).suffix.lower() in [".gif", ".webp"]:
            self.q_media = QtGui.QMovie(media_path)
            # don't start but show the first frame
            self.q_media.jumpToFrame(0)
            self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
            self.setMovie(self.q_media)
            self.is_movie = True
        else:
            self.q_media = QtGui.QPixmap(media_path)
            self.setPixmap(self.q_media)
            self.is_movie = False

    # start playing the movie if the mouse is over the widget
    def enterEvent(self, _):
        if self.is_movie:
            self.q_media.start()

    # pause playing it the mouse leaves the widget
    def leaveEvent(self, _):
        if self.is_movie:
            self.q_media.setPaused(True)

    def resizeEvent(self, _resize_event):
        height = self.width()
        self.setMinimumHeight(int(height / self.aspect_ratio))
        self.setMaximumHeight(int(height / self.aspect_ratio))

class NotesEditor(QtWidgets.QPlainTextEdit):
    """Custom notes editor widget."""
    notes_updated = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        """Initialize the NotesEditor."""
        super().__init__(*args, **kwargs)
        self.version_obj = None

        self.setReadOnly(True)
        self.setTabChangesFocus(True)
        self.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.right_click_menu)

    def set_version(self, version_obj):
        """Set the base object."""
        self.clear()
        self.version_obj = version_obj
        if self.version_obj:
            self.setPlainText(version_obj.notes)

    def can_edit(self):
        """Check if the notes can be edited."""
        if not self.version_obj:
            return False
        if self.version_obj.object_type != ObjectType.WORK_VERSION:
            return False
        if self.version_obj.guard.user != self.version_obj.user:
            return False
        return True

    def right_click_menu(self, position):
        """Right click menu for the notes editor."""
        # Create the default context menu
        right_click_menu = self.createStandardContextMenu()
        # Add a separator
        right_click_menu.addSeparator()

        # Add custom actions
        edit_action = QtWidgets.QAction(self.tr("Edit Notes"), self)
        right_click_menu.addAction(edit_action)
        edit_action.triggered.connect(self.show_edit_dialog)

        # if there is no version obj, or the version is not a work version,
        # disable the edit
        if not self.can_edit():
            edit_action.setEnabled(False)

        # Execute the combined menu
        right_click_menu.exec_(self.mapToGlobal(position))

    def show_edit_dialog(self):
        """Pop-up a dialog to edit the notes."""
        dialog = QtWidgets.QDialog(parent=self)
        dialog.setModal(True)
        dialog.setWindowTitle("Edit Notes")

        layout = QtWidgets.QVBoxLayout()
        dialog.setLayout(layout)

        label = QtWidgets.QLabel("Edit Notes:")
        layout.addWidget(label)

        editor = QtWidgets.QPlainTextEdit()
        editor.setPlainText(self.toPlainText())
        layout.addWidget(editor)

        buttonbox = TikButtonBox()
        buttonbox.addButton("Ok", QtWidgets.QDialogButtonBox.AcceptRole)
        buttonbox.addButton("Cancel", QtWidgets.QDialogButtonBox.RejectRole)
        layout.addWidget(buttonbox)

        buttonbox.accepted.connect(dialog.accept)
        buttonbox.rejected.connect(dialog.reject)
        # emit the notes_updated signal when the dialog is accepted
        # buttonbox.accepted.connect(self.notes_updated.emit)

        ret = dialog.exec_()
        if ret:
            if editor.toPlainText() == self.toPlainText():
                return
            self.setPlainText(editor.toPlainText())
            self.version_obj.notes = self.toPlainText()
            self.notes_updated.emit()
