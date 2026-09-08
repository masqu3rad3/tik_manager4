"""Extract the built rig as a Maya binary scene."""

import shutil
from pathlib import Path

from tik_manager4.dcc.extract_core import ExtractCore
from tik_manager4.dcc.trigger3._host import host


class Rig(ExtractCore):
    """The rig scene: copied from the publish set, or built and saved."""

    nice_name = "Rig"
    color = (0, 50, 255)

    def __init__(self):
        super().__init__()
        self.extension = ".mb"
        self.publish_set = None

    def set_publish_set(self, publish_set):
        """Use a set the publish action already built instead of building."""
        self.publish_set = publish_set

    def _extract_default(self):
        target = Path(self.resolve_output())
        if self.publish_set is not None:
            rig = next(
                (item for item in self.publish_set.artifacts if item.kind == "rig"),
                None,
            )
            if rig is None:
                raise RuntimeError("The publish set carries no rig.")
            shutil.copy2(rig.path, target)
            return
        from maya import cmds

        session = host().session
        if session is None:
            raise RuntimeError("No Trigger session to build.")
        session.build()
        original = cmds.file(query=True, sceneName=True) or ""
        cmds.file(rename=str(target))
        try:
            cmds.file(save=True, type="mayaBinary", force=True)
        finally:
            cmds.file(rename=original)
