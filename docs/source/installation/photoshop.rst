Photoshop Integration
=====================

1. Locate the ``tik_manager4/dcc/photoshop/setup/extensions/tikManager4`` folder.
2. Copy the entire tikManager4 folder under the extensions folder to the Photoshop extension directory

.. tip:: 
    
    Per-user extension folder
        - Windows: ``C:\Users\<USERNAME>\AppData\Roaming\Adobe\CEP\extensions``
  
    Details can be found in `this github link <https://github.com/Adobe-CEP/CEP-Resources/blob/master/CEP_8.x/Documentation/CEP%208.0%20HTML%20Extension%20Cookbook.md#extension-folders>`_.

3. Locate the **index.html** in ``../extensions/tikManager4/client/index.html``
4. Replace the ``PATH\TO\PARENT\FOLDER\OF\TIKMANAGER4\`` with the path of where the tik_manager folder is. Use **single slashes** between folder names.
5. Locate the **index.jsx** file in ``../extensionFolder/tikManager/host/index.jsx``
6. Replace the ``PATH//TO//PARENT//FOLDER//OF//TIKMANAGER4`` with the path of where the tik_manager folder is. Use **double BACK Slashes** between folder names

.. attention:: 
    The Path MUST be the parent of the tik_manager4 folder. If you extracted the contents directly from the zip file it will be something like ``tik_manager4-4.0.1-alpha``.
    
    e.g ``C:\Program Files\TikWorks\tik_manager4-4.0.1-alpha``

7. Locate the **playerDebug.reg** file in ``tik_manager4/dcc/maya/setup/``. Right click and merge it into the registry. (for Windows 11 Right click -> Show More Options -> Merge)