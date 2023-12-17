"""Extract Alembic from Maya scene"""

from maya import cmds
from maya import OpenMaya as om
from tik_manager4.dcc.extract_core import ExtractCore
from tik_manager4.dcc.maya import utils

# The Collector will only collect classes inherit ExtractCore
class Usd(ExtractCore):
    """Extract Alembic from Maya scene"""
    name = "usd" # IMPORTANT. Must match to the one in category_definitions.json
    nice_name = "USD"
    color = (71, 143, 203)
    _ranges = utils.get_ranges()
    default_settings = {
        "Animation": {
            "startTime": _ranges[0],
            "endTime": _ranges[3],
            "frameStride": 1.0,
            "frameSample": 0.0,
            "eulerFilter": 0,
            "staticSingleSample": 0,
        }
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
        self.category_functions = {"Model": self._extract_model,
                                   "Animation": self._extract_animation,
                                   "Fx": self._extract_fx}

    def _extract_model(self):
        """Extract method for model category"""
        _file_path = self.resolve_output()
        settings = self.settings.get("Animation", {})
        frame_range = settings.get_property("frame_range")
        step = settings.get_property("step")
        _options = ";exportUVs=1;exportSkels=none;exportSkin=none;exportBlendShapes=0;exportDisplayColor=0;;exportColorSets=1;exportComponentTags=1;defaultMeshScheme=catmullClark;animation=0;eulerFilter=0;staticSingleSample=0;startTime=1;endTime=1;frameStride=1;frameSample=0.0;defaultUSDFormat=usdc;parentScope=;shadingMode=useRegistry;convertMaterialsTo=[UsdPreviewSurface,MaterialX];exportInstances=1;exportVisibility=1;mergeTransformAndShape=1;stripNamespaces=0;materialsScopeName=mtl"
        cmds.file(_file_path, force=True, type="USD Export", prompt=False, exportAll=True, options=_options)
        # cmds.mayaUSDExport(
        #     file=_file_path,
        #     exportUVs=True,
        #     exportSkels=None,
        #     exportSkin=None,
        #     exportBlendShapes=False,
        #     exportDisplayColor=False,
        #     exportColorSets=True,
        #     exportComponentTags=True,
        #     defaultMeshScheme="catmullClark",
        #     animation=False,
        #     eulerFilter=False,
        #     staticSingleSample=False,
        #     startTime=1,
        #     endTime=1,
        #     frameStride=1,
        #     frameSample=0.0,
        #     defaultUSDFormat="usdc",
        #     parentScope="",
        #     shadingMode="useRegistry",
        #     convertMaterialsTo=["UsdPreviewSurface", "MaterialX"],
        #     exportInstances=True,
        #     exportVisibility=True,
        #     mergeTransformAndShape=True,
        #     stripNamespaces=False,
        #     materialsScopeName="mtl"
        # )

    def _extract_animation(self):
        """Extract method for animation category"""
        _file_path = self.resolve_output()
        settings = self.settings.get("Animation", {})
        start_time = settings.get_property("startTime")
        end_time = settings.get_property("endTime")
        frame_stride = settings.get_property("frameStride")
        frame_sample = settings.get_property("frameSample")
        euler_filter = settings.get_property("eulerFilter")
        static_single_sample = settings.get_property("staticSingleSample")
        _options = f";exportUVs=1;exportSkels=none;exportSkin=none;exportBlendShapes=0;exportDisplayColor=0;;exportColorSets=1;exportComponentTags=1;defaultMeshScheme=catmullClark;animation=1;eulerFilter={euler_filter};staticSingleSample={static_single_sample};startTime={start_time};endTime={end_time};frameStride={frame_stride};frameSample={frame_sample};defaultUSDFormat=usdc;parentScope=;shadingMode=useRegistry;convertMaterialsTo=[UsdPreviewSurface,MaterialX];exportInstances=1;exportVisibility=1;mergeTransformAndShape=1;stripNamespaces=0;materialsScopeName=mtl"
        cmds.file(_file_path, force=True, type="USD Export", prompt=False, exportAll=True, options=_options)

    def _extract_fx(self):
        """Extract method for fx category"""
        om.MGlobal.displayWarning("Fx category is not implemented yet")
        pass

    def _extract_default(self):
        """Extract method for any non-specified category"""
        om.MGlobal.displayWarning("Default category is not implemented yet")
        pass
