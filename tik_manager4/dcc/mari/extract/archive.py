"""Archive the Mari Project."""

import mari

from tik_manager4.dcc.extract_core import ExtractCore


class Archive(ExtractCore):
    """Archive the Mari Project."""

    nice_name = "Archive Mari Project"
    color = (255, 255, 255)
    def __init__(self):
        super(Archive, self).__init__()

        self.extension = ".mra"

    def _extract_default(self):
        """Extract method for any non-specified category"""
        _file_path = self.resolve_output()
        project = mari.projects.current()
        if not project:
            raise RuntimeError("No Mari project is open. You need to be in a project to save it.")
        uuid = project.uuid()
        project.save()
        project.close()
        mari.projects.archive(uuid, _file_path)
        mari.projects.open(uuid)