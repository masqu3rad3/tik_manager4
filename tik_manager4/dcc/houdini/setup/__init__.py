from pathlib import Path
import hou

# current location
self_location = Path(__file__).parent
icons_folder = self_location / "icons"

try:
    tik_manager4_shelf = hou.shelves.shelves()["TikManager4"]
except KeyError:
    tik_manager4_shelf = hou.shelves.newShelf(name="TikManager4", label="TikManager4")

tik_manager4_shelf.setTools([])

tools = []

main_ui_command = """
from tik_manager4.ui import main as tik4_main
tik4_main.launch(dcc="Houdini")
"""
main_ui_icon = str(icons_folder / "tik4_main_ui.png")
main_ui_tool = hou.shelves.newTool(name="MainUI", label="MainUI", script=main_ui_command, icon=main_ui_icon)
tools.append(main_ui_tool)

new_version_command = """
from tik_manager4.ui import main as tik4_main
tui = tik4_main.launch(dcc='Houdini', dont_show=True)
tui.on_new_version()
"""
new_version_icon = str(icons_folder / "tik4_new_version.png")
new_version_tool = hou.shelves.newTool(name="NewVersion", label="NewVersion", script=new_version_command, icon=new_version_icon)
tools.append(new_version_tool)

publish_scene_command = """
from tik_manager4.ui import main as tik4_main
tui = tik4_main.launch(dcc='Houdini', dont_show=True)
tui.on_publish_scene()
"""
publish_scene_icon = str(icons_folder / "tik4_publish.png")
publish_scene_tool = hou.shelves.newTool(name="PublishScene", label="PublishScene", script=publish_scene_command, icon=publish_scene_icon)
tools.append(publish_scene_tool)

tik_manager4_shelf.setTools(tools)