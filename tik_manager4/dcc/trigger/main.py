"""Main module for trigger modular rigger integration."""

import logging

from tik_manager4.dcc.main_core import MainCore
from tik_manager4.dcc.trigger import validate
from tik_manager4.dcc.trigger import extract
from tik_manager4.dcc.trigger import ingest

LOG = logging.getLogger(__name__)
class Dcc(MainCore):
    """Trigger class."""

    name = "trigger"
    formats = [".tr"]  # File formats supported by the DCC
    preview_enabled = False  # Whether or not to enable the preview in the UI
    validations = validate.classes
    extracts = extract.classes
    ingests = ingest.classes

    trigger_main_window = None

    def post_save(self):
        """Post save."""
        if not self.trigger_main_window:
            raise RuntimeError("Trigger main window is not defined.")
        self.trigger_main_window.vcs.update_info()

    def post_publish(self):
        """Post publish."""
        if not self.trigger_main_window:
            raise RuntimeError("Trigger main window is not defined.")
        self.trigger_main_window.vcs.update_info()

    def save_scene(self):
        """Saves the current session."""
        if not self.trigger_main_window:
            raise RuntimeError("Trigger main window is not defined.")
        self.trigger_main_window.save_trigger()

    def save_as(self,file_path):
        """Saves the current scene to the given file path."""
        if not self.trigger_main_window:
            raise RuntimeError("Trigger main window is not defined.")

        self.trigger_main_window.vcs_save_session(file_path)
        return file_path

    def save_prompt(self):
        """Pop up the save prompt."""
        if not self.trigger_main_window:
            raise RuntimeError("Trigger main window is not defined.")
        self.trigger_main_window.save_trigger()
        return True # this is important or else will be an indefinite loop

    def open(self, file_path, force=True):
        """Open the given file path."""
        if not self.trigger_main_window:
            raise RuntimeError("Trigger main window is not defined.")
        self.trigger_main_window.open_trigger(file_path, force=force)

    def is_modified(self):
        """Returns True if the scene has unsaved changes"""
        if not self.trigger_main_window:
            raise RuntimeError("Trigger main window is not defined.")
        self.trigger_main_window.actions_handler.is_modified()

    def get_scene_file(self):
        """Get the current trigger session."""
        if not self.trigger_main_window:
            raise RuntimeError("Trigger main window is not defined.")
        return self.trigger_main_window.actions_handler.session_path

    def get_dcc_version(self):
        """Return the version of the DCC."""
        if not self.trigger_main_window:
            raise RuntimeError("Trigger main window is not defined.")
        return self.trigger_main_window.get_version()

    @classmethod
    def set_trigger_main_window(cls, trigger_main_window):
        """Set the trigger main window."""
        cls.trigger_main_window = trigger_main_window
