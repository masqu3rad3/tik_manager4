"""Extract Png file."""
from win32com.client import Dispatch

from tik_manager4.dcc.extract_core import ExtractCore

class Tif(ExtractCore):
    """Extract Tif from Photoshop file."""

    nice_name = "Tif"
    color = (0, 149, 255)

    global_exposed_settings = {
        "AlphaChannels": True,
        "EmbedColorProfile": True,
        "Layers": False,
    }
    def __init__(self):
        super(Tif, self).__init__()

        self.com_link = Dispatch("Photoshop.Application")

        self.extension = ".tif"

    def _extract_default(self):
        """Extract Tif."""
        file_path = self.resolve_output()
        active_doc = self.com_link.Application.ActiveDocument
        save_options = Dispatch("Photoshop.TiffSaveOptions")
        alpha = self.global_exposed_settings["AlphaChannels"]
        save_options.AlphaChannels = alpha
        embed = self.global_exposed_settings["EmbedColorProfile"]
        save_options.EmbedColorProfile = embed
        layers = self.global_exposed_settings["Layers"]
        save_options.Layers = layers
        active_doc.SaveAs(file_path, save_options, True)
