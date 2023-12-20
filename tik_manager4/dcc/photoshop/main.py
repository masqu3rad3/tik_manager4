from win32com.client import Dispatch

from tik_manager4.dcc.main_core import MainCore

# test dispatch
psApp = Dispatch("Photoshop.Application")


class Dcc(MainCore):
    """Photoshop DCC class"""

    pass
    # TODO mix-match from Tik Manager 3
