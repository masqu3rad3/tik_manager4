"""Extract Png file."""
from win32com.client import Dispatch

from tik_manager4.dcc.extract_core import ExtractCore

class Tga(ExtractCore):
    """Extract Tga from Photoshop file."""

    nice_name = "Tga"
    color = (0, 60, 255)

    def __init__(self):
        super(Tga, self).__init__()

        self.com_link = Dispatch("Photoshop.Application")

        self.extension = ".tga"

    def _extract_default(self):
        """Extract Tga."""
        file_path = self.resolve_output()
        active_doc = self.com_link.Application.ActiveDocument
        save_options = Dispatch("Photoshop.TargaSaveOptions")
        save_options.Resolution = 32
        save_options.AlphaChannels = True
        save_options.RLECompression = True
        active_doc.SaveAs(file_path, save_options, True)
