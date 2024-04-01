"""Source Back Mari Archives."""

from tik_manager4.dcc.ingest_core import IngestCore
from tik_manager4.dcc.mari import utils

class Source(IngestCore):
    """Source Back Mari Archives."""

    nice_name = "Ingest Backup or Arcive"
    valid_extensions = [".mra", '.mri']
    referencable = False

    def _bring_in_default(self):
        """Open Mari Archive."""
        utils.load(self.ingest_path, force=False)

