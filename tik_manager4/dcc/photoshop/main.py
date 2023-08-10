from win32com.client import Dispatch

from tik_manager4.dcc.main_core import DccTemplate

# test dispatch
psApp = Dispatch("Photoshop.Application")


class Dcc(DccTemplate):
    """Photoshop DCC class"""

    pass
    # TODO mix-match from Tik Manager 3
