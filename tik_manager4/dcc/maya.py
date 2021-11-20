import os
import maya.cmds as cmds
import maya.mel as mel

NAME = "Maya"

def new_scene(force=True, fps=None):
    cmds.file(new=True, f=force)
    if fps:
        fpsDict = {15: "game",
                   24: "film",
                   25: "pal",
                   30: "ntsc",
                   48: "show",
                   50: "palf",
                   60: "ntscf"}
        ranges = get_ranges()
        cmds.currentUnit(time=fpsDict[fps])
        set_ranges(ranges)
        cmds.currentTime(1)

def get_ranges():
    R_ast = cmds.playbackOptions(q=True, ast=True)
    R_min = cmds.playbackOptions(q=True, min=True)
    R_max = cmds.playbackOptions(q=True, max=True)
    R_aet = cmds.playbackOptions(q=True, aet=True)
    return [R_ast, R_min, R_max, R_aet]

def set_ranges(range_list):
    """
    sets the timeline ranges

    Args:
        range_list: list of ranges as [<animation start>, <user min>, <user max>, <animation end>]

    Returns: None

    """
    cmds.playbackOptions(ast=range_list[0], min=range_list[1], max=range_list[2], aet=range_list[3])