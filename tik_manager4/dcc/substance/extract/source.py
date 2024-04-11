"""Extract Substance Painter project."""

import substance_painter

from tik_manager4.dcc.extract_core import ExtractCore

class Source(ExtractCore):
    """Extract Substance Painter project."""

    nice_name = "Substance Project"
    color = (255, 255, 255)

    def __init__(self):
        super(Source, self).__init__()

        self.extension = ".spp"

    def _extract_default(self):
        """Extract for any non-specified category."""
        _file_path = self.resolve_output()  # this won't have an extension.
        full_save_mode = substance_painter.project.ProjectSaveMode.Full
        substance_painter.project.save_as_copy(_file_path, mode=full_save_mode)