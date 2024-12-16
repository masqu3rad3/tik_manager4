"""Custom class for thumbnail section. Keeps the aspect ratio when resized."""
from pathlib import Path
from tik_manager4.ui.Qt import QtWidgets, QtGui, QtCore
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
            # self.q_media.start()
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


