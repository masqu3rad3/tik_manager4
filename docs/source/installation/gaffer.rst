Gaffer Integration
==================

1. Locate the ``startup\gui`` folder inside gaffer installation folder.

2. Find the ``tik_4_init.py`` file in the ``tik_manager4/dcc/gaffer/setup`` folder and copy it to the Gaffer ``startup\gui`` scripts folder.

3. Open the copied ``tik_4_init.py`` with a text editor and replace the ``PATH\\TO\\PARENT\\FOLDER\\OF\\TIKMANAGER4\\`` with the extracted parent of the tik_manager4 folder.

.. attention::
    The Path MUST be the parent of the tik_manager4 folder. If you extracted the contents directly from the zip file it will be something like ``tik_manager4-4.0.7-beta``.

4. Open Gaffer and you should see the Tik Manager menu in the top menu bar.