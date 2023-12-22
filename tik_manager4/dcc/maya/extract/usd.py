"""Extract Alembic from Maya scene"""

from maya import cmds
from maya import OpenMaya as om
from tik_manager4.dcc.extract_core import ExtractCore
from tik_manager4.dcc.maya import utils


# The Collector will only collect classes inherit ExtractCore
class Usd(ExtractCore):
    """Extract Alembic from Maya scene"""

    nice_name = "USD"
    color = (71, 143, 203)
    _ranges = utils.get_ranges()

    # these are the exposed settings in the UI
    # WARNING: Caution removing keys from this dict! It will likely throw a KeyError on the _extract_* methods
    default_settings = {
        "Animation": {
            "start_frame": _ranges[0],
            "end_frame": _ranges[3],
            "sub_steps": 1,
            "euler_filter": False,
            "static_single_sample": False,
        },
        "Layout": {
            "start_frame": _ranges[0],
            "end_frame": _ranges[3],
            "sub_steps": 1,
            "euler_filter": False,
            "static_single_sample": False,
        },
        "Fx": {
            "start_frame": _ranges[0],
            "end_frame": _ranges[3],
            "sub_steps": 1,
            "euler_filter": False,
            "static_single_sample": False,
        },
        "Lighting": {
            "start_frame": _ranges[0],
            "end_frame": _ranges[3],
            "sub_steps": 1,
            "euler_filter": False,
            "static_single_sample": False,
        },
    }

    def __init__(self):
        super(Usd, self).__init__()
        if not cmds.pluginInfo("mayaUsdPlugin", loaded=True, query=True):
            try:
                cmds.loadPlugin("mayaUsdPlugin")
            except Exception as e:
                om.MGlobal.displayInfo("USD Plugin cannot be initialized")
                raise e

        om.MGlobal.displayInfo("USD Extractor loaded")

        self._extension = ".usd"
        # Category names must match to the ones in category_definitions.json (case sensitive)
        self.category_functions = {
            "Model": self._extract_model,
            "LookDev": self._extract_lookdev,
            "Assembly": self._extract_assembly,
            "Layout": self._extract_layout,
            "Animation": self._extract_animation,
            "Fx": self._extract_fx,
            "Lighting": self._extract_lighting,
        }

    def _extract_model(self):
        """Extract method for model category"""
        _file_path = self.resolve_output()
        settings = self.settings.get("Model", {})
        cmds.mayaUSDExport(
            file=_file_path,
            exportBlendShapes=False,
            exportSkels=None,
            exportSkin=None,
            exportMaterialCollections=False,
            frameRange=[1, 1],
            ignoreWarnings=True,
            renderableOnly=True,
            selection=False,
        )

    def _extract_lookdev(self):
        """Extract method for lookdev category"""
        # identical to model
        self._extract_model()

    def _extract_assembly(self):
        """Extract method for assembly category"""
        # identical to model
        self._extract_model()

    def _extract_animation(self):
        """Extract method for animation category"""
        _file_path = self.resolve_output()
        settings = self.settings.get("Animation", {})
        _start_frame = settings.get("start_frame")
        _end_frame = settings.get("end_frame")
        _frame_stride = float(1.0 / settings.get("sub_steps"))
        cmds.mayaUSDExport(
            file=_file_path,
            exportBlendShapes=False,
            exportSkels=None,
            exportSkin=None,
            exportMaterialCollections=False,
            eulerFilter=settings.get_property("euler_filter"),
            frameRange=[_start_frame, _end_frame],
            frameStride=_frame_stride,
            ignoreWarnings=True,
            renderableOnly=False,
            selection=False,
            staticSingleSample=settings.get_property("static_single_sample"),
        )

    def _extract_fx(self):
        """Extract method for fx category"""
        # identical to animation
        self._extract_animation()

    def _extract_lighting(self):
        """Extract method for lighting category"""
        # identical to animation
        self._extract_animation()

    def _extract_layout(self):
        """Extract method for layout category"""
        # identical to animation
        self._extract_animation()

    def _extract_default(self):
        """Extract method for any non-specified category"""
        _file_path = self.resolve_output()
        cmds.mayaUSDExport(file=_file_path)
