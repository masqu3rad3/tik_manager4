"""Mixin for localizing files and folders"""

from pathlib import Path

from tik_manager4.core import utils
from tik_manager4.core.constants import ObjectType
from tik_manager4.objects.entity import Entity

from tik_manager4.core import filelog

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")

class LocalizeMixin(Entity):
    """Localize mixin for Works and Publishes."""
    def __init__(self):
        """Initialize LocalizeMixin."""
        super().__init__()
        self._localized: bool = False
        self._localized_path: str = ""
        self._elements = []

    @property
    def localized(self):
        """The localization status of the work version."""
        return self._localized

    @property
    def localized_path(self):
        """The localized path of the work version."""
        return self._localized_path

    def get_output_path(self, *args):
        """Decide the output path for the entity.

        This depends on the localization settings.
        """
        if not self.can_localize():
            return self.get_abs_project_path(*args)

        localized_path_obj = self.get_localized_path(*args, return_str=False)
        try:
            localized_path_obj.parent.mkdir(parents=True, exist_ok=True)
        except PermissionError as exc:
            LOG.error(f"No write permissions to the local cache folder: {self.guard.localize_settings.get('local_cache_folder')}")
            return None
        except Exception as exc:
            LOG.error(f"An error occured: {exc}")
            return None
        return localized_path_obj.as_posix()


    def get_localized_path(self, *args, return_str=True):
        """Return the localized path for the entity.

        Args:
            args (str): The path arguments.
                Any values passed here will be appended to the path.
            return_str (bool): Return the string path instead of the Path object.
        """
        local_folder = self.guard.localize_settings.get("local_cache_folder")
        if not local_folder:
            LOG.error("Local cache folder not set.")
            return None
        project_name = Path(self.guard.project_root).name
        localized_path = Path(local_folder, project_name, self.path, *args)
        if return_str:
            return str(localized_path)
        return localized_path

    def can_localize(self):
        """Check if the entity can be localized."""
        if not self.guard.localize_settings.get("enabled"):
            return False
        pairing = {
            ObjectType.WORK: self.guard.localize_settings.get("cache_works", True),
            ObjectType.WORK_VERSION: self.guard.localize_settings.get("cache_works", True),
            ObjectType.PUBLISH: self.guard.localize_settings.get("cache_publishes", False),
            ObjectType.PUBLISH_VERSION: self.guard.localize_settings.get("cache_publishes", False),
        }
        return pairing.get(self.object_type)

    def get_resolved_path(self, *args):
        """Return the path to the entity.

        If the entity is localized, return the localized path.
        """
        if self.localized:
            return self.localized_path
        return self.get_abs_project_path(*args)

    def get_resolved_purgatory_path(self, *args):
        """Return the path to the purgatory entity.

        If the entity is localized, return the localized purgatory path.
        """
        if self.localized:
            local_folder = self.guard.localize_settings.get(
                "local_cache_folder")
            project_name = Path(self.guard.project_root).name
            localized_purgatory_path = Path(local_folder, project_name, ".purgatory", self.path, *args)
            return localized_purgatory_path.as_posix()
        return self.get_purgatory_project_path(*args)

    def show_project_folder(self):
        """Override the show_project_folder method to resolve the local or project path."""
        file_path = Path(self.get_resolved_path())
        if file_path.is_file():
            self._open_folder(file_path.parent.as_posix())
        else:
            self._open_folder(file_path.as_posix())

    def show_database_folder(self):
        """Override the show_database_folder method to resolve the local or database path."""
        if self.object_type in (
        ObjectType.WORK_VERSION, ObjectType.PUBLISH_VERSION):
            file_path = Path(self.get_abs_database_path())
            # open two folder up
            self._open_folder(file_path.parent.parent.as_posix())
        else:
            super().show_database_folder()

    def sync(self):
        """Sync the entity to the origin.

        This will copy the entity to the origin path. Sync is single direction.
        """
        if not self.localized:
            LOG.error("Entity is not localized.")
            return False
        LOG.info("Syncing...")
        if self.object_type == ObjectType.WORK_VERSION:
            ret, msg = utils.move(self.localized_path,  self.get_abs_project_path(), force=False)
            if not ret:
                return False, msg
            self._localized = False
            self._localized_path = ""
        elif self.object_type == ObjectType.PUBLISH_VERSION:
            # before moving, validate all paths
            publish_base = Path(self.localized_path)
            sources = [publish_base / el["path"] for el in
                       self._elements]
            targets = [Path(self.get_abs_project_path(el["path"])) for el in
                       self._elements]
            list_of_errors = list(self.validate_paths(sources, targets))
            if list_of_errors:
                return False, list_of_errors

            for source, target in zip(sources, targets):
                ret, msg = utils.move(source.as_posix(), target.as_posix(), force=False)
                if not ret:
                    return False, msg
            self._localized = False
            self.edit_property("localized", False)
            self._localized_path = ""
            self.edit_property("localized_path", "")
            self.apply_settings(force=True)
        else:
            msg = f"Syncing is not supported for {self.object_type.value}."
            LOG.error(msg)
            return False, msg
        return True, "Sync successful."

    # A helper function to validate paths before attempting the actual move
    def validate_paths(self, sources, targets):
        """Validate that all source files exist and can be moved to target locations."""
        for src, tgt in zip(sources, targets):
            if not src.exists():
                msg = f"Source path does not exist: {src.as_posix()}"
                LOG.error(msg)
                yield msg
            if tgt.exists():
                msg = f"Target path already exists: {tgt.as_posix()}. Origin cannot be overwritten."
                LOG.warning(msg)
                yield msg
