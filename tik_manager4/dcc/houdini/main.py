import hou

from tik_manager4.dcc.main_core import DccTemplate

NAME = "Houdini"


class Dcc(DccTemplate):
    hou.displayMessage("Houdini DCC loaded")
    pass
    # TODO mix-match from Tik Manager 3
