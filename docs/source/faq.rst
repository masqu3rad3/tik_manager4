F.A.Q
==========================

.. contents::
   :local:

..
  Frequently asked questions should be questions that actually got asked.
  Formulate them as a question and an answer.
  Consider that the answer is best as a reference to another place in the documentation.


Overall workflow and troubleshooting
------------------------------------


.. Old reference

I just installed Tik Manager. It asks me a password. What is it?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The default password for all default users is 1234. You can change it in the settings.

.. seealso::

   :doc:`User Guide </user_guide>` :ref:`(Settings) <settings>`

   :doc:`Getting Started </getting_started>` :ref:`(Adding Users) <adding_users>`

We are starting a remote working project. Do we need to use the same 'commons' folder?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ideally, yes. The common folder is used to share templates and user data between different users of the application. It also holds the whole user data in it.
Therefore, it is important to define a folder that is accessible to all users.

What does it mean when I see an item color-coded yellow?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yellow color codes have different meanings depending on the context. However in all cases, it slightly warns the user about the item.

In versions (dropdown list) yellow means that the version you are looking and about to load is not the latest version. There might be multiple reasons for this:
- The scene that is currently opened may be this older version as it tries to resolve to the active scene.
- You may be working on the same work branch with someone else at the same time and they might have just iterated a new verison.
- You may have left it that way before exiting the main ui. (It remembers the last state of the UI.)

In work files, yellow color coding means that the work branch doesn't have any publishes yet. The works with publishes turns to green. This is to signal the next artist who will pick this up.

Whenever I save a new version, a pop-up warns me about the FPS: "The current fps (x) does not match the defined fps (x)?" How can I fix this?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The FPS warning checks the related metadata (fps) from the task. As all metadatas, fps values are inherited from hiearchy.
If you defined the fps value at project level and never touched again in any sub-project or task, it will be the same as the project's fps value.
However, you can define different fps values for each tasks. Or you can define a new fps value for a sub-project and it will be inherited by all tasks and
sub-projects under that sub-project.

If the scene you are about to save has a different fps value than the task's fps value, it will warn you about it.
You can either change the scene's fps value or the edit the task's fps value by simply 'right-click edit' to match the scene's fps value.

I can see the Tik Manager Icons and/or menu but the UI doesn't get launched. What should I do?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First thing you should check the script editor/console/logs for any errors.

- Maya -> Windows -> General Editors -> Script Editor
- Houdini -> (Launch Houdini from a terminal)
- Nuke -> (Launch Nuke from a terminal)
- Blender -> Window -> Toggle System Console
- Katana - (System window opens as a separate window when you launch Katana)
- Mari -> Python -> Show Console
- Gaffer -> (Launch Gaffer from a terminal)
- Substance Painter -> Window -> Log

if you see an error like "No module named tik_manager" or "No module named tik_manager4" it means that the module is not installed properly.
Windows only:
- reinstalling Tik Manager from packaged installer may work.
- Alternatively, you can locate the `install_dccs.exe` under the tik_manager4/dist/tik4 folder and run it. It will launch a CLI installer to install selected or all DCCs.

Windows, Linux and MacOS:
Dccs can be installed manually by following the instructions in the documentation.

.. seealso::

   :doc:`installation`

.. warning:: 
   The most common mistake is specifying the path incorrectly. The Path MUST be the parent of the 
   tik_manager4 folder. If you extracted the contents directly from the zip file it will be something 
   like tik_manager4-4.3.0.

   As an example, where we have a hierarchy like this:

   .. code-block:: bash

      home
      └── user
         └── tik_manager4-4.3.0
            └── tik_manager4
                  ├── core
                  ├── dcc
                  └── ..

   The correct path should be:
   `/home/user/tik_manager4-4.3.0/tik_manager4``
      