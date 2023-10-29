# pylint: disable=super-with-arguments
# pylint: disable=consider-using-f-string
"""Publisher Handler."""

from tik_manager4 import dcc

class Publisher():
    _dcc_handler = dcc.Dcc()

    def __init__(self, work_object):
        """Initialize the Publisher object."""
        self._work_object = work_object
    def resolve(self):
        """Resolve the validations, extracts, variables, etc."""
        pass
    def reserve(self):
        """Reserve the slot for publish.

        Makes sure that the publish is not overriden by other users during the process.
        """
        pass

    def validate(self):
        """Validate the scene."""
        pass

    def extract(self):
        """Extract the elements."""
        pass

    def publish(self):
        """Finalize the publish by updating the reserved slot."""
        pass