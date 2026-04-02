"""Extract images from Krita file."""

from pathlib import Path

from krita import Krita, InfoObject

from tik_manager4.dcc.extract_core import ExtractCore


class Image(ExtractCore):
    """Extract images from Krita file."""

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
                    "webp"
                ],
                "value": "png",
            },
            "Quality": {
                "display_name": "Quality (Jpg, Webp)",
                "type": "integer",
                "value": 90,
            },
            "Compression": {
                "display_name": "Compression (Png)",
                "type": "integer",
                "value": 6,
            },
            "Alpha": {
                "display_name": "Alpha Channel (Png, Tga, Tif, Webp)",
                "type": "boolean",
                "value": True,
            },
            "FlattenLayers": {
                "display_name": "Flatten Layers (Tif)",
                "type": "boolean",
                "value": True,
            },
            "WebpLossless": {
                "display_name": "Lossless (Webp)",
                "type": "boolean",
                "value": False,
            },
        }
        super(Image, self).__init__(
            global_exposed_settings=global_exposed_settings)

        # Extension will be defined in the _extract_default method.
        self.extension = ""

        self.format_map = {
            "jpg": self.extract_jpg,
            "png": self.extract_png,
            "tga": self.extract_tga,
            "tif": self.extract_tif,
            "webp": self.extract_webp,
        }

    def extract_jpg(self, output_path):
        """Extract Jpg."""
        doc = Krita.instance().activeDocument()
        info = InfoObject()
        info.setProperty("quality", self.global_settings.get("Quality"))
        info.setProperty("subsampling", 0)
        info.setProperty("progressive", False)
        info.setProperty("optimize", True)
        info.setProperty("smoothing", 0)
        doc.exportImage(str(output_path), info)

    def extract_png(self, output_path):
        """Extract Png."""
        doc = Krita.instance().activeDocument()
        info = InfoObject()
        info.setProperty("compression",
                         self.global_settings.get("Compression"))
        info.setProperty("alpha", self.global_settings.get("Alpha"))
        info.setProperty("interlaced", False)
        info.setProperty("indexed", False)
        info.setProperty("saveSRGBProfile", False)
        info.setProperty("forceSRGB", False)
        doc.exportImage(str(output_path), info)

    def extract_tga(self, output_path):
        """Extract Tga."""
        doc = Krita.instance().activeDocument()
        info = InfoObject()
        info.setProperty("compression", 1)  # 1 = RLE
        info.setProperty("alpha", self.global_settings.get("Alpha"))
        doc.exportImage(str(output_path), info)

    def extract_tif(self, output_path):
        """Extract Tif."""
        doc = Krita.instance().activeDocument()
        info = InfoObject()
        info.setProperty("alpha", self.global_settings.get("Alpha"))
        info.setProperty("flatten", self.global_settings.get("FlattenLayers"))
        info.setProperty("compression", 1)  # 1 = LZW
        info.setProperty("saveAsPhotoshop", False)
        doc.exportImage(str(output_path), info)

    def extract_webp(self, output_path):
        """Extract Webp."""
        doc = Krita.instance().activeDocument()
        info = InfoObject()
        info.setProperty("lossless", self.global_settings.get("WebpLossless"))
        info.setProperty("quality", self.global_settings.get("Quality"))
        info.setProperty("alpha", self.global_settings.get("Alpha"))
        doc.exportImage(str(output_path), info)

    def _extract_default(self):
        """Extract the image with the specified format."""
        file_format = self.global_settings.get("file_format")
        # resolve_output will return without extension because we didn't
        # specify it in the init method.
        file_path_without_suffix = self.resolve_output()
        self.extension = f".{file_format}"
        file_path = Path(file_path_without_suffix).with_suffix(self.extension)
        self.format_map[file_format](file_path)
