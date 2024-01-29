""" This module contains utility functions for Blender. """

import bpy


def get_ranges():
    """Get the frame range."""
    start = bpy.context.scene.frame_start
    end = bpy.context.scene.frame_end
    return [start, start, end, end]

def set_ranges(range_list):
    """Set the frame range."""
    bpy.context.scene.frame_start = range_list[0]
    bpy.context.scene.frame_end = range_list[-1]

def get_override_context(context=None):
    ctx = bpy.context.copy()

    for window in bpy.context.window_manager.windows:
        ctx["window"] = window
        screen = window.screen
        ctx["screen"] = screen

        if context:
            for area in screen.areas:
                if area.type == context:
                    ctx["area"] = area
                    for region in area.regions:
                        if region.type == "WINDOW":
                            ctx["region"] = region
                            return ctx

        for area in screen.areas:
            if area.type == "VIEW_3D":
                ctx["area"] = area
                return ctx

        for area in screen.areas:
            if area.type == "IMAGE_EDITOR":
                ctx["area"] = area
                return ctx

    return ctx
