import subprocess

from tik_manager4.dcc.main_core import MainCore
from tik_manager4.ui.Qt import QtWidgets, QtCore


class Dcc(MainCore):
    formats = [".txt", ".log"]
    preview_enabled = False

    @staticmethod
    def save_as(file_path):
        """Save (mockup) the file.
        Args:
            file_path: (String) File path that will be written
            file_format: (String) File format
            **extra_arguments: Compatibility arguments

        Returns:

        """
        with open(file_path, "w") as f:
            f.write("test")

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

