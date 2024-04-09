"""Ingest Substance Project."""

import substance_painter

from tik_manager4.dcc.ingest_core import IngestCore


class Source(IngestCore):
    """Ingest Substance Painter project."""

    nice_name = "Ingest Substance Project"
    valid_extensions = [".spp"]
    referencable = False
    importable = False

    # def _bring_in_default(self):
    #     """Open Substance Painter project."""
    #     substance_painter.project.open(self.ingest_path)