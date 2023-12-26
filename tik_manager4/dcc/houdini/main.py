import hou

from tik_manager4.dcc.main_core import MainCore

NAME = "Houdini"


class Dcc(MainCore):
    hou.displayMessage("Houdini DCC loaded")
    pass
    # TODO mix-match from Tik Manager 3
