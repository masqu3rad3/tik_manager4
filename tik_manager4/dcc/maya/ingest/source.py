"""Ingest source scene."""

from maya import cmds
from tik_manager4.dcc.ingest_core import IngestCore

class Source(IngestCore):
    """Ingest Source Maya Scene."""
    name = "source"
    nice_name =  "Ingest Source Scene"
    valid_extensions = [".mb", ".ma"]

    def __init__(self):
        super(Source, self).__init__()

    def _bring_in_default(self, file_path):
        """Import the Maya scene."""
        cmds.file(file_path, i=True)

    def reference(self, file_path, namespace=None):
        """Reference the Maya scene."""
        ref = cmds.file(file_path,
                        reference=True,
                        groupLocator=True,
                        mergeNamespacesOnClash=False,
                        namespace=namespace,
                        returnNewNodes=True
                        )
        return ref
