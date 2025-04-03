"""Validation for non centered pivots in Maya scene"""

from maya import cmds
from tik_manager4.dcc.validate_core import ValidateCore

class NonCenteredPivots(ValidateCore):
    """Validate class for Maya"""

    nice_name = "Non-Centered Pivots"

    def __init__(self):
        super().__init__()
        self.autofixable = True
        self.ignorable = True
        self.selectable = True

        self.non_centered_pivots = []

    def collect(self):
        """Collect all mesh transforms in the scene."""
        self.collection = cmds.ls(type="transform")

    def validate(self):
        """Validate unique names in Maya scene."""
        self.collect()
        self.non_centered_pivots.clear()
        for node in self.collection:
            pivot = cmds.xform(node, query=True, worldSpace=True, rotatePivot=True)
            if pivot != [0, 0, 0]:
                self.non_centered_pivots.append(node)
        if self.non_centered_pivots:
            self.failed(msg=f"Objects with non-centered pivots found: {self.non_centered_pivots}")
        else:
            self.passed()

    def fix(self):
        """Center all non-centered pivots."""
        for node in self.non_centered_pivots:
            cmds.xform(node, centerPivots=True)
        self.validate()

    def select(self):
        """Selects all forbidden nodes"""
        cmds.select(self.non_centered_pivots)
