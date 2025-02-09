"""Work and Publish objects."""

from pathlib import Path

from tik_manager4.core import utils
from tik_manager4.core.constants import ObjectType
from tik_manager4.core.settings import Settings
from tik_manager4.mixins.localize import LocalizeMixin
from tik_manager4.core import filelog

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")

class PublishVersion(Settings, LocalizeMixin):
    """PublishVersion object class.

    This class handles the publish version objects.
    Unlike work versions, publish versions are directly represented by files.
    name and path properties are required during first creation.
    When read from the file, these properties are initialized from the file.
    """
    object_type = ObjectType.PUBLISH_VERSION

    def __init__(self, absolute_path, name=None, path=None):
        """Initialize the publish version object.

        Args:
            absolute_path (str): The absolute path of the publish version file.
            name (str, optional): The name of the publish version.
                Defaults to None.
            path (str, optional): The relative path of the publish version.
                Defaults to None.
        """
        super().__init__()
        self._dcc_handler = self.guard.dcc_handler
        self.settings_file = absolute_path

        self._name:str = name
        self._creator:str = self.guard.user
        self._category:str = None
        self._dcc = self.guard.dcc
        self._publish_id = self._id
        self._version = 1
        self._work_version = None
        self._notes:str = ""
        self._previews: dict = {}
        self._task_name = None
        self._task_id = None
        self._thumbnail: str = ""
        self._relative_path = path
        self._dcc_version = None
        self._elements = []
        self._localized: bool = False
        self._localized_path: str = ""
        self._deleted: bool = False

        self.modified_time = None  # to compare and update if necessary

        self.init_properties()

        # get the current folder path
        _folder = Path(self.settings_file).parent
        promoted_file = _folder / "promoted.json"
        self._promoted_object = Settings(promoted_file)

    def init_properties(self):
        """Initialize the properties of the publish."""
        self._category = self.get_property("category", self._category)
        self._creator = self.get_property("creator", self._creator)
        self._dcc = self.get_property("dcc", self._dcc)
        self._dcc_version = self.get_property("dcc_version", self._dcc_version)
        self._elements = self.get_property("elements", self._elements)
        self._name = self.get_property("name", self._name)
        self._notes = self.get_property("notes", self._notes)
        self._previews = self.get_property("previews", self._previews)
        self._publish_id = self.get_property("publish_id", self._publish_id)
        self._relative_path = self.get_property("path", self._relative_path)
        self._task_id = self.get_property("task_id", self._task_id)
        self._task_name = self.get_property("task_name", self._task_name)
        self._thumbnail = self.get_property("thumbnail", self._thumbnail)
        self._version = self.get_property("version_number", self._version)
        self._work_version = self.get_property("work_version", self._work_version)
        self._localized = self.get_property("localized", self._localized)
        self._localized_path = self.get_property("localized_path", self._localized_path)
        self._deleted = self.get_property("deleted", self._deleted)

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
    def dcc_handler(self):
        """DCC handler object."""
        return self._dcc_handler

    @property
    def publish_id(self):
        """Unique id of the publish version."""
        return self._publish_id

    @property
    def version(self):
        """Number of the publish version."""
        return self._version

    @property
    def notes(self):
        """Notes of the publish version."""
        return self._notes

    @property
    def task_name(self):
        """Task name of the publish version."""
        return self._task_name

    @property
    def task_id(self):
        """Task id of the publish version."""
        return self._task_id

    @property
    def thumbnail(self):
        """Thumbnail of the publish version."""
        return self._thumbnail

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
        return {
            element.get("name", element["type"]): element["type"]
            for element in self.elements
        }

    @property
    def previews(self):
        """The previews of the publish version."""
        return self._previews

    @previews.setter
    def previews(self, value):
        self._previews = value

    @property
    def user(self):
        """The user of the publish version. Alias for creator."""
        return self._creator

    @property
    def deleted(self):
        """The deleted status of the publish version."""
        return self._deleted

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
                path = (
                    element["path"]
                    if relative
                    # else (self.get_abs_project_path(element["path"]))
                    else (self.get_resolved_path(element["path"]))
                )
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
                return element.get("suffix", "")
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

    def move_to_purgatory(self):
        """Move the publish version to the purgatory folder."""

        errors = []
        for element in self.elements:
            relative_path = element["path"]
            source_abs_path = self.get_resolved_path(relative_path)
            target_abs_path = self.get_resolved_purgatory_path(relative_path)
            result, msg = utils.move(source_abs_path, target_abs_path)
            if not result:
                errors.append(msg)

        if errors:
            return False, "\n".join(errors)
        self._deleted = True
        self.edit_property("deleted", True)
        self.apply_settings(force=True)
        return True, "Success"

    def resurrect(self):
        """Bring back the publish version from purgatory."""
        errors = []
        for element in self.elements:
            relative_path = element["path"]
            source_abs_path = self.get_resolved_purgatory_path(relative_path)
            target_abs_path = self.get_resolved_path(relative_path)
            result, msg = utils.move(source_abs_path, target_abs_path)
            if not result:
                errors.append(msg)

        if errors:
            return False, "\n".join(errors)

        # make sure hiearchy is resurrected (or not deleted)
        # TODO we need the parent work to resurrect upstream

        self._deleted = False
        self.edit_property("deleted", False)
        self.apply_settings(force=True)
        return True, "Success"


class WorkVersion(LocalizeMixin):
    """WorkVersion object class.

    Work versions are not directly represented by files. They are stored in the
    main work database.
    """
    object_type = ObjectType.WORK_VERSION

    # def __init__(self, parent_path, data_dictionary=None):
    def __init__(self, parent_path, data_dictionary, parent_work):
        super().__init__()
        self._dcc_version: str = "NA"
        self._file_format: str = ""
        self._notes: str = ""
        self._previews: dict = {}
        self._scene_path: str = ""
        self._thumbnail: str = ""
        self._user: str = ""
        self._version_number: int = 0
        self._workstation: str = ""
        self._relative_path = parent_path
        self._deleted: bool = False
        # if data_dictionary:
        #     self.from_dict(data_dictionary)
        self.from_dict(data_dictionary)
        self.parent_work = parent_work

    @property
    def dcc_version(self):
        """The dcc version of the work version."""
        return self._dcc_version

    @property
    def file_format(self):
        """The file format of the work version."""
        return self._file_format

    @property
    def notes(self):
        """The notes of the work version."""
        return self._notes

    @notes.setter
    def notes(self, value):
        self._notes = value

    @property
    def previews(self):
        """The previews of the work version."""
        return self._previews

    @previews.setter
    def previews(self, value):
        self._previews = value

    @property
    def path(self):
        """The relative path of the work version."""
        return Path(self._relative_path, self._scene_path).as_posix()

    @property
    def scene_path(self):
        """The scene path of the work version."""
        return self._scene_path

    @property
    def thumbnail(self):
        """The thumbnail path of the work version."""
        return self._thumbnail

    @thumbnail.setter
    def thumbnail(self, value):
        self._thumbnail = value

    @property
    def user(self):
        """The user of the work version."""
        return self._user

    @property
    def version(self):
        """The version number of the work version."""
        return self._version_number

    @property
    def workstation(self):
        """The workstation of the work version."""
        return self._workstation

    @property
    def deleted(self):
        """The deleted status of the work version."""
        return self._deleted

    def from_dict(self, dictionary):
        """Apply the values from given dictionary."""
        for key, value in dictionary.items():
            # add a leading underscore to directly write into protected attrs.
            key = f"_{key}"
            setattr(self, key, value)

    def to_dict(self):
        """Convert the WorkVersion object to a dictionary."""
        return {
            "dcc_version": self._dcc_version,
            "file_format": self._file_format,
            "localized": self._localized,
            "localized_path": self._localized_path,
            "notes": self._notes,
            "previews": self._previews,
            "scene_path": self._scene_path,
            "thumbnail": self._thumbnail,
            "user": self._user,
            "version_number": self._version_number,
            "workstation": self._workstation,
            "deleted": self._deleted
        }

    def move_to_purgatory(self):
        """Move the work version to the purgatory folder."""
        source_abs_path = self.get_resolved_path()
        target_abs_path = self.get_resolved_purgatory_path()
        result, msg = utils.move(source_abs_path, target_abs_path)
        if not result:
            LOG.error(msg)
            return False, msg

        self._deleted = True
        return True, f"{source_abs_path} moved to {target_abs_path}."

    def resurrect(self):
        """Bring back the work version from purgatory."""
        source_abs_path = self.get_resolved_purgatory_path()
        target_abs_path = self.get_resolved_path()
        result, msg = utils.move(source_abs_path, target_abs_path)
        if not result:
            LOG.error(msg)
            return False, msg
        # make sure hiearchy is resurrected (or not deleted)
        if self.parent_work.deleted:
            self.parent_work.resurrect(dont_resurrect_versions=True)

        self._deleted = False
        self.parent_work.apply_settings()
        return True, f"{source_abs_path} moved to {target_abs_path}."

    def __str__(self):
        """Return the type of the class and the current data."""
        return f"{type(self).__name__}({self.to_dict()})"
    def __repr__(self):
        """Return the type of the class and the current data."""
        return str(self.to_dict())
