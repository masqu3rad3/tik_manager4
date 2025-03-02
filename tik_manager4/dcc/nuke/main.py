"""Main module for Nuke DCC integration."""

from pathlib import Path
import logging
import platform

import nuke
from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui, QtCompat

from tik_manager4.dcc.main_core import MainCore
from tik_manager4.dcc.nuke import utils
from tik_manager4.dcc.nuke import validate
from tik_manager4.dcc.nuke import extract
from tik_manager4.dcc.nuke import ingest
from tik_manager4.dcc.nuke import extension

LOG = logging.getLogger(__name__)


class Dcc(MainCore):
    """Nuke DCC class."""

    name = "Nuke"
    _main_format = ".nk" if not nuke.env.get("nc") else ".nknc"
    formats = [_main_format]
    preview_enabled = False  # Whether or not to enable the preview in the UI
    validations = validate.classes
    extracts = extract.classes
    ingests = ingest.classes
    extensions = extension.classes

    @staticmethod
    def get_main_window():
        """Get the main window."""
        app = QtWidgets.QApplication.instance()
        for widget in app.topLevelWidgets():
            if widget.metaObject().className() == "Foundry::UI::DockMainWindow":
                return widget
        return None

    @staticmethod
    def save_scene():
        """Save the current nuke script."""
        nuke.scriptSave()

    @staticmethod
    def save_as(file_path):
        """
        Saves the file to the given path
        Args:
            file_path: (String) File path that will be written
            file_format: (String) File format

        Returns: (String) File path

        """
        if nuke.env.get("nc"):
            file_path = str(Path(file_path).with_suffix(".nknc"))
        nuke.scriptSaveAs(file_path)
        return file_path

    @staticmethod
    def save_prompt():
        """Pop up the save prompt and wait for user action."""
        _r = nuke.scriptSave()
        # Return True (or any other value you need)
        return True

    @staticmethod
    def open(file_path, force=True, **extra_arguments):
        """
        Opens the given file path
        Args:
            file_path: (String) File path to open
            force: (Bool) if true any unsaved changes on current scene will be lost

        Returns: (String) File path

        """
        nuke.scriptClose(ignoreUnsavedChanges=force)
        nuke.scriptOpen(file_path)
        return file_path

    @staticmethod
    def get_ranges():
        """Get the frame ranges."""
        return utils.get_ranges()

    @staticmethod
    def set_ranges(range_list):
        """Set the frame ranges."""
        utils.set_ranges(range_list)

    @staticmethod
    def set_project(file_path):
        """
        Sets the project to the given path
        Args:
            file_path: (String) File path to set as project

        Returns: None

        """
        nuke.root().knob("project_directory").setValue(file_path)

    @staticmethod
    def is_modified():
        """Check if the current scene is modified."""
        return nuke.modified()

    @staticmethod
    def get_scene_file():
        """Get the current scene file."""
        return str(Path(nuke.root().knob("name").value()))

    @staticmethod
    def get_current_frame():
        """Get the current frame."""
        return nuke.frame()

    def generate_thumbnail(self, file_path, width, height):
        """Generate a thumbnail for the current scene."""
        try:
            active_node = nuke.activeViewer().node().input(0)

            # create reformat node
            reformat_node = nuke.createNode("Reformat")
            reformat_node["type"].setValue(1)
            reformat_node["box_fixed"].setValue(1)
            reformat_node["box_width"].setValue(width)
            reformat_node["box_height"].setValue(height)
            reformat_node["black_outside"].setValue(1)
            reformat_node.setInput(0, active_node)

            # create a write node
            write_node = nuke.createNode("Write")
            write_node.setName("tik_tempWrite")
            write_node["file"].setValue(Path(file_path).as_posix())
            write_node["use_limit"].setValue(True)
            frame = self.get_current_frame()
            write_node["first"].setValue(frame)
            write_node["last"].setValue(frame)

            # execute & cleanup
            nuke.execute(write_node, frame, frame)
            nuke.delete(write_node)
            nuke.delete(reformat_node)
            return file_path

        except:  # pylint: disable=bare-except
            try:
                QtGui.QPixmap.grabWindow(
                    QtWidgets.QApplication.desktop().winId(),
                    0,
                    0,
                    QtWidgets.QApplication.desktop().screenGeometry().width() * 0.8,
                    QtWidgets.QApplication.desktop().screenGeometry().height() * 0.8,
                ).save(file_path)
                # resize
                ratio = width / height
                pixmap_resized = QtGui.QPixmap(file_path).scaled(
                    width, width / ratio, QtCore.Qt.KeepAspectRatio
                )
                pixmap_resized.save(file_path)
                return file_path
            except:  # pylint: disable=bare-except
                LOG.warning("Could not generate thumbnail")
                return ""

    @staticmethod
    def get_dcc_version():
        """Get the current nuke version."""
        return nuke.NUKE_VERSION_STRING
