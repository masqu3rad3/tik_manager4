Houdini Integration
===================

1. Locate or create the ``456.py`` file under scripts folder in the ``HOUDINI_PATH``. 

.. tip:: 
    Default Windows location is ``%programfiles%\Side Effects Software\<HOUDINI VERSION>\houdini\scripts`` or ``%UserProfile%\Documents\<HOUDINI VERSION>\scripts``

2. Add the following lines to the ``456.py``

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

4. Restart Houdini
5. Run the following command from python shell:
   
::

    from tik_manager4.dcc.houdini.setup

6. Click the **+** button at the end of the shelf set. From dropdown menu select Shelves and check **Tik Manager4** to reveal the Tik Manager shelf
