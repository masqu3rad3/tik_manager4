bl_info = {
    "name": "Tik Main UI",
    "blender": (4, 0, 0),
    "category": "Object",
}

import bpy
import sys

p_path = "D:\\dev\\tik_manager4\\tik_manager4\\dcc\\blender\\site-packages"
s_path = "D:\\dev\\tik_manager4\\"

if p_path not in sys.path:
    sys.path.append(p_path)

if s_path not in sys.path:
    sys.path.append(s_path)

from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.ui import main


class TikMainUI(bpy.types.Operator):
    bl_idname = "object.tik4"
    bl_label = "Tik4"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        tik_ui = main.launch(dcc="Blender")
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(TikMainUI.bl_idname)


def register():
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)

    bpy.utils.register_class(TikMainUI)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(TikMainUI)


if __name__ == "__main__":
    register()