"""Localize Module for Tik Manager."""

from pathlib import Path
# from tik_manager4.objects.guard import Guard
from tik_manager4.core import filelog

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")

class Localize:
    """Localize class for Tik Manager."""
    # guard = Guard()

    def __init__(self, guard_obj):
        """Initialize Localize class."""
        self.guard = guard_obj
        self._origin_path = None

    @property
    def origin_path(self):
        """Return original path."""
        return self._origin_path

    @origin_path.setter
    def origin_path(self, value: str):
        """Set original path."""
        self._origin_path = Path(value)

    @property
    def is_enabled(self):
        """Check if localizing is enabled."""
        return self.guard.localize_settings.get("enabled")

    @property
    def can_cache_works(self):
        """Check if caching works."""
        return self.guard.localize_settings.get("cache_works", True)

    @property
    def can_cache_previews(self):
        """Check if caching previews."""
        return self.guard.localize_settings.get("cache_previews", True)

    @property
    def can_cache_publishes(self):
        """Check if caching publishes."""
        return self.guard.localize_settings.get("cache_publishes", False)

    @property
    def can_write_to_save_path(self):
        """Check if there is write permissions to the save path."""
        pass

    @property
    def output_path(self):
        """Absolute path of where to save the file.

        Gets the local path if localizing is enabled, otherwise returns the original path.
        """
        if self.is_enabled:
            _path = self.get_local_path()
            _path.parent.mkdir(parents=True, exist_ok=True)
            return self.get_local_path().as_posix()
        return self._origin_path

    def get_local_path(self):
        """Get the local path for the file or folder"""
        if not self.is_enabled:
            return None
        if not self.guard.localize_settings.get("local_cache_folder"):
            LOG.warning("Local cache folder is not defined.")
            return None
        # get the relative path of the file
        if not self.guard.project_root:
            LOG.warning("Project root is not defined.")
            return None
        project_root = Path(self.guard.project_root)
        local_cache_folder = Path(self.guard.localize_settings.get("local_cache_folder"))
        try:
            relative_path = self._origin_path.relative_to(project_root)
        except ValueError:
            raise ValueError(f"Original path is not within the project root: {self._origin_path}")
        # get the cache path
        cache_path = local_cache_folder / project_root.name / relative_path
        # return the cache path
        return cache_path


if __name__ == "__main__":
    import tik_manager4
    tik = tik_manager4.initialize("standalone")
    localize = Localize(tik.project.guard)
    localize.origin_path = "D:\\PROJECT_AND_ARGE\\Elf_Facial_Collaboration\\Elf\\main\\Model\\Maya\\main_Model_blendshape_pack_v002.mb"

    print("returns:", localize.get_local_path())
    print("ann", localize.guard.preview_settings)