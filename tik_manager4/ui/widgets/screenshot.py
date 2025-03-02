from pathlib import Path

from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui


class ScreenShot(QtWidgets.QDialog):
    def __init__(self, folder_path):
        super(ScreenShot, self).__init__()

        self.folder_path = folder_path
        self.file_path = None
        self.image_map = None
        self.origin = None

        screen_rect = QtCore.QRect()
        for screen_index in range(len(QtWidgets.QApplication.screens())):
            screen_rect = screen_rect.united(
                QtWidgets.QApplication.screens()[screen_index].geometry())

        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setCursor(QtCore.Qt.CrossCursor)
        self.setGeometry(screen_rect)

        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.WindowStaysOnTopHint
            | QtCore.Qt.SplashScreen
        )

        self.rubberband = QtWidgets.QRubberBand(
            QtWidgets.QRubberBand.Rectangle, self)
        self.rubberband.setWindowOpacity(0.5)

        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        if hasattr(event, "position"):
            self.origin = event.position().toPoint()
        else:
            self.origin = event.pos()
        self.rubberband.setGeometry(QtCore.QRect(self.origin, QtCore.QSize()))
        self.rubberband.show()
        QtWidgets.QWidget.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if self.origin is not None:
            if hasattr(event, "position"):
                rect = QtCore.QRect(self.origin,
                                    event.position().toPoint()).normalized()
            else:
                rect = QtCore.QRect(self.origin,
                                    event.pos().toPoint()).normalized()
            self.rubberband.setGeometry(rect)

        self.repaint()
        QtWidgets.QWidget.mouseMoveEvent(self, event)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        painter.setBrush(QtGui.QColor(0, 0, 0, 100))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRect(event.rect())

        if self.origin is not None:
            rect = QtCore.QRect(self.origin,
                                self.mapFromGlobal(QtGui.QCursor.pos()))
            painter.setCompositionMode(QtGui.QPainter.CompositionMode_Clear)
            painter.drawRect(rect)
            painter.setCompositionMode(
                QtGui.QPainter.CompositionMode_SourceOver)

            pen = QtGui.QPen(QtGui.QColor(200, 150, 0, 255), 1)
            painter.setPen(pen)
            painter.drawLine(rect.left(), rect.top(), rect.right(), rect.top())
            painter.drawLine(rect.left(), rect.top(), rect.left(),
                             rect.bottom())
            painter.drawLine(rect.right(), rect.top(), rect.right(),
                             rect.bottom())
            painter.drawLine(rect.left(), rect.bottom(), rect.right(),
                             rect.bottom())

        QtWidgets.QWidget.paintEvent(self, event)

    def mouseReleaseEvent(self, event):
        if self.origin is not None:
            self.rubberband.hide()
            self.hide()
            rect = self.rubberband.geometry()
            screen = QtWidgets.QApplication.primaryScreen()

            pos = self.mapToGlobal(rect.topLeft())
            self.image_map = screen.grabWindow(0, pos.x(), pos.y(),
                                               rect.width(),
                                               rect.height())

            self.save_image(self.folder_path)

            self.accept()

        QtWidgets.QWidget.mouseReleaseEvent(self, event)

    def save_image(self, folder_path=None):
        """Save the image to the specified path"""
        if not folder_path:
            return self.file_path

        screenshot_temp_path = Path(folder_path)
        screenshot_temp_path.mkdir(parents=True, exist_ok=True)

        self.file_path = screenshot_temp_path / "screenshot_temp.jpg"

        self.image_map.save(str(self.file_path))


def take_screen_area(file_path):
    screen_shot = ScreenShot(file_path)
    if screen_shot.exec() == QtWidgets.QDialog.Accepted:
        # Calling save_image() without argument ensures the image is saved
        # only once, as the file path was already provided when initializing
        # the ScreenShot object.
        return screen_shot.save_image()
    return None
