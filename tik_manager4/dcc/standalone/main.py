import sys
from pathlib import Path
import subprocess
import shutil

import logging
from tik_manager4.dcc.main_core import MainCore
from tik_manager4.ui.Qt import QtWidgets, QtGui, QtCore
from tik_manager4.dcc.standalone import extract

LOG = logging.getLogger(__name__)

class Dcc(MainCore):
    """Standalone DCC class"""

    name = "Standalone"
    formats = [""] # This means all formats.
    preview_enabled = False
    extracts = extract.classes

    @staticmethod
    def save_as(file_path, source_path=None, **extra_arguments):
        """Save (mockup) the file.
        Args:
            file_path: (String) File path that will be written
            source_path: (String) Source file or folder path
            **extra_arguments: Compatibility arguments

        Returns:
            (String) File path of the saved file

        """
        if not source_path:
            LOG.warning("Source path is not defined. Creating Test File.")
            with open(file_path, "w") as f:
                f.write("test")
            return file_path

        # check if the source path is a file or a folder
        if not Path(source_path).exists():
            LOG.warning(f"Source path does not exist: {source_path}")
            return None

        if Path(source_path).is_file():
            # if it is a file, copy it to the destination
            shutil.copyfile(source_path, file_path)
        else:
            # if it is a folder, copy it to the destination
            shutil.copytree(source_path, file_path)

        return file_path

    @staticmethod
    def open(file_path, force=True, **extra_arguments):
        """Open the given file path.
        Args:
            file_path: (String) File path to open
            force: (Bool) if true any unsaved changes on current scene will be lost
            **extra_arguments: Compatibility arguments for other DCCs

        Returns: None

        """
        subprocess.Popen([file_path], shell=True)

    @staticmethod
    def generate_thumbnail(file_path, width, height):
        """Generate a thumbnail for the given file.
        Args:
            file_path: (String) File path to generate thumbnail from
            width: (int) Thumbnail width
            height: (int) Thumbnail height

        Returns: (String) File path of the generated thumbnail

        """
        # find the main window
        app = QtWidgets.QApplication.instance()
        if app:
            window = app.activeWindow()
            # momenterarly minimize the window before taking the screenshot
            window.showMinimized()
            window.setVisible(False)

            # wait for the window to be minimized
            QtWidgets.QApplication.processEvents()
            screenshot = QtWidgets.QApplication.primaryScreen().grabWindow(QtWidgets.QApplication.desktop().winId())

            ratio = width / height
            new_height = int(width / ratio)

            # Apply scaling directly to the screenshot pixmap and save it
            screenshot_resized = screenshot.scaled(width*2, new_height*2, QtCore.Qt.KeepAspectRatio,
                                                   QtCore.Qt.SmoothTransformation)
            screenshot_resized.save(file_path, 'jpg', quality=95)  # Adjust quality as needed

            QtWidgets.QApplication.processEvents()


            # bring back the window
            window.setVisible(True)
            window.showNormal()

            # make sure the window focus is back
            window.activateWindow()
            return file_path

        return None

    @staticmethod
    def text_to_image(text, save_path, width, height, color="orange", scale=0.5):
        """Convert text to an image."""

        # app = QtWidgets.QApplication(sys.argv)
        app = QtWidgets.QApplication.instance()


        # Create a QLabel to render the text
        label = QtWidgets.QLabel()
        label.setText(text)

        # Create a QFontMetrics object to measure text dimensions
        font = QtGui.QFont('Arial', 12)  # You can adjust the font settings as needed
        metrics = QtGui.QFontMetrics(font)
        text_width = metrics.width(text)
        text_height = metrics.height()

        # Calculate the scale factor for resizing
        scale_factor_width = width / text_width
        scale_factor_height = height / text_height
        scale_factor = min(scale_factor_width, scale_factor_height) * scale

        # Scale font size based on the minimum scale factor
        font.setPointSize(int(font.pointSize() * scale_factor))
        metrics = QtGui.QFontMetrics(font)

        # Set fixed width and height for the QLabel
        label.setFixedSize(width, height)

        # Create a QPixmap with specified width, height, and alpha channel
        pixmap = QtGui.QPixmap(width, height)
        pixmap.fill(QtCore.Qt.transparent)  # Fill with transparent background

        # Create a QPainter to draw on the pixmap
        painter = QtGui.QPainter(pixmap)

        # Set the font and color
        painter.setFont(font)
        painter.setPen(QtGui.QColor(color))

        # Calculate the bounding rectangle for the text
        text_rect = QtCore.QRect(0, 0, width, height)
        text_option = QtGui.QTextOption()
        text_option.setAlignment(QtCore.Qt.AlignCenter)
        painter.drawText(text_rect, QtCore.Qt.AlignCenter, text)

        # Save the pixmap as an image
        pixmap.save(save_path, 'PNG')

        # Cleanup
        painter.end()
        # app.quit()

        return save_path