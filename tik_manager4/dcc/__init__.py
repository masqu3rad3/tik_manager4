import os

NAME = os.getenv("TIK_DCC")

if NAME == "Maya":
    from tik_manager4.dcc.maya.main import Dcc
elif NAME == "3dsmax":
    from tik_manager4.dcc.max.main import Dcc
elif NAME == "Houdini":
    from tik_manager4.dcc.houdini.main import Dcc
elif NAME == "Nuke":
    from tik_manager4.dcc.nuke.main import Dcc
elif NAME == "Photoshop":
    from tik_manager4.dcc.photoshop.main import Dcc
elif NAME == "Standalone":
    from tik_manager4.dcc.standalone.main import Dcc
