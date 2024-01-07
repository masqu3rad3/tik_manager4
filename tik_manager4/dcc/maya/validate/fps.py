"""Simple validation to check the FPS."""

from tik_manager4.dcc.maya import utils
from tik_manager4.dcc.validate_core import ValidateCore

class FPS(ValidateCore):
    """Validate class for Maya"""

    nice_name = "FPS"
    def __init__(self):
        super().__init__()
        self.autofixable = True
        self.ignorable = True
        self.selectable = True
        self._defined_fps : float
        self._current_fps : float
    def validate(self):
        """Validate FPS"""
        # check the fps value from the metadata
        self._defined_fps = self.metadata.get_value("fps")
        if not self._defined_fps:
            self.ignored()
            self.autofixable = False
        self._current_fps = utils.get_scene_fps()
        if self._current_fps != self._defined_fps:
            self.failed(msg="FPS is not correct. Expected: {}, Found: {}".format(self._defined_fps, self._current_fps))
        else:
            self.passed()

    def fix(self):
        """Fix FPS"""
        utils.set_scene_fps(self._defined_fps)
        self.validate()
