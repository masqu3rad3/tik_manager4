3ds Max Integration
===================

1. Locate the ``tik_path.ms`` file in the ``tik_manager4/dcc/max/setup/`` folder
2. Copy the *tik_path.ms* into one of the 3ds Max startup scripts folder.

.. tip:: 
    The Startup Scripts directory is defined on the Configure System Paths dialog. Common paths for startup scripts are:
    ``%localappdata%\Autodesk\3dsMax\<YOUR MAX VERSION>\ENU\scripts\startup``
    ``%programfiles%\Autodesk\<YOUR MAX VERSION>\scripts\Startup``

3. Open the copied *tik_path.ms* with a text editor and replace the ``PATH//TO//PARENT//FOLDER//OF//TIKMANAGER4//`` with the extracted parent of the tik_manager4 folder.

.. attention:: 
    The Path MUST be the parent of the tik_manager4 folder. If you extracted the contents directly from the zip file it will be something like ``tik_manager4-4.0.1-alpha``.

4. Copy all ``.bmp`` files inside the ``tik_manager4/dcc/max/setup/icons`` folder into the usericons folder of 3ds Max.

.. tip::
    Default path for usericons folder for 3ds Max is ``%localappdata%\Autodesk\3dsMax\2023 – 64bit\ENU\usericons``

5. Launch 3dsMax. Locate ``setup_3dsmax.ms`` in ``tik_manager4/dcc/max/setup/`` folder and run it either by using the Scripting -> Run Script menu or drag & dropping it into the 3ds Max viewport.
6. Link the MacroScripts to the Toolbar or QuadMenu. Details about MacroScripts can be found in scriptspot_ or autodesk_

.. _scriptspot: https://www.scriptspot.com/3ds-max/tutorials/3ds-max-maxscript-how-to-install-a-macroscript
.. _autodesk: https://help.autodesk.com/view/MAXDEV/2023/ENU/?guid=GUID-6E21C768-7256-4500-AB1F-B144F492F055
