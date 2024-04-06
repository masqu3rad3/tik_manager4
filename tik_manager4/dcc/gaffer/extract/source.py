"""Extract Gaffer Scene."""

from tik_manager4.dcc.gaffer import gaffer_menu

from tik_manager4.dcc.extract_core import ExtractCore

class Source(ExtractCore):
    """Extract Gaffer scene."""

    nice_name = "Source Scene"
    color = (255, 255, 255)

    def __init__(self):
        super(Source, self).__init__()
        self.gaffer = gaffer_menu.GafferMenu()
        self.extension = ".gfr"

    def _extract_default(self):
        """Extract method for any non-specified category"""
        _file_path = self.resolve_output()
        _original_path = self.gaffer.script["fileName"].getValue()
        self.gaffer.script["fileName"].setValue(_file_path)
        self.gaffer.script.save()
        self.gaffer.script["fileName"].setValue(_original_path)