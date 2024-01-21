"""Extract Jpg file."""
from win32com.client import Dispatch

from tik_manager4.dcc.extract_core import ExtractCore

class Jpg(ExtractCore):
    """Extract Jpg from Photoshop file."""

    nice_name = "Jpg"
    color = (144, 0, 255)

    global_exposed_settings = {
        "EmbedColorProfile": True,
        "Quality": 12,
    }

    def __init__(self):
        super(Jpg, self).__init__()

        self.com_link = Dispatch("Photoshop.Application")

        self.extension = ".jpg"

    def _extract_default(self):
        """Extract Jpg."""
        file_path = self.resolve_output()
        active_doc = self.com_link.Application.ActiveDocument
        save_options = Dispatch("Photoshop.JPEGSaveOptions")
        embed = self.global_exposed_settings["EmbedColorProfile"]
        save_options.EmbedColorProfile = embed
        save_options.FormatOptions = 1
        save_options.Matte = 1
        quality = self.global_exposed_settings["Quality"]
        save_options.Quality = quality
        active_doc.SaveAs(file_path, save_options, True)