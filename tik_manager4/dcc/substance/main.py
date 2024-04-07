"""Main module for Substance Painter integration."""

import logging

import substance_painter

from tik_manager4.ui.Qt import QtGui

from tik_manager4.dcc.main_core import MainCore
from tik_manager4.dcc.substance import validate
from tik_manager4.dcc.substance import extract
from tik_manager4.dcc.substance import ingest
from tik_manager4.dcc.substance import utils

LOG = logging.getLogger(__name__)
class Dcc(MainCore):
    """<template_dcc_name> DCC class."""

    name = "Substance Painter"
    formats = [".spp"]  # File formats supported by the DCC
    preview_enabled = False  # Whether or not to enable the preview in the UI
    validations = validate.classes
    extracts = extract.classes
    ingests = ingest.classes

    # Override the applicable methods from the MainCore class

    # def __get_save_project_action(self):
    #     """Return the QAction which triggers Substance Painter's save project action."""
    #
    #     main_window = self.get_main_window()
    #
    #     menubar = main_window.menuBar()
    #     save_action = None
    #     for action in menubar.actions():
    #         menu = action.menu()
    #         if not menu:
    #             continue
    #         if menu.objectName() != "file":
    #             continue
    #
    #         save_action = next(action for action in menu.actions() if action.shortcut() == QtGui.QKeySequence.Save)
    #         break
    #     return save_action

    @staticmethod
    def get_main_window():
        """Get the main window of the DCC."""
        return substance_painter.ui.get_main_window()

    @staticmethod
    def pre_save_issues():
        """Checks to be done before saving a file."""
        if not substance_painter.project.is_open():
            return "No Substance Painter project is open. You need to be in a project to save it."

    @staticmethod
    def save_scene():
        """Save the scene."""
        full_save_mode = substance_painter.project.ProjectSaveMode.Full
        substance_painter.project.save(mode=full_save_mode)

    @staticmethod
    def save_as(file_path):
        """Save the file as the given file path."""
        full_save_mode = substance_painter.project.ProjectSaveMode.Full
        substance_painter.project.save_as(file_path, mode=full_save_mode)
        return file_path

    def save_prompt(self):
        """Prompt the user to save the scene."""
        save_action = utils.get_save_project_action()
        if not save_action:
            return None
        save_action.trigger()
        return True # this is important or else will be an indefinite loop

    @staticmethod
    def open(file_path, force=True, **_extra_arguments):
        """Open the file in the DCC."""
        if substance_painter.project.is_open():
            substance_painter.project.close()

        substance_painter.project.open(file_path)

    @staticmethod
    def is_modified():
        """Check if the scene has unsaved changes."""
        if not substance_painter.project.is_open():
            return False
        return substance_painter.project.needs_saving()

    @staticmethod
    def get_scene_file():
        """Get the scene file path."""
        utils.get_scene_path()
    @staticmethod
    def get_dcc_version():
        """Get the DCC version."""
        return substance_painter.application.version()