"""Open a published Trigger session bundle."""

from pathlib import Path

from tik_manager4.dcc.ingest_core import IngestCore
from tik_manager4.dcc.trigger3._host import host, session_file_in

BUNDLE_MATCH_ID = 31


class Source(IngestCore):
    """Open the ``.tr`` inside a published bundle folder."""

    nice_name = "Open Trigger Session"
    valid_extensions = [".tr"]
    bundle = True
    bundle_match_id = BUNDLE_MATCH_ID
    referencable = False

    @property
    def ingest_path(self):
        """The bundle folder (or the ``.tr`` itself)."""
        return self._file_path

    @ingest_path.setter
    def ingest_path(self, ingest_path):
        """Accept a folder: a bundle is a folder, not a file."""
        path = Path(ingest_path)
        if not path.exists():
            raise ValueError(f"Path does not exist: {ingest_path}")
        if path.is_file() and path.suffix not in self.valid_extensions:
            raise ValueError(f"File extension not valid: {path.suffix}")
        self._file_path = str(path)

    def _bring_in_default(self):
        host().open(session_file_in(self.ingest_path))
