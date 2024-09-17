import hou
from tik_manager4.dcc.houdini.hda.nodes import callbacks

class SopImportCallbacks(callbacks.Callbacks):
    def __init__(self):
        super(SopImportCallbacks, self).__init__()

    def update_path(self, version_obj, element_type):
        hda_node = hou.pwd()
        switch_node = hda_node.node("element_switch")
        alembic_node = hda_node.node("ALEMBIC")
        usd_node = hda_node.node("USD")
        switch_node.parm("input").set(0)
        alembic_node.parm("fileName").set("")
        usd_node.parm("filepath1").set("")
        # set the switch

        parm = hda_node.parm("resolvedPathDisplay")
        parm.lock(False)
        if not all([version_obj, element_type]):
            hda_node.parm("resolvedPathDisplay").set("")
            parm.lock(True)
            return

        abs_path = version_obj.get_element_path(element_type, relative=False)

        # element type as key, [file node, switch value] as value
        switch_map = {
            "alembic": [alembic_node.parm("fileName"), 1],
            "usd": [usd_node.parm("filepath1"), 2],
        }

        mapped = switch_map[element_type.lower()]
        mapped[0].set(abs_path)
        switch_node.parm("input").set(mapped[1])

        hda_node.parm("resolvedPathDisplay").set(abs_path)
        parm.lock(True)
