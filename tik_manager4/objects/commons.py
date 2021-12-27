import os
import shutil
from tik_manager4.core.settings import Settings
from tik_manager4 import defaults


class Commons(object):
    def __init__(self, folder_path):
        super(Commons, self).__init__()

        self._folder_path = folder_path

        self.exportSettings = None
        self.importSettings = None
        self.manager = None
        self.users = None
        self.template = None

        self._validate_commons_folder()

    def _validate_commons_folder(self):
        """Makes sure the commons folder contains the necessary setting files"""
        for default_file in defaults.all:
            base_name = os.path.basename(default_file)
            common_file = os.path.join(self._folder_path, base_name)
            if not os.path.isfile(common_file):
                shutil.copy(default_file, common_file)

        self.exportSettings = Settings(file_path=os.path.join(self._folder_path, "exportSettings.json"))
        self.importSettings = Settings(file_path=os.path.join(self._folder_path, "importSettings.json"))
        self.manager = Settings(file_path=os.path.join(self._folder_path, "manager.json"))
        self.users = Settings(file_path=os.path.join(self._folder_path, "users.json"))
        self.template = Settings(file_path=os.path.join(self._folder_path, "templates.json"))
