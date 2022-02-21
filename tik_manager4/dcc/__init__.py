import os

try:
    from maya import OpenMayaUI as omui
    from tik_manager4.dcc.maya import Dcc
except ImportError:
    pass

try:
    from pymxs import runtime as rt
    from tik_manager4.dcc.max import Dcc
except ImportError:
    pass

try:
    import hou
    from tik_manager4.dcc.houdini import Dcc
except ImportError:
    pass

try:
    import nuke
    from tik_manager4.dcc.nuke import Dcc
except ImportError:
    pass

try:
    if bool(os.getenv("PS_APP")):  # if the request is coming from the SmPhotoshop
        from tik_manager4.dcc.photoshop import Dcc
except ImportError:
    Dcc = None