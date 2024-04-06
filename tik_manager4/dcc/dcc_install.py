# pylint: disable=too-many-locals, line-too-long, too-many-statements

"""Convenience functions for installing and integrating DCCs."""
import getopt
import logging
import os
import platform
import shutil
import sys
import winreg as reg
from pathlib import Path

import psutil

if platform.system() != "Windows":
    raise OSError("This module currently only works on Windows")

from tik_manager4 import _version
from tik_manager4.core import utils


LOG = logging.getLogger(__name__)

FROZEN = getattr(sys, 'frozen', False)

def print_msg(msg):
    """Prints a message to the console."""
    sys.stdout.write(f"{msg}\n")

class Installer:
    """A simple command line interface for installing software."""
    def __init__(self, argv):
        self.argv = argv

        # variables
        self.user_home = Path(utils.get_home_dir())
        self.user_documents = self.user_home / "Documents"
        self.tik_local = self.user_home / "TikManager4"
        self.tik_local.mkdir(exist_ok=True)

        if FROZEN:
            self.tik_root = Path(sys.executable).parent.parent.parent
        else:
            self.tik_root = Path(__file__).parent.parent

        self.tik_dcc_folder = self.tik_root / "dcc"

        # when changing the mapping, the install all function should be updated
        # Any changes here also needs to be reflected to the package/release_package.py
        # and packacge/tik_manager4_innosetup.iss
        self.dcc_mapping = {
        "Maya": self.maya_setup,
        "Houdini": self.houdini_setup,
        "3dsMax": self.max_setup,
        "Blender": self.blender_setup,
        "Nuke": self.nuke_setup,
        "Photoshop": self.photoshop_setup,
        "Katana": self.katana_setup,
        "Mari": self.mari_setup,
        "Gaffer": self.gaffer_setup,
        }

    def install_all(self):
        """Installs all the plugins."""
        self.maya_setup(prompt=False)
        self.houdini_setup(prompt=False)
        self.max_setup(prompt=False)
        self.blender_setup(prompt=False)
        self.nuke_setup(prompt=False)
        self.photoshop_setup(prompt=False)
        self.katana_setup(prompt=False)
        self.mari_setup(prompt=False)
        self.gaffer_setup(prompt=False)
        ret = input("Setup Completed. Press Enter to Exit...")
        assert isinstance(ret, str)
        sys.exit()

    def maya_setup(self, prompt=True):
        """Installs the Maya plugin."""
        print_msg("Starting Maya Setup...")

        if self.check_running_instances("maya") == -1:
            print_msg("Installation aborted by user.")
            return

        user_maya_folder = self.user_documents / "maya"

        if not user_maya_folder.exists():
            print_msg("No Maya version can be found in the user's documents directory")
            print_msg("Make sure Maya is installed and try again. "
                      "Alternatively you can try manual install. "
                      "Check the documentation for more information.")
            if prompt:
                _r = input("Press Enter to continue...")
                assert isinstance(_r, str)
            return

        modules_folder = user_maya_folder / "modules"
        modules_folder.mkdir(parents=True, exist_ok=True)
        tik_manager_module = self.tik_dcc_folder / "maya" / "setup" / "tik_manager_module"

        module_file = modules_folder / "tik_manager4.mod"
        module_content = f"+ tik_manager4 4.0.1 {tik_manager_module.as_posix()}"
        injector = Injector(module_file)
        injector.replace_all(module_content)

        print_msg("Maya setup completed.")
        if prompt:
            _r = input("Press Enter to continue...")
            assert isinstance(_r, str)

    def houdini_setup(self, prompt=True):
        """Installs the Houdini plugin."""
        print_msg("Starting Houdini Setup...")

        if self.check_running_instances("houdini") == -1:
            print_msg("Installation aborted by user.")
            return

        print_msg("Finding Houdini Versions...")

        # find all folders under user documents folder that start with "houdini"
        houdini_folders = [x for x in self.user_documents.iterdir() if x.is_dir() and x.name.startswith("houdini")]

        if houdini_folders:
            print_msg("Houdini versions found:")
            for folder in houdini_folders:
                print_msg(f"{folder.name}")
        else:
            if prompt:
                print_msg("No Houdini version can be found in the user's documents directory.")
                print_msg("Make sure Houdini is installed and try again. Alternatively you can try manual install. "
                          "Check the documentation for more information.")
                if prompt:
                    _r = input("Press Enter to continue...")
                    assert isinstance(_r, str)
            return

        main_ui_icon = self.tik_dcc_folder / "houdini" / "setup" / "icons" / "tik4_main_ui.png"
        new_version_icon = self.tik_dcc_folder / "houdini" / "setup" / "icons" / "tik4_new_version.png"
        publish_icon = self.tik_dcc_folder / "houdini" / "setup" / "icons" / "tik4_publish.png"

        script456_content = [
            "# Tik Manager 4 [Start]\n",
            "import sys\n",
            f"tik_path = '{self.tik_root.parent.as_posix()}'\n",
            "if not tik_path in sys.path:\n",
            "    sys.path.append(tik_path)\n",
            "# Tik Manager 4 [End]\n",
        ]

        shelf_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<shelfDocument>
  <!-- This file contains definitions of shelves, toolbars, and tools.
 It should not be hand-edited when it is being used by the application.
 Note, that two definitions of the same element are not allowed in
 a single file. -->

  <toolshelf name="TikManager4" label="TikManager4">
    <memberTool name="MainUI"/>
    <memberTool name="NewVersion"/>
    <memberTool name="PublishScene"/>
  </toolshelf>

  <tool name="MainUI" label="MainUI" icon="{main_ui_icon.as_posix()}">
    <script scriptType="python"><![CDATA[
from tik_manager4.ui import main as tik4_main
tik4_main.launch(dcc="Houdini")
]]></script>
  </tool>

  <tool name="NewVersion" label="NewVersion" icon="{new_version_icon.as_posix()}">
    <script scriptType="python"><![CDATA[
from tik_manager4.ui import main as tik4_main
tui = tik4_main.launch(dcc='Houdini', dont_show=True)
tui.on_new_version()
]]></script>
  </tool>

  <tool name="PublishScene" label="PublishScene" icon="{publish_icon.as_posix()}">
    <script scriptType="python"><![CDATA[
from tik_manager4.ui import main as tik4_main
tui = tik4_main.launch(dcc='Houdini', dont_show=True)
tui.on_publish_scene()
]]></script>
  </tool>
</shelfDocument>
"""
        for version in houdini_folders:
            print_msg(f"Setting up {version.name}...")
            scripts_folder = version / "scripts"
            scripts_folder.mkdir(parents=True, exist_ok=True)
            script456_file = scripts_folder / "456.py"
            print_msg("Path configuration added to 456.py")

            injector = Injector(script456_file)
            injector.inject_between(script456_content,
                                    start_line="# Tik Manager 4 [Start]\n",
                                    end_line="# Tik Manager 4 [End]\n")

            shelf_folder = version / "toolbar"
            shelf_folder.mkdir(parents=True, exist_ok=True)
            shelf_file = shelf_folder / "tik_manager4.shelf"
            injector.set_file_path(shelf_file)
            injector.replace_all(shelf_content)
            print_msg("Shelf file created.")

        print_msg("Inside Houdini, Tik Manager shelf should be enabled "
                  "for the desired shelf set by clicking to '+' "
                  "icon and selecting 'shelves' sub menu.")

        print_msg("Houdini setup completed.")
        if prompt:
            _r = input("Press Enter to continue...")
            assert isinstance(_r, str)

    def max_setup(self, prompt=True):
        """Installs the 3ds Max plugin."""
        print_msg("Starting 3dsmax Setup...")

        if self.check_running_instances("3dsmax") == -1:
            print_msg("Installation aborted by user.")
            return

        user_max_dir = self.user_home / "AppData" / "Local" / "Autodesk" / "3dsMax"

        pack_16a = self.tik_dcc_folder / "max" / "setup" / "icons" / "TikManager4_16a.bmp"
        pack_16i = self.tik_dcc_folder / "max" / "setup" / "icons" / "TikManager4_16i.bmp"
        pack_24a = self.tik_dcc_folder / "max" / "setup" / "icons" / "TikManager4_24a.bmp"
        pack_24i = self.tik_dcc_folder / "max" / "setup" / "icons" / "TikManager4_24i.bmp"

        work_space_injection ="""        <Window name="Tik Manager4" type="T" rank="0" subRank="2" hidden="0" dPanel="1" tabbed="0" curTab="-1" cType="1" toolbarRows="1" toolbarType="3">
            <FRect left="198" top="125" right="350" bottom="199" />
            <DRect left="1395" top="53" right="1504" bottom="92" />
            <DRectPref left="2147483647" top="2147483647" right="-2147483648" bottom="-2147483648" />
            <CurPos left="198" top="125" right="600" bottom="199" floating="1" panelID="16" />
            <Items>
                <Item typeID="2" type="CTB_MACROBUTTON" width="0" height="0" controlID="0" macroTypeID="3" macroType="MB_TYPE_ACTION" actionTableID="647394" imageID="-1" imageName="" actionID="tik4Main`Tik Manager4" tip="Tik Manager 4 - Main UI" label="Tik4 Main UI" />
                <Item typeID="2" type="CTB_MACROBUTTON" width="0" height="0" controlID="0" macroTypeID="3" macroType="MB_TYPE_ACTION" actionTableID="647394" imageID="-1" imageName="" actionID="tik4NewVersion`Tik Manager4" tip="Tik Manager 4 - New Version" label="New Version" />
                <Item typeID="2" type="CTB_MACROBUTTON" width="0" height="0" controlID="0" macroTypeID="3" macroType="MB_TYPE_ACTION" actionTableID="647394" imageID="-1" imageName="" actionID="tik4Publish`Tik Manager4" tip="Tik Manager 4 - Publish" label="Publish" />
            </Items>
        </Window>\n"""

        max_folders = [x for x in user_max_dir.iterdir() if x.is_dir()]

        if max_folders:
            print_msg("3dsMax versions found:")
            for folder in max_folders:
                print_msg(f"{folder.name}")
        else:
            if prompt:
                print_msg("No 3dsMax version can be found in the 3ds Max user directory")
                print_msg("Make sure 3ds Max is installed and try again. Alternatively you can try manual install. "
                          "Check the documentation for more information.")
                if prompt:
                    ret = input("Press Enter to continue...")
                    assert isinstance(ret, str)
            return

        for version in max_folders:
            print_msg(f"Setting up {version.name}...")
            scripts_folder = user_max_dir / version / "ENU" / "scripts" / "startup"
            scripts_folder.mkdir(parents=True, exist_ok=True)
            icons_folder = user_max_dir / version / "ENU" / "usericons"
            icons_folder.mkdir(parents=True, exist_ok=True)
            macros_folder = user_max_dir / version / "ENU" / "usermacros"
            macros_folder.mkdir(parents=True, exist_ok=True)
            print_msg("Copying icons...")
            shutil.copy(pack_16a, icons_folder / "TikManager4_16a.bmp")
            shutil.copy(pack_16i, icons_folder / "TikManager4_16i.bmp")
            shutil.copy(pack_24a, icons_folder / "TikManager4_24a.bmp")
            shutil.copy(pack_24i, icons_folder / "TikManager4_24i.bmp")

            workspace_folder = user_max_dir / version / "ENU" / "en-US" / "UI" / "Workspaces" / "usersave"
            workspace_folder.mkdir(parents=True, exist_ok=True)
            workspace_file = workspace_folder / "Workspace1__usersave__.cuix"

            print_msg("Creating MacroScripts...")
            main_ui_macro = """
macroScript tik4Main
category: "Tik Manager4"
tooltip: "Tik Manager4 - Main UI"
ButtonText: "Main UI"
icon: #("TikManager4",1)
(
	python.Execute "from tik_manager4.ui import main as tik4_main"
	python.Execute "tik4_main.launch(dcc='3dsmax')"
)"""
            new_version_macro = """
macroScript tik4NewVersion
category: "Tik Manager4"
tooltip: "Tik Manager4 - New Version"
ButtonText: "New Version"
icon: #("TikManager4",2)
(
	python.Execute "from tik_manager4.ui import main as tik4_main"
	python.Execute "tui = tik4_main.launch(dcc='3dsmax', dont_show=True)"
	python.Execute "tui.on_new_version()"
)"""
            publish_macro = """
macroScript tik4Publish
category: "Tik Manager4"
tooltip: "Tik Manager4 - Publish Scene"
ButtonText: "Publish"
icon: #("TikManager4",3)
(
	python.Execute "from tik_manager4.ui import main as tik4_main"
	python.Execute "tui = tik4_main.launch(dcc='3dsmax', dont_show=True)"
	python.Execute "tui.on_publish_scene()"
)"""
            injector = Injector(macros_folder / "Tik Manager4-tik4Main.mcr")
            injector.replace_all(main_ui_macro)
            injector.set_file_path(macros_folder / "Tik Manager4-tik4NewVersion.mcr")
            injector.replace_all(new_version_macro)
            injector.set_file_path(macros_folder / "Tik Manager4-tik4Publish.mcr")
            injector.replace_all(publish_macro)

            print_msg("Creating Workspaces...")
            injector.set_file_path(workspace_file)
            injector.force = False
            injector.match_mode = "contains"
            state = injector.inject_between(work_space_injection, start_line='"Tik Manager4"',
                                            end_line="</Window>", suppress_warnings=True)
            if not state: # fresh install
                state = injector.inject_before(work_space_injection, line="</CUIWindows>")
                if not state:
                    print_msg("Toolbar cannot be injected to the workplace, "
                              "you can set toolbar manually within 3ds max\n")
                    print_msg("3ds Max Setup FAILED.")
                    if prompt:
                        ret = input("Press Enter to continue...")
                        assert isinstance(ret, str)
                    return

            print_msg("3ds Max setup completed.")

            if prompt:
                ret = input("Press Enter to continue...")
                assert isinstance(ret, str)

    def blender_setup(self, prompt=True):
        """Installs the Blender plugin."""
        print_msg("Starting Blender Setup...")

        if self.check_running_instances("Blender") == -1:
            print_msg("Installation aborted by user.")
            return

        blender_user_folder = (self.user_home / "AppData" / "Roaming" /
                               "Blender Foundation" / "Blender")
        versions = [x for x in blender_user_folder.iterdir() if x.is_dir()]
        init_source = self.tik_dcc_folder / "blender" / "setup" / "tik_4_init_windows.py"

        for version in versions:
            print_msg(f"Setting up {version.name}...")
            startup_folder = version / "scripts" / "startup"
            startup_folder.mkdir(parents=True, exist_ok=True)
            init_file = startup_folder / "tik_4_init_windows.py"
            if init_file.exists():
                init_file.unlink()
            shutil.copy(init_source, init_file)
            injector = Injector(init_file)
            injector.match_mode = "contains"
            injector.replace_single_line(f"tik_path = '{self.tik_root.parent.as_posix()}'",
                                         line="tik_path = ")

        print_msg("Blender setup completed.")

        if prompt:
            _r = input("Press Enter to continue...")
            assert isinstance(_r, str)

    def nuke_setup(self, prompt=True):
        """Installs the Nuke plugin."""
        print_msg("Starting Nuke Setup...")

        if self.check_running_instances("Nuke") == -1:
            print_msg("Installation aborted by user.")
            return

        user_nuke_folder = self.user_home / ".nuke"

        if not user_nuke_folder.exists():
            if prompt:
                print_msg("No Nuke version can be found in the user's home directory")
                print_msg("Make sure Nuke is installed and try again. Alternatively you can try manual install. "
                          "Check the documentation for more information.")
                if prompt:
                    _r = input("Press Enter to continue...")
                    assert isinstance(_r, str)
            return

        init_file = user_nuke_folder / "init.py"
        menu_file = user_nuke_folder / "menu.py"

        main_ui_icon = self.tik_dcc_folder / "nuke" / "setup" / "icons" / "tik4_main_ui.png"
        new_version_icon = self.tik_dcc_folder / "nuke" / "setup" / "icons" / "tik4_new_version.png"
        publish_icon = self.tik_dcc_folder / "nuke" / "setup" / "icons" / "tik4_publish.png"

        shutil.copyfile(main_ui_icon, user_nuke_folder / "tik4_main_ui.png")
        shutil.copyfile(new_version_icon, user_nuke_folder / "tik4_new_version.png")
        shutil.copyfile(publish_icon, user_nuke_folder / "tik4_publish.png")

        init_content = [
            "# Tik Manager 4 [Start]\n",
            "import sys\n",
            f"tik_path = '{self.tik_root.parent.as_posix()}'\n",
            "if not tik_path in sys.path:\n",
            "    sys.path.append(tik_path)\n",
            "# Tik Manager 4 [End]\n",
        ]

        injector = Injector(init_file)
        injector.inject_between(init_content, start_line="# Tik Manager 4 [Start]\n", end_line="# Tik Manager 4 [End]\n")
        print_msg("init.py file updated.")

        menu_content = [
        "# Tik Manager 4 [Start]\n",
        "toolbar = nuke.menu('Nodes')\n",
        "smMenu = toolbar.addMenu('TikManager4', icon='tik4_main_ui.png')\n",
        "smMenu.addCommand('Main UI', 'from tik_manager4.ui import main as tik4_main\\ntik4_main.launch(dcc=\"Nuke\")', icon='tik4_main_ui.png')\n",
        "smMenu.addCommand('New Version', 'from tik_manager4.ui import main\\ntui = main.launch(dcc=\"Nuke\", dont_show=True)\\ntui.on_new_version()', icon='tik4_new_version.png')\n",
        "smMenu.addCommand('Publish', 'from tik_manager4.ui import main\\ntui = main.launch(dcc=\"Nuke\", dont_show=True)\\ntui.on_publish_scene()', icon='projectMaterials_ICON.png')\n",
        "# Tik Manager 4 [End]\n"
        ]

        injector.set_file_path(menu_file)
        injector.inject_between(menu_content, start_line="# Tik Manager 4 [Start]\n",
                                end_line="# Tik Manager 4 [End]\n")
        print_msg("menu.py file updated.")

        print_msg("Nuke setup completed.")
        if prompt:
            _r = input("Press Enter to continue...")
            assert isinstance(_r, str)

    def katana_setup(self, prompt=True):
        """Installs the Katana plugin."""
        print_msg("Starting Katana Setup...")

        if self.check_running_instances("Katana") == -1:
            print_msg("Installation aborted by user.")
            return

        user_katana_folder = self.user_home / ".katana"

        init_file = user_katana_folder / "init.py"
        init_content = [
        "# Tik Manager 4 [Start]\n",
        "import sys\n",
        f"tik_path = '{self.tik_root.parent.as_posix()}'\n",
        "if not tik_path in sys.path:\n",
        "    sys.path.append(tik_path)\n",
        "# Tik Manager 4 [End]\n"
        ]

        print_msg("Updating init.py file...")
        injector = Injector(init_file)
        injector.inject_between(init_content, start_line="# Tik Manager 4 [Start]\n",
                                end_line="# Tik Manager 4 [End]\n")

        print_msg("Creating shelves.")
        source_shelf_folder = self.tik_dcc_folder / "katana" / "setup" / "tik4"
        target_shelf_folder = user_katana_folder / "Shelves" / "tik4"

        if target_shelf_folder.exists():
            shutil.rmtree(target_shelf_folder)
        shutil.copytree(source_shelf_folder, target_shelf_folder)

        main_ui_icon = (self.tik_dcc_folder / "katana" / "setup" / "icons" /
                        "tik4_main_ui.png")
        new_version_icon = (self.tik_dcc_folder / "katana" / "setup" / "icons" /
                            "tik4_new_version.png")
        publish_icon = (self.tik_dcc_folder / "katana" / "setup" / "icons" /
                        "tik4_publish.png")

        main_ui_py = target_shelf_folder / "main_ui.py"
        new_version_py = target_shelf_folder / "new_version.py"
        publish_py = target_shelf_folder / "publish.py"

        injector.set_file_path(main_ui_py)
        injector.match_mode = "contains"
        injector.replace_single_line(f"ICON: {main_ui_icon.as_posix()}", line="ICON:")
        injector.set_file_path(new_version_py)
        injector.replace_single_line(f"ICON: {new_version_icon.as_posix()}", line="ICON:")
        injector.set_file_path(publish_py)
        injector.replace_single_line(f"ICON: {publish_icon.as_posix()}", line="ICON:")

        print_msg("Katana setup completed.")
        if prompt:
            _r = input("Press Enter to continue...")
            assert isinstance(_r, str)

    def mari_setup(self, prompt=True):
        """Install Mari."""
        print_msg("Starting Mari Setup...")

        if self.check_running_instances("Mari") == -1:
            print_msg("Installation aborted by user.")
            return

        user_mari_scripts_folder = self.user_home / "Documents" / "Mari" / "Scripts"
        user_mari_scripts_folder.mkdir(parents=True, exist_ok=True)

        source_script = self.tik_dcc_folder / "mari" / "setup" / "tikmanager4_init.py"

        # copy the source to the user's scripts folder
        init_file = user_mari_scripts_folder / "tikmanager4_init.py"
        shutil.copy(source_script, init_file)

        injector = Injector(init_file)
        injector.match_mode = "contains"
        injector.replace_single_line(f"tik_path = '{self.tik_root.parent.as_posix()}'",
                                     line="tik_path = ")

        print_msg("Mari setup completed.")
        if prompt:
            _r = input("Press Enter to continue...")
            assert isinstance(_r, str)

    def photoshop_setup(self, prompt=True):
        """Install the Photoshop plugin."""
        print_msg("Starting Photoshop Setup...")

        if self.check_running_instances("Photoshop") == -1:
            print_msg("Installation aborted by user.")
            return

        extensions_source_folder = (self.tik_dcc_folder / "photoshop" / "setup" /
                                    "extensions" / "tikManager4")
        extensions_target_folder = (self.user_home / "AppData" / "Roaming" / "Adobe" /
                                    "CEP" / "extensions" / "tikManager4")

        if not extensions_target_folder.exists():
            print_msg("No Photoshop version can be found in the user's home directory.")
            print_msg("Make sure Photoshop is installed and try again. "
                      "Alternatively you can try manual install. "
                      "Check the documentation for more information.")
            if prompt:
                ret = input("Press Enter to continue...")
                assert isinstance(ret, str)
            return

        print_msg("Copying extensions...")
        # if the target folder exists, delete it
        if extensions_target_folder.exists():
            shutil.rmtree(extensions_target_folder)
        # copy the source folder and overwrite the target folder
        shutil.copytree(extensions_source_folder, extensions_target_folder,
                        dirs_exist_ok=True, symlinks=True)

        main_ui_icon = self.tik_dcc_folder / "photoshop" / "setup" / "icons" / "tik4_main_ui.png"
        new_version_icon = (self.tik_dcc_folder / "photoshop" / "setup" /
                            "icons" / "tik4_new_version.png")
        publish_icon = self.tik_dcc_folder / "photoshop" / "setup" / "icons" / "tik4_publish.png"

        html_file = extensions_target_folder / "client" / "index.html"
        html_content = f"""<!DOCTYPE html>
<html>
<body style="background-color:black;">
<head>
    <meta charset="utf-8">
    <title>Tik Manager4</title>
</head>
<body>
    <input type="image" id="tikManager4-button" src="{main_ui_icon}" />
    <input type="image" id="newVersion-button" src="{new_version_icon}" />
    <input type="image" id="publish-button" src="{publish_icon}" />
    <!-- Do not display this at the moment
    <button id="open-button">Open</button>
    -->
    <script type="text/javascript" src="CSInterface.js"></script>
    <script type="text/javascript" src="index.js"></script>
</body>
</html>"""

        injector = Injector(html_file)
        injector.replace_all(html_content)

        host_file = extensions_target_folder / "host" / "index.jsx"
        main_ui_exe = self.tik_root / "dist" / "tik4" / "tik4_photoshop.exe"
        new_version_exe = self.tik_root / "dist" / "tik4" / "tik4_ps_new_version.exe"
        publish_exe = self.tik_root / "dist" / "tik4" / "tik4_ps_publish.exe"

        host_content = f"""function tikUI(){{
    var bat = new File("{main_ui_exe.as_posix()}");
    bat.execute();
}}
function tikSaveVersion(){{
    var bat = new File("{new_version_exe.as_posix()}");
    bat.execute();
}}
function tikPublish(){{
    var bat = new File("{publish_exe.as_posix()}");
    bat.execute();
}}"""
        injector.set_file_path(host_file)
        injector.replace_all(host_content)

        print_msg("Adding registry keys to enable PS plugins...")
        _ = [self.__set_csx_key(x) for x in range(20)]

        print_msg("Photoshop setup completed.")
        if prompt:
            ret = input("Press Enter to continue...")
            assert isinstance(ret, str)

    def gaffer_setup(self, prompt=True):
        """Install Gaffer integration."""
        print_msg("Starting Gaffer Setup...")

        # find the gaffer installation folder.
        places_to_look = ["C:/Program Files", "C:/Program Files (x86)", "C:/opt", "C:/software"]

        gaffer_versions = []
        for place in places_to_look:
            # it the place doesn't exist, skip it
            if not Path(place).exists():
                continue
            # look for folders that starts with "gaffer" and append them to the list
            for x in Path(place).iterdir():
                # print("path", x)
                if x.is_dir() and x.name.startswith("gaffer"):
                    print("gaffer", x)
                    gaffer_versions.append(x)
            # gaffer_versions.extend([x for x in Path(place).iterdir() if x.is_dir() and x.name.startswith("gaffer")])

        # for each gaffer version check for the startup/gui folders. If they don't exist, skip the version
        for version in list(gaffer_versions):
            gui_folder = version / "startup" / "gui"
            if not gui_folder.exists():
                gaffer_versions.remove(version)
        if not gaffer_versions:
            print_msg("No Gaffer version can be found.")
            print_msg(f"Make sure Gaffer is installed in one of the following folder and try again. {places_to_look}"
                      "Alternatively you can try manual install. "
                      "Check the documentation for more information.")
            if prompt:
                ret = input("Press Enter to continue...")
                assert isinstance(ret, str)
            return
        source_init_file = self.tik_dcc_folder / "gaffer" / "setup" / "tik_4_init.py"

        for version in gaffer_versions:
            print_msg(f"Setting up {version.name}...")
            gui_folder = version / "startup" / "gui"
            init_file = gui_folder / "tik_4_init.py"
            shutil.copy(source_init_file, init_file)
            injector = Injector(init_file)
            injector.match_mode = "contains"
            injector.replace_single_line(f"tik_path = '{self.tik_root.parent.as_posix()}'",
                                         line="tik_path = ")

        print_msg("Gaffer setup completed.")
        if prompt:
            _r = input("Press Enter to continue...")
            assert isinstance(_r, str)

    def __set_csx_key(self, val):
        """Convenience function to set the csx key."""
        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, fr"Software\Adobe\CSXS.{val}",
                              0, reg.KEY_ALL_ACCESS)
            reg.SetValueEx(key, "PlayerDebugMode", 1, reg.REG_SZ, "1")
            reg.CloseKey(key)
            return key
        except WindowsError:
            return None

    def _ok_cancel(self, msg):
        """Displays a message box with OK and Cancel buttons."""
        reply = input(f"{msg} (y/n): ")
        assert isinstance(reply, str)
        reply = reply.lower().strip()

        if reply[0] == "y":
            return True
        if reply[0] == "n":
            return False
        return self._ok_cancel(msg)

    def _cli(self):
        """Launches a command line interface."""
        # folderCheck(network_path)
        header = f"""
-----------------------------------
Tik Manager v{_version.__version__} - DCC Installer
-----------------------------------"""

        self.dcc_mapping.update({
            "Install All": self.install_all,
            "Exit": sys.exit
        })
        print_msg(header)

        while True:
            print_msg("""
Choose the software you want to setup Scene Manager:
----------------------------------------------------""")

            # convert the self.dcc_mapping into a list of dictionaries for the menu
            menu_items = [{k: v} for k, v in self.dcc_mapping.items()]

            for item in menu_items:
                print_msg(f"[{menu_items.index(item)}] {list(item.keys())[0]}")

            choice = input(">> ")
            assert isinstance(choice, str)

            try:
                if int(choice) < 0:
                    raise ValueError
                key = list(menu_items[int(choice)])[0]
                cmd = menu_items[int(choice)][key]
                cmd()

                os.system("cls")
            except (ValueError, IndexError):
                pass

    def check_running_instances(self, instance_name):
        """Checks if the instance is running. If it is, asks the user to close it."""
        running = True
        aborted = False

        while not aborted and running:
            running = False
            for process in psutil.process_iter():
                name = str(process.name())
                if name:
                    if name.startswith(instance_name):
                        running = True
                        break

            if running:
                msg = f"{instance_name} is running. Exit software and type 'y'. type 'n' to abort"
                reply = self._ok_cancel(msg)
                if reply:
                    pass
                else:
                    aborted = True
        if aborted:
            return -1
        return 1

    def _no_cli(self, dcc_list):
        """Installs software without launching a CLI."""
        for item in dcc_list:
            func = self.dcc_mapping.get(item, None)
            if not func:
                print_msg(f"Software {item} not found in the list. Skipping...")
                continue
            func(prompt=False)
        _r = input("Setup Completed. Press Enter to Exit...")
        assert isinstance(_r, str)

    def main(self):
        """Decides to launch a CLI or proceed with installation based on arguments."""
        # parse the arguments
        opts, args = getopt.getopt(self.argv, "b", ["batchMode"])

        if not opts and not args:
            self._cli()

        elif args:
            self._no_cli(args)
        else:
            sys.exit()


class Injector:
    """Inject contents to ASCII files."""
    def __init__(self, file_path):
        self.file_path = None
        self.content = None
        self.search_list = None # search content may be reversed or not

        self._search_direction = "forward"
        self._match_mode = "equal"
        self.force = True
        self.set_file_path(file_path)

    @property
    def search_direction(self):
        """Return defined search direction."""
        return self._search_direction

    @search_direction.setter
    def search_direction(self, value):
        """Set the search direction."""
        if value not in ["forward", "backward"]:
            raise ValueError("Invalid value")
        self._search_direction = value
        self.search_list = self.__get_search_list()

    @property
    def match_mode(self):
        """Return defined match mode."""
        return self._match_mode

    @match_mode.setter
    def match_mode(self, value):
        if value not in ["equal", "contains"]:
            raise ValueError("Invalid value")
        self._match_mode = value

    def set_file_path(self, value):
        """Sets the file path."""
        if isinstance(value, str):
            self.file_path = Path(value)
        elif isinstance(value, Path):
            self.file_path = value
        else:
            raise ValueError("Invalid value")
        self.content = self.read()
        self.search_list = self.__get_search_list()

    def __get_search_list(self):
        if self.search_direction == "forward":
            return self.content
        return self.content[::-1]

    def __add_content(self, new_content, start_idx, end_idx):
        """Adds the new content to the content list."""
        if isinstance(new_content, str):
            new_content = [new_content]
        if self.search_direction == "forward":
            added_content = self.content[:start_idx] + new_content + self.content[end_idx +1:]
        else:
            added_content = self.content[:-end_idx] + new_content + self.content[-start_idx - 1:]
        return added_content

    def inject_between(self, new_content, start_line, end_line, suppress_warnings=False):
        """Injects the new content between the start and end lines."""
        if not self.file_path.is_file():
            if self.force:
                self._dump_content(self.content)
                print_msg(f"File {self.file_path} created with new content.")
                return True
            if not suppress_warnings:
                print_msg(f"File {self.file_path} not found. Aborting.")
            return False
        start_idx, end_idx = None, None
        start_idx = self._find_index(self.search_list, start_line)
        if start_idx is not None:
            end_idx = self._find_index(self.search_list, end_line, begin_from=start_idx)
        if start_idx is None or end_idx is None:
            if self.force:
                if not suppress_warnings:
                    print_msg("Start or end line not found. Injecting at the end of the file.")
                self._dump_content(self.content + new_content)
                return True
            if not suppress_warnings:
                print_msg("Start or end line not found. Aborting.")
            return False
        injected_content = self.__add_content(new_content, start_idx, end_idx)
        self._dump_content(injected_content)
        return True

    def inject_after(self, new_content, line, suppress_warnings=False):
        """Injects the new content after the line."""
        if not self.file_path.is_file():
            if self.force:
                self._dump_content(self.content)
                print_msg(f"File {self.file_path} created with new content.")
                return True
            if not suppress_warnings:
                print_msg(f"File {self.file_path} not found. Aborting.")
            return False
        start_idx = self._find_index(self.search_list, line)
        if not start_idx:
            if self.force:
                if not suppress_warnings:
                    print_msg("Line not found. Injecting at the end of the file.")
                self._dump_content(self.content + new_content)
                return True
            if not suppress_warnings:
                print_msg("Line not found. Aborting.")
            return False
        injected_content = self.__add_content(new_content, start_idx, start_idx+1)
        self._dump_content(injected_content)
        return True

    def inject_before(self, new_content, line, suppress_warnings=False):
        """Injects the new content before the line."""
        if not self.file_path.is_file():
            if self.force:
                self._dump_content(self.content)
                print_msg(f"File {self.file_path} created with new content.")
                return True
            if not suppress_warnings:
                print_msg(f"File {self.file_path} not found. Aborting.")
            return False
        start_idx = self._find_index(self.search_list, line)
        if not start_idx:
            if self.force:
                if not suppress_warnings:
                    print_msg("Line not found. Injecting at the end of the file.")
                self._dump_content(self.content + new_content)
                return True
            if not suppress_warnings:
                print_msg("Line not found. Aborting.")
            return False
        injected_content = self.__add_content(new_content, start_idx, start_idx-1)
        self._dump_content(injected_content)
        return True

    def replace_all(self, new_content):
        """Replace the whole file with the new content."""
        self._dump_content(new_content)
        return True

    def replace_single_line(self, new_content, line, suppress_warnings=False):
        """Replace the given line with the new content."""
        if isinstance(new_content, str):
            # if its not ending with a break line add it
            if not new_content.endswith("\n"):
                new_content = f"{new_content}\n"
            new_content = [new_content]

        if not self.file_path.is_file():
            if self.force:
                self._dump_content(self.content)
                print_msg(f"File {self.file_path} created with new content.")
                return True
            if not suppress_warnings:
                print_msg(f"File {self.file_path} not found. Aborting.")
            return False
        start_idx = self._find_index(self.search_list, line)
        if not start_idx:
            if self.force:
                if not suppress_warnings:
                    print_msg("Line not found. Injecting at the end of the file.")
                self._dump_content(self.content + new_content)
                return True
            if not suppress_warnings:
                print_msg("Line not found. Aborting.")
            return False
        injected_content = self.__add_content(new_content, start_idx, start_idx)
        self._dump_content(injected_content)
        return True

    def read(self):
        """Reads the file."""
        if not self.file_path.is_file():
            self._dump_content([])
            return []
        with open(self.file_path, "r", encoding="utf-8") as file_data:
            if file_data.mode != "r":
                return None
            content_list = file_data.readlines()
        return content_list

    def _dump_content(self, list_of_lines):
        """Write the content to the file."""
        temp_file_path = self.file_path.parent / f"{self.file_path.stem}_TMP{self.file_path.suffix}"
        with open(temp_file_path, "w+", encoding="utf-8") as temp_file:
            temp_file.writelines(list_of_lines)
        shutil.move(temp_file_path, self.file_path)

    def _find_index(self, search_list, line, begin_from=0):
        """Get the index of a line in a list of lines."""
        if self.match_mode == "equal" and line in search_list:
            return search_list.index(line)

        if self.match_mode == "contains":
            for idx in range(begin_from, len(search_list)):
                if line in search_list[idx]:
                    return idx
        return None

if __name__ == "__main__":
    install_handler = Installer(sys.argv[1:])
    install_handler.main()
