"""Extract images from Photoshop file."""

from pathlib import Path
from win32com.client import Dispatch
from tik_manager4.dcc.extract_core import ExtractCore


class Image(ExtractCore):
    """Extract images from Photoshop file."""

    nice_name = "Image"
    color = (160, 15, 200)  # Purple
    bundled = False

    def __init__(self):
        global_exposed_settings = {
            "file_format": {
                "display_name": "Format",
                "type": "combo",
                "items": [
                    "jpg",
                    "png",
                    "tga",
                    "tif",
                ],
                "value": "png",
            },
            "EmbedColorProfile": {
                "display_name": "Embed Color Profile (Jpg, Tif)",
                "type": "boolean",
                "value": True,
            },
            "Quality": {
                "display_name": "Quality (Jpg)",
                "type": "integer",
                "value": 12,
            },
            "AlphaChannels": {
                "display_name": "Alpha Channels (Tif)",
                "type": "boolean",
                "value": True,
            },
            "Layers": {
                "display_name": "Layers (Tif)",
                "type": "boolean",
                "value": False,
            }
        }
        super(Image, self).__init__(global_exposed_settings=global_exposed_settings)

        self.com_link = Dispatch("Photoshop.Application")

        # Extension will be defined in the _extract_default method.
        self.extension = ""

        self.format_map = {
            "jpg": self.extract_jpg,
            "png": self.extract_png,
            "tga": self.extract_tga,
            "tif": self.extract_tif,
        }

    def extract_jpg(self, output_path):
        """Extract Jpg."""
        active_doc = self.com_link.Application.ActiveDocument
        save_options = Dispatch("Photoshop.JPEGSaveOptions")
        embed = self.global_settings.get("EmbedColorProfile")
        save_options.EmbedColorProfile = embed
        save_options.FormatOptions = 1
        save_options.Matte = 1
        quality = self.global_settings.get("Quality")
        save_options.Quality = quality
        active_doc.SaveAs(output_path, save_options, True)

    def extract_png(self, output_path):
        """Extract Png."""
        active_doc = self.com_link.Application.ActiveDocument
        save_options = Dispatch("Photoshop.PNGSaveOptions")
        active_doc.SaveAs(output_path, save_options, True)

    def extract_tga(self, output_path):
        """Extract Tga."""
        active_doc = self.com_link.Application.ActiveDocument
        save_options = Dispatch("Photoshop.TargaSaveOptions")
        save_options.Resolution = 32
        save_options.AlphaChannels = True
        save_options.RLECompression = True
        active_doc.SaveAs(output_path, save_options, True)

    def extract_tif(self, output_path):
        """Extract Tif."""
        active_doc = self.com_link.Application.ActiveDocument
        save_options = Dispatch("Photoshop.TiffSaveOptions")
        alpha = self.global_settings.get("AlphaChannels")
        save_options.AlphaChannels = alpha
        embed = self.global_settings.get("EmbedColorProfile")
        save_options.EmbedColorProfile = embed
        layers = self.global_settings.get("Layers")
        save_options.Layers = layers
        active_doc.SaveAs(output_path, save_options, True)

    def _extract_default(self):
        """Extract the image with the specified format."""
        file_format = self.global_settings.get("file_format")
        # resolve_output will return without extension because we didn't
        # specify it in the init method.
        file_path_without_suffix = self.resolve_output()
        self.extension = f".{file_format}"
        file_path = Path(file_path_without_suffix).with_suffix(self.extension)
        self.format_map[file_format](file_path)
