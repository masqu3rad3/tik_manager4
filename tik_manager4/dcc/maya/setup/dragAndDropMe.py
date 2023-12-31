"""Drag & Drop installer for Maya 2018+"""

import os, sys

# confirm the maya python interpreter
CONFIRMED = False
try:
    from maya import cmds

    CONFIRMED = True
except ImportError:
    CONFIRMED = False


def onMayaDroppedPythonFile(*args, **kwargs):
    _add_module()


def _add_module():
    trigger_module = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "tik_manager_module")
    )
    module_file_content = """+ tik_manager 4.0.1 %s""" % trigger_module

    user_module_dir = os.path.join(cmds.internalVar(uad=True), "modules")
    if not os.path.isdir(user_module_dir):
        os.mkdir(user_module_dir)
    user_module_file = os.path.join(user_module_dir, "tik_manager4.mod")
    if os.path.isfile(user_module_file):
        os.remove(user_module_file)

    f = open(user_module_file, "w+")
    f.writelines(module_file_content)
    f.close()

    # first time initialize
    cmds.confirmDialog(
        title="Tik Manager4",
        message="Tik Manager 4 Installed. Please restart Maya to see the shelf and menu items.",
    )
    pass


def _edit_usersetup():
    file_location = os.path.join(os.path.dirname(__file__))
    pass
