"""Main module for Gaffer integration."""

import logging

from pathlib import Path

import Gaffer
import GafferUI

from tik_manager4.dcc.gaffer import gaffer_menu

from tik_manager4.dcc.main_core import MainCore
from tik_manager4.dcc.gaffer import validate
from tik_manager4.dcc.gaffer import extract
from tik_manager4.dcc.gaffer import ingest
from tik_manager4.dcc.gaffer import extension

LOG = logging.getLogger(__name__)

class Dcc(MainCore):
    """Gaffer DCC class."""

    name = "Gaffer"
    formats = [".gfr"]  # File formats supported by the DCC
    preview_enabled = False  # Whether or not to enable the preview in the UI
    validations = validate.classes
    extracts = extract.classes
    ingests = ingest.classes
    extensions = extension.classes

    # Override the applicable methods from the MainCore class

    def __init__(self):
        """Initialize the Gaffer DCC."""
        super(Dcc, self).__init__()
        self.gaffer = gaffer_menu.GafferMenu()

        self.project_root = None
        self.project_name = None

    def get_main_window(self):
        """Get the main window of the DCC."""
        return self.gaffer.script_window._qtWidget()

    def save_scene(self):
        """Save the current scene."""
        self.gaffer.script.save()

    def save_as(self, file_path):
        """Save the current scene as the given file path."""
        self.gaffer.script["fileName"].setValue(file_path)
        self.gaffer.script.save()

        if self.gaffer.application:
            GafferUI.FileMenu.addRecentFile(self.gaffer.application, file_path)

        return file_path

    def save_prompt(self):
        """Pop up the save prompt."""
        GafferUI.FileMenu.save(self.gaffer.menu)
        return True  # this is important or else will be an indefinite loop

    def open(self, file_path, force=True, **_extra_arguments):
        """Open the given file path
        Args:
            file_path: (String) File path to open
            force: (Bool) if true any unsaved changes on current scene will be lost
            **_extra_arguments: Compatibility arguments for other DCCs

        Returns: None
        """
        self.gaffer.script["fileName"].setValue(file_path)
        self.gaffer.script.load()

        self.gaffer.script["variables"]["projectRootDirectory"]["value"].setValue(self.project_root)
        self.gaffer.script["variables"]["projectName"]["value"].setValue(self.project_name)

    def set_project(self, file_path):
        """Set the project file path and name."""
        # we are doing a trick here...
        # instead of setting the project, we are setting a variable.
        # the reason for that is this function gets called during initialization before the
        # creation of the script node. So we can't set the project directly.
        self.project_root = file_path
        self.project_name = Path(file_path).name


    def is_modified(self):
        """Check if the current scene is modified."""
        return self.gaffer.script["unsavedChanges"].getValue()

    def get_scene_file(self):
        """Get the current scene file path."""
        _filename = self.gaffer.script["fileName"].getValue()
        return _filename


    def get_ranges(self):
        """Get the viewport ranges."""
        playback_range = GafferUI.Playback.acquire( self.gaffer.script.context() ).getFrameRange()
        r_ast = self.gaffer.script["frameRange"]["start"].getValue()
        r_min = playback_range[0]
        r_max = playback_range[1]
        r_aet = self.gaffer.script["frameRange"]["end"].getValue()
        return [r_ast, r_min, r_max, r_aet]

    def get_current_frame(self):
        """Get the current frame."""
        return self.gaffer.script["frame"].getValue()

    def set_ranges(self, range_list):
        """Set the viewport ranges."""
        self.gaffer.script["frameRange"]["start"].setValue(range_list[0])
        GafferUI.Playback.acquire(self.gaffer.script.context()).setFrameRange(range_list[1], range_list[2])
        self.gaffer.script["frameRange"]["end"].setValue(range_list[3])

    def generate_thumbnail(self, file_path, width, height):
        """Generate a thumbnail for the current scene."""
        GafferUI.WidgetAlgo.grab(self.gaffer.script_window, file_path)
        # TODO: figure out a way to resize/crop the image to the width and height
        return file_path

    def get_scene_fps(self):
        """Get the FPS of the scene."""
        return self.gaffer.script["framesPerSecond"].getValue()

    def set_scene_fps(self, fps_value):
        """Set the FPS of the scene."""
        self.gaffer.script["framesPerSecond"].setValue(fps_value)

    @staticmethod
    def get_dcc_version():
        """Get the version of the DCC."""
        return Gaffer.About.versionString()