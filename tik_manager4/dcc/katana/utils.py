"""Collection of utility functions for Katana

These are essentially methods are both required by the main module and the ingest,
extract and/or validate modules.
To prevent circular imports, these methods are collected here.
"""

from Katana import NodegraphAPI # pylint: disable=import-error
from Katana import Utils # pylint: disable=import-error

def get_ranges():
    """Get the viewport ranges.
        Returns (list): [<absolute range start>, <user range start>, <user range end>,
        <absolute range end>
    """
    r_ast = NodegraphAPI.GetInTime()
    r_min = NodegraphAPI.GetWorkingInTime()
    r_max = NodegraphAPI.GetWorkingOutTime()
    r_aet = NodegraphAPI.GetOutTime()
    return [r_ast, r_min, r_max, r_aet]


def set_ranges(range_list):
    """Set the timeline ranges.
    Args:
        range_list: list of ranges as [<animation start>, <user min>, <user max>,
                                        <animation end>]

    Returns: None
    """
    NodegraphAPI.SetInTime(range_list[0])
    NodegraphAPI.SetWorkingInTime(range_list[1])
    NodegraphAPI.SetWorkingOutTime(range_list[2])
    NodegraphAPI.SetOutTime(range_list[3])