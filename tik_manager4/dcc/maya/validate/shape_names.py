"""Validation for all shape names are following the maya standards to match their transforms."""

import re

from maya import cmds
from tik_manager4.dcc.validate_core import ValidateCore

class ShapeNames(ValidateCore):
    """Validate the shape names"""

    nice_name = "Shape Names"

    def __init__(self):
        super(ShapeNames, self).__init__()
        self.autofixable = True
        self.ignorable = False
        self.selectable = True

        self.bad_names = []

    def collect(self):
        """Collect all transform nodes in the scene."""
        self.collection = cmds.ls(type="transform")

    def validate(self):
        """Validate the shape names."""
        self.bad_names = []
        self.collect()
        for transform in self.collection:
            if not self.check_shapename(transform):
                self.bad_names.append(transform)
        if self.bad_names:
            self.failed(msg=f"Shape names under following parent transforms are not following the standard: {self.bad_names}")
        else:
            self.passed()

    def fix(self):
        """Fix the shape names."""
        for transform in self.bad_names:
            shapes = cmds.listRelatives(transform, shapes=True)
            if shapes:
                for shape in shapes:
                    cmds.rename(shape, "%sShape" % transform)
            else:
                pass


    def select(self):
        """Select the bad shapes."""
        # do something to select the non-valid objects
        cmds.select(self.bad_names)

    def check_shapename(self, transform_node):
        """Check the shape name(s) under the given transform node."""
        shapes = cmds.listRelatives(transform_node, shapes=True)
        if shapes:
            for shape in shapes:
                digits = re.search('.*?([0-9]+)$', shape)
                stripped_shapename = shape if not digits else re.search("(.*)(%s)$" % digits.groups()[0], shape).groups()[0]
                if stripped_shapename.endswith("Shape"):
                    return True
                else:
                    return False
        else:
            return True