import os, sys
from maya import cmds
from maya import mel

dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.abspath(os.path.join(dir_path, os.pardir))
SHELF_DIR = os.path.join(parent_dir, "shelves")

if not os.path.exists(SHELF_DIR):
    print('\n\n WARNING \n\n')


def add_python_path():
    """adds the python path to during launch"""
    setup_path = os.path.abspath(os.path.join(parent_dir, os.pardir))
    maya_path = os.path.abspath(os.path.join(setup_path, os.pardir))
    dcc_path = os.path.abspath(os.path.join(maya_path, os.pardir))
    tik_manager4_path = os.path.abspath(os.path.join(dcc_path, os.pardir))
    home_path = os.path.abspath(os.path.join(tik_manager4_path, os.pardir))
    if home_path not in sys.path:
        sys.path.append(home_path)
    print("%s added to the python path" % home_path)


def load_shelves(reset=False):
    """
    Loads all shelves under SHELF_DIR.
    Args:
        reset: (Bool) if True, deletes the existing shelves and re-creates them

    Returns: None

    """
    if os.path.isdir(SHELF_DIR) and not cmds.about(batch=True):
        for s in os.listdir(SHELF_DIR):
            path = os.path.join(SHELF_DIR, s).replace('\\', '/')
            if not os.path.isfile(path): continue
            name = os.path.splitext(s)[0].replace('shelf_', '')
            # Delete existing shelf before loading
            if cmds.shelfLayout(name, exists=True):
                if reset:
                    cmds.deleteUI(name)
                    mel.eval('loadNewShelf("{}")'.format(path))
            else:
                mel.eval('loadNewShelf("{}")'.format(path))


def load_menu():
    main_ui_command = "from tik_manager4.ui import main as tik4_main\ntik4_main.launch(dcc='Maya')"
    add_to_menu("TikManager", "Main UI", main_ui_command)

    # add a separator
    cmds.menuItem(divider=True)
    recreate_command = "tik_manager_setup.load_shelves(reset=True)"
    add_to_menu("TikManager", "Re-create Shelves", recreate_command)


def add_to_menu(menu, menu_item, command):
    main_window = mel.eval('$tmpVar=$gMainWindow')
    menu_widget = '%s_widget' % menu

    # dont create another menu if already exists
    if cmds.menu(menu_widget, label=menu, exists=True, parent=main_window):
        tik_manager_menu = '%s|%s' % (main_window, menu_widget)
    else:
        tik_manager_menu = cmds.menu(menu_widget, label=menu, parent=main_window, tearOff=True)

    # skip the process if the menu_item exists
    item_array = cmds.menu(menu_widget, query=True, itemArray=True)
    if item_array:
        for item in item_array:
            label = cmds.menuItem(item, query=True, label=True)
            if label == menu_item:
                return

    cmds.menuItem(label=menu_item, command=command)
