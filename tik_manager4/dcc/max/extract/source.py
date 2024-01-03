"""Extract 3ds Max scene."""

from pymxs import runtime as rt
from tik_manager4.dcc.extract_core import ExtractCore

# The Collector will only collect classes inherit ExtractCore
class Source(ExtractCore):
    """Extract Source Maya scene"""

    nice_name = "Source Scene"
    color = (255, 255, 255)

    def __init__(self):
        super(Source, self).__init__()
        self._extension = ".max"

    def _extract_default(self):
        """Extract method for any non-specified category"""
        _file_path = self.resolve_output()
        # file_format = "mayaAscii" if extension == ".ma" else "mayaBinary"
        rt.saveMaxFile(
            _file_path, clearNeedSaveFlag=False, useNewFile=False, quiet=True
        )
