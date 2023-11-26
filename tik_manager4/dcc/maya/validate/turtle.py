"""Make sure there are no Turtle nodes in the scene."""

from maya import cmds
from tik_manager4.dcc.validate_core import ValidateCore

class Turtle(ValidateCore):
    """Turtle nodes validation class for Maya"""

    # Name of the validation
    name = "turtle"
    nice_name = "Turtle Nodes"

    turtle_nodes = ["TurtleDefaultBakeLayer", "TurtleBakeLayerManager", "TurtleRenderOptions", "TurtleUIOptions"]

    def __init__(self):
        super(Turtle, self).__init__()
        self.autofixable = True
        self.ignorable = True
        self.selectable = True

        self.turtle_nodes = []
    def validate(self):
        """Check for turtle nodes."""
        self.turtle_nodes = cmds.ls(self.turtle_nodes)
        if self.turtle_nodes:
            self.failed(msg="Turtle nodes found: {}".format(self.turtle_nodes))
        else:
            self.passed()

    def fix(self):
        """Get rig of all the turtle nodes."""
        self.delete_object(self.turtle_nodes)
        cmds.unloadPlugin("Turtle", force=True)

    def select(self):
        """Select the turtle nodes in the scene."""
        cmds.select(self.turtle_nodes)

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

