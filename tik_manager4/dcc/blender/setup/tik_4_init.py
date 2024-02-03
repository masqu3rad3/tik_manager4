bl_info = {
    "name": "Tik Main UI",
    "blender": (4, 0, 0),
    "category": "Object",
}

import sys

import bpy

tik_path = "PATH\\TO\\TIK_MANAGER4\\"

if tik_path not in sys.path:
    sys.path.append(tik_path)

from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.ui import main


# Define an operator for the Main UI
class WM_OT_TikMainUI(bpy.types.Operator):
    bl_idname = "wm.tik_main_ui"
    bl_label = "Tik Main UI"

    def execute(self, context):
        tik_ui = main.launch(dcc="Blender")
        self.report({'INFO'}, "Tik Main UI Launched")
        return {'FINISHED'}


# Define an operator for the Save Version action
class WM_OT_TikSaveVersion(bpy.types.Operator):
    bl_idname = "wm.tik_new_version"
    bl_label = "Tik New Version"

    def execute(self, context):
        tik_ui = main.launch(dcc="Blender", dont_show=True)
        tik_ui.on_new_version()
        return {'FINISHED'}

    # Define an operator for the Publish action


class WM_OT_TikPublish(bpy.types.Operator):
    bl_idname = "wm.tik_publish"
    bl_label = "Tik Publish"

    def execute(self, context):
        tik_ui = main.launch(dcc="Blender", dont_show=True)
        tik_ui.on_publish_scene()
        return {'FINISHED'}

    # Define the Tik Manager menu


class VIEW3D_MT_tik_manager(bpy.types.Menu):
    bl_label = "Tik Manager"
    bl_idname = "VIEW3D_MT_tik_manager"

    def draw(self, context):
        layout = self.layout

        # Add the commands to launch the external UI
        layout.operator("wm.tik_main_ui")
        # Add a separator between commands
        layout.separator()
        layout.operator("wm.tik_new_version")
        layout.operator("wm.tik_publish")


# Add the Tik Manager menu to the top bar at the end of the list
def menu_func(self, context):
    self.layout.menu("VIEW3D_MT_tik_manager")


def register():
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    bpy.utils.register_class(WM_OT_TikMainUI)
    bpy.utils.register_class(WM_OT_TikSaveVersion)
    bpy.utils.register_class(WM_OT_TikPublish)
    bpy.utils.register_class(VIEW3D_MT_tik_manager)
    bpy.types.TOPBAR_HT_upper_bar.prepend(menu_func)


def unregister():
    bpy.utils.unregister_class(WM_OT_TikMainUI)
    bpy.utils.unregister_class(VIEW3D_MT_tik_manager)


if __name__ == "__main__":
    register()
