import os

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
