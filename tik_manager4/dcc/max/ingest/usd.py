"""Ingest USD."""

from pymxs import runtime as rt
from tik_manager4.dcc.ingest_core import IngestCore


class USD(IngestCore):
    """Ingest USD."""

    nice_name = "Ingest USD"
    valid_extensions = [".usd", ".usda", ".usdc"]
    referencable = False

    def __init__(self):
        super().__init__()
        if not rt.pluginManager.loadclass(rt.USDImporter):
            raise ValueError("USD Importer cannot be initialized.")
        self.category_functions = {
            "Model": self._bring_in_model,
        }

    def _base_settings(self, override=None):
        """Set the base settings for the Alembic import with an override option."""
        override = override or {}

        base_dict = {
            "Materials": True,
            "TimeMode": "frameRange",
        }
        base_dict.update(override)


        import_options = rt.USDImporter.createOptions()

        import_options.Materials = base_dict["Materials"]
        import_options.TimeMode = rt.name(base_dict["TimeMode"])

        return import_options

    def _bring_in_model(self):
        """Import USD File."""
        override = {
            "TimeMode": "current",
        }
        rt.USDImporter.ImportFile(self.ingest_path, importOptions=self._base_settings(override))

    def _bring_in_default(self):
        """Import USD File with default settings."""
        rt.USDImporter.ImportFile(self.ingest_path, importOptions=self._base_settings())
