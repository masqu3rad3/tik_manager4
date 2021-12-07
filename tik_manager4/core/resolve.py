import os

import tik_manager4.dcc as source
from tik_manager4.core import io
from tik_manager4.core import settings

class Database(object):
    def __init__(self):
        super(Database, self).__init__()

        self._user_dir = self._get_user_dir()
        # self._user_settings = io.IO(file_path=os.path.join(self._user_dir, "settings.json"))
        self._user_settings = settings.Settings(file_path=os.path.join(self._user_dir, "userSettings.json"))
        self._user_states = io.IO(file_path=os.path.join(self._user_dir, "states.json"))
        # self._user_states = settings.Settings(file_path=os.path.join(self._user_dir, "states.json"))

        self._common_dir = None
        self._project_dir = None

        self._user_settings_file = None
        self._user_projects_file = None
        self._user_states_file = None


    def _get_user_dir(self):
        """Returns Documents Directory"""
        dir = os.path.expanduser('~')
        if not "Documents" in dir:
            dir = os.path.join(dir, "Documents")
        tik_manager4_folder = os.path.normpath(os.path.join(dir, "TikManager4"))
        self.io.folder_check(tik_manager4_folder)

        return tik_manager4_folder

    @property
    def user_settings(self):
        return self._user_settings.read()

    @user_settings.setter
    def user_settings(self, data):
        self._user_settings.write(data=data)



































    #
    # @property
    # def user_directory(self):
    #     return self._user_dir
    #
    # @property
    # def common_directory(self):
    #     return self._common_dir
    #
    # @common_directory.setter
    # def common_directory(self, common_dir):
    #
    #
    #
    #
    #
    # def _get_common_dir(self):
    #     common_folder_file = os.path.join(self._user_dir,
    #
    # def _getCommonFolder(self):
    #     """prompts input for the common folder"""
    # if os.path.isfile(self._pathsDict["commonFolderFile"]):
    #     commonFolder = self._loadJson(self._pathsDict["commonFolderFile"])
    #     if commonFolder == -2:
    #         return -2
    # else:
    #     msg = "Common Folder is not defined.\n\nDo you want to define now?"
    #     if self._question(msg):
    #         commonFolder = self._defineCommonFolder()
    #     else:
    #         return -1
    # return commonFolder
    #
    # @property
    # def dcc(self):
    #     return source.dcc.NAME
    #
    # @staticmethod
    # def _folderCheck(folder):
    #     if not os.path.isdir(os.path.normpath(folder)):
    #         os.makedirs(os.path.normpath(folder))
    #     return folder
