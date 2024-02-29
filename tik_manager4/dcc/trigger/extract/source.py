"""Extract Trigger Session."""

import trigger.version_control.api as trigger
from tik_manager4.dcc.extract_core import ExtractCore


class Source(ExtractCore):
    """Exctract Source Trigger Session."""

    nice_name = "Source Trigger Session"
    color = (255, 255, 255)

    def __init__(self):
        super(Source, self).__init__()

        self.extension = ".tr"

        self.trigger_api = trigger.ApiHandler()

    def _extract_default(self):
        """Extract method for any non-specified category"""
        self.trigger_api.export_session(self.resolve_output())
