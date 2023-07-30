"""Core class for validations."""


class ValidateCore(object):
    """Core class for validations."""

    def __init__(self, *args, **kwargs):
        """Initialize class."""
        self._args = args
        self._kwargs = kwargs

        self.name: str = ""

        self.ignorable: bool = True
        self.autofixable: bool = False
        self.selectable: bool = False

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

    def validate(self):
        """Validate the given arguments."""
        pass

    def fix(self):
        """Fix the validation."""
        pass

    def select(self):
        """Select the objects related to the validation."""
        pass