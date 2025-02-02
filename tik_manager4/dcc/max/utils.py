from pymxs import runtime as rt

def get_ranges():
    """Get the viewport ranges."""
    r_ast = float(rt.animationRange.start)
    r_min = float(rt.animationRange.start)
    r_max = float(rt.animationRange.end)
    r_aet = float(rt.animationRange.end)
    return [r_ast, r_min, r_max, r_aet]

def set_ranges(range_list):
    """
    Set the timeline ranges.

    Args:
        range_list: list of ranges as [<animation start>, <user min>, <user max>,
                                        <animation end>]

    Returns: None

    """
    rt.animationRange = rt.interval(range_list[0], range_list[-1])

def get_scene_fps():
    """Return the current FPS value set by DCC. None if not supported."""
    return rt.framerate

def set_scene_fps(fps_value):
    """
    Set the FPS value in DCC if supported.
    Args:
        fps_value: (integer) fps value

    Returns: None

    """
    range = get_ranges()
    rt.framerate = fps_value
    set_ranges(range)