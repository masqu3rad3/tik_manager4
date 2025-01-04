"""Validation for empty groups in Maya scene"""

from maya import cmds
from tik_manager4.dcc.validate_core import ValidateCore

class EmptyGroups(ValidateCore):
    """Validate class for Maya"""

    nice_name = "Empty Groups"

    def __init__(self):
        super().__init__()
        self.autofixable = True
        self.ignorable = True
        self.selectable = True

        self.empty_groups = []

    def collect(self):
        """Collect data"""
        pass  # no need to collect data

    def validate(self):
        """Validate unique names in Maya scene."""
        self.empty_groups = list(self._get_empty_groups())
        if self.empty_groups:
            self.failed(msg=f"Forbidden nodes found: {self.empty_groups}")
        else:
            self.passed()

    def fix(self):
        """Delete all empty groups"""
        self.delete_object(self.empty_groups)
        self.validate()

    def select(self):
        """Select all empty groups"""
        cmds.select(self.empty_groups)

    def _get_empty_groups(self):
        """Get empty groups in the scene"""
        transforms = cmds.ls(type="transform")
        for transform in transforms:
            if not cmds.listRelatives(transform, allDescendents=True):
                yield transform

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
