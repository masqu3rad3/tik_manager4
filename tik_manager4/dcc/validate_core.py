"""Core class for validations."""


class ValidateCore(object):
    """Core class for validations."""

    def __init__(self, *args, **kwargs):
        """Initialize class."""
        self._args = args
        self._kwargs = kwargs

        self.ignorable = True
        self.passed= False
        self.error=False
        self.ignored=False

        self.autofixable = False

    def validate(self):
        """Validate the given arguments."""
        pass

    def fix(self):
        """Fix the validation."""
        pass
