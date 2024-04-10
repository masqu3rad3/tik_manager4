"""Main module for Substance Painter integration."""

import logging

import substance_painter

from tik_manager4.ui.Qt import QtCore

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
        return utils.get_scene_path()

    @staticmethod
    def generate_thumbnail(file_path, width, height):
        """Generate a thumbnail for the given file."""
        main_window = substance_painter.ui.get_main_window()
        screenshot = main_window.grab()

        ratio = width / height
        new_height = int(width / ratio)

        screenshot_resized = screenshot.scaled(width * 2, new_height * 2, QtCore.Qt.KeepAspectRatio,
                                               QtCore.Qt.SmoothTransformation)

        screenshot_resized.save(file_path, 'jpg', quality=100)

    @staticmethod
    def get_dcc_version():
        """Get the DCC version."""
        return substance_painter.application.version()