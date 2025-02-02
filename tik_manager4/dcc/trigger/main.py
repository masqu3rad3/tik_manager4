"""Main module for trigger modular rigger integration."""

import logging

import trigger.version_control.api as trigger

from tik_manager4.dcc.main_core import MainCore
from tik_manager4.dcc.trigger import validate
from tik_manager4.dcc.trigger import extract
from tik_manager4.dcc.trigger import ingest
from tik_manager4.dcc.trigger import extension

LOG = logging.getLogger(__name__)
class Dcc(MainCore):
    """Trigger class."""

    name = "trigger"
    formats = [".tr"]  # File formats supported by the DCC
    preview_enabled = False  # Whether or not to enable the preview in the UI
    validations = validate.classes
    extracts = extract.classes
    ingests = ingest.classes
    extensions = extension.classes

    trigger_api = trigger.ApiHandler()

    def post_save(self):
        """Post save."""
        self.trigger_api.main_ui.vcs.update_info()

    def post_publish(self):
        """Post publish."""
        self.trigger_api.main_ui.vcs.update_info()

    def save_scene(self):
        """Saves the current session."""
        self.trigger_api.save_session()

    def save_as(self,file_path):
        """Saves the current scene to the given file path."""
        self.trigger_api.save_session_as(file_path)
        return file_path

    def save_prompt(self):
        """Pop up the save prompt."""
        self.trigger_api.save_session()
        return True # this is important or else will be an indefinite loop

    def open(self, file_path, force=True):
        """Open the given file path."""
        self.trigger_api.open_session(file_path)

    def is_modified(self):
        """Returns True if the scene has unsaved changes"""
        self.trigger_api.is_modified()

    def get_scene_file(self):
        """Get the current trigger session."""
        return self.trigger_api.get_session_file()

    def get_dcc_version(self):
        """Return the version of the DCC."""
        return self.trigger_api.get_trigger_version()

