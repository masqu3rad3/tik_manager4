"""Core class for validations."""


class ValidateCore():
    """Core class for validations."""
    name: str = ""
    nice_name: str = ""
    def __init__(self, *args, **kwargs):
        """Initialize class."""
        self._args = args
        self._kwargs = kwargs

        self.ignorable: bool = True
        self.autofixable: bool = False
        self.selectable: bool = False

        self.collection = []

        self._state: str = "idle"
        self._fail_message: str = ""

    @property
    def state(self):
        return self._state

    @property
    def fail_message(self):
        return self._fail_message

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
