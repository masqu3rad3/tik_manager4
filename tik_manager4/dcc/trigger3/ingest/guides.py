"""Import a published .trg into the active Trigger session's guides."""

from tik_manager4.dcc.ingest_core import IngestCore
from tik_manager4.dcc.trigger3._host import host


class Guides(IngestCore):
    """Add the modules of a ``.trg`` to the active session."""

    nice_name = "Import Guides"
    valid_extensions = [".trg"]
    referencable = False

    def _bring_in_default(self):
        session = host().session
        if session is None:
            raise RuntimeError("No Trigger session to import guides into.")
        session.guides.import_(self.ingest_path)
