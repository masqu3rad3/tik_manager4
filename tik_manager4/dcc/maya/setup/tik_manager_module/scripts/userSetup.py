from maya import cmds
import tik_manager_setup

cmds.evalDeferred(tik_manager_setup.add_python_path)
cmds.evalDeferred(tik_manager_setup.load_menu)
