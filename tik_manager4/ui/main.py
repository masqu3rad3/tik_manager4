"""Main UI for Tik Manager 4."""

from tik_manager4.ui.Qt import QtWidgets, QtCore

from tik_manager4.ui.mcv.subproject_tree import TikProjectLayout
from tik_manager4.ui.mcv.task_tree import TikTaskLayout
from tik_manager4.ui.mcv.category import TikCategoryLayout
from tik_manager4.ui.mcv.version import TikVersionLayout
import tik_manager4._version as version
import tik_manager4



class MainUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainUI, self).__init__()

        self.setWindowTitle("Tik Manager {}".format(version.__version__))
        tik = tik_manager4.initialize("Standalone")

        # set window size
        self.resize(1200, 800)


