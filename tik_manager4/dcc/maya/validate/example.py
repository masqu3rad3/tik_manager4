"""Validation for unique names in Maya scene"""

import maya.cmds as cmds
from tik_manager4.dcc.validate_core import ValidateCore

class Example(ValidateCore):
    """Validate class for Maya"""

    name = "Example"
    def __init__(self):
        super(Example, self).__init__()
        self.autofixable = True



    def validate(self):
        """Validate unique names in Maya scene."""
        passed = True
        if not passed:
            self.error = True
    def fix(self):
        """Deletes all forbidden nodes"""
        fixed = True
        # if fixed:
        #     self.
        # if not fixed:

    @staticmethod
    def delete_object(keyword, force=True):
        """
        Deletes the object only if exists.
        Accepts wildcards.

        Args:
            keyword: (String) name of the object with or without wildcards
            force: (Bool) If True, the node will be deleted even if it's locked. Default True

        Returns: (List) Non - existing nodes

        """
        node_list = cmds.ls(keyword)
        non_existing = []
        for node in node_list:
            if cmds.objExists(node):
                if force:
                    cmds.lockNode(node, lock=False)
                cmds.delete(node)
            else:
                non_existing.append(node)
        return non_existing
