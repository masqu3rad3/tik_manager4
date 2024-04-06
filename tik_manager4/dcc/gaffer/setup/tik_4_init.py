# Tik Manager 4 [Start]
import sys
tik_path = 'PATH\\TO\\PARENT\\FOLDER\\OF\\TIKMANAGER4\\'
if not tik_path in sys.path:
    sys.path.append(tik_path)
# Tik Manager 4 [End]

import Gaffer
import GafferUI
import GafferScene

import tik_manager4
INIT = tik_manager4.initialize("Gaffer")

from tik_manager4.ui import main
from tik_manager4.dcc.gaffer.gaffer_menu import GafferMenu

def __main_ui(menu):
    _gaffer_menu = GafferMenu
    GafferMenu.set_menu(menu)
    main.launch(dcc="Gaffer")

def __new_version(menu):
    _gaffer_menu = GafferMenu
    GafferMenu.set_menu(menu)
    tui = main.launch("Gaffer", dont_show=True)
    tui.on_new_version()

def __publish(menu):
    _gaffer_menu = GafferMenu
    GafferMenu.set_menu(menu)
    tui = main.launch("Mari", dont_show=True)
    tui.on_publish_scene()

GafferUI.ScriptWindow.menuDefinition(application).append( "/TikManager/Main UI", { "command" : __main_ui } )
GafferUI.ScriptWindow.menuDefinition(application).append( "/TikManager/New Version", { "command" : __new_version } )
GafferUI.ScriptWindow.menuDefinition(application).append( "/TikManager/Publish", { "command" : __publish } )