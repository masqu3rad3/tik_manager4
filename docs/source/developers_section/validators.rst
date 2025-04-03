.. _developing_validators:

Developing Validators
=====================

Validators are sanity checks that gets run during publishing. They are
defined in the `validate` directory -> ``tik_manager4/dcc/<dcc_name>/validate``.

.. tip::

        Starting from v4.3.8, Tik Manager can access validators from ``<common>/plugins/maya/validation/`` folder. This is the suggested location for any custom validators as they will be immediately available with the entire team and won't be affected by Tik Manager version updates.


Below is a simple example of a validator for Maya that checks if the work file is following a hierarchy convention.

.. code-block:: python

    """Example Hierarchy Checker for Maya."""

    from maya import cmds
    from tik_manager4.dcc.validate_core import ValidateCore

    class HierarchyChecker(ValidateCore):
        """Simple Hierarchy Checker for Maya."""

        nice_name = "Hierarchy Checker"

        def __init__(self):
            super().__init__()
            self.autofixable = True
            self.ignorable = False
            self.selectable = True

        def collect(self):
            """Collect the transform nodes in the root."""
            default_cams = ["front", "persp", "side", "top"]
            self.collection = [node for node in cmds.ls(assemblies=True) if node not in default_cams]

        def validate(self):
            """Check if the hierarchy is correct."""
            self.collect()

            # let's say our pipe requires each publish needs to be stored under a single group.
            if len(self.collection) > 1:
                self.failed(msg="More than one root node found.")
                return

            # the root group needs to be named as root
            if self.collection[0] != "root":
                self.failed(msg="Root node is not named as 'root'.")
                return

            # the root group must have exactly 3 child groups called render, guide and proxy
            children = cmds.listRelatives(self.collection[0], children=True)
            if not children:
                self.failed(msg="No child groups found.")
                return

            if len(children) != 3:
                self.failed(msg="Exactly 3 child groups are required.")
                return

            if not all([child in ["render", "guide", "proxy"] for child in children]):
                self.failed(msg="Child groups are not named correctly.")
                return

            self.passed()

        def fix(self):
            """Fix the hierarchy."""
            self.collect()
            if len(self.collection) > 1:
                # there are more groups than expected, We tag this unfixable
                added_message = f"{self.fail_message}\nAuto-fix failed."
                self.failed(msg=added_message)
                return
            if self.collection[0] != "root":
                cmds.rename(self.collection[0], "root")

        def select(self):
            """Select any root nodes other than the 'root'."""
            self.collect()
            cmds.select([node for node in self.collection if node != "root"])



.. collapse:: Detailed Explanation

    First we import the necessary modules and classes.

    .. code-block:: python

        from maya import cmds
        from tik_manager4.dcc.validate_core import ValidateCore

    Then we define our validator class.

    .. code-block:: python

        class HierarchyChecker(ValidateCore):
            """Simple Hierarchy Checker for Maya."""

            nice_name = "Hierarchy Checker"

    It is important to inherit from the `ValidateCore` class. This class provides the necessary methods and properties to create a validator.
    Than we define the `nice_name` attribute. This is the name of the validator that will be displayed to the user.

    .. code-block:: python

        def __init__(self):
            super().__init__()
            self.autofixable = True
            self.ignorable = False
            self.selectable = True
    
    In the `__init__` method, we define the `autofixable`, `ignorable` and `selectable` attributes. These attributes are used to 
    determine the behavior of the validator. If `autofixable` is set to `True`, the user will be able to automatically fix the issue.
    If `ignorable` is set to `True`, the user will be able to ignore the issue. If `selectable` is set to `True`, the user will be 
    able to select the problematic nodes.

    Next we define the `collect` method. This method is used to collect the items that will be validated. In this case, we are collecting the transform nodes in the root.

    .. code-block:: python

        def collect(self):
            """Collect the transform nodes in the root."""
            default_cams = ["front", "persp", "side", "top"]
            self.collection = [node for node in cmds.ls(assemblies=True) if node not in default_cams]

    Afterwards we define the `validate` method. This method is used to check if the collected items are following the convention.

    .. code:: python

        def validate(self):
            """Check if the hierarchy is correct."""
            self.collect()

            # let's say our pipe requires each publish needs to be stored under a single group.
            if len(self.collection) > 1:
                self.failed(msg="More than one root node found.")
                return

            # the root group needs to be named as root
            if self.collection[0] != "root":
                self.failed(msg="Root node is not named as 'root'.")
                return

            # the root group must have exactly 3 child groups called render, guide and proxy
            children = cmds.listRelatives(self.collection[0], children=True)
            if not children:
                self.failed(msg="No child groups found.")
                return

            if len(children) != 3:
                self.failed(msg="Exactly 3 child groups are required.")
                return

            if not all([child in ["render", "guide", "proxy"] for child in children]):
                self.failed(msg="Child groups are not named correctly.")
                return

            self.passed()

    The 'validate' method is actually overridden from the parent class. The parent class has a default implementation that always passes.
    It is important to call the `passed` or `failed` methods to set the state of the validation.
    If the validation fails, the `failed` method is called with a message.
    If the validation passes, the `passed` method is called.

    Next we define the `fix` method. This method is used to fix the issue automatically.

    .. code-block:: python

        def fix(self):
            """Fix the hierarchy."""
            self.collect()
            if len(self.collection) > 1:
                # there are more groups than expected, We tag this unfixable
                added_message = f"{self.fail_message}\nAuto-fix failed."
                self.failed(msg=added_message)
                return
            if self.collection[0] != "root":
                cmds.rename(self.collection[0], "root")

    In this example, just for the purpose of demonstration, 
    We first checking the length of the collection. If there are more than one root nodes, we tag this as unfixable.
    If the issue cannot be fixed, the `failed` method is called with a message.
    For the sake of simplicity and demonstration, we only check if the root node is named as ``root`` and renaming it if it is not.

    Finally we define the `select` method. This method is used to select the problematic nodes.

    .. code-block:: python

        def select(self):
            """Select any root nodes other than the 'root'."""
            self.collect()
            cmds.select([node for node in self.collection if node != "root"])

    Again, for the sake of simplicity and demonstration, we are selecting the root nodes other than the one named as ``root``.

    Similar to ``validate`` and ``fix`` methods, the ``select`` method is also overridden from the parent class. 
    The parent class has a default implementation that does nothing.

    .. note::

        ``fix`` and ``select`` methods are optional and they will only become active if the ``autofixable`` and ``selectable`` attributes are set to ``True`` respectively.


----------------------------

Common Validator Attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Class attributes:**

- ``nice_name``: The name of the validator that will be displayed to the user.
- ``checked_by_default``: If True, the validator will be active by default. 

**Instance attributes:**

- ``ignorable``: If True, the validator can be ignored by the user even if it fails.
- ``autofixable``: If True, it will be possible to automatically fix the issue [1]_.
- ``selectable``: If True, the user can select the culprit nodes [2]_.
- ``collection``: List of items to be validated. Can be hardcoded or defined by logic functions.

**Properties:**

- ``state``: The state of validation. Can be `idle`, `failed`, `passed` or `ignored`.
- ``fail_message``: The message to be displayed when the validation fails.
- ``metadata``: The metadata coming from the sub-project of the work file about to be published.


.. [1] This option requires that ``fix`` method is implemented in the validator.
.. [2] This option requires that ``select`` method is implemented in the validator.