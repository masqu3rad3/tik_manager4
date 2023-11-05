import uuid
import os
from pathlib import Path
import subprocess
import platform

from tik_manager4.external import pyperclip
from tik_manager4.objects.guard import Guard
from tik_manager4.core import filelog

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")


class Entity(object):
    guard = Guard()

    def __init__(self, name="", uid=None):
        self._id = uid
        self._relative_path = ""
        self._name = name
        self.__mode = "entity"

    @property
    def id(self):
        if not self._id:
            self._id = self.generate_id()
        return self._id

    @id.setter
    def id(self, val):
        self._id = val

    @property
    def path(self):
        return str(Path(self._relative_path).as_posix())

    @path.setter
    def path(self, val):
        self._relative_path = val

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        self._name = val

    @property
    def permission_level(self):
        return self.guard.permission_level

    @property
    def is_authenticated(self):
        return self.guard.is_authenticated

    @staticmethod
    def generate_id():
        return uuid.uuid1().time_low

    def check_permissions(self, level):
        """Checks the user permissions for project actions."""
        if self.permission_level < level:
            LOG.warning("This user does not have permissions for this action")
            return -1

        if not self.is_authenticated:
            LOG.warning("User is not authenticated")
            return -1
        return 1

    def get_abs_database_path(self, *args):
        return str(Path(self.guard.database_root, self.path, *args))

    def get_abs_project_path(self, *args):
        return str(Path(self.guard.project_root, self.path, *args))

    def get_purgatory_project_path(self, *args):
        return str(Path(self.guard.project_root, "__purgatory", self.path, *args))

    def get_purgatory_database_path(self, *args):
        return str(Path(self.guard.project_root, "__purgatory", "tikDatabase",  self.path, *args))

    @staticmethod
    def _open_folder(target):
        """Open the path in Windows Explorer(Windows) or Nautilus(Linux)."""
        if Path(target).is_file():
            target = Path(target).stem
        if platform.system() == "Windows":
            os.startfile(target)
        elif platform.system() == "Linux":
            subprocess.Popen(["xdg-open", target])
        else:
            subprocess.Popen(["open", target])


    def copy_path_to_clipboard(self, file_or_folder_path):
        """Copy the path to the clipboard."""
        pyperclip.copy(file_or_folder_path)

    def show_project_folder(self):
        """Open the path in Windows Explorer(Windows) or Nautilus(Linux)"""
        self._open_folder(self.get_abs_project_path())

    def show_database_folder(self):
        """Open the database path in Windows Explorer(Windows) or Nautilus(Linux)."""
        self._open_folder(self.get_abs_database_path())
