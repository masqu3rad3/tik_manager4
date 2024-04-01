# Tik Manager 4 [Start]
import mari
import sys
tik_path = 'PATH\\TO\\PARENT\\FOLDER\\OF\\TIKMANAGER4\\'
if not tik_path in sys.path:
    sys.path.append(tik_path)

tik_main_ui_action = mari.actions.create('Main UI', 'from tik_manager4.ui import main;main.launch("mari")')
mari.menus.addAction(tik_main_ui_action, 'MainWindow/Tik Manager')

tik_new_version = mari.actions.create('New Version', 'from tik_manager4.ui import main;tui = main.launch("Mari", dont_show=True);tui.on_new_version()')
mari.menus.addAction(tik_new_version, 'MainWindow/Tik Manager')

tik_publish = mari.actions.create('Publish', 'from tik_manager4.ui import main;tui = main.launch("Mari", dont_show=True);tui.on_publish_scene()')
mari.menus.addAction(tik_publish, 'MainWindow/Tik Manager')
# Tik Manager 4 [End]


