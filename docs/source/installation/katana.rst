Katana Integration
==================

1. Locate the startup scripts folder

.. tip::

    In Windows, it is under ``%userprofile%/.katana``

2. If it is not already exists, create `init.py` in startup folder and add the following lines:

::

    # Tik Manager 4 [Start]
    import sys
    import os
    tik_path = "PATH/TO/PARENT/FOLDER/OF/TIKMANAGER4/"
    if not tik_path in sys.path:
        sys.path.append(tik_path)
    os.environ["QT_PREFERRED_BINDING_JSON"] = '{"tik_manager4.ui.Qt": ["PyQt5"], "default":["PyQt5"]}'
    # Tik Manager 4 [End]

3. Replace ``PATH/TO/PARENT/FOLDER/OF/TIKMANAGER4/`` with the path of where the PARENT of tik_manager folder is. Use forward slashes between folder names.

.. attention::
    The Path MUST be the parent of the tik_manager4 folder. If you extracted the contents directly from the zip file it will be something like ``tik_manager4-4.0.1-alpha``.

4. In the same startup directory, locate the `shelves` folder and copy the entire `/tik_manager4/dcc/katana/setup/tik4` folder to the `shelves` folder.

5. (Optional) To get the icons to show up in the shelf, you can edit the all shelf files (`main_ui.py`, `new_version.py`, `publish.py`) and replace the icon paths with the correct paths. Simply replace `PATH/TO/PARENT/FOLDER/OF/TIKMANAGER4` parts with the physical path of the parent folder of tik_manager4.

6. Restart Katana. Shelf should be visible on main menu Shelf Actions button (The one with the gear icon).

