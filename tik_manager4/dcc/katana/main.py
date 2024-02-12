"""Main module for Katana DCC integration."""

import logging

# from PyQt5 import QtWidgets, QtGui, QtCore
from tik_manager4.ui.Qt import QtWidgets, QtGui, QtCore
from Katana import KatanaFile  # pylint: disable=import-error
from Katana import NodegraphAPI  # pylint: disable=import-error

from tik_manager4.ui.main import MainUI as tik_main_ui_class
from tik_manager4.dcc.katana import utils
from tik_manager4.dcc.main_core import MainCore
from tik_manager4.dcc.katana import validate
from tik_manager4.dcc.katana import extract
from tik_manager4.dcc.katana import ingest

LOG = logging.getLogger(__name__)
class Dcc(MainCore):
    """Katana DCC class."""

    name = "katana"
    formats = [".katana"]  # File formats supported by the DCC
    preview_enabled = False  # Whether or not to enable the preview in the UI
    validations = validate.classes
    extracts = extract.classes
    ingests = ingest.classes

    # Override the applicable methods from the MainCore class

    @staticmethod
    def get_main_window():
        """Get the memory adress of the main window to connect Qt dialog to it.
        Returns:
            (long or int) Memory Adress
        """
        app = QtWidgets.QApplication.instance()
        # layouts = [x for x in QtWidgets.qApp.topLevelWidgets() if type(x).__name__ == 'LayoutsMenu']
        layouts = [x for x in app.topLevelWidgets() if type(x).__name__ == 'LayoutsMenu']

        if not layouts:
            return

        return layouts[0].parent()

    @staticmethod
    def save_scene():
        """Save the current scene."""
        pass

    @staticmethod
    def save_as(file_path):
        """Save the current scene as a new file.
        Args:
            file_path (str): The file path to save the scene to.
        Returns:
            (str) The file path that the scene was saved to.
        """
        KatanaFile.Save(file_path)
        return file_path

    @staticmethod
    def save_prompt():
        """Pop up the save prompt."""
        # TODO: We need to find a way to invoke the File > Save command in Katana
        pass

    @staticmethod
    def open(file_path, **_extra_arguments):
        """Open the given file path
        Args:
            file_path: (String) File path to open
            force: (Bool) if true any unsaved changes on current scene will be lost
            **extra_arguments: Compatibility arguments for other DCCs

        Returns: None
        """
        KatanaFile.Load(file_path)

    @staticmethod
    def get_ranges():
        """Get the viewport ranges."""
        return utils.get_ranges()

    @staticmethod
    def set_ranges(range_list):
        """Set the timeline ranges."""
        utils.set_ranges(range_list)

    @staticmethod
    def is_modified():
        """Returns True if the scene has unsaved changes"""
        return KatanaFile.IsFileDirty()

    @staticmethod
    def get_scene_file():
        """Return the current scene file"""
        path = NodegraphAPI.GetProjectFile()
        if path == ".katana":
            return ""
        return NodegraphAPI.GetProjectFile()

    @staticmethod
    def get_current_frame():
        """Return the current frame"""
        return NodegraphAPI.GetCurrentTime()

    @staticmethod
    def get_tik_manager_main_ui():
        """Return the main Tik Manager UI."""
        app = QtWidgets.QApplication.instance()
        for widget in app.topLevelWidgets():
            if isinstance(widget, tik_main_ui_class):
                return widget
        return
    @staticmethod
    def get_tik_manager_dialogs():
        import inspect
        namespace = "tik_manager4.ui"
        for widget in QtWidgets.QApplication.allWidgets():
            if isinstance(widget, QtWidgets.QDialog):
                module_name = inspect.getmodule(widget).__name__
                if module_name.startswith(namespace):
                    yield widget

    def generate_thumbnail(self, file_path, width, height):
        """Generate a thumbnail for the given file path."""

        tik_main_ui = self.get_tik_manager_main_ui()
        if tik_main_ui:
            # finding the main ui doesn't mean it may be active. It is possible it may have closed but not
            # garbage collected yet. Check its state and flag it
            if tik_main_ui.isMinimized() or not tik_main_ui.isVisible():
                tik_main_ui = None
            else:
                tik_main_ui.setVisible(False)
                tik_main_ui.setWindowState(QtCore.Qt.WindowMinimized)
                tik_main_ui.showMinimized()
        tik_dialogs = list(self.get_tik_manager_dialogs())
        for dialog in tik_dialogs:
            dialog.setVisible(False)
            dialog.showMinimized()

        QtWidgets.QApplication.processEvents()

        main_ui = self.get_main_window()
        # focus to the main applications ui
        main_ui.activateWindow()
        QtWidgets.QApplication.processEvents()

        screenshot = QtWidgets.QApplication.primaryScreen().grabWindow(QtWidgets.QApplication.desktop().winId())
        ratio = width / height
        new_height = int(width / ratio)

        # Apply scaling directly to the screenshot pixmap and save it
        screenshot_resized = screenshot.scaled(width*2, new_height*2, QtCore.Qt.KeepAspectRatio,
                                               QtCore.Qt.SmoothTransformation)
        screenshot_resized.save(file_path, 'jpg', quality=95)  # Adjust quality as needed

        # bring back the window
        if tik_main_ui:
            tik_main_ui.setVisible(True)
            tik_main_ui.setWindowState(QtCore.Qt.WindowNoState)
            # tik_main_ui.activateWindow()
        for dialog in tik_dialogs:
            dialog.setVisible(True)
            dialog.showNormal()

        return file_path

    @staticmethod
    def get_dcc_version():
        """Return the version of the DCC."""
        return NodegraphAPI.Version.KatanaInfo.version