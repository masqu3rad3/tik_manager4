"""Core module for Tik Manager Objects."""

import uuid
import os
from pathlib import Path
import subprocess
import platform

from tik_manager4.external import pyperclip
from tik_manager4.objects.guard import Guard
from tik_manager4.core import filelog

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")


class Entity:
    """Base class for all Tik Manager entities."""
    guard = Guard()

    def __init__(self, name="", uid=None):
        """Initializes the Entity class.

        Args:
            name (str): The name of the entity.
            uid (int): The unique id of the entity.
        """
        self._id = uid
        self._relative_path = ""
        self._name = name
        self.__mode = "entity"

    @property
    def id(self):
        """Return the unique id of the entity."""
        if not self._id:
            self._id = self.generate_id()
        return self._id

    @id.setter
    def id(self, val):
        """Set the unique id of the entity."""
        self._id = val

    @property
    def path(self):
        """Return the relative path of the entity."""
        return str(Path(self._relative_path).as_posix())

    @path.setter
    def path(self, val):
        """Set the relative path of the entity."""
        self._relative_path = val

    @property
    def name(self):
        """Return the name of the entity."""
        return self._name

    @name.setter
    def name(self, val):
        """Set the name of the entity."""
        self._name = val

    @property
    def permission_level(self):
        """Return the permission level of the user."""
        return self.guard.permission_level

    @property
    def is_authenticated(self):
        """Return the authentication status of the user."""
        return self.guard.is_authenticated

    @staticmethod
    def generate_id():
        """Generate a unique id for the entity."""
        return uuid.uuid1().time_low

    def check_permissions(self, level):
        """Check the user permissions for project actions.

        Args:
            level (int): The permission level required for the action.

        Returns:
            int: 1 if the user has permissions, -1 otherwise.
        """
        if self.permission_level < level:
            LOG.warning("This user does not have permissions for this action")
            return -1

        if not self.is_authenticated:
            LOG.warning("User is not authenticated")
            return -1
        return 1

    def get_abs_database_path(self, *args):
        """Return the absolute database path for the entity.

        Args:
            args (str): The path arguments.
                Any values passed here will be appended to the path.
        """
        return str(Path(self.guard.database_root, self.path, *args))

    def get_abs_project_path(self, *args):
        """Return the absolute project path for the entity.

        Args:
            args (str): The path arguments.
                Any values passed here will be appended to the path.
        """
        return str(Path(self.guard.project_root, self.path, *args))

    def get_purgatory_project_path(self, *args):
        """Return the purgatory project path for the entity.

        Args:
            args (str): The path arguments.
                Any values passed here will be appended to the path.
        """
        return str(Path(self.guard.project_root, ".purgatory", self.path, *args))

    def get_purgatory_database_path(self, *args):
        """Return the purgatory database path for the entity.

        Args:
            args (str): The path arguments.
                Any values passed here will be appended to the path.
        """
        return str(Path(self.guard.project_root, ".purgatory", "tikDatabase",  self.path, *args))

    @staticmethod
    def _open_folder(target):
        """Open the path in Windows Explorer(Windows) or Nautilus(Linux).

        Args:
            target (str): The path to open.
        """
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

    def get_metadata(self, parent_task, key=None):
        """Convenience method to get the metadata for work and category objects."""

        if not parent_task:
            return None
        if key:
            return parent_task.metadata.get_value(key, None)
        return parent_task.metadata

        # parent_sub = parent_task.parent_sub
        # if not parent_sub:
        #     return None
        # if key:
        #     return parent_sub.metadata.get_value(key, None)
        # return parent_sub.metadata
