"""Extract Alembic from Maya scene"""

import logging

import hou

from tik_manager4.dcc.extract_core import ExtractCore
from tik_manager4.dcc.houdini import utils

LOG = logging.getLogger(__name__)


class Usd(ExtractCore):
    """Extract Alembic from Maya scene."""

    nice_name = "Usd"
    optional = False
    color = (71, 143, 203)
    _ranges = utils.get_ranges()

    # these are the exposed settings in the UI
    exposed_settings = {
        "Animation": {
            "start_frame": _ranges[0],
            "end_frame": _ranges[3],
            "sub_steps": 1,
        },
        "Fx": {
            "start_frame": _ranges[0],
            "end_frame": _ranges[3],
            "sub_steps": 1,
        },
        "Layout": {
            "start_frame": _ranges[0],
            "end_frame": _ranges[3],
        },
        "Lighting": {
            "start_frame": _ranges[0],
            "end_frame": _ranges[3],
        },
    }

    def __init__(self):
        super().__init__()
        if hou.isApprentice():
            self._extension = ".usdnc"
            self._message = "USD export is not supported in Houdini Apprentice. Format will be saved as .usdnc"
        else:
            self._extension = ".usd"

        # Category names must match to the ones in category_definitions.json (case sensitive)
        self.category_functions = {
            "Model": self._extract_model,
            "Animation": self._extract_animation,
            "Fx": self._extract_fx,
            "Layout": self._extract_layout,
            "Lighting": self._extract_lighting,
        }

    def __extract_base(self):
        """Convenience method for the shared parts of the extract methods."""

        root_node = hou.node("obj")
        export_list = root_node.children()

        if not export_list:
            msg = "No nodes to export."
            LOG.errror(msg)
            raise Exception(msg)

        # check if the export node exists
        geo_node = root_node.node("__tik_export_usd")
        if geo_node:
            # start from scratch if it exists
            geo_node.destroy()

        geo_node = root_node.createNode("geo", node_name="__tik_export_usd")
        # this is to delete any existing nodes in the geo node
        try:
            geo_node.allSubChildren()[0].destroy()
        except IndexError:
            pass

        merge_node = geo_node.createNode("object_merge")
        number_of_objects = len(export_list)
        merge_node.parm("numobj").set(number_of_objects)
        merge_node.parm("xformtype").set("local")
        merge_node.parm("pack").set(True)

        for nmb, node in enumerate(export_list):
            parameter = f"objpath{nmb+1}"
            merge_node.parm(parameter).set(node.path())

        # rop sop
        rop_sop = geo_node.createNode("usdexport")
        rop_sop.setInput(0, merge_node)
        return geo_node, rop_sop

    def _extract_model(self):
        """Extract method for model category"""
        _file_path = self.resolve_output()
        geo_node, rop_sop = self.__extract_base()

        rop_sop.parm("lopoutput").set(_file_path)

        # set properties
        rop_sop.parm("trange").set("off")

        rop_sop.parm("execute").pressButton()
        geo_node.destroy()
        return True

    def _extract_animation(self):
        """Extract method for animation category"""
        settings = self.settings.get("Animation", {})
        _file_path = self.resolve_output()
        _start_frame = settings.get_property("start_frame")
        _end_frame = settings.get_property("end_frame")
        step = float(1.0 / settings.get_property("sub_steps"))

        geo_node, rop_sop = self.__extract_base()

        rop_sop.parm("lopoutput").set(_file_path)
        # set properties
        rop_sop.parm("trange").set("normal")
        rop_sop.parm("f1").deleteAllKeyframes()
        rop_sop.parm("f2").deleteAllKeyframes()
        rop_sop.parm("f1").set(_start_frame)
        rop_sop.parm("f2").set(_end_frame)
        rop_sop.parm("f3").set(step)

        rop_sop.parm("execute").pressButton()
        geo_node.destroy()

    def _extract_layout(self):
        """Extract method for fx category"""
        settings = self.settings.get("Animation", {})
        _file_path = self.resolve_output()
        _start_frame = settings.get_property("start_frame")
        _end_frame = settings.get_property("end_frame")

        geo_node, rop_sop = self.__extract_base()

        rop_sop.parm("lopoutput").set(_file_path)
        # set properties
        rop_sop.parm("trange").set("normal")
        rop_sop.parm("f1").deleteAllKeyframes()
        rop_sop.parm("f2").deleteAllKeyframes()
        rop_sop.parm("f1").set(_start_frame)
        rop_sop.parm("f2").set(_end_frame)

        rop_sop.render()
        geo_node.destroy()

    def _extract_fx(self):
        """Extract method for fx category"""
        # identical to animation
        self._extract_animation()

    def _extract_lighting(self):
        """Extract method for lighting category"""
        # identical to layout
        self._extract_layout()

    def _extract_default(self):
        """Extract method for any non-specified category"""
        # Single frame export
        _file_path = self.resolve_output()
        geo_node, rop_sop = self.__extract_base()

        rop_sop.parm("lopoutput").set(_file_path)

        # set properties
        rop_sop.parm("trange").set("off")

        rop_sop.parm("execute").pressButton()
        geo_node.destroy()
        return True
