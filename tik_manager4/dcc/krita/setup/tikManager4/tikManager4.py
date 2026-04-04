import io
import sys
from pathlib import Path

from krita import Extension, Krita

if sys.stderr is None:
    sys.stderr = io.StringIO()
if sys.stdout is None:
    sys.stdout = io.StringIO()

tik_path = 'PATH\\TO\\PARENT\\FOLDER\\OF\\TIKMANAGER4\\'
script_dir = Path(__file__).parent

if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))
if str(tik_path) not in sys.path:
    sys.path.append(tik_path)

import qt_compat

from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.ui import main


class TikManagerExtension(Extension):
    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        menubar = window.qwindow().menuBar()
        tik_menu = QtWidgets.QMenu("Tik Manager", menubar)
        menubar.addMenu(tik_menu)
        action_main = tik_menu.addAction("Main UI")
        action_main.triggered.connect(self.launch_main_ui)
        action_new_version = tik_menu.addAction("New Version")
        action_new_version.triggered.connect(self.launch_new_version)
        action_publish = tik_menu.addAction("Publish")
        action_publish.triggered.connect(self.launch_publish)

    def launch_main_ui(self):
        main.launch(dcc="krita")

    def launch_new_version(self):
        tik_ui = main.launch(dcc="krita", dont_show=True)
        tik_ui.on_new_version()

    def launch_publish(self):
        tik_ui = main.launch(dcc="krita", dont_show=True)
        tik_ui.on_publish_scene()


Krita.instance().addExtension(TikManagerExtension(Krita.instance()))
