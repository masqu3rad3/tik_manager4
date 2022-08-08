import os


# def get_dcc():
#     try:
#         from maya import OpenMayaUI as omui
#         return "Maya"
#     except ImportError:
#         pass
#     try:
#         from pymxs import runtime as rt
#         return "Max"
#     except ImportError:
#         pass
#     try:
#         import hou
#         return "Houdini"
#     except ImportError:
#         pass
#     try:
#         import nuke
#         return "Nuke"
#     except ImportError:
#         pass
#
#     if bool(os.getenv("PS_APP")):  # if the request is coming from the SmPhotoshop
#         return "Photoshop"
#     else:
#         return "Standalone"

# NAME = get_dcc()

NAME = os.getenv("TIK_DCC")

if NAME == "Maya":
    from tik_manager4.dcc.maya.core import Dcc
elif NAME == "Max":
    from tik_manager4.dcc.max.core import Dcc
elif NAME == "Houdini":
    from tik_manager4.dcc.houdini.core import Dcc
elif NAME == "Nuke":
    from tik_manager4.dcc.nuke.core import Dcc
elif NAME == "Photoshop":
    from tik_manager4.dcc.photoshop.core import Dcc
elif NAME == "Standalone":
    from tik_manager4.dcc.standalone.core import Dcc
