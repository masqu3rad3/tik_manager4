"""Core class for validations."""

import importlib
from pathlib import Path
from tik_manager4.objects.metadata import Metadata


class ValidateCore:
    """Core class for validations."""

    nice_name: str = ""
    checked_by_default: bool = True

    def __init__(self, *args, **kwargs):
        """Initialize class."""
        self.name = str(Path(__file__).stem)
        self._args = args
        self._kwargs = kwargs

        self.ignorable: bool = True
        self.autofixable: bool = False
        self.selectable: bool = False

        self._metadata: Metadata

        self.collection: list = []

        self._state: str = "idle"
        self._fail_message: str = ""

    def __init_subclass__(cls, **kwargs):
        # Get the base name of the file without the extension using pathlib
        module = importlib.import_module(cls.__module__)
        module_file_path = Path(module.__file__).resolve()
        module_name = module_file_path.stem
        # Set the 'name' variable in the subclass
        cls.name = module_name
        super().__init_subclass__(**kwargs)

    @property
    def state(self):
        return self._state

    @property
    def fail_message(self):
        return self._fail_message

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        self._metadata = metadata

    def reset(self):
        """Reset the validation."""
        self._state = "idle"
        self._fail_message = ""

    def failed(self, msg: str = ""):
        """Set the validation as failed."""
        self._state = "failed"
        self._fail_message = msg

    def passed(self):
        """Set the validation as passed."""
        self._state = "passed"

    def ignored(self, msg=""):
        """Set the validation as ignored."""
        if self.ignorable:
            self._state = "ignored"
        else:
            raise ValueError("Validation is not ignorable.")

    def collect(self):
        """Collect the objects related to the validation.

        collection list needs to be updated on this method.
        self.collection = [obj1, obj2, ...]
        """
        pass

    def validate(self):
        """Validate the given arguments."""
        pass

    def fix(self):
        """Fix the validation."""
        pass

    def select(self):
        """Select the objects related to the validation."""
        pass

    def info(self):
        """Information about the validation."""
        pass
