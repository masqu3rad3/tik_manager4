"""Ingest Alembic."""

from pymxs import runtime as rt
from tik_manager4.dcc.ingest_core import IngestCore


class Alembic(IngestCore):
    """Ingest Alembic."""

    nice_name = "Ingest Alembic"
    valid_extensions = [".abc"]
    referencable = False

    def __init__(self):
        super().__init__()
        if not rt.pluginManager.loadclass(rt.Alembic_Import):
            raise ValueError("Alembic Plugin cannot be initialized")
        self.category_functions = {
            "Model": self._bring_in_model,
        }

    def _base_settings(self, override=None):
        """Set the base settings for the Alembic import with an override option."""
        # get the coordinate system if its in metadata
        up_axis = self.metadata.get_value("up_axis", fallback_value="y")
        mapping = {"y": "Yup", "z": "Zup"}
        coordinate_system = mapping.get(up_axis, "Yup")
        override = override or {}
        base_dict = {
            "CoordinateSystem": coordinate_system,
            "ImportToRoot": False,
            "FitTimeRange": True,
            "SetStartTime": True,
            "UVs": True,
            "Normals": True,
            "VertexColors": True,
            "ExtraChannels": True,
            "Velocity": True,
            "MaterialIDs": True,
            "Visibility": True,
            "ShapeSuffix": False
        }
        base_dict.update(override)

        rt.Alembic_Import.CoordinateSystem = rt.Name(base_dict["CoordinateSystem"])
        rt.Alembic_Import.ImportToRoot = base_dict["ImportToRoot"]
        rt.Alembic_Import.FitTimeRange = base_dict["FitTimeRange"]
        rt.Alembic_Import.SetStartTime = base_dict["SetStartTime"]
        rt.Alembic_Import.UVs = base_dict["UVs"]
        rt.Alembic_Import.Normals = base_dict["Normals"]
        rt.Alembic_Import.VertexColors = base_dict["VertexColors"]
        rt.Alembic_Import.ExtraChannels = base_dict["ExtraChannels"]
        rt.Alembic_Import.Velocity = base_dict["Velocity"]
        rt.Alembic_Import.MaterialIDs = base_dict["MaterialIDs"]
        rt.Alembic_Import.Visibility = base_dict["Visibility"]
        rt.Alembic_Import.ShapeSuffix = base_dict["ShapeSuffix"]

    def _bring_in_model(self):
        """Import Alembic File."""
        override = {
            "FitTimeRange": False,
            "SetStartTime": False,
            "Velocity": False,
        }
        self._base_settings(override)
        rt.importFile(self.ingest_path, rt.Name("NoPrompt"), using=rt.Alembic_Import)

    def _bring_in_default(self):
        """Import Alembic File."""
        self._base_settings()
        rt.importFile(self.ingest_path, rt.Name("NoPrompt"), using=rt.Alembic_Import)