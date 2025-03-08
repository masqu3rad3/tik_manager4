"""Validation for unique names in Maya scene"""

from maya import cmds
from tik_manager4.dcc.validate_core import ValidateCore

class ForbiddenNodes(ValidateCore):
    """Validate class for Maya"""

    nice_name = "Forbidden Nodes"
    forbiddenNodeTypes = ["polyBlindData", "unknown", "blindDataTemplate"]

    def __init__(self):
        super().__init__()
        self.autofixable = True
        self.ignorable = True
        self.selectable = True

    def collect(self):
        """Collect data"""
        pass # no need to collect data

    def validate(self):
        """Validate unique names in Maya scene."""
        forbidden_nodes = cmds.ls(type=self.forbiddenNodeTypes)
        if forbidden_nodes:
            self.failed(msg=f"Forbidden nodes found: {forbidden_nodes}")
        else:
            self.passed()
    def fix(self):
        """Deletes all forbidden nodes"""
        self.delete_object(cmds.ls(type=self.forbiddenNodeTypes))
        self.validate()

    def select(self):
        """Selects all forbidden nodes"""
        cmds.select(cmds.ls(type=self.forbiddenNodeTypes))

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
