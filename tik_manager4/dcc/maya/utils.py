"""Collection of utility functions for Maya

These are essentially methods are both required by the main module and the ingest,
extract and/or validate modules.
To prevent circular imports, these methods are collected here.
"""

from functools import wraps
from maya import cmds  # pylint: disable=import-error
from maya import mel  # pylint: disable=import-error


def get_ranges():
    """Get the viewport ranges.
    Returns (list): [<absolute range start>, <user range start>, <user range end>,
    <absolute range end>
    """
    r_ast = cmds.playbackOptions(query=True, animationStartTime=True)
    r_min = cmds.playbackOptions(query=True, minTime=True)
    r_max = cmds.playbackOptions(query=True, maxTime=True)
    r_aet = cmds.playbackOptions(query=True, animationEndTime=True)
    return [r_ast, r_min, r_max, r_aet]


def set_ranges(range_list):
    """Set the timeline ranges.
    Args:
        range_list: list of ranges as [<animation start>, <user min>, <user max>,
                                        <animation end>]

    Returns: None
    """
    cmds.playbackOptions(
        animationStartTime=range_list[0],
        minTime=range_list[1],
        maxTime=range_list[2],
        animationEndTime=range_list[3],
    )


def get_scene_fps():
    """Return the current FPS value set by DCC. None if not supported."""
    return mel.eval("currentTimeUnitToFPS")


def set_scene_fps(fps_value):
    """
    Set the FPS value in DCC if supported.
    Args:
        fps_value: (integer) fps value

    Returns: None

    """
    # maya is a bit weird with fps.
    # there are number of predefined fps values. Some float, some int.
    # Int ones don't accept float values and vice versa.
    if int(fps_value) == fps_value:
        fps_value = int(fps_value)
    try:
        mel.eval(f"currentUnit -time {fps_value}fps;")
    except RuntimeError as exc:
        raise RuntimeError("Invalid FPS value") from exc


def keepselection(func):
    """Decorator method to keep the current selection. Useful where
    the wrapped method messes with the current selection"""
    @wraps(func)
    def _keepfunc(*args, **kwargs):
        original_selection = cmds.ls(selection=True)
        component_state = cmds.selectMode(query=True, component=True)
        object_state = cmds.selectMode(query=True, object=True)
        try:
            # start an undo chunk
            return func(*args, **kwargs)
        except Exception as exc:
            raise exc
        finally:
            # after calling the func, end the undo chunk and undo
            cmds.selectMode(object=object_state, component=component_state)
            cmds.select(original_selection)

    return _keepfunc

def unique_name(name, return_counter=False, suffix=None):
    """
    Searches the scene for match and returns a unique name for given name
    Args:
        name: (String) Name to query
        return_counter: (Bool) If true, returns the next available number instead of the object name
        suffix: (String) If defined and if name ends with this suffix, the increment numbers will be put before the.

    Returns: (String) uniquename

    """
    search_name = name
    base_name = name
    if suffix and name.endswith(suffix):
        base_name = name.replace(suffix, "")
    else:
        suffix = ""
    id_counter = 0
    while cmds.objExists(search_name):
        search_name = "{0}{1}{2}".format(base_name, str(id_counter + 1), suffix)
        id_counter = id_counter + 1
    if return_counter:
        return id_counter
    else:
        if id_counter:
            result_name = "{0}{1}{2}".format(base_name, str(id_counter), suffix)
        else:
            result_name = name
        return result_name
