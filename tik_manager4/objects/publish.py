# pylint: disable=super-with-arguments
"""Publish object module."""

from pathlib import Path
from tik_manager4.core.settings import Settings
from tik_manager4.objects.entity import Entity
from tik_manager4 import dcc


class Publish(Entity):
    """Class to represent a publish.

    This class is not represented by a file. Publish-PublishVersion relationship
    is opposite of Work-WorkVersion relationship. PublishVersions have database files,
    Publishes don't.
    """

    def __init__(self, work_object):
        """Initialize the publish object."""
        super(Publish, self).__init__()
        self._work_object = work_object

        self._publish_versions = {}

    @property
    def name(self):
        """Return the name of the publish."""
        return self._work_object.name

    @property
    def publish_id(self):
        """Return the publish id of the publish."""
        return self._work_object.id

    @property
    def path(self):
        """Return the path of the publish."""
        return Path(self._work_object.path, "publish").as_posix()

    @property
    def dcc(self):
        """Return the dcc of the publish."""
        return self._work_object.dcc

    @property
    def versions(self):
        """Return the publish versions of the publish."""
        self.scan_publish_versions()
        return self._publish_versions

    @property
    def version_count(self):
        """Return the number of publish versions."""
        return len(list(self.versions.keys()))

    def get_last_version(self):
        """Return the last publish version."""
        # find the latest publish version
        _publish_version_numbers = [data.version for publish_path, data in self.versions.items()]
        return 0 if not _publish_version_numbers else max(_publish_version_numbers)

    def get_publish_data_folder(self):
        """Return the publish data folder."""
        return self._work_object.get_abs_database_path("publish", self._work_object.name)

    def get_publish_scene_folder(self):
        """Return the publish scene folder."""
        return self._work_object.get_abs_project_path("publish", self._work_object.name)

    def scan_publish_versions(self):
        """Get the publish versions in the publish folder."""
        # search directory is resolved from the work object
        _search_dir = Path(self.get_publish_data_folder())
        if not _search_dir.exists():
            return {}
        _publish_version_paths = _search_dir.glob("*.tpub")

        for _p_path, _p_data in dict(self._publish_versions).items():
            if _p_path not in _publish_version_paths:
                self._publish_versions.pop(_p_path)
        for _publish_version_path in _publish_version_paths:
            existing_publish = self._publish_versions.get(_publish_version_path, None)
            if not existing_publish:
                _publish = PublishVersion(_publish_version_path)
                self._publish_versions[_publish_version_path] = _publish
            else:
                if existing_publish.is_modified():
                    existing_publish.reload()

        return self._publish_versions


class PublishVersion(Settings, Entity):
    """PublishVersion object class."""
    _dcc_handler = dcc.Dcc()

    def __init__(self, absolute_path, name=None, path=None):
        """Initialize the publish version object."""
        super(PublishVersion, self).__init__()
        self.settings_file = absolute_path

        self._name = name
        self._creator = self.guard.user
        self._category = None
        self._dcc = self.guard.dcc
        self._publish_id = self._id
        self._version = 1
        self._work_version = None
        self._task_name = None
        self._task_id = None
        self._relative_path = path
        self._dcc_version = None
        self._elements = []

        self.modified_time = None  # to compare and update if necessary

        self.init_properties()

        # get the current folder path
        _folder = Path(self.settings_file).parent
        promoted_file = _folder / "promoted.json"
        self._promoted_object = Settings(promoted_file)

    def init_properties(self):
        """Initialize the properties of the publish."""
        self._name = self.get_property("name", self._name)
        self._creator = self.get_property("creator", self._creator)
        self._category = self.get_property("category", self._category)
        self._dcc = self.get_property("dcc", self._dcc)
        self._publish_id = self.get_property("publish_id", self._publish_id)
        self._version = self.get_property("version", self._version)
        self._work_version = self.get_property("work_version", self._work_version)
        self._task_name = self.get_property("task_name", self._task_name)
        self._task_id = self.get_property("task_id", self._task_id)
        self._relative_path = self.get_property("path", self._relative_path)
        self._dcc_version = self.get_property("dcc_version", self._dcc_version)
        self._elements = self.get_property("elements", self._elements)

    @property
    def creator(self):
        """Return the creator of the publish."""
        return self._creator

    @property
    def category(self):
        """Return the category of the publish."""
        return self._category

    @property
    def dcc(self):
        """Return the dcc of the publish."""
        return self._dcc

    @property
    def dcc_version(self):
        """Return the dcc version of the publish."""
        return self._dcc_version

    @property
    def publish_id(self):
        """Return the publish id of the publish."""
        return self._publish_id

    @property
    def version(self):
        """Return the version of the publish."""
        return self._version

    @property
    def task_name(self):
        """Return the task name of the publish."""
        return self._task_name

    @property
    def task_id(self):
        """Return the task id of the publish."""
        return self._task_id

    @property
    def relative_path(self):
        """Return the relative path of the publish."""
        return self._relative_path

    @property
    def software_version(self):
        """Return the software version of the publish."""
        return self._dcc_version

    @property
    def elements(self):
        """Return the elements of the publish."""
        return self._elements

    def is_promoted(self):
        """Check the 'promoted' file in the publish folder. If the content is matching with the publish id, return True"""
        _id = self._promoted_object.get_property("publish_id", default=None)
        return _id == self._publish_id

    def promote(self):
        """Promote the publish editing the promoted.json"""
        _data = {
            "publish_id": self._publish_id,
            "name": self._name,
            "path": self._relative_path,
        }
        self._promoted_object.set_data(_data)
        self._promoted_object.apply_settings()
