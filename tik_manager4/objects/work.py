# pylint: disable=super-with-arguments
# pylint: disable=consider-using-f-string
import os
import socket
from tik_manager4.core.settings import Settings
from tik_manager4.objects.entity import Entity
from tik_manager4 import dcc


class Work(Settings, Entity):
    _dcc_handler = dcc.Dcc()

    def __init__(self, absolute_path, name=None, path=None):
        super(Work, self).__init__()
        self.settings_file = absolute_path

        self._name = self.get_property("name") or name
        self._creator = self.get_property("creator") or self.guard.user
        self._category = self.get_property("category") or None
        self._dcc = self.get_property("dcc") or self.guard.dcc
        self._versions = self.get_property("versions") or []
        self._work_id = self.get_property("work_id") or self._id
        self._task_name = self.get_property("task_name") or None
        self._task_id = self.get_property("task_id") or None
        self._relative_path = self.get_property("path") or path
        self._software_version = self.get_property("softwareVersion") or None
        # there are 3 states: working, published, omitted
        self._state = self.get_property("state") or "working"
        self.modified_time = None  # to compare and update if necessary

        self._publishes = {}

    @property
    def state(self):
        return self._state

    @property
    def dcc(self):
        return self._dcc

    @property
    def id(self):
        return self._work_id

    @property
    def creator(self):
        return self._creator

    @property
    def publishes(self):
        return self._publishes

    @property
    def versions(self):
        return self._versions

    @property
    def version_count(self):
        """Return the number of versions."""
        return len(self._versions)

    def reload(self):
        """Reload from file"""
        self.__init__(self.settings_file)

    def omit_work(self):
        """Omit the work."""
        self._state = "omitted"
        self.edit_property("state", self._state)
        self.apply_settings()

    def revive_work(self):
        """Revive the work."""
        self._state = "working" if not self.publishes else "published"
        self.edit_property("state", self._state)
        self.apply_settings()

    def get_last_version(self):
        """Return the last version of the work."""
        # First try to get last version from the versions list. If not found, return 0.
        if self._versions:
            return self._versions[-1].get("version_number", self.version_count)
        else:
            return 0

    def get_version(self, version_number):
        """Return the version dictionary by version number."""
        for version in self._versions:
            if version.get("version_number") == version_number:
                return version

    def new_version(self, file_format=None, notes=""):
        """Create a new version of the work."""

        state = self.check_permissions(level=1)
        if state != 1:
            return -1

        # validate file format
        file_format = file_format or self._dcc_handler.formats[0]
        if file_format not in self._dcc_handler.formats:
            raise ValueError("File format is not valid.")

        # get filepath of current version
        _version_number, _version_name, _thumbnail_name = self.construct_names(
            file_format
        )

        _abs_version_path = self.get_abs_project_path(_version_name)
        _thumbnail_path = self.get_abs_database_path("thumbnails", _thumbnail_name)
        self._io.folder_check(_abs_version_path)

        # save the file
        self._dcc_handler.save_as(_abs_version_path)

        # generate thumbnail
        # create the thumbnail folder if it doesn't exist
        self._io.folder_check(_thumbnail_path)
        self._dcc_handler.generate_thumbnail(_thumbnail_path, 100, 100)

        # add it to the versions
        _version = {
            "version_number": _version_number,
            "workstation": socket.gethostname(),
            "notes": notes,
            "thumbnail": os.path.join("thumbnails", _thumbnail_name).replace("\\", "/"),
            "scene_path": os.path.join("", _version_name).replace("\\", "/"),
            "user": self.guard.user,
            "preview": "",
        }
        self._versions.append(_version)
        self.edit_property("versions", self._versions)
        self.apply_settings(force=True)
        return _version

    def make_publish(self, notes, elements=None):
        """Create a publish from the currently loaded version on DCC."""

        # valid file_format keyword can be collected from main.dcc.formats
        state = self.check_permissions(level=1)
        if state != 1:
            return -1

    def construct_names(self, file_format):
        """Construct a name for the work version.

        Args:
            extension (str): The extension of the file.
            file_format (str): The file format of the file.

        """
        version_number = self.get_last_version() + 1
        version_name = f"{self._name}_v{version_number:03d}{file_format}"
        # version_name = "{0}_{1}_v{2}{3}".format(
        #     self._name, self._creator, str(version_number).zfill(3), file_format
        # )
        thumbnail_name = f"{self._name}_v{version_number:03d}_thumbnail.jpg"
        # thumbnail_name = "{0}_{1}_v{2}_thumbnail.jpg".format(
        #     self._name, self._creator, str(version_number).zfill(3)
        # )
        return version_number, version_name, thumbnail_name

    def load_version(self, version_number):
        """Load the given version of the work."""
        version_obj = self.get_version(version_number)
        if version_obj:
            relative_path = version_obj.get("scene_path")
            abs_path = self.get_abs_project_path(relative_path)
            self._dcc_handler.open(abs_path)

    def import_version(self, version_number):
        """Import the given version of the work to the scene."""
        version_obj = self.get_version(version_number)
        if version_obj:
            relative_path = version_obj.get("scene_path")
            abs_path = self.get_abs_project_path(relative_path)
            self._dcc_handler.import_file(abs_path)

    def delete_work(self):
        """Delete the work."""
        # TODO: implement this. This should move the work to the purgatory.
        pass
