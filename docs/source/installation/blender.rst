Blender Integration
===================

Windows
+++++++

1. Locate the ``tik_4_init_windows.py`` file in the ``tik_manager4/dcc/blender/setup`` folder.
2. Find the **Blender User directory** on your system.

.. tip::
    Windows: ``%USERPROFILE%\AppData\Roaming\Blender Foundation\Blender\<BLENDER-VERSION>\``

3. If it is not already exist, create the ``/scripts/startup`` folder under the **Blender User Directory**. Copy the **tik_4_init_windows.py** file into this folder.
4. With a text editor, open the **tik_4_init_windows.py** file, find the line ``tik_path = "PATH\\TO\\PARENT\\FOLDER\\OF\\TIKMANAGER4\\"``. Change the path to the tik_manager4 folder to match the location where you installed the tik_manager4 folder.
   
.. attention:: 
    The Path MUST be the parent of the tik_manager4 folder. If you extracted the contents directly from the zip file it will be something like ``tik_manager4-4.0.1-alpha``.

Linux & macOS
+++++++++++++

For Linux and macOs, pySide2 or PyQt5 needs to be installed to the Blender Python environment.
Essentially, PySide2 can be pip installed to the system Python environment and then copied to the Blender Python environment.
There are detailed instructions on how to do this here:
https://github.com/friedererdmann/blender_pyside2_example

After PySide2 is installed, the process is similar as for Windows:

1. Locate the ``tik_4_init.py`` file in the ``tik_manager4/dcc/blender/setup`` folder.
2. Find the Blender User directory on your system.
   
.. tip::
    - Linux: ``/Users/$USER/Library/Application Support/Blender/<BLENDER-VERSION>/``
    - macOS: ``/Users/$USER/Library/Application Support/Blender/<BLENDER-VERSION>/``

3. If it is not already exist, create the ``/scripts/startup`` folder under the **Blender User Directory**. Copy the **tik_4_init.py** file into this folder.
4. With a text editor, open the **tik_4_init.py** file, find the line ``tik_path = "PATH\\TO\\PARENT\\FOLDER\\OF\\TIKMANAGER4\\"``. Change the path to the tik_manager4 folder to match the location where you installed the tik_manager4 folder.
   