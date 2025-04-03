from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui


class ScreenShot(QtWidgets.QDialog):
    """
    This module captures a selected area of the screen.

    Attributes:
        file_path (str): The path where the screenshot will be saved.
        image_map (QPixmap): Stores the captured image.
        origin (QPoint): The starting point of the selection rectangle.
    """

    def __init__(self, file_path):
        """
        Initializes the screenshot widget.

        Args:
            file_path (str): The path where the captured image will be saved.
        """
        super(ScreenShot, self).__init__()

        self.file_path = file_path
        self.image_map = None
        self.origin = None

        # Calculate the full screen size covering all monitors
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
        """
        Handles mouse press events to start the selection.

        Args:
            event (QMouseEvent): The mouse press event.
        """
        self.origin = event.pos()
        self.rubberband.setGeometry(QtCore.QRect(self.origin, QtCore.QSize()))
        self.rubberband.show()
        QtWidgets.QWidget.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        """
        Handles mouse movement to resize the selection area.

        Args:
            event (QMouseEvent): The mouse move event.
        """
        if self.origin is not None:
            pos = event.pos()
            rect = QtCore.QRect(self.origin, pos).normalized()
            self.rubberband.setGeometry(rect)

        self.repaint()
        QtWidgets.QWidget.mouseMoveEvent(self, event)

    def paintEvent(self, event):
        """
        Handles painting the semi-transparent overlay and selection area.

        Args:
            event (QPaintEvent): The paint event.
        """
        painter = QtGui.QPainter(self)

        painter.setBrush(QtGui.QColor(0, 0, 0, 100))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRect(event.rect())

        if self.origin is not None:
            # Get the selected rectangle
            rect = QtCore.QRect(self.origin,
                                self.mapFromGlobal(QtGui.QCursor.pos()))
            painter.setCompositionMode(QtGui.QPainter.CompositionMode_Clear)
            painter.drawRect(rect)
            painter.setCompositionMode(
                QtGui.QPainter.CompositionMode_SourceOver)

            # Draw a highlighted border around the selection
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
        """
        Handles mouse release events to finalize the screenshot.

        Args:
            event (QMouseEvent): The mouse release event.
        """
        if self.origin is not None:
            self.rubberband.hide()
            self.hide()
            rect = self.rubberband.geometry()
            screen = QtWidgets.QApplication.primaryScreen()

            # Capture the selected area
            pos = self.mapToGlobal(rect.topLeft())
            self.image_map = screen.grabWindow(0, pos.x(), pos.y(),
                                               rect.width(),
                                               rect.height())
            self.image_map.save(self.file_path)  # Save the screenshot

            self.accept()

        QtWidgets.QWidget.mouseReleaseEvent(self, event)


def take_screen_area(file_path):
    """
    Initiates the screen capture process and returns the saved file path.

    Args:
        file_path (str): The path where the screenshot will be saved.

    Returns:
        str or None: The file path if the screenshot is successfully taken,
        otherwise None.
    """
    screen_shot = ScreenShot(file_path)
    if screen_shot.exec() == QtWidgets.QDialog.Accepted:
        return screen_shot.file_path
    return None
