# import hashlib
import os
import shutil

from tik_manager4.core import filelog
from tik_manager4.core.settings import Settings
from tik_manager4 import defaults

log = filelog.Filelog(logname=__name__, filename="tik_manager4")


class Commons(object):
    exportSettings = None
    importSettings = None
    # manager = None
    user_settings = None
    project_settings = None
    users = None
    template = None
    structures = None
    metadata = None

    def __init__(self, folder_path):
        super(Commons, self).__init__()

        self._folder_path = folder_path
        self._validate_commons_folder()

    def _validate_commons_folder(self):
        """Makes sure the 'commons folder' contains the necessary setting files"""
        # copy the default template files to common folder
        for default_file in defaults.all:
            base_name = os.path.basename(default_file)
            common_file = os.path.join(self._folder_path, base_name)
            if not os.path.isfile(common_file):
                shutil.copy(default_file, common_file)

        self.exportSettings = Settings(file_path=os.path.join(self._folder_path, "exportSettings.json"))
        self.importSettings = Settings(file_path=os.path.join(self._folder_path, "importSettings.json"))
        self.category_definitions = Settings(file_path=os.path.join(self._folder_path, "category_definitions.json"))
        self.user_settings = Settings(file_path=os.path.join(self._folder_path, "user_settings.json"))
        self.project_settings = Settings(file_path=os.path.join(self._folder_path, "project_settings.json"))
        self.users = Settings(file_path=os.path.join(self._folder_path, "users.json"))
        self.template = Settings(file_path=os.path.join(self._folder_path, "templates.json"))
        self.structures = Settings(file_path=os.path.join(self._folder_path, "structures.json"))
        self.metadata = Settings(file_path=os.path.join(self._folder_path, "metadata.json"))

    def check_user_permission_level(self, user_name):
        """Returns the permission level for given user"""
        return self.users.get_property(user_name).get("permissionLevel", 0)

    def get_users(self):
        """Returns the list of all active users"""
        return self.users.keys

    def get_project_structures(self):
        """Returns list of available project structures defined in defaults"""
        return self.structures.keys
