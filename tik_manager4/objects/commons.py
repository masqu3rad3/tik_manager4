import hashlib
import os
import shutil

from tik_manager4.core import filelog
from tik_manager4.core.settings import Settings
from tik_manager4 import defaults

log = filelog.Filelog(logname=__name__, filename="tik_manager4")


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

    def __hash_pass(self, password):
        """Hashes the password"""
        return hashlib.sha1(str(password).encode('utf-8')).hexdigest()

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

    def create_user(self, user_name, initials, password, permission_level):
        """Creates a new user and stores it in database"""
        if user_name in self.users.keys():
            return -1, log.error("User %s already exists. Aborting" % user_name)
        user_data = {
            "initials": initials,
            "pass": self.__hash_pass(password),
            "permissionLevel": permission_level
        }
        self.users.add_property(user_name, user_data)
        self.users.apply_settings()

    def delete_user(self, user_name):
        """Removes the user from database"""
        if user_name in self.users.keys():
            return -1, log.error("%s does not exist. Aborting" % user_name)
        self.users.delete_property(user_name)
        self.users.apply_settings()

    def change_user_password(self, user_name, old_password, new_password):
        """Changes the user password"""
        if self.__hash_pass(old_password) == self.users.get_property(user_name).get("pass"):
            self.users.get_property(user_name)["pass"] = self.__hash_pass(new_password)
            self.users.apply_settings()
        else:
            return -1, log.error("Old password for %s does not match" %user_name)
        pass

    def check_password(self, user_name, password):
        """checks the given password against the hashed password"""
        hashed_pass = self.__hash_pass(password)
        if self.users.get_property(user_name).get("pass", "") == hashed_pass:
            return True
        else:
            return False
