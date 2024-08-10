"""Simple USD file extractor for 3ds Max."""

from pymxs import runtime as rt

from tik_manager4.dcc.extract_core import ExtractCore



class Usd(ExtractCore):
    """Extract USD from 3ds Max scene."""

    nice_name = "USD"
    color = (71, 143, 203)

    def __init__(self):
        _range_start = int(rt.animationRange.start)
        _range_end = int(rt.animationRange.end)

        global_settings = {
            "up_axis": {
                "display_name": "Up Axis",
                "type": "combo",
                "items": ["y", "z"],
                "value": "y",
            }
        }

        exposed_settings = {
            "Animation": {
                "start_frame": {
                    "display_name": "Start Frame",
                    "type": "integer",
                    "value": _range_start,
                },
                "end_frame": {
                    "display_name": "End Frame",
                    "type": "integer",
                    "value": _range_end,
                },
                "sub_steps": {
                    "display_name": "Sub Steps",
                    "type": "integer",
                    "value": 1,
                },
            },
            "Layout": {
                "start_frame": {
                    "display_name": "Start Frame",
                    "type": "integer",
                    "value": _range_start,
                },
                "end_frame": {
                    "display_name": "End Frame",
                    "type": "integer",
                    "value": _range_end,
                },
            },
            "Fx": {
                "start_frame": {
                    "display_name": "Start Frame",
                    "type": "integer",
                    "value": _range_start,
                },
                "end_frame": {
                    "display_name": "End Frame",
                    "type": "integer",
                    "value": _range_end,
                },
                "sub_steps": {
                    "display_name": "Sub Steps",
                    "type": "integer",
                    "value": 1,
                },
            },
            "Lighting": {
                "start_frame": {
                    "display_name": "Start Frame",
                    "type": "integer",
                    "value": _range_start,
                },
                "end_frame": {
                    "display_name": "End Frame",
                    "type": "integer",
                    "value": _range_end,
                },
                "sub_steps": {
                    "display_name": "Sub Steps",
                    "type": "integer",
                    "value": 1,
                },
            },
        }
        super().__init__(exposed_settings=exposed_settings,
                         global_exposed_settings=global_settings)

        if not rt.pluginManager.loadclass(rt.USDExporter):
            raise ValueError("USD Exporter cannot be initialized.")

        self._extension = ".usd"

        self.category_functions = {
            "Model": self._extract_model,
            "Animation": self._extract_animation,
            "Fx": self._extract_fx,
            "Layout": self._extract_layout,
            "Lighting": self._extract_lighting,
        }

    def _base_settings(self, override=None):
        """Set the base settings with an override option."""
        override = override or {}
        base_dict = {
            "Meshes": True,
            "Shapes": True,
            "Lights": True,
            "Cameras": True,
            "Skin": True,
            "Morpher": True,
            "Materials": True,
            "ShadingMode": "useRegistry",
            "AllMaterialTargets": "UsdPreviewSurface",
            "UsdStagesAsReferences": True,
            "HiddenObjects": True,
            "UseUSDVisibility": True,
            "AllowNestedGprims": False,
            "FileFormat": "binary",
            "Normals": "asPrimvar",
            "MeshFormat": "fromScene",
            "TimeMode": "frameRange",
            "StartFrame": float(rt.animationRange.start),
            "EndFrame": float(rt.animationRange.end),
            "SamplesPerFrame": 1,
            "UpAxis": "y",
            "BakeObjectOffsetTransform": True,
            "PreserveEdgeOrientation": True,
            "RootPrimPath": "/"
        }
        base_dict.update(override)

        export_options = rt.USDExporter.createOptions()

        export_options.Meshes = base_dict["Meshes"]
        export_options.Shapes = base_dict["Shapes"]
        export_options.Lights = base_dict["Lights"]
        export_options.Cameras = base_dict["Cameras"]
        export_options.Skin = base_dict["Skin"]
        export_options.Morpher = base_dict["Morpher"]
        export_options.Materials = base_dict["Materials"]
        export_options.ShadingMode = rt.name(base_dict["ShadingMode"])
        export_options.AllMaterialTargets = rt.name(base_dict["AllMaterialTargets"])
        export_options.UsdStagesAsReferences = base_dict["UsdStagesAsReferences"]
        export_options.HiddenObjects = base_dict["HiddenObjects"]
        export_options.UseUSDVisibility = base_dict["UseUSDVisibility"]
        export_options.AllowNestedGprims = base_dict["AllowNestedGprims"]
        export_options.FileFormat = rt.name(base_dict["FileFormat"])
        export_options.Normals = rt.name(base_dict["Normals"])
        export_options.MeshFormat = rt.name(base_dict["MeshFormat"])
        export_options.TimeMode = rt.name(base_dict["TimeMode"])
        export_options.StartFrame = base_dict["StartFrame"]
        export_options.EndFrame = base_dict["EndFrame"]
        export_options.SamplesPerFrame = base_dict["SamplesPerFrame"]
        export_options.UpAxis = rt.name(base_dict["UpAxis"])
        export_options.BakeObjectOffsetTransform = base_dict["BakeObjectOffsetTransform"]
        export_options.PreserveEdgeOrientation = base_dict["PreserveEdgeOrientation"]
        export_options.RootPrimPath = base_dict["RootPrimPath"]

        return export_options

    def _extract_default(self):
        """Extract USD from 3ds Max scene."""
        file_path = self.resolve_output()
        export_options = self._base_settings()
        rt.USDExporter.ExportFile(
            file_path,
            exportOptions=export_options,
            contentSource=rt.name("all")
        )

    def _extract_model(self):
        """Extract method for Model category."""
        file_path = self.resolve_output()
        up_axis = self.global_settings.get("up_axis")

        override = {
            "Shapes": False,
            "Lights": False,
            "Cameras": False,
            "Skin": False,
            "Morpher": True,
            "TimeMode": "current",
            "UpAxis": up_axis,
        }

        export_options = self._base_settings(override)
        rt.USDExporter.ExportFile(
            file_path,
            exportOptions=export_options,
            contentSource=rt.name("all")
        )

    def _extract_animation(self):
        """Extract method for Animation category."""
        file_path = self.resolve_output()
        settings = self.settings.get("Animation")
        up_axis = self.global_settings.get("up_axis")

        override = {
            "StartFrame": float(settings.get("start_frame")),
            "EndFrame": float(settings.get("end_frame")),
            "SamplesPerFrame": settings.get("sub_steps"),
            "UpAxis": up_axis,
        }

        export_options = self._base_settings(override)
        rt.USDExporter.ExportFile(
            file_path,
            exportOptions=export_options,
            contentSource=rt.name("all")
        )

    def _extract_fx(self):
        """Extract method for Fx category."""
        file_path = self.resolve_output()
        settings = self.settings.get("Fx")
        up_axis = self.global_settings.get("up_axis")

        override = {
            "StartFrame": settings.get("start_frame"),
            "EndFrame": settings.get("end_frame"),
            "SamplesPerFrame": settings.get("sub_steps"),
            "UpAxis": up_axis,
        }

        export_options = self._base_settings(override)
        rt.USDExporter.ExportFile(
            file_path,
            exportOptions=export_options,
            contentSource=rt.name("all")
        )

    def _extract_layout(self):
        """Extract method for Layout category."""
        file_path = self.resolve_output()
        settings = self.settings.get("Layout")
        up_axis = self.global_settings.get("up_axis")

        override = {
            "StartFrame": settings.get("start_frame"),
            "EndFrame": settings.get("end_frame"),
            "UpAxis": up_axis,
        }

        export_options = self._base_settings(override)
        rt.USDExporter.ExportFile(
            file_path,
            exportOptions=export_options,
            contentSource=rt.name("all")
        )

    def _extract_lighting(self):
        """Extract method for Lighting category."""
        file_path = self.resolve_output()
        settings = self.settings.get("Lighting")
        up_axis = self.global_settings.get("up_axis")

        override = {
            "StartFrame": settings.get("start_frame"),
            "EndFrame": settings.get("end_frame"),
            "SamplesPerFrame": settings.get("sub_steps"),
            "UpAxis": up_axis,
        }

        export_options = self._base_settings(override)
        rt.USDExporter.ExportFile(
            file_path,
            exportOptions=export_options,
            contentSource=rt.name("all")
        )

