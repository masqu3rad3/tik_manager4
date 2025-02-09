"""Gate keeper of heavens and earth."""

from pathlib import Path
import shutil

class Purgatory(object):
    """Purgatory is the place where all entities go to be deleted."""

    def __init__(self, main_object):
        super().__init__()
        self.main = main_object

    def purge_origin(self):
        """Purge all the entities in origin project purgatory"""
        purgatory_folder = Path(self.main.project.absolute_path) / ".purgatory"
        if not purgatory_folder.exists():
            return True, "Origin Project Purgatory already empty."
        # delete the purgatory folder
        try:
            shutil.rmtree(purgatory_folder)
        except Exception as exc:
            return False, f"Error purging purgatory: {exc}"
        return True, "Origin Purgatory purged successfully."

    def purge_local(self):
        """Purge all the entities in local project purgatory"""
        local_cache_folder = self.main.user.localization.get(
            "local_cache_folder", None)
        if not local_cache_folder:
            return False, "Local cache folder not set."
        purgatory_folder = Path(
            local_cache_folder) / self.main.project.name / ".purgatory"
        if not purgatory_folder.exists():
            return True, "Local Project Purgatory already empty."
        # delete the purgatory folder
        try:
            shutil.rmtree(purgatory_folder)
        except Exception as exc:
            return False, f"Error purging purgatory: {exc}"
        return True, "Local Purgatory purged successfully."

    # TODO: Implement move to and from purgatory functions here with clean feedbacks.
