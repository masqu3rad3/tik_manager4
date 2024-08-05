from pathlib import Path

import nuke

from tik_manager4.dcc.extract_core import ExtractCore
from tik_manager4.external.fileseq import filesequence as fileseq
from tik_manager4.dcc.nuke import utils


class Render(ExtractCore):
    """Render the Active write nodes in the Nuke script."""

    nice_name = "Render"
    color = (160, 15, 200)  # Purple
    bundled = True

    def __init__(self):
        _ranges = utils.get_ranges()
        global_exposed_settings = {
            "start_frame": {
                "display_name": "Start Frame",
                "type": "integer",
                "value": _ranges[0],
            },
            "end_frame": {
                "display_name": "End Frame",
                "type": "integer",
                "value": _ranges[3],
            },
            "file_format": {
                "display_name": "Format",
                "type": "combo",
                "items": [
                    "Use Node Settings",
                    "exr",
                    "dpx",
                    "tif",
                    "tiff",
                    "png",
                    "jpg",
                    "jpeg",
                    "tga",
                ],
                "value": "exr",
            },
            "colorspace": {
                "display_name": "Colorspace",
                "type": "string",
                "placeholder": "(Leave empty for write node value)",
                "value": "",
            },
        }

        super().__init__(global_exposed_settings=global_exposed_settings)

    @staticmethod
    def collect():
        """Collect the write nodes in the scene."""
        return [node for node in nuke.allNodes("Write") if not node["disable"].value()]

    def update_write_node(self, write_node, file_path):
        """Update the write node with the file path."""
        write_node["file"].fromUserText(file_path)

    def _extract_default(self):
        """Extract method for any non-specified category"""
        write_nodes = self.collect()
        bundle_info = {}
        if not write_nodes:
            self.bundle_info = {}
            return

        _str_directory = self.resolve_output()
        bundle_directory = Path(_str_directory)
        bundle_directory.mkdir(parents=True, exist_ok=True)

        start_frame = self.global_settings.get("start_frame")
        end_frame = self.global_settings.get("end_frame")
        file_format = self.global_settings.get("file_format")
        colorspace = self.global_settings.get("colorspace")

        f_handler = fileseq.FileSequence("")

        for write_node in write_nodes:
            if file_format == "Use Node Settings":
                _format = write_node["file_type"].value()
            else:
                write_node["file_type"].setValue(file_format)
                _format = file_format

            if colorspace:
                write_node["colorspace"].setValue(colorspace)
            write_node["file"].setValue(
                (bundle_directory / f"{write_node.name()}.####.{_format}").as_posix()
            )
            nuke.execute(write_node, start_frame, end_frame)

            seq = f_handler.findSequencesOnDisk((bundle_directory / f"{write_node.name()}.@.{_format}").as_posix())[0]

            # print("DEBUG")
            # print("-----------------")
            # print(write_node["file"].value())
            # print("-----------------")

            bundle_info[write_node.name()] = {
                "extension": f".{_format}",  # e.g ".txt"
                "path": seq.format(),
                "sequential": True,
            }

        # explicitly set the bundle_info property
        self.bundle_info = bundle_info
