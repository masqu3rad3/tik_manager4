"""Ingest source scene."""

from pathlib import Path

from maya import cmds
from maya import OpenMaya as om
from tik_manager4.dcc.ingest_core import IngestCore


class Source(IngestCore):
    """Ingest Source Maya Scene."""

    nice_name = "Ingest Source Scene"
    valid_extensions = [".mb", ".ma"]

    def __init__(self):
        super(Source, self).__init__()

    def _bring_in_default(self):
        """Import the Maya scene."""
        om.MGlobal.displayInfo("Bringing in Source Scene")
        cmds.file(self.file_path, i=True)

    def _reference_default(self):
        """Reference the Maya scene."""

        # this method will be used for all categories
        om.MGlobal.displayInfo("Referencing Source Scene")
        namespace = self.namespace or Path(self.file_path).stem
        ref = cmds.file(
            self.file_path,
            reference=True,
            groupLocator=True,
            mergeNamespacesOnClash=False,
            namespace=namespace,
            returnNewNodes=True,
        )
        return ref
