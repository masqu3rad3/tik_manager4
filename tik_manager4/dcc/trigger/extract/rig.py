"""Extract the rig."""

import trigger.version_control.api as trigger

from maya import cmds
from tik_manager4.dcc.extract_core import ExtractCore

class Rig(ExtractCore):
    """Extract the rig as Maya scene."""

    nice_name = "Rig"
    color = (0, 50, 255)

    def __init__(self):
        super(Rig, self).__init__()

        self.extension = ".mb"

        self.trigger_api = trigger.ApiHandler()

    def _extract_default(self):
        """Extract method for any non-specified category"""
        # build the rig before extracting. right?
        self.trigger_api.build_session()
        _file_path = self.resolve_output()
        _original_path = cmds.file(query=True, sceneName=True)
        cmds.file(rename=_file_path)
        try:
            cmds.file(save=True, type="mayaBinary")
        except RuntimeError as e:
            cmds.file(rename=_original_path)
            raise RuntimeError(e)
        finally:
            cmds.file(rename=_original_path)