.. _developing_extensions:

Developing Extensions
=====================

Extensions are additional dcc related functionalities that can be added to the Tik Manager.

.. tip::

        Starting from v4.3.8, Tik Manager can access extensions from ``<common>/plugins/maya/extension/`` folder. This is the suggested location for any custom extensions as they will be immediately available with the entire team and won't be affected by Tik Manager version updates.

The extension plugins added to the extension folder will be automatically loaded by Tik Manager and
the functionality will be available in the respective DCC menu item.

Hello World
-----------

Below is a simple example to create an extension for Maya.
This will add a new menu item under the Tik Manager main UI Maya menu called "Hello World".

.. code-block:: python

    """Hello World Extension for Maya."""

    from maya import cmds
    from tik_manager4.dcc.extension_core import ExtensionCore

    class HelloWorld(ExtensionCore): # Inherit from ExtensionCore
        """Simple Hello World Extension for Maya."""

        def execute(self):
            """Initial execution."""
            # This will add a new menu item under the Tik Manager main UI Maya menu called "Hello World".
            self.add_function_to_main_menu(self.on_hello_world, "Hello World")

        def on_hello_world(self):
            """This method will be called when the menu item is clicked."""
            cmds.inViewMessage( msg='<span style="color: #FE7E00;">Hello World</span>', fontSize=50, pos='topCenter', fade=True)


In the above example, we have created a simple extension that adds a new menu item under the Tik Manager main UI Maya menu called "Hello World".
When the menu item is clicked, it will display an inViewMessage with the text "Hello World" in the Maya viewport.

The ``execute`` method is the initial execution method that will be called when the extension is loaded.
We are using this method to add a new menu item. However, this can be used to perform any initial setup required.
For example, if you want a cube to be created each time you launch the Tik Manager, you can add the code to create the cube in the ``execute`` method.
(I have no idea why you would want to do that though.)

the ``add_function_to_main_menu`` method is an inherited method from the ``ExtensionCore`` class.
This method takes two arguments:
1. The function that will be called when the menu item is clicked.
2. The name of the menu item.

The ``on_hello_world`` method is the function that will be called when the menu item is clicked. This can be any arbitrary function that you want to execute when the menu item is clicked.

Let's add some Tik Manager integration functionalities to this extension.
Just like other integration plugins, extensions are metadata aware as well. Based on the current work file, they can get the metadata and perform actions accordingly.

We can query the current work file and version with the ``get_work_and_version`` inherited method.

.. code-block:: python

    def on_hello_world(self):
        """This method will be called when the menu item is clicked."""
        work, version = self.get_work_and_version()
        # get the parent task from the work
        metadata = work.parent_task.metadata
        lens = metadata.get_value("lens", "No Lens Information")
        fps = metadata.get_value("fps", "No FPS Information")
        message =f"""Work Info
        Work Name: <hl>{work.name}</hl>
        Lens: <hl>{lens}</hl>
        FPS: <hl>{fps}</hl>"""

        cmds.inViewMessage(amg=message, pos='topCenter', fadeStayTime=3000, fontSize=20, fade=True)

Now we have a simple but functional extension that can display the current work and some metadata information when clicked.

The complete code for the extension is as follows:

.. code-block:: python

    """Hello World Extension for Maya."""

    from maya import cmds
    from tik_manager4.dcc.extension_core import ExtensionCore

    class HelloWorld(ExtensionCore): # Inherit from ExtensionCore
        """Simple Hello World Extension for Maya."""

        def execute(self):
            """Initial execution."""
            # This will add a new menu item under the Tik Manager main UI Maya menu called "Hello World".
            self.add_function_to_main_menu(self.on_hello_world, "Hello World")

        def on_hello_world(self):
            """This method will be called when the menu item is clicked."""
            work, version = self.get_work_and_version()
            # get the parent task from the work
            metadata = work.parent_task.metadata
            lens = metadata.get_value("lens", "No Lens Information")
            fps = metadata.get_value("fps", "No FPS Information")
            message =f"""Work Info
            Work Name: <hl>{work.name}</hl>
            Lens: <hl>{lens}</hl>
            FPS: <hl>{fps}</hl>"""

            cmds.inViewMessage(amg=message, pos='topCenter', fadeStayTime=3000, fontSize=20, fade=True)