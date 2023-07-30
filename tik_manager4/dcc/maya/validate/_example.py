"""Example of a validation class for Maya."""

import maya.cmds as cmds
from tik_manager4.dcc.validate_core import ValidateCore

class Example(ValidateCore):
    """Example validation for Maya"""

    # Name of the validation
    name = "Example"

    def __init__(self):
        super(Example, self).__init__()
        self.autofixable = True
        self.ignorable = True
        self.selectable = True

    def validate(self):
        """Dummy validation. Which always fails."""
        # do something to validate the scene
        self.failed(msg="This is a dummy validation. It always fails.")

    def fix(self):
        """Dummy fix. Which always passes."""
        # do something to fix the validation
        self.passed()

    def select(self):
        """Dummy select. Which selects all objects in the scene."""
        # do something to select the non-valid objects
        cmds.select(cmds.ls())
