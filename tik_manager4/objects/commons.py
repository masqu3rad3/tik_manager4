from pathlib import Path
import shutil

from tik_manager4.core.settings import Settings
from tik_manager4 import defaults


class Commons:
    """Class to handle the common settings and user data"""
    exportSettings = None
    importSettings = None
    user_defaults = None
    project_settings = None
    users = None
    template = None
    structures = None
    metadata = None

    def __init__(self, folder_path):
        super().__init__()

        self._folder_path = folder_path
        self.is_valid = self._validate_commons_folder()

    def _validate_commons_folder(self):
        """Makes sure the 'commons folder' contains the necessary setting files"""
        # copy the default template files to common folder
        for default_file in defaults.all:
            _default_file_path = Path(default_file)
            base_name = _default_file_path.name
            _common_file_path = Path(self._folder_path, base_name)
            if not _common_file_path.is_file():
                try:
                    shutil.copy(default_file, str(_common_file_path))
                except PermissionError:
                    return False

        self.category_definitions = Settings(
            file_path=str(Path(self._folder_path, "category_definitions.json"))
        )
        self.user_defaults = Settings(
            file_path=str(Path(self._folder_path, "user_defaults.json"))
        )
        self.project_settings = Settings(
            file_path=str(Path(self._folder_path, "project_settings.json"))
        )
        self.preview_settings = Settings(
            file_path=str(Path(self._folder_path, "preview_settings.json"))
        )
        self.users = Settings(
            file_path=str(Path(self._folder_path, "users.json"))
        )
        self.template = Settings(
            file_path=str(Path(self._folder_path, "templates.json"))
        )
        self.structures = Settings(
            file_path=str(Path(self._folder_path, "structures.json"))
        )
        self.metadata = Settings(
            file_path=str(Path(self._folder_path, "metadata.json"))
        )

        return True

    def check_user_permission_level(self, user_name):
        """Returns the permission level for given user"""
        return self.users.get_property(user_name).get("permissionLevel", 0)

    def get_users(self):
        """Returns the list of all active users"""
        return self.users.keys

    def get_project_structures(self):
        """Returns list of available project structures defined in defaults"""
        return self.structures.keys
