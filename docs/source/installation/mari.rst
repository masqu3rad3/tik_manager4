Mari Integration
===================

1. Locate the Mari scripts folder. (Create the Scripts folder if it doesn't exist)

.. tip::
    | On Linux: ``/Mari/Scripts``
    | On Windows: ``Documents\Mari\Scripts``
    | On Mac: ``/Documents/Mari/Scripts``

2. Find the ``tikmanager4_init.py`` file in the ``tik_manager4/dcc/mari/setup`` folder and copy it to the Mari scripts folder.

3. Open the copied ``tikmanager4_init.py`` with a text editor and replace the ``PATH\\TO\\PARENT\\FOLDER\\OF\\TIKMANAGER4\\`` with the extracted parent of the tik_manager4 folder.

.. attention:: 
    The Path MUST be the parent of the tik_manager4 folder. If you extracted the contents directly from the zip file it will be something like ``tik_manager4-4.0.7-beta``.

4. Open Mari and you should see the Tik Manager menu in the top menu bar.