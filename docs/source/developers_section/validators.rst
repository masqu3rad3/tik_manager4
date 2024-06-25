Developing Validators
=====================

Validators are sanity checks that gets run during publishing. They are
defined in the `validate` directory -> ``tik_manager4/dcc/<dcc_name>/validate``.


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