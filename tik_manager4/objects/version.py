"""Work and Publish objects."""

from pathlib import Path

from tik_manager4.core import utils
from tik_manager4.core.constants import ObjectType, ColorCodes, ValidationResult, ValidationState, BranchingModes
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

    def __init__(self, absolute_path, name=None, path=None, live_object=None, promoted_object=None):
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

        # In case the live and promoted objects are not provided,
        _folder = Path(self.settings_file).parent
        live_file = _folder / "live.json"
        promoted_file = _folder / "promoted.json"

        self._live_object = live_object or Settings(live_file)
        self._promoted_object = promoted_object or Settings(promoted_file)

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
    def nice_name(self):
        """Return the nice name of the publish version."""
        return str(self.version)

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

    def _get_live_folder(self):
        """Return the PATH object of the LIVE folder."""
        # resolve the LIVE folder
        live_folder = Path(self.get_abs_project_path()).parent / "LIVE"
        return live_folder

    def _get_promoted_folder(self):
        """Return the PATH object of the PROMOTED folder."""
        # resolve the LIVE folder
        promoted_folder = Path(self.get_abs_project_path()).parent / "PROMOTED"
        return promoted_folder

    def is_deleted(self):
        """Convenience method to check if the publish version is deleted."""
        return self._deleted

    def is_live(self):
        """Check if the publish version is a live version."""
        if not self._live_object:
            return False
        _id = self._live_object.get_property("publish_id", default=None)
        return _id == self._publish_id

    def _make_live_with_active_branching(self):
        """Make the publish version a live version with active branching."""
        # resolve the LIVE folder
        # live_folder = Path(self.get_abs_project_path()).parent / "LIVE"
        live_folder = self._get_live_folder()
        live_folder.mkdir(parents=True, exist_ok=True)

        _data = {
            "publish_id": self._publish_id,
            "name": self._name,
            "path": live_folder.relative_to(self.guard.project_root).as_posix(),
            "version_number": self._version,
            "elements": []
        }

        for element_data in self.elements:
            element_type = element_data["type"]
            publish_path = Path(self.get_element_path(element_type, relative=False))
            # construct the name of the LIVE element from the data
            # if it's a usd
            if publish_path.suffix.startswith(".usd"):
                live_element_name = f"{element_type.upper()}_{self._name}.usda"
                live_path = live_folder / live_element_name
                if publish_path.suffix.startswith(".usd"):
                    utils.write_unprotect(live_path)
                    with open(live_path, "w") as f:
                        f.write(f"""#usda 1.0
(
    subLayers = [
            @{str(publish_path).replace(str(Path(self.get_abs_project_path()).parent), "../")}@
    ]
)
                                    """)
                    utils.write_protect(live_path)
            # if it's any other file type (not usd)
            else:
                live_element_name = f"{element_type.upper()}_{self._name}{publish_path.suffix}"
                live_path = live_folder / live_element_name
                state, msg = utils.copy(publish_path.as_posix(), live_path.as_posix())
                if not state:
                    # TODO: FIX - TEST - STREAMLINE
                    LOG.error(f"Error copying {publish_path} to {live_path}: {msg}")
                    return ValidationResult(ValidationState.ERROR, msg, False)
            # get the relative path against the project path

            # relative_path = Path(self.guard.project_root).relative_to(live_path.parent)
            relative_path = live_path.relative_to(live_folder)

            # add the element to the promoted data
            _data["elements"].append({
                "name": element_data["name"],
                "type": element_type,
                "suffix": element_data["suffix"],
                "path": relative_path.as_posix(),
                "bundled": element_data["bundled"],
                "bundle_info": element_data["bundle_info"],
                "bundle_match_id": element_data["bundle_match_id"],
            })
        self._live_object.set_data(_data)
        self._live_object.apply_settings(force=True)

    def make_live(self):
        """Make the publish version a live version."""

        # if the active branch method is selected, use it
        if self.guard.project_settings.get("branching_mode", BranchingModes.ACTIVE.value):
            self._make_live_with_active_branching()
            return
        # otherwise, use the default method
        _data = {
            "publish_id": self._publish_id,
            "name": self._name,
            "path": self._relative_path,
            "version_number": self.version,
            "elements": self._elements
        }
        self._live_object.set_data(_data)
        self._live_object.apply_settings(force=True)


    def is_promoted(self):
        """Return if the publish is promoted or not.

        This method checks the 'promoted' file in the publish folder.
        If the content is matching with the publish id, return True
        """
        if not self._promoted_object:
            return False
        # self._promoted_object.reload()
        _id = self._promoted_object.get_property("publish_id", default=None)
        return _id == self._publish_id

    def can_promote(self):
        """Check if the publish version can be promoted."""
        return True

    def _promote_with_active_branching(self):
        """Promoting with the active branch method."""
        # promoted_folder = Path(self.get_abs_project_path()).parent / "LIVE"
        promoted_folder = self._get_promoted_folder()
        promoted_folder.mkdir(parents=True, exist_ok=True)

        _data = {
            "publish_id": self._publish_id,
            "name": self._name,
            "path": promoted_folder.relative_to(self.guard.project_root).as_posix(),
            "version_number": self.version,
            "elements": []
        }

        for element_data in self.elements:
            element_type = element_data["type"]
            publish_path = Path(self.get_element_path(element_type, relative=False))
            # construct the name of the LIVE element from the data
            # if it's a usd
            if publish_path.suffix.startswith(".usd"):
                promoted_element_name = f"{element_type.upper()}_{self._name}.usda"
                promoted_path = promoted_folder / promoted_element_name
                if publish_path.suffix.startswith(".usd"):
                    utils.write_unprotect(publish_path)
                    with open(promoted_path, "w") as f:
                        f.write(f"""#usda 1.0
(
    subLayers = [
            @{str(publish_path).replace(str(Path(self.get_abs_project_path()).parent), "../")}@
    ]
)
                                                """)
                    utils.write_protect(promoted_path)
            # if it's any other file type (not usd)
            else:
                promoted_element_name = f"{element_type.upper()}_{self._name}{publish_path.suffix}"
                promoted_path = promoted_folder / promoted_element_name
                state, msg = utils.copy(publish_path.as_posix(), promoted_path.as_posix())
                if not state:
                    LOG.error(f"Error copying {publish_path} to {promoted_path}: {msg}")
                    return ValidationResult(ValidationState.ERROR, msg, False)
            # get the relative path against the project path

            relative_path = promoted_path.relative_to(promoted_folder)

            # add the element to the promoted data
            _data["elements"].append({
                "name": element_data["name"],
                "type": element_type,
                "suffix": element_data["suffix"],
                "path": relative_path.as_posix(),
                "bundled": element_data.get("bundled", False),
                "bundle_info": element_data.get("bundle_info", {}),
                "bundle_match_id": element_data.get("bundle_match_id", 0),
            })
        self._promoted_object.set_data(_data)
        self._promoted_object.apply_settings(force=True)
        return ValidationResult(ValidationState.SUCCESS, "Success", False)

    def promote(self):
        """Promote the publish editing the promoted.json."""
        if self.check_permissions(level=3) == -1:
            return ValidationResult(ValidationState.ERROR, f"{self.guard.user} doesn't have the permissions to promote publish versions.", False)

        # if the active branch method is selected, use it
        if self.guard.project_settings.get("branching_mode", BranchingModes.ACTIVE.value):
            result: ValidationResult = self._promote_with_active_branching()



            if result.state != ValidationState.SUCCESS:
                return result
            return ValidationResult(ValidationState.SUCCESS, "Success")

        # otherwise, use the default method
        _data = {
            "publish_id": self._publish_id,
            "name": self._name,
            "path": self._relative_path,
            "version_number": self.version,
            "elements": self._elements
        }
        self._promoted_object.set_data(_data)
        self._promoted_object.apply_settings(force=True)
        return ValidationResult(ValidationState.SUCCESS, "Success")

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

        self._deleted = False
        self.edit_property("deleted", False)
        self.apply_settings(force=True)
        return True, "Success"

    def get_display_color(self):
        """Return the display color of the version.

        Returns:
            str: The display color of the publish version.
        """
        if self.deleted:
            return ColorCodes.DELETED.value
        if self.is_promoted():
            return ColorCodes.PROMOTED.value
        if self.is_live():
            return ColorCodes.LIVE.value
        return ColorCodes.NORMAL.value

    def to_dict(self):
        """Convert the WorkVersion object to a dictionary."""
        return {
            "category": self._category,
            "creator": self._creator,
            "dcc": self._dcc,
            "dcc_version": self._dcc_version,
            "elements": self._elements,
            "name": self._name,
            "notes": self._notes,
            "publish_id": self._publish_id,
            "relative_path": self._relative_path,
            "task_id": self._task_id,
            "task_name": self._task_name,
            "thumbnail": self._thumbnail,
            "version_number": self._version,
            "work_version": self._work_version,
            "localized": self._localized,
            "localized_path": self._localized_path,
            "deleted": self._deleted,
        }

class LiveVersion(PublishVersion):
    """Customized PublishVersion object class."""
    object_type = ObjectType.PUBLISH_VERSION

    def is_promoted(self):
        """Override the is_promoted method to always return False.

        This is to prevent doubling the promoted publish version.
        """
        return False

    def is_live(self):
        """Override the is_live method to always return True."""
        return True

    @property
    def nice_name(self):
        """Override the nice_name property to return the name of the publish version."""
        return "LIVE"

    @property
    def version(self):
        """Override the version property to return 0."""
        return -1 # -1 means the version is live, not a number.

    def get_resolved_path(self, *args):
        """Override the get_resolved_path method to return the path."""
        live_folder = self._get_live_folder()
        return Path(live_folder, *args).as_posix()

    def get_display_color(self):
        """Return the display color of the version.

        Returns:
            str: The display color of the publish version.
        """
        return ColorCodes.LIVE.value

class PromotedVersion(PublishVersion):
    """Customized PublishVersion object class."""
    object_type = ObjectType.PUBLISH_VERSION

    def is_promoted(self):
        """Override the is_promoted method to always return False.

        This is to prevent doubling the promoted publish version.
        """
        return False

    def is_live(self):
        """Override the is_live method to always return False."""
        return False

    def can_promote(self):
        """Override the can_promote method to always return False."""
        return False

    def promote(self):
        """Override the promote method to do nothing."""
        pass

    @property
    def nice_name(self):
        """Override the nice_name property to return the name of the publish version."""
        return "PRO"

    @property
    def version(self):
        """Override the version property to return 0."""
        return 0

    def get_resolved_path(self, *args):
        """Override the get_resolved_path method to return the path."""
        promoted_folder = self._get_promoted_folder()
        return Path(promoted_folder, *args).as_posix()

    def get_display_color(self):
        """Return the display color of the version.

        Returns:
            str: The display color of the publish version.
        """
        return ColorCodes.PROMOTED.value

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
    def nice_name(self):
        """Return the nice name of the work version."""
        return str(self.version)

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
            "version_number": self._version_number,
            "user": self._user,
            "scene_path": self._scene_path,
            "file_format": self._file_format,
            "notes": self._notes,
            "dcc_version": self._dcc_version,
            "localized": self._localized,
            "localized_path": self._localized_path,
            "previews": self._previews,
            "thumbnail": self._thumbnail,
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
        # make sure hierarchy is resurrected (or not deleted)
        if self.parent_work.deleted:
            self.parent_work.resurrect(dont_resurrect_versions=True)

        self._deleted = False
        self.parent_work.apply_settings()
        return True, f"{source_abs_path} moved to {target_abs_path}."

    def get_display_color(self):
        """Return the display color of the version.

        Returns:
            str: The display color of the publish version.
        """
        return ColorCodes.NORMAL.value

        # if self.deleted:
        #     return ColorCodes.DELETED.value
        # if self.is_promoted():
        #     return ColorCodes.PROMOTED.value
        # if self.is_live():
        #     return ColorCodes.LIVE.value

    def __str__(self):
        """Return the type of the class and the current data."""
        return f"{type(self).__name__}({self.to_dict()})"
    def __repr__(self):
        """Return the type of the class and the current data."""
        return str(self.to_dict())
