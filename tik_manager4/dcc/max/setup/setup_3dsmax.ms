macroScript tik4Main
category: "Tik Manager4"
tooltip: "Tik Manager4 - Main UI"
ButtonText: "Main UI"
icon: #("tik4",1)
(
	python.Execute "from tik_manager4.ui import main as tik4_main"
	python.Execute "tik4_main.launch(dcc='3dsmax')"
)

macroScript tik4NewVersion
category: "Tik Manager4"
tooltip: "Tik Manager4 - New Version"
ButtonText: "New Version"
icon: #("tik4",2)
(
	python.Execute "from tik_manager4.ui import main as tik4_main"
	python.Execute "tui = tik4_main.launch(dcc='3dsmax', dont_show=True)"
	python.Execute "tui.on_new_version()"
)

macroScript tik4Publish
category: "Tik Manager4"
tooltip: "Tik Manager4 - Publish Scene"
ButtonText: "Publish"
icon: #("tik4",3)
(
	python.Execute "from tik_manager4.ui import main as tik4_main"
	python.Execute "tui = tik4_main.launch(dcc='3dsmax', dont_show=True)"
	python.Execute "tui.on_publish_scene()"
)
