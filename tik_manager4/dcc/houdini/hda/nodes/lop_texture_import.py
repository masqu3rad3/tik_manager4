import hou
from tik_manager4.dcc.houdini.hda.nodes import callbacks

class LopTextureImportCallbacks(callbacks.Callbacks):
    def __init__(self):
        super(LopTextureImportCallbacks, self).__init__()
        self.valid_elements = ["texture_bundle"]

    def update_path(self, version_obj, element_type):
        print("update_path")
        print("----------------")
        # print(version_obj)
        # print(element_type)
        # print("----------------")
        # hda_node = hou.pwd()
        # reference_node = hda_node.node("REFERENCE")
        # sublayer_node = hda_node.node("SUBLAYER")
        #
        # reference_node.parm("filepath1").set("")
        # sublayer_node.parm("filepath1").set("")
        # # set the switch
        #
        # parm = hda_node.parm("resolvedPathDisplay")
        # parm.lock(False)
        # if not all([version_obj, element_type]):
        #     hda_node.parm("resolvedPathDisplay").set("")
        #     parm.lock(True)
        #     return
        #
        # abs_path = version_obj.get_element_path(element_type, relative=False)
        #
        # reference_node.parm("filepath1").set(abs_path)
        # sublayer_node.parm("filepath1").set(abs_path)
        # hda_node.parm("resolvedPathDisplay").set(abs_path)
        # parm.lock(True)
