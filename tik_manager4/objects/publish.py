# pylint: disable=super-with-arguments
"""Publish object module."""

import shutil

from pathlib import Path
from tik_manager4.core.settings import Settings
from tik_manager4.objects.entity import Entity
from tik_manager4.core import filelog

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")


class Publish(Entity):
    object_type = "publish"
    """Class to represent a publish.

    Publish objects are created from the work objects. Publishes are the
    final versions of the works. Publishes are not editable.
    This class is not represented by a file. Publish-PublishVersion relationship
    is opposite of Work-WorkVersion relationship.
    PublishVersions have database files, publishes don't.
    """

    def __init__(self, work_object):
        """Initialize the publish object."""
        super(Publish, self).__init__()
        self._dcc_handler = work_object.guard.dcc_handler
        self.work_object = work_object

        self._publish_versions = {}

    @property
    def name(self):
        """Publish name."""
        return self.work_object.name

    @property
    def publish_id(self):
        """Return the publish id of the publish."""
        return self.work_object.id

    @property
    def path(self):
        """Relative publish path."""
        return Path(self.work_object.path, "publish").as_posix()

    @property
    def dcc(self):
        """Dcc of the publish."""
        return self.work_object.dcc

    @property
    def versions(self):
        """Versions of the publish."""
        self.scan_publish_versions()
        return list(self._publish_versions.values())

    @property
    def version_count(self):
        """Number of publish versions."""
        # return len(list(self.versions.keys()))
        return len(self.versions)

    @property
    def state(self):
        """State of the publish."""
        return self.work_object.state

    @property
    def parent_task(self):
        """Parent task of the publish."""
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
        """Return the publish versions in the publish folder."""
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
        """Return the publish version.

        Args:
            version_number (int): The version number.
        """
        for version in self.versions:
            if version.version == version_number:
                return version
        return None

    def load_version(self, version_number, force=False, element_type="source", read_only=False):
        """Load the publish version.

        Args:
            version_number (int): The version number.
            force (bool, optional): If True, loads the file without prompting
                for saving. Defaults to False.
            element_type (str, optional): The element type to load.
                Defaults to "source".
            read_only (bool, optional): Published files are write protected.
                If this argument is True, the file will be opened in
                read-only mode. If false, the file will be iterated as a new
                working version instead of opening the publish.
                Default is False.

        Raises:
            ValueError: If the element type is not found in the publish
                version.
        """
        # loading published files is not safe, therefore we are loading the file and immediately save it
        # as a new working version.
        version_obj = self.get_version(version_number)
        if version_obj:
            if element_type in version_obj.element_types:
                relative_path = version_obj.get_element_path(element_type)
                abs_path = self.get_abs_project_path(relative_path)
                suffix = Path(abs_path).suffix
                self._dcc_handler.open(abs_path, force=force)
                if not read_only:
                    self.work_object.new_version(notes=f"Auto Saved from publish version {version_obj.version}", file_format=suffix)
            else:
                raise ValueError(f"{element_type} element is not found in the publish version.")

    def import_version(self, version_number, element_type=None, ingestor=None):
        """Import the given version of the work to the scene.

        Args:
            version_number (int): The version number.
            element_type (str, optional): The element type to import.
                Defaults to None.
            ingestor (str, optional): The ingestor to use. Defaults to None.

        Raises:
            ValueError: If the element type is not given or not supported.
        """
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
            _import_obj.metadata = self.work_object.get_metadata(self.work_object.parent_task)
            _import_obj.category = self.work_object.category
            _import_obj.ingest_path = abs_path # This path can be a folder if its a bundled type.
            _import_obj.bring_in()

    def reference_version(
            self,
            version_number,
            element_type=None,
            ingestor=None
    ):
        """Reference the given version of the work to the scene.

        Args:
            version_number (int): The version number.
            element_type (str, optional): The element type to reference.
                Defaults to None.
            ingestor (str, optional): The ingestor to use. Defaults to None.

        Raises:
            ValueError: If the element type is not given or not supported.
        """
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
        """Shortcut and wrapper for the check_permissions method.

        Returns:
            bool: True if the user has the permission to delete the publish,
                False otherwise.
        """
        if self.check_permissions(level=3) == -1:
            return False, "Only Admins can delete publishes."
        return True, ""

    def destroy(self):
        """Delete ALL PUBLISHES of the work.

        Use with caution.

        Returns:
            tuple: (state(int), message(str)): 1 if the operation is
                successful, -1 otherwise. A message is returned as well.
        """
        state, msg = self.check_destroy_permissions()
        if not state:
            LOG.warning(msg)
            return -1, msg

        # move the whole publish folder to purgatory
        _purgatory_path = Path(
            self.work_object.get_purgatory_project_path(),
            "publish"
        )
        _purgatory_path.mkdir(parents=True, exist_ok=True)
        _work_folder = _purgatory_path / self.work_object.name
        if _work_folder.exists():
            try:
                shutil.rmtree(str(_work_folder))
            except PermissionError:
                msg = f"There is another folder in the purgatory with the same name. Please delete it manually or purge the purgatory.\n\n{str(_work_folder)}"
                LOG.error(msg)
                return -1, msg
        shutil.move(
            self.get_publish_project_folder(),
            str(_purgatory_path / self.work_object.name),
            copy_function=shutil.copytree
        )

        # move the database files to purgatory
        _purgatory_db_path = Path(
            self.work_object.get_purgatory_database_path(),
            "publish"
        )
        _purgatory_db_path.mkdir(parents=True, exist_ok=True)
        shutil.move(
            self.get_publish_data_folder(),
            str(_purgatory_db_path / self.work_object.name),
            copy_function=shutil.copytree
        )

        # clear the publish versions
        self._publish_versions = {}
        return 1, "success"

    def check_owner_permissions(self, version_number=None):
        """Shortcut and wrapper for the check_permissions method.

        This is a polymorphic method. version_number argument is not used in
        this method but an argument is required for the counterpart of the
        method in work object.

        Args:
            version_number (int, optional): This argument is not used in this
                method.
        """
        _ = version_number
        if self.check_permissions(level=3) == -1:
            return False, "Only Admins can delete publishes."
        return True, ""

    def delete_version(self, version_number):
        """Delete the given publish version.

        Args:
            version_number (int): The version number.

        Returns:
            tuple: (state(int), message(str)): 1 if the operation is
                successful, -1 otherwise. A message is returned as well.
        """
        state, msg = self.check_owner_permissions(version_number)
        if not state:
            LOG.warning(msg)
            return -1, msg

        version_obj = self.get_version(version_number)
        if not version_obj:
            msg = f"Version {version_number} not found."
            LOG.warning(msg)
            return -1, msg
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
        return 1, "success"

class PublishVersion(Settings, Entity):
    """PublishVersion object class.

    This class handles the publish version objects.
    Unlike work versions, publish versions are directly represented by files.
    name and path properties are required during first creation.
    When read from the file, these properties are initialized from the file.
    """

    def __init__(self, absolute_path, name=None, path=None):
        """Initialize the publish version object.

        Args:
            absolute_path (str): The absolute path of the publish version file.
            name (str, optional): The name of the publish version.
                Defaults to None.
            path (str, optional): The relative path of the publish version.
                Defaults to None.
        """
        super(PublishVersion, self).__init__()
        self._dcc_handler = self.guard.dcc_handler
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
        """The creator of the publish version."""
        return self._creator

    @property
    def category(self):
        """The category of the publish version."""
        return self._category

    @property
    def dcc(self):
        """The dcc of the publish version."""
        return self._dcc

    @property
    def dcc_version(self):
        """Dcc version used while publishing the version."""
        return self._dcc_version

    @property
    def publish_id(self):
        """Unique id of the publish version."""
        return self._publish_id

    @property
    def version(self):
        """Number of the publish version."""
        return self._version

    @property
    def task_name(self):
        """Task name of the publish version."""
        return self._task_name

    @property
    def task_id(self):
        """Task id of the publish version."""
        return self._task_id

    @property
    def relative_path(self):
        """Relative path of the publish version."""
        return self._relative_path

    @property
    def software_version(self):
        """Dcc version used while publishing the version.

        Identical to dcc_version property.
        """
        return self._dcc_version

    @property
    def elements(self):
        """The elements of the publish version."""
        return self._elements

    @property
    def element_types(self):
        """The element types of the publish version."""
        return [element["type"] for element in self.elements]

    @property
    def element_mapping(self):
        """The element mapping of the publish version.

        Element mapping is a dictionary where each key is the element name and
        the value is the element type.
        """
        return {element.get("name", element["type"]):
                    element["type"] for element in self.elements}

    def is_promoted(self):
        """Return if the publish is promoted or not.

        This method checks the 'promoted' file in the publish folder.
        If the content is matching with the publish id, return True
        """
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

    def get_element_by_type(self, element_type):
        """Return the element by the given type.

        Args:
            element_type (str): The type of the element.

        Returns:
            dict: The element or None if not found.
        """
        for element in self.elements:
            if element["type"] == element_type:
                return element
        return None

    def get_element_path(self, element_type, relative=True):
        """Return the element path of the given element type.

        Args:
            element_type (str): The type of the element.
            relative (bool, optional): If True, returns the relative path.
                If False, returns the absolute path. Default is True.

        Returns:
            str: The path of the element or None if not found.
        """
        for element in self.elements:
            if element["type"] == element_type:
                path = element["path"] if relative else (
                    self.get_abs_project_path(element["path"]))
                return path
        return None

    def get_element_suffix(self, element_type):
        """Return the element suffix of the given element type.

        Args:
            element_type (str): The type of the element.

        Returns:
            str: The suffix of the element or None if not found.
        """
        for element in self.elements:
            if element["type"] == element_type:
                return element["suffix"]
        return None

    def is_element_bundled(self, element_type):
        """Return if the element is bundled or not.

        Args:
            element_type (str): The type of the element.

        Returns:
            bool: True if the element is bundled, False otherwise.
        """
        for element in self.elements:
            if element["type"] == element_type:
                return element.get("bundled", False)
        return None
