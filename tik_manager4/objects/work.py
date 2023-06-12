# pylint: disable=super-with-arguments
# pylint: disable=consider-using-f-string
import os
import socket
from tik_manager4.core.settings import Settings
from tik_manager4.objects.entity import Entity
from tik_manager4 import dcc


class Work(Settings, Entity):
    _dcc_handler = dcc.Dcc()

    def __init__(self, absolute_path,
                 name=None,
                 path=None
                 ):
        super(Work, self).__init__()
        self.settings_file = absolute_path

        self._name = self.get_property("name") or name
        self._creator = self.get_property("creator") or self.guard.user
        self._category = self.get_property("category") or None
        self._dcc = self.get_property("dcc") or self.guard.dcc
        self._versions = self.get_property("versions") or []
        self._work_id = self.get_property("work_id") or self._id
        self._relative_path = self.get_property("path") or path
        self._software_version = self.get_property("softwareVersion") or None
        self.modified_time = None  # to compare and update if necessary

        self._publishes = {}

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
    def version_count(self):
        """Return the number of versions."""
        return len(self._versions)

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

        # validate file format
        file_format = file_format or self._dcc_handler.formats[0]
        if file_format not in self._dcc_handler.formats:
            raise ValueError("File format is not valid.")

        # get filepath of current version
        _version_number = self.get_last_version() + 1
        _version_name = "{0}_{1}_v{2}{3}".format(self._name, self._creator,
                                                 str(_version_number).zfill(3),
                                                 file_format)
        _abs_version_path = self.get_abs_project_path(_version_name)
        _thumbnail_name = "{0}_{1}_v{2}_thumbnail.jpg".format(self._name, self._creator,
                                                              str(_version_number).zfill(3))
        _thumbnail_path = self.get_abs_database_path("thumbnails", _thumbnail_name)
        self._io.folder_check(_abs_version_path)

        # save the file
        self._dcc_handler.save_as(_abs_version_path)

        # generate thumbnail
        self._dcc_handler.generate_thumbnail(_thumbnail_path, 100, 100)

        # add it to the versions
        _version = {
            "version_number": _version_number,
            "workstation": socket.gethostname(),
            "notes": notes,
            # "thumbnail": os.path.join(self._relative_path, "thumbnails", _thumbnail_name).replace("\\", "/"),
            "thumbnail": os.path.join("thumbnails", _thumbnail_name).replace("\\", "/"),
            # "scene_path": os.path.join(self._relative_path, _version_name).replace("\\", "/"),
            "scene_path": os.path.join("", _version_name).replace("\\", "/"),
            "user": self.guard.user,
            "preview": "",
        }
        self._versions.append(_version)
        self.edit_property("versions", self._versions)
        self.apply_settings(force=True)
    def make_publish(self):
        """Create a publish from the currently loaded version on DCC."""
        pass