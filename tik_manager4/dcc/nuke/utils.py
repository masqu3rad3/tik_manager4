"""Collection of utility functions for Nuke

These are essentially methods are both required by the main module and the ingest,
extract and/or validate modules.
To prevent circular imports, these methods are collected here.
"""

import nuke


def get_ranges():
    """
    Get the viewport ranges.
    Returns: (list) [<absolute range start>, <user range start>, <user range end>,
    <absolute range end>
    """
    start_frame = nuke.Root().firstFrame()
    end_frame = nuke.Root().lastFrame()
    return [start_frame, start_frame, end_frame, end_frame]

def set_ranges(range_list):
    """
    Set the timeline ranges.

    Args:
        range_list: list of ranges as [<animation start>, <user min>, <user max>,
                                        <animation end>]

    Returns: None

    """
    nuke.Root().setFirstFrame(range_list[0])
    nuke.Root().setLastFrame(range_list[3])
