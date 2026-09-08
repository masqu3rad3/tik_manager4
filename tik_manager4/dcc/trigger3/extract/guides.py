"""Extract the guides as a .trg library file."""

import shutil
from pathlib import Path

from tik_manager4.dcc.extract_core import ExtractCore
from tik_manager4.dcc.trigger3._host import export_guides, host


class Guides(ExtractCore):
    """The session's guides as a ``.trg``."""

    nice_name = "Guides"
    color = (212, 176, 74)

    def __init__(self):
        super().__init__()
        self.extension = ".trg"
        self.publish_set = None

    def set_publish_set(self, publish_set):
        """Use a set the publish action already built instead of exporting."""
        self.publish_set = publish_set

    def _extract_default(self):
        target = Path(self.resolve_output())
        if self.publish_set is not None:
            guides = next(
                (
                    item
                    for item in self.publish_set.artifacts
                    if item.kind == "guides"
                ),
                None,
            )
            if guides is None:
                raise RuntimeError("The publish set carries no guides.")
            shutil.copy2(guides.path, target)
            return
        session = host().session
        if session is None:
            raise RuntimeError("No Trigger session to export guides from.")
        export_guides(session, target)
