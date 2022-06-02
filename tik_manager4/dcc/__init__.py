import os


def get_dcc():
    try:
        from maya import OpenMayaUI as omui
        return "Maya"
    except ImportError:
        pass
    try:
        from pymxs import runtime as rt
        return "Max"
    except ImportError:
        pass
    try:
        import hou
        return "Houdini"
    except ImportError:
        pass
    try:
        import nuke
        return "Nuke"
    except ImportError:
        pass

    if bool(os.getenv("PS_APP")):  # if the request is coming from the SmPhotoshop
        return "Photoshop"
    else:
        return "Standalone"


NAME = get_dcc()

if NAME == "Maya":
    from tik_manager4.dcc.maya import Dcc
elif NAME == "Max":
    from tik_manager4.dcc.max import Dcc
elif NAME == "Houdini":
    from tik_manager4.dcc.houdini import Dcc
elif NAME == "Nuke":
    from tik_manager4.dcc.nuke import Dcc
elif NAME == "Photoshop":
    from tik_manager4.dcc.photoshop import Dcc
elif NAME == "Standalone":
    from tik_manager4.dcc.standalone import Dcc

# try:
#     from maya import OpenMayaUI as omui
#     from tik_manager4.dcc.maya import Dcc
#
#     NAME = "Maya"
# except ImportError:
#     pass
#
# try:
#     from pymxs import runtime as rt
#     from tik_manager4.dcc.max import Dcc
#
#     NAME = "Max"
# except ImportError:
#     pass
#
# try:
#     import hou
#     from tik_manager4.dcc.houdini import Dcc
#
#     NAME = "Houdini"
# except ImportError:
#     pass
#
# try:
#     import nuke
#     from tik_manager4.dcc.nuke import Dcc
#
#     NAME = "Nuke"
# except ImportError:
#     pass
#
# try:
#     if bool(os.getenv("PS_APP")):  # if the request is coming from the SmPhotoshop
#         from tik_manager4.dcc.photoshop import Dcc
#
#         NAME = "Photoshop"
#     else:
#         Dcc = None
#         NAME = "Standalone"
# except ImportError:
#     Dcc = None
#     NAME = "Standalone"
