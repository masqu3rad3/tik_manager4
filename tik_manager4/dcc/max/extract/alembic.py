"""Extract Alembic from 3dsMax Scene."""

from pymxs import runtime as rt
from tik_manager4.dcc.extract_core import ExtractCore


class Alembic(ExtractCore):
    """Extract Alembic from 3ds Max scene."""

    nice_name = "Alembic"
    color = (244, 132, 132)
    bundled = False

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
                "particle_as_mesh": {
                    "display_name": "Particle as Mesh",
                    "type": "boolean",
                    "value": False,
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
            },
        }
        super().__init__(exposed_settings=exposed_settings,
                         global_exposed_settings=global_settings)
        if not rt.pluginManager.loadclass(rt.Alembic_Export):
            raise ValueError("Alembic Plugin cannot be initialized")

        self._extension = ".abc"

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
            "coordinate_system": "YUp",
            "archive_type": "Ogawa",
            "particle_as_mesh": True,
            "shape_suffix": False,
            "sub_steps": 1,
            "hidden": True,
            "normals": True,
            "vertex_colors": True,
            "extra_channels": True,
            "velocity": True,
            "material_ids": True,
            "visibility": True,
            "layer_name": True,
            "material_name": True,
            "object_id": True,
            "custom_attributes": True,
            "anim_time_range": "StartEnd",
            "start_frame": int(rt.animationRange.start),
            "end_frame": int(rt.animationRange.end),
        }

        base_dict.update(override)

        rt.AlembicExport.CoordinateSystem = rt.Name(base_dict["coordinate_system"])
        rt.AlembicExport.ArchiveType = rt.Name(base_dict["archive_type"])
        rt.AlembicExport.ParticleAsMesh = base_dict["particle_as_mesh"]
        rt.AlembicExport.ShapeSuffix = base_dict["shape_suffix"]
        rt.AlembicExport.SamplesPerFrame = base_dict["sub_steps"]
        rt.AlembicExport.Hidden = base_dict["hidden"]
        rt.AlembicExport.Normals = base_dict["normals"]
        rt.AlembicExport.VertexColors = base_dict["vertex_colors"]
        rt.AlembicExport.ExtraChannels = base_dict["extra_channels"]
        rt.AlembicExport.Velocity = base_dict["velocity"]
        rt.AlembicExport.MaterialIDs = base_dict["material_ids"]
        rt.AlembicExport.Visibility = base_dict["visibility"]
        rt.AlembicExport.LayerName = base_dict["layer_name"]
        rt.AlembicExport.MaterialName = base_dict["material_name"]
        rt.AlembicExport.ObjectID = base_dict["object_id"]
        rt.AlembicExport.CustomAttributes = base_dict["custom_attributes"]
        rt.AlembicExport.AnimTimeRange = rt.Name(base_dict["anim_time_range"])
        rt.AlembicExport.StartFrame = base_dict["start_frame"]
        rt.AlembicExport.EndFrame = base_dict["end_frame"]

    def __get_coordinate_system(self):
        """Get the coordinate system from the global settings."""
        mapping = {
            "y": "YUp",
            "z": "ZUp",
        }

        return mapping.get(self.global_settings.get("up_axis"), "YUp")

    def _extract_model(self):
        """Extract method for Model category."""
        _file_path = self.resolve_output()

        override = {
            "coordinate_system": self.__get_coordinate_system(),
            "velocity": False,
            "anim_time_range": "CurrentFrame",
        }
        self._base_settings(override)

        rt.exportFile(
            _file_path,
            rt.Name("NoPrompt"),
            selectedOnly=False,
            using=rt.Alembic_Export
        )

    def _extract_animation(self):
        """Extract method for Animation category."""
        _file_path = self.resolve_output()

        settings = self.settings.get("Animation")
        override = {
            "coordinate_system": self.__get_coordinate_system(),
            "start_frame": settings.get("start_frame"),
            "end_frame": settings.get("end_frame"),
            "sub_steps": settings.get("sub_steps"),
            "particle_as_mesh": False,
        }
        self._base_settings(override)

        rt.exportFile(
            _file_path,
            rt.Name("NoPrompt"),
            selectedOnly=False,
            using=rt.Alembic_Export
        )

    def _extract_fx(self):
        """Extract method for Fx category."""
        _file_path = self.resolve_output()

        settings = self.settings.get("Fx")
        override = {
            "coordinate_system": self.__get_coordinate_system(),
            "start_frame": settings.get("start_frame"),
            "end_frame": settings.get("end_frame"),
            "sub_steps": settings.get("sub_steps"),
            "particle_as_mesh": settings.get("particle_as_mesh"),
        }
        self._base_settings(override)

        rt.exportFile(
            _file_path,
            rt.Name("NoPrompt"),
            selectedOnly=False,
            using=rt.Alembic_Export
        )

    def _extract_layout(self):
        """Extract method for layout category."""
        _file_path = self.resolve_output()

        settings = self.settings.get("Layout")
        override = {
            "coordinate_system": self.__get_coordinate_system(),
            "start_frame": settings.get("start_frame"),
            "end_frame": settings.get("end_frame"),
        }
        self._base_settings(override)

        rt.exportFile(
            _file_path,
            rt.Name("NoPrompt"),
            selectedOnly=False,
            using=rt.Alembic_Export
        )

    def _extract_lighting(self):
        """Extract method for lighting category."""
        _file_path = self.resolve_output()

        settings = self.settings.get("Lighting")
        override = {
            "coordinate_system": self.__get_coordinate_system(),
            "start_frame": settings.get("start_frame"),
            "end_frame": settings.get("end_frame"),
            "hidden": False,
        }
        self._base_settings(override)

        rt.exportFile(
            _file_path,
            rt.Name("NoPrompt"),
            selectedOnly=False,
            using=rt.Alembic_Export
        )

    def _extract_default(self):
        """Extract method for any non-specified category."""
        _file_path = self.resolve_output()
        self._base_settings()
        rt.exportFile(
            _file_path,
            rt.Name("NoPrompt"),
            selectedOnly=False,
            using=rt.Alembic_Export
        )
