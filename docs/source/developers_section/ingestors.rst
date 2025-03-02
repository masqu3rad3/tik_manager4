.. _developing_ingestors:

Developing Ingestors
====================

Ingestors are the components that take data from a source and convert it into a
standardized format that can be ingested into the system. Ingestors are
responsible for:

.. tip::

        Starting from v4.3.8, Tik Manager can access ingestors from ``<common>/plugins/maya/ingest/`` folder. This is the suggested location for any custom ingestors as they will be immediately available with the entire team and won't be affected by Tik Manager version updates.


- Getting data from the source
- Making it compatible for a specific purpose
- Storing it in the database (Currently in progress)

Apart from obvious importing the compatible data into the dcc (e.g. importing an alembic cache file),
an ingestor can also be used using a data source to create a new dataset in the dcc.

The following example will show how a text file can be used to create a 3d object in the Maya.

Copying this code into a ``text_to_obj.py`` file in the ``tik_manager4/dcc/maya/ingest`` folder will make the ingestor available to Tik Manager.

.. code-block:: python

    """Example module to demonstrate how to create an ingestor for Maya."""

    from maya import cmds
    from tik_manager4.dcc.ingest_core import IngestCore

    class TextToObj(IngestCore):
        """Ingest a text file and create a poly cube with the file content as name."""

        nice_name = "Ingest Text to Obj"
        valid_extensions = [".txt"]
        referencable = False

        def _bring_in_default(self):
            """Create a polygon object from text file."""
            with open(self.ingest_path, "r") as file:
                text = file.read()
            # Create a polygon object and name it with the text content
            cmds.polyCube(name=text)

In this simple example, the ingestor reads the content of a text file and creates a cube in maya using the
contents of the text file as its name.

.. warning:: 

    The ingestors works ONLY on published elements. If there are no published element that a particular
    ingestor can work on, the ingestor will not be available on dropdown list.

.. note:: 

    Ingestors works on snapshot published elements as well. This means you can simply drag & drop files and snapshot publish the work files to get them ready to be ingested.

.. collapse:: Detailed Explanation

    Every ingestor must inherit the ``IngestCore`` class. This class provides the basic functionality for the ingestor to work.

    .. code:: python

        from tik_manager4.dcc.ingest_core import IngestCore

    We define the ``nice_name`` attribute to give a human-readable name to the ingestor. This name will be displayed in the UI.

    .. code:: python

        nice_name = "Ingest Text to Obj"

    Valid extensions is the most important attribute of an ingestor. Without a valid extension, Tik Manager cannot resolve the
    appropriate ingestor for a publish element. There can as many valid extensions as needed. For example, a single ingestor
    can import ``.abc``, ``.fbx`` and ``.usd`` files.

    .. code:: python

        valid_extensions = [".txt"]

    ``referencable`` attribute tells the UI to enable or disable the reference functionality.

    .. code:: python

        referencable = False

    We override the ``_bring_in_default``. This method is the main method of the ingestor which is called when the ingestor is triggered.

    .. code:: python

        def _bring_in_default(self):
            """Create a polygon object from text file."""
            with open(self.ingest_path, "r") as file:
                text = file.read()
            # Create a polygon object and name it with the text content
            cmds.polyCube(name=text)

-----------------------------

Selective Categories
~~~~~~~~~~~~~~~~~~~~

Similar to the :doc:`/developers_section/extractors` we can define certain actions for specific categories.
This becomes very useful when we want to have different actions from the same ingestor for different disciplines.

.. note:: 

    The categories are resolved from the published element. Meaning that the if an item published from the model category, the resolved
    category will be "model" as well.

.. code-block:: python

    from maya import cmds
    from tik_manager4.dcc.ingest_core import IngestCore


    class TextToObj(IngestCore):
        """Ingest a text file and create a poly cube with the file content as name."""

        nice_name = "Ingest Text to Obj"
        valid_extensions = [".txt"]
        referencable = False

        def __init__(self):
            super().__init__()
            self.category_functions = {
                "Model": self.bring_in_model,
                "Rig": self.bring_in_rig
            }

        def  _read_me(self):
            """Return the content of the text file."""
            with open(self.ingest_path, "r") as file:
                text = file.read()
            return text

        def _bring_in_default(self):
            """Create a cube named after the text file."""
            text = self._read_me()
            # Create a polygon object and name it with the text content
            cmds.polyCube(name=text)
        
        def bring_in_model(self):
            """Create a sphere named after the text file."""
            text = self._read_me()
            # Create a polygon object and name it with the text content
            cmds.polySphere(name=text)

        def bring_in_rig(self):
            """Create a plane named after the text file."""
            text = self._read_me()
            # Create a polygon object and name it with the text content
            cmds.polyPlane(name=text)

The above example shows how we can define different actions for different categories.
In this example, the ingestor will create a sphere for the `Model` category and a plane for the `Rig`` category.
For any other category, it will create a cube.

-----------------------------

Bundle Ingestors
~~~~~~~~~~~~~~~~

Ingestors can be configured to work on bundled folders.
In this case, the ``bundled`` attribute should be set to ``True``.

.. code-block:: python

    from maya import cmds
    from tik_manager4.dcc.ingest_core import IngestCore

    class BundleIngestor(IngestCore):
        """Ingest a bundle folder and create a poly cube with the file content as name."""

        nice_name = "Ingest Bundle to Obj"
        # we explicitly set the valid extensions to an empty list to indicate that this ingestor
        # This way, the ingestor will not be picked up for single files and will only be available for the matching bundled extractors.
        valid_extensions = []
        referencable = False
        bundled = True
        bundled_match_id = 1234 # The ingestor will only be available for the bundles which is extracted from an extractor with the same ID.

        def _bring_in_default(self):
            """Create a polygon object from text file."""
            bundle_folder = self.ingest_path # The ingest path will resolve to the bundle folder
            # Do something with the bundle folder

More complex ingestors can be created using the bundled ingestors. 

Unlike a single file ingestors, bundled ingestors can work with multiple files and folders, allowing to process multiple data files to create a single output.
For example, assuming a we have a bundle folder that contains a camera alembic, a file contains animation curves (such as .atom file) and an image sequence, we can combine all of these element and create an animated camera with a backdrop.

Each ingestor has a ``bundle_match_id`` attribute. This attribute is used to match the ingestor with extracted bundle.
If the ingestor and extracted bundle shares the same ID, the ingestor will be available for the extracted bundle.
Using this attribute, we can ensure that the ingestor is only available for a specific extracted bundle.
By default this attribute is set to 0.

.. warning:: 

    Sequences of images and cache files are exception. Even though they are stored in a folder and extracted from a bundled extractor, they are getting
    treated as a single file. This for ingesting a sequence the ingestor **shouldn't** be bundled.

Metadata access
~~~~~~~~~~~~~~~

Ingestors can access the metadata of the published element. This can be useful to get additional information about the published element.

The following example uses the published elements parent sub-project metadata to create a plane matching to the defined resolution.

.. code-block:: python

    """Example module to demonstrate how to create an ingestor for Maya."""

    from maya import cmds
    from tik_manager4.dcc.ingest_core import IngestCore

    class TextToObj(IngestCore):
        """Ingest a text file and create a poly cube with the file content as name."""

        nice_name = "Ingest Text to Obj"
        valid_extensions = [".txt"]
        referencable = False

        def _bring_in_default(self):
            """Create a polygon object from text file."""
            with open(self.ingest_path, "r") as file:
                text = file.read()
            # Try to get the scale of the plane from the metadata
            resolution = self.metadata.get_value("resolution", fallback_value=[1000, 1000])
            cmds.polyPlane(name=text, width=resolution[0], height=resolution[1])

-----------------------------

Common Ingestor Attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Class attributes:**

- ``nice_name``: The name of the ingestor that will be displayed in the UI.
- ``valid_extensions``: A list of valid file extensions that the ingestor can work with.
- ``bundled``: A boolean that indicates if the ingestor is designed to work with bundle folder or single file.
- ``importable``: A boolean that indicates if the ingestor can be used to import data into the dcc. UI buttons enabled or disabled accordingly.
- ``referencable``: A boolean that indicates if the ingestor can be used as a reference. UI buttons enabled or disabled accordingly.

**Instance attributes:**

- ``category_functions``: A mapping dictionary to pair methods with categories.
- ``category_reference_functions``: Similar to ``category_functions`` but for referencing.

**Properties:**

- ``category``: The category that the element to be ingested belongs to.
- ``state``: Current state of the ingestors. Can be `idle`, `success` or `failed`.
- ``ingest_path``: The path of the file (or folder for bundles) to be ingested.
- ``namespace``: Mostly useful for referencing. The namespace of the referenced object [1]_. 
- ``metadata``: The metadata of the published elements sub-project. This is a dynamic property and not embedded into the publish data. When the related sub-projects metadata edited, this will be updated as well.


.. [1] Currently namespaces doesn't have a proper implementation. This attribute will be more useful in the future.


