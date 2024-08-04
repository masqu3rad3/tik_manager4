"""Ingest STL."""

from pathlib import Path

import hou

from tik_manager4.dcc.ingest_core import IngestCore


class Stl(IngestCore):
    """Ingest STL."""
    nice_name = "Ingest STL"
    valid_extensions = [".stl"]
    referencable = False

    def __init__(self):
        super(Stl, self).__init__()

    def _bring_in_default(self):
        """Import STL File."""
        _path = Path(self.ingest_path)

        project_path = hou.getenv("JOB")
        root_node = hou.node("/obj")

        # Global import settings
        geo_node = root_node.createNode("geo", node_name=_path.stem)
        try: geo_node.allSubChildren()[0].destroy()
        except IndexError: pass
        geo_node.moveToGoodPosition()

        file_node = geo_node.createNode("file", node_name=_path.stem)
        file_node.moveToGoodPosition()
        # try to make it a relative path
        try: final_path = "$JOB" / _path.relative_to(project_path)
        except ValueError: final_path = _path
        file_node.parm("file").set(str(final_path))