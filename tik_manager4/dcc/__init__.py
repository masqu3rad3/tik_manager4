import os

try:
    from maya import OpenMayaUI as omui
    from tik_manager4.dcc import maya as dcc
except ImportError:
    pass

try:
    from pymxs import runtime as rt
    from tik_manager4.dcc import max as dcc
except ImportError:
    pass

try:
    import hou
    from tik_manager4.dcc import houdini as dcc
except ImportError:
    pass

try:
    import nuke
    from tik_manager4.dcc import nuke as dcc
except ImportError:
    pass

try:
    if bool(os.getenv("PS_APP")):  # if the request is coming from the SmPhotoshop
        from tik_manager4.dcc import photoshop as dcc
except ImportError:
    dcc = None