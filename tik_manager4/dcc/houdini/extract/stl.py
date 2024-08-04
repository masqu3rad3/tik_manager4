"""Extract STL from Houdini."""

from pathlib import Path
import logging

import hou

from tik_manager4.dcc.extract_core import ExtractCore

LOG = logging.getLogger(__name__)


class Stl(ExtractCore):
    """Extract STL from Houdini."""

    nice_name = "STL"
    optional = False
    color = (100, 200, 0)
    bundled = True

    # global exposed settings will apply ALL categories
    global_exposed_settings = {"discard_export_nodes": True}

    def __init__(self):
        super().__init__()
        self._extension = ".stl"
        # we don't need to define category functions for STL

        self.export_geo_node_name = "tik_STL_export"

    def collect(self):
        """Collect bundle data from the scene."""
        # get all the geo nodes
        geo_nodes = hou.node("/obj").allSubChildren()
        # get the geo nodes which have a file sop
        geo_nodes = [node for node in geo_nodes if node.type().name() == "geo"]
        # filter any node starting with the reserved export geo node name
        geo_nodes = [
            node
            for node in geo_nodes
            if not node.name().startswith(self.export_geo_node_name)
        ]
        return geo_nodes

    def _extract_default(self):
        """Default extract method for STL.
        Extract an individual STL file for each geo node.
        """

        root_node = hou.node("/obj")
        bundle_nodes = self.collect()
        if not bundle_nodes:
            LOG.error("No geo nodes found in the scene.")
            raise ValueError("No geo nodes found in the scene.")

        bundle_directory = self.resolve_output()
        # create the path if it doesn't exist
        Path(bundle_directory).mkdir(parents=True, exist_ok=True)

        export_node = root_node.createNode("geo", self.export_geo_node_name)
        export_node.moveToGoodPosition()

        _bundle_info = {}
        for geo_node in bundle_nodes:
            nice_name = geo_node.name()
            file_path = Path(bundle_directory, f"{nice_name}.stl")
            # try to make it a relative path
            project_path = hou.getenv("JOB")
            try:
                final_path = "$JOB" / file_path.relative_to(project_path)
            except ValueError:
                final_path = file_path

            merge_node = export_node.createNode("object_merge")
            # change the name of the merge_node
            merge_node.setName(f"{nice_name}_merge")

            merge_node.moveToGoodPosition()
            merge_node.parm("numobj").set(1)
            merge_node.parm("xformtype").set("local")
            merge_node.parm("pack").set(False)
            merge_node.parm("objpath1").set(geo_node.path())

            # rop sop
            rop_sop = export_node.createNode("rop_geometry")
            rop_sop.moveToGoodPosition()
            rop_sop.setInput(0, merge_node)
            rop_sop.parm("sopoutput").set(str(final_path))

            rop_sop.parm("execute").pressButton()
            _bundle_info[file_path.stem] = {
                "extension": ".stl",
                "path": file_path.name,
                "sequential": False
            }

        # explicitly set the bundle info.
        self.bundle_info = _bundle_info

        if self.global_settings.get("discard_export_nodes", True):
            export_node.destroy()
