"""Custom class for thumbnail section. Keeps the aspect ratio when resized."""
from pathlib import Path

from tik_manager4.core.constants import ObjectType
from tik_manager4.ui.Qt import QtWidgets, QtGui, QtCore
from tik_manager4.ui.widgets.common import TikButtonBox
from tik_manager4.ui import pick

class LightboxDialog(QtWidgets.QDialog):
    """Minimalistic lightbox dialog to show full size image."""
    def __init__(self, media_path, parent=None):
        super().__init__(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Window)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        # Make it cover the parent window or screen
        if parent:
            # Cover the parent widget area
            top_left = parent.mapToGlobal(QtCore.QPoint(0, 0))
            self.setGeometry(top_left.x(), top_left.y(), parent.width(), parent.height())
        else:
            self.showFullScreen()

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        
        self.label = QtWidgets.QLabel()
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.label)
        
        self.media_path = media_path
        self.set_media()

    def paintEvent(self, event):
        """Draw the semi-transparent background."""
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 200))
        
    def set_media(self):
        if not Path(self.media_path).exists():
            return
            
        screen_size = self.size()
        # Leave some margin
        max_w = screen_size.width() * 0.9
        max_h = screen_size.height() * 0.9
        
        if Path(self.media_path).suffix.lower() in [".gif", ".webp"]:
            movie = QtGui.QMovie(self.media_path)
            movie.setScaledSize(QtCore.QSize(int(max_w), int(max_h))) # This might distort if not careful, but QMovie scaling is tricky
            # Better to not scale movie or scale properly? 
            # QMovie doesn't support aspect ratio scaling easily without subclassing or manual frame handling.
            # For now let's just show it. If it's too big it might be an issue.
            # Let's try to just set it.
            self.label.setMovie(movie)
            movie.start()
        else:
            pixmap = QtGui.QPixmap(self.media_path)
            scaled = pixmap.scaled(int(max_w), int(max_h), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.label.setPixmap(scaled)

    def mousePressEvent(self, event):
        self.close()
        
    def keyPressEvent(self, event):
        self.close()

class ImageWidget(QtWidgets.QLabel):
    """Custom class for thumbnail section. Keeps the aspect ratio when resized."""

    def __init__(self):
        super().__init__()
        self.aspect_ratio = 1.0
        self.settings = None
        self.ratio_key = "ThumbnailDisplayRatio"
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        size_policy.setHeightForWidth(True)
        self.setSizePolicy(size_policy)
        self.setProperty("image", True)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setScaledContents(False)

        self.is_movie = False
        self.q_media = None
        self.media_path = None

    def set_preview_settings(self, settings):
        """Set the preview settings object."""
        self.settings = settings
        self.update_aspect_ratio()

    def update_aspect_ratio(self):
        """Update the aspect ratio from settings."""
        if self.settings:
            ratio_str = self.settings.get(self.ratio_key, "16:9")
            self.aspect_ratio = 1.0 if ratio_str == "1:1" else 1.777

    def set_media(self, media_path):
        """Set the media to the widget."""
        self.media_path = media_path
        if not Path(media_path).exists():
            self.q_media = pick.pixmap("empty_thumbnail.png")
            self.is_movie = False
            self.update()
            return
        if Path(media_path).suffix.lower() in [".gif", ".webp"]:
            self.q_media = QtGui.QMovie(media_path)
            # don't start but show the first frame
            self.q_media.jumpToFrame(0)
            self.q_media.frameChanged.connect(self.update)
            self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
            # self.setMovie(self.q_media) # We draw manually
            self.is_movie = True
        else:
            self.q_media = QtGui.QPixmap(media_path)
            self.setScaledContents(False)
            self.setAlignment(QtCore.Qt.AlignCenter)
            self.is_movie = False
        self.update()

    def clear(self):
        """Clear the thumbnail image."""
        self.set_media("")

    def paintEvent(self, event):
        """Paint the image or movie frame with aspect fill."""
        painter = QtGui.QPainter(self)
        
        # Determine what to draw
        pixmap = None
        if self.is_movie and self.q_media:
            pixmap = self.q_media.currentPixmap()
        elif not self.is_movie and self.q_media:
            pixmap = self.q_media
            
        if not pixmap or pixmap.isNull():
            super().paintEvent(event)
            return

        # Calculate Aspect Fill
        widget_rect = self.rect()
        widget_w = widget_rect.width()
        widget_h = widget_rect.height()
        
        if widget_w == 0 or widget_h == 0:
            return

        pix_w = pixmap.width()
        pix_h = pixmap.height()
        
        # Scale factor to cover the widget
        scale_w = widget_w / pix_w
        scale_h = widget_h / pix_h
        scale = max(scale_w, scale_h)
        
        new_w = int(pix_w * scale)
        new_h = int(pix_h * scale)
        
        # Center the image
        x = (widget_w - new_w) // 2
        y = (widget_h - new_h) // 2
        
        target_rect = QtCore.QRect(x, y, new_w, new_h)
        
        # Draw
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        painter.drawPixmap(target_rect, pixmap)

    def mousePressEvent(self, event):
        """Handle mouse press event to open lightbox."""
        if event.button() == QtCore.Qt.LeftButton and self.media_path and Path(self.media_path).exists():
            # Find the main window to cover
            parent = self.window()
            lightbox = LightboxDialog(self.media_path, parent=parent)
            lightbox.exec_()
        super().mousePressEvent(event)

    # start playing the movie if the mouse is over the widget
    def enterEvent(self, _):
        if self.is_movie:
            self.q_media.start()

    # pause playing it the mouse leaves the widget
    def leaveEvent(self, _):
        if self.is_movie:
            self.q_media.setPaused(True)

    def resizeEvent(self, _resize_event):
        self.adjust_height_to_ratio()

    def adjust_height_to_ratio(self):
        """Adjust the height of the widget to match the aspect ratio."""
        if self.settings:
            self.update_aspect_ratio()
        width = self.width()
        if width <= 0:
            return
        target_height = int(width / self.aspect_ratio)
        
        if self.minimumHeight() != target_height or self.maximumHeight() != target_height:
            self.setMinimumHeight(target_height)
            self.setMaximumHeight(target_height)
            self.updateGeometry()
        
        self.update()

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
