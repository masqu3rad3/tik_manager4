"""Ingest image sequence as image plane."""

from maya import cmds
from tik_manager4.external.fileseq import filesequence as fileseq
from tik_manager4.dcc.ingest_core import IngestCore


class ImagePlane(IngestCore):
    """Ingest image sequence as image plane."""

    nice_name = "Ingest Image Plane"
    valid_extensions = [".jpg", ".jpeg", ".png", ".tif", ".tiff", ".exr", ".tga"]
    referencable = False

    def _bring_in_default(self):
        """Import the sequence as image plane."""
        ip_trns, ip_shape = cmds.imagePlane()
        seq = fileseq.FileSequence(self.ingest_path)
        cmds.setAttr(f"{ip_shape}.imageName", list(seq)[0], type="string")
        cmds.setAttr(f"{ip_shape}.useFrameExtension", 1)
        cmds.setAttr(f"{ip_shape}.width", 12)

