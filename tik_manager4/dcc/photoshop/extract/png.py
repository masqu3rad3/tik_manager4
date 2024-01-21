"""Extract Png file."""
from win32com.client import Dispatch

from tik_manager4.dcc.extract_core import ExtractCore

class Png(ExtractCore):
    """Extract Png from Photoshop file."""

    nice_name = "Png"
    color = (68, 0, 255)

    def __init__(self):
        super(Png, self).__init__()

        self.com_link = Dispatch("Photoshop.Application")

        self.extension = ".png"

    def _extract_default(self):
        """Extract Png."""
        file_path = self.resolve_output()
        active_doc = self.com_link.Application.ActiveDocument
        save_options = Dispatch("Photoshop.PNGSaveOptions")
        active_doc.SaveAs(file_path, save_options, True)