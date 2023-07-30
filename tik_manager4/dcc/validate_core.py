"""Core class for validations."""


class ValidateCore(object):
    """Core class for validations."""

    def __init__(self, *args, **kwargs):
        """Initialize class."""
        self._args = args
        self._kwargs = kwargs

        self.name = ""

        self.ignorable = True
        self.passed= False
        self.ignored=False
        self.autofixable = False

        self._state = "idle"

    @property
    def state(self):
        return self._state

    def validate(self):
        """Validate the given arguments."""
        pass

    def fix(self):
        """Fix the validation."""
        pass
