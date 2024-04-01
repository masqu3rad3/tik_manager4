"""Ingest STL."""

from pathlib import Path

import hou

from tik_manager4.dcc.ingest_core import IngestCore


class Stl(IngestCore):
    """Ingest STL."""
    nice_name = "Ingest STL"
    valid_extensions = [".stl"]
    bundled = True
    referencable = False

    def __init__(self):
        super(Stl, self).__init__()

    def _bring_in_default(self):
        """Import STL File."""
        all_files = list(Path(self.ingest_path).glob("*"))
        stl_files = [file for file in all_files if file.suffix.lower() in self.valid_extensions]

        project_path = hou.getenv("JOB")
        root_node = hou.node("/obj")
        for stl_file in stl_files:
            # Global import settings
            geo_node = root_node.createNode("geo", node_name=stl_file.stem)
            try: geo_node.allSubChildren()[0].destroy()
            except IndexError: pass
            geo_node.moveToGoodPosition()

            file_node = geo_node.createNode("file", node_name=stl_file.stem)
            file_node.moveToGoodPosition()
            # try to make it a relative path
            try: final_path = "$JOB" / stl_file.relative_to(project_path)
            except ValueError: final_path = stl_file
            file_node.parm("file").set(str(final_path))