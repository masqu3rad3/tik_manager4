# Tik Manager 4 [Start]
import sys
tik_path = 'PATH\\TO\\PARENT\\FOLDER\\OF\\TIKMANAGER4\\'
if not tik_path in sys.path:
    sys.path.append(tik_path)
# Tik Manager 4 [End]

from tik_manager4.ui.Qt import QtWidgets
import substance_painter.ui
from tik_manager4.ui import main

plugin_widgets = []

def __main_ui():
    """Launch main ui."""
    tui = main.launch(dcc="Substance")
    # plugin_widgets.append(tui)

def __new_version():
    """New version."""
    tui = main.launch("Substance", dont_show=True)
    # plugin_widgets.append(tui)
    tui.on_new_version()

def __publish():
    """New version."""
    tui = main.launch("Substance", dont_show=True)
    # plugin_widgets.append(tui)
    tui.on_publish_scene()

def start_plugin():
    # Get the application main window.
    mainWindow = substance_painter.ui.get_main_window()
    plugin_widgets.append(mainWindow)

    tik_manager_menu = mainWindow.menuBar().addMenu("Tik Manager")
    plugin_widgets.append(tik_manager_menu)

    main_ui_action = QtWidgets.QAction("Main UI")    
    plugin_widgets.append(main_ui_action)
    tik_manager_menu.addAction(main_ui_action)

    new_version_action = tik_manager_menu.addAction("New Version")
    plugin_widgets.append(new_version_action)

    publish_action = tik_manager_menu.addAction("Publish")
    plugin_widgets.append(publish_action)

    # SIGNALS
    main_ui_action.triggered.connect(__main_ui)
    new_version_action.triggered.connect(__new_version)
    publish_action.triggered.connect(__publish)

def close_plugin():
    # Remove all tik manager widgets that are lingering around.
    for widget in QtWidgets.QApplication.topLevelWidgets():
    # for widget in QtWidgets.QApplication.allWidgets():
        if widget.__module__.startswith("tik_manager4."):
            substance_painter.ui.delete_ui_element(widget)

if __name__ == "__main__":
    start_plugin()