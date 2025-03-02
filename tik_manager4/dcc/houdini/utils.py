"""Collection of utility functions for Houdini.

These are essentially methods are both required by the main module and the ingest, extract and/or validate modules.
To prevent circular imports, these methods are collected here.
"""

import hou


def get_ranges():
    """Get the viewport ranges."""
    r_ast = int(hou.playbar.frameRange()[0])
    r_min = int(hou.playbar.playbackRange()[0])
    r_max = int(hou.playbar.playbackRange()[1])
    r_aet = int(hou.playbar.frameRange()[1])
    return [r_ast, r_min, r_max, r_aet]


def set_ranges(range_list):
    """
    Set the timeline ranges.

    Args:
        range_list: list of ranges as [<animation start>, <user min>, <user max>,
                                        <animation end>]

    Returns: None

    """
    hou.playbar.setFrameRange(range_list[0], range_list[3])
    hou.playbar.setPlaybackRange(range_list[1], range_list[2])

def get_scene_fps():
    """Return the current FPS value set by DCC. None if not supported."""
    return hou.fps()

def set_scene_fps(fps_value):
    """
    Set the FPS value in DCC if supported.
    Args:
        fps_value: (integer) fps value

    Returns: None

    """
    scene_range = get_ranges()
    hou.setFps(fps_value)
    set_ranges(scene_range)

def set_environment_variable(var, value):
    """Set the environment variable."""
    hou.allowEnvironmentToOverwriteVariable(var, True)
    hou.putenv(var, value)
    value = value.replace("\\", "/")
    hscript_command = "set -g %s = '%s'" % (var, value)
    hou.hscript(str(hscript_command))

def resolve_extension():
    """Return the appropriate format for non-commercial version."""
    if hou.isApprentice() or hou.licenseCategory() == hou.licenseCategoryType.Education:
        return ".hipnc"
    return ".hip"