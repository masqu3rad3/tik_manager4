Nuke Integration
================

1. Locate the startup scripts folder

.. tip:: 

    Check `this link <https://learn.foundry.com/nuke/developers/63/pythondevguide/startup.html>`_ to locate the folder for different operating systems.
    Alternatively available folders can be found by running `nuke.pluginPath()` command from the Nuke script editor.

2. If it is not already exists, create `init.py` in one of the startup folders and add the following lines:

::

    # Tik Manager 4 [Start]
    import sys
    tik_path = "PATH//TO//PARENT//FOLDER//OF//TIKMANAGER4//"
    if not tik_path in sys.path:
        sys.path.append(tik_path)
    # Tik Manager 4 [End]

3. Replace ``PATH//TO//PARENT//FOLDER//OF//TIKMANAGER4//`` with the path of where the PARENT of tik_manager folder is. Use double BACK Slashes between folder names.
   
.. attention:: 
    The Path MUST be the parent of the tik_manager4 folder. If you extracted the contents directly from the zip file it will be something like ``tik_manager4-4.0.1-alpha``.

4. In the same startup directory, if it is not already exists, create `menu.py` and add the following lines:

::

    # Tik Manager 4 [Start]
    toolbar = nuke.menu('Nodes')
    smMenu = toolbar.addMenu('SceneManager', icon='tik4_main_ui.png')
    smMenu.addCommand('Main UI', 'from tik_manager4.ui import main as tik4_main\ntik4_main.launch(dcc='Nuke')', icon='tik4_main_ui.png')
    smMenu.addCommand('New Version', 'from tik_manager4.ui import main\ntui = main.launch(dcc='Nuke', dont_show=True)\ntui.on_new_version()', icon='tik4_new_version.png')
    smMenu.addCommand('Publish', 'from tik_manager4.ui import main\ntui = main.launch(dcc='Nuke', dont_show=True)\ntui.on_publish_scene()', icon='tik4_publish.png')
    # Tik Manager 4 [End]

5. Copy all **.png** files under the ``tik_manager4/dcc/maya/setup`` folder to the nuke startup scripts folder
6. Restart Nuke