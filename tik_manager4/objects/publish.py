# pylint: disable=super-with-arguments
"""Publish object module."""

import shutil

from pathlib import Path
from tik_manager4.core.settings import Settings
from tik_manager4.objects.entity import Entity
from tik_manager4.core import filelog

from tik_manager4 import dcc


LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")


class Publish(Entity):
    object_type = "publish"
    try:
        _dcc_handler = dcc.Dcc()
    except:
        _dcc_handler = None
    """Class to represent a publish.

    This class is not represented by a file. Publish-PublishVersion relationship
    is opposite of Work-WorkVersion relationship. PublishVersions have database files,
    Publishes don't.
    """

    def __init__(self, work_object):
        """Initialize the publish object."""
        super(Publish, self).__init__()
        self.work_object = work_object

        self._publish_versions = {}

    @property
    def name(self):
        """Return the name of the publish."""
        return self.work_object.name

    @property
    def publish_id(self):
        """Return the publish id of the publish."""
        return self.work_object.id

    @property
    def path(self):
        """Return the path of the publish."""
        return Path(self.work_object.path, "publish").as_posix()

    @property
    def dcc(self):
        """Return the dcc of the publish."""
        return self.work_object.dcc

    @property
    def versions(self):
        """Return the publish versions of the publish."""
        self.scan_publish_versions()
        return list(self._publish_versions.values())

    @property
    def version_count(self):
        """Return the number of publish versions."""
        # return len(list(self.versions.keys()))
        return len(self.versions)

    @property
    def state(self):
        """Return the state of the publish."""
        return self.work_object.state

    @property
    def parent_task(self):
        """Return the parent task of the publish."""
        return self.work_object.parent_task

    def reload(self):
        """Reload the publish object."""
        self.work_object.reload()
        self.scan_publish_versions()

    def omit(self):
        """Omit the work."""
        self.work_object._state = "omitted"
        self.work_object.edit_property("state", self.work_object._state)
        self.work_object.apply_settings()

    def revive(self):
        """Revive the work."""
        self.work_object._state = "working" if not self.versions else "published"
        self.work_object.edit_property("state", self.work_object._state)
        self.work_object.apply_settings()

    def get_last_version(self):
        """Return the last publish version."""
        # find the latest publish version
        _publish_version_numbers = [data.version for data in self.versions]
        return 0 if not _publish_version_numbers else max(_publish_version_numbers)

    def get_publish_data_folder(self):
        """Return the publish data folder."""
        return self.work_object.get_abs_database_path("publish", self.work_object.name)

    def get_publish_project_folder(self):
        """Return the publish scene folder."""
        return self.work_object.get_abs_project_path("publish", self.work_object.name)

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

    def get_version(self, version_number):
        """Return the publish version."""
        for version in self.versions:
            if version.version == version_number:
                return version
        return None

    def load_version(self, version_number, force=False):
        """Load the publish version."""
        # loading published files is not safe, therefore we are loading the file and immediately save it
        # as a new working version.
        version_obj = self.get_version(version_number)
        if version_obj:
            if "source" in version_obj.element_types:
                relative_path = version_obj.get_element_path("source")
                abs_path = self.get_abs_project_path(relative_path)
                suffix = Path(abs_path).suffix
                self._dcc_handler.open(abs_path, force=force)
                self.work_object.new_version(notes=f"Auto Saved from publish version {version_obj.version}", file_format=suffix)
            else:
                raise ValueError("Source element is not found in the publish version.")

    def import_version(self, version_number, element_type=None, ingestor=None):
        """Import the given version of the work to the scene."""
        if not element_type:
            raise ValueError("Element type is not given.")
        if not ingestor:
            ingestor = self._dcc_handler.ingests.get(element_type, None)
        version_obj = self.get_version(version_number)
        if version_obj:
            relative_path = version_obj.get_element_path(element_type)
            abs_path = self.get_abs_project_path(relative_path)
            _func = self._dcc_handler.ingests.get(ingestor, None)
            if not _func:
                raise ValueError(f"Element type not supported: {element_type}")
            _import_obj = _func()
            _import_obj.category = self.work_object.category
            _import_obj.ingest_path = abs_path # This path can be a folder if its a bundled type.
            _import_obj.bring_in()

    def reference_version(self, version_number, element_type=None, ingestor=None):
        """Reference the given version of the work to the scene."""
        if not element_type:
            raise ValueError("Element type is not given.")
        if not ingestor:
            ingestor = self._dcc_handler.ingests.get(element_type, None)
        version_obj = self.get_version(version_number)
        if version_obj:
            relative_path = version_obj.get_element_path(element_type)
            abs_path = self.get_abs_project_path(relative_path)
            _func = self._dcc_handler.ingests.get(ingestor, None)
            if not _func:
                raise ValueError(f"Element type not supported: {element_type}")
            _import_obj = _func()
            _import_obj.category = self.work_object.category
            _import_obj.ingest_path = abs_path
            _import_obj.reference()

    def check_destroy_permissions(self):
        """Shortcut and wrapper for the check_permissions method."""
        if self.check_permissions(level=3) == -1:
            return False, "Only Admins can delete publishes."
        return True, ""
    def destroy(self):
        """Delete ALL PUBLISHES of the work.

        Use with caution.
        """
        state, msg = self.check_destroy_permissions()
        if not state:
            LOG.warning(msg)
            return -1

        # move the whole publish folder to purgatory
        _purgatory_path = Path(self.work_object.get_purgatory_project_path(), "publish")
        _purgatory_path.mkdir(parents=True, exist_ok=True)
        shutil.move(self.get_publish_project_folder(), str(_purgatory_path / self.work_object.name), copy_function=shutil.copytree)

        # move the database files to purgatory
        _purgatory_db_path = Path(self.work_object.get_purgatory_database_path(), "publish")
        _purgatory_db_path.mkdir(parents=True, exist_ok=True)
        shutil.move(self.get_publish_data_folder(), str(_purgatory_db_path / self.work_object.name), copy_function=shutil.copytree)

        # clear the publish versions
        self._publish_versions = {}
        return 1

    def check_delete_version_permissions(self, version_number):
        """Shortcut and wrapper for the check_permissions method."""
        if self.check_permissions(level=3) == -1:
            return False, "Only Admins can delete publishes."
        return True, ""

    def delete_version(self, version_number):
        """Delete the given publish version."""
        state, msg = self.check_delete_version_permissions(version_number)
        if not state:
            LOG.warning(msg)
            return -1

        version_obj = self.get_version(version_number)
        if version_obj:
            for element in version_obj.elements:
                relative_path = element["path"]
                source_abs_path = version_obj.get_abs_project_path(relative_path)
                dest_abs_path = version_obj.get_purgatory_project_path(relative_path)
                Path(dest_abs_path).parent.mkdir(parents=True, exist_ok=True)
                shutil.move(source_abs_path, dest_abs_path, copy_function=shutil.copytree)

            # move the thumbnail to purgatory
            thumbnail_relative_path = version_obj.get("thumbnail", None)
            if thumbnail_relative_path:
                thumbnail_abs_path = version_obj.get_abs_database_path(thumbnail_relative_path)
                thumbnail_dest_abs_path = version_obj.get_purgatory_database_path(thumbnail_relative_path)
                Path(thumbnail_dest_abs_path).parent.mkdir(parents=True, exist_ok=True)
                shutil.move(thumbnail_abs_path, thumbnail_dest_abs_path, copy_function=shutil.copytree)

            # move the database file to purgatory
            _file_name = Path(version_obj.settings_file).name
            dest_abs_file_path = version_obj.get_purgatory_database_path(version_obj.name, _file_name)
            Path(dest_abs_file_path).parent.mkdir(parents=True, exist_ok=True)
            shutil.move(version_obj.settings_file, dest_abs_file_path, copy_function=shutil.copytree)

            # remove the publish version from the publish versions
            self._publish_versions.pop(version_obj.settings_file)
            return 1
        else:
            return -1

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
        self._version = self.get_property("version_number", self._version)
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

    @property
    def element_types(self):
        """Return the element types of the publish."""
        return [element["type"] for element in self.elements]

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

    def get_element_path(self, element_type):
        """Return the element path of the given element type."""
        for element in self.elements:
            if element["type"] == element_type:
                return element["path"]
        return None

    def get_element_suffix(self, element_type):
        """Return the element suffix of the given element type."""
        for element in self.elements:
            if element["type"] == element_type:
                return element["suffix"]
        return None

    def is_element_bundled(self, element_type):
        """Return if the element is bundled or not."""
        for element in self.elements:
            if element["type"] == element_type:
                return element.get("bundled", False)
        return None
