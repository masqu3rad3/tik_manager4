"""Main module for Krita integration."""

import logging

from krita import Krita

from tik_manager4.dcc.krita import extension
from tik_manager4.dcc.krita import extract
from tik_manager4.dcc.krita import ingest
from tik_manager4.dcc.main_core import MainCore
from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.ui.main import MainUI as tik4MainUI

LOG = logging.getLogger(__name__)


class Dcc(MainCore):
    """Krita DCC class"""

    name = "Krita"
    formats = [".kra"]
    preview_enabled = False
    extracts = extract.classes
    ingests = ingest.classes
    extensions = extension.classes
    custom_launcher = True

    @staticmethod
    def get_main_window():
        """Get the main window."""
        app = QtWidgets.QApplication.instance()
        for widget in app.topLevelWidgets():
            if isinstance(widget, QtWidgets.QMainWindow):
                return widget
        return None

    @staticmethod
    def save_scene() -> None:
        """Saves the current scene."""
        Krita.instance().activeDocument().save()

    @staticmethod
    def save_as(file_path: str) -> str:
        """
        Saves the scene to the given path.
        Args:
            file_path: (str) File path that will be written.
        Returns: (str) File path.
        """
        Krita.instance().activeDocument().saveAs(file_path)
        return file_path

    @staticmethod
    def open(file_path: str, force: bool = True) -> None:
        """
        Opens the given file path.
        Args:
            file_path: (str) File path to open.
            force: (bool) If True, unsaved changes on the current scene will be lost.
        Returns: None
        """
        application = Krita.instance()
        existing_docs = application.documents()
        for doc in existing_docs:
            if file_path == doc.fileName():
                doc.close()
        doc = application.openDocument(file_path)
        application.activeWindow().addView(doc)

    @staticmethod
    def generate_thumbnail(file_path: str, width: int, height: int) -> str:
        """
        Generates a thumbnail for the current frame.
        Args:
            file_path: (str) Output file path for the thumbnail.
            width: (int) Thumbnail width.
            height: (int) Thumbnail height.
        Returns: (str) File path of the generated thumbnail.
        """
        Krita.instance().activeDocument().thumbnail(width, height).save(
            file_path)
        return file_path

    @staticmethod
    def get_scene_file() -> str:
        """
        Gets the current scene file path.
        Returns: (str) Scene file path.
        """
        return Krita.instance().activeDocument().fileName()

    @staticmethod
    def get_dcc_version() -> str:
        """
        Gets the current version of Krita.
        Returns: (str) Krita version.
        """
        version = Krita.instance().version().split(" ")[0]
        return version

    def launch(self, tik_main_object, window_name=None, dont_show=False):
        """Launch Tik Main UI with DCC specific way."""
        parent = self.get_main_window()
        window_name = window_name + "NoShow" if dont_show else window_name

        for widget in QtWidgets.QApplication.allWidgets():
            try:
                if widget.objectName() == window_name:
                    widget.close()
                    widget.deleteLater()
            except (AttributeError, TypeError):
                continue

        if dont_show:
            tik4_main_ui = tik4MainUI(
                tik_main_object,
                window_name=window_name,
                parent=parent
            )
        else:
            tik4_main_ui = tik4MainUI(
                tik_main_object,
                window_name=window_name,
                parent=parent
            )
            tik4_main_ui.show()

        return tik4_main_ui
