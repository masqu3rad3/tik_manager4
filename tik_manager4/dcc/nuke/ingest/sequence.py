"""Ingest the sequence."""

import nuke
from tik_manager4.external.fileseq import filesequence as fileseq
from tik_manager4.dcc.ingest_core import IngestCore


class Sequence(IngestCore):
    """Ingest the Sequence to Nuke."""

    nice_name = "Ingest Sequence"
    valid_extensions = [
        ".exr",
        ".dpx",
        ".tif",
        ".tiff",
        ".png",
        ".jpg",
        ".jpeg",
        ".tga",
    ]
    referencable = False

    def _bring_in_default(self):
        """Import the sequence."""
        seq = fileseq.FileSequence(self.ingest_path)

        nuke.tprint("Bringing in Sequence")
        read_node = nuke.createNode("Read")
        # get the file path of the first frame

        padding_count = len(str(seq.frameSet()).split("-")[0])
        seq.setPadding("#" * padding_count)
        read_node["file"].fromUserText(
            seq.format(template="{dirname}{basename}{padding}{extension}")
        )

        read_node["first"].setValue(seq.start())
        read_node["last"].setValue(seq.end())
        read_node["origfirst"].setValue(seq.start())
        read_node["origlast"].setValue(seq.end())

        # set the resolution if available in metadata
        read_node["file"].evaluate()
        width = read_node.metadata("input/width")
        height = read_node.metadata("input/height")

        if width and height:
            format_string = f"{width} {height} 0 0 {width} {height} 1"
            new_format = nuke.addFormat(format_string)
            read_node["format"].setValue(new_format.name())

        # if there is a color space defined in the metadata, set it
        if self.metadata.exists("colorspace"):
            read_node["colorspace"].setValue(self.metadata.get_value("colorspace"))
