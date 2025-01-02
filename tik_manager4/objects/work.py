# pylint: disable=super-with-arguments
# pylint: disable=consider-using-f-string
"""Module for Work object."""

import socket
import shutil
from pathlib import Path

from tik_manager4.core import utils
from tik_manager4.core.constants import ObjectType
from tik_manager4.dcc.standalone.main import Dcc as StandaloneDcc
from tik_manager4.core.settings import Settings
from tik_manager4.core import filelog
from tik_manager4.objects.publish import Publish
from tik_manager4.objects.version import WorkVersion
from tik_manager4.mixins.localize import LocalizeMixin

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")


class Work(Settings, LocalizeMixin):
    """Work object to handle works and publishes."""

    _standalone_handler = StandaloneDcc()
    object_type = ObjectType.WORK

    def __init__(self, absolute_path, name=None, path=None, parent_task=None):
        """Initialize the Work object.

        Args:
            absolute_path (str): Absolute path of the settings file.
            name (str): Name of the work.
            path (str): Relative path of the work.
            parent_task (Task): Parent task object.
        """
        super(Work, self).__init__()
        self.settings_file = Path(absolute_path)
        self._dcc_handler = self.guard.dcc_handler
        # self.localize = Localize(self.guard)
        self._name = name
        self._creator = self.guard.user
        self._category = None
        self._dcc = self.guard.dcc
        self._dcc_version = None
        self._versions = []
        self._work_id = self._id
        self._task_name = None
        self._task_id = None
        self._relative_path = path
        self._software_version = None
        self._thumbnail_resolution = self.guard.preview_settings.get("ThumbnailResolution")

        # there are 3 states: working, published, omitted
        self._parent_task = None
        if parent_task:
            self.set_parent_task(parent_task)
        self._state = "working"

        self.modified_time = None  # to compare and update if necessary
        self.publish = Publish(
            self
        )  # publish object does not have a settings file, the publish versions do

        self.init_properties()

    def init_properties(self):
        """Initialize the properties of the work from the inherited dictionary."""
        self._name = self.get_property("name", self._name)
        self._creator = self.get_property("creator", self.guard.user)
        self._category = self.get_property("category", self._category)
        self._dcc = self.get_property("dcc", self.guard.dcc)
        self._dcc_version = self.get_property("dcc_version", self._dcc_version)
        self._work_id = self.get_property("work_id", self._id)
        self._task_name = self.get_property("task_name", self._task_name)
        self._task_id = self.get_property("task_id")
        self._relative_path = self.get_property("path", self._relative_path)
        self._versions = [WorkVersion(self._relative_path, version) for version in self.get_property("versions", [])]
        self._software_version = self.get_property("softwareVersion")
        self._state = self.get_property("state", self._state)
        # keeping the 'working' state for backward compatibility.
        if self._state == "active" or self._state == "working":
            if self.publish.versions:
                self._state = "published"

    @property
    def state(self):
        """Current state of the work."""
        return self._state

    @property
    def dcc(self):
        """Name of the DCC that the work is originated from."""
        return self._dcc

    @property
    def dcc_version(self):
        """Version of the dcc that the work is originated from."""
        return self._dcc_version

    @property
    def dcc_handler(self):
        """DCC handler object."""
        return self._dcc_handler

    @property
    def id(self):
        """Unique id of the work."""
        return self._work_id

    @property
    def task_id(self):
        """Unique id of the task that the work belongs to."""
        return self._task_id

    @property
    def task_name(self):
        """Name of the task that the work belongs to."""
        return self._task_name

    @property
    def parent_task(self):
        """Parent task object that the work lives in."""
        return self._parent_task

    @property
    def creator(self):
        """The creator of the work."""
        return self._creator

    @property
    def category(self):
        """The category of the work."""
        return self._category

    @property
    def versions(self):
        """Versions of the work in a list."""
        return self._versions

    @property
    def version_count(self):
        """Total number of versions belonging to the work."""
        return len(self._versions)

    def set_parent_task(self, task_obj):
        """Set the parent task of the work."""
        self._parent_task = task_obj
        self._task_id = task_obj.id
        self._task_name = task_obj.name

    def reload(self):
        """Reload the work from file."""
        self.__init__(
            self.settings_file,
            name=self._name,
            path=self._relative_path,
            parent_task=self._parent_task,
        )

    def omit(self):
        """Omit the work."""
        self._state = "omitted"
        self.edit_property("state", self._state)
        self.apply_settings()

    def revive(self):
        """Revive the work."""
        self._state = "active"
        self.edit_property("state", self._state)
        self.apply_settings()

    def get_last_version(self):
        """Return the last version of the work."""
        # First try to get the last version from the versions list. If not found, return 0.
        if self._versions:
            return self._versions[-1].version
        else:
            return 0

    def get_version(self, version_number):
        """Return the version dictionary by version number.

        Args:
            version_number (int): Version number.
        """
        for version in self._versions:
            if version.version == version_number:
                return version

    def new_version_from_path(self, file_path, notes=""):
        """Register a given path (file or folder) as a new version of the work.

        Args:
            file_path (str): The file path of the source file. This will be copied to the project.
            notes (str): Notes for the version.
            ignore_checks (bool): If True, skip all pre-checks.

        Returns:
            dict: The version dictionary.
        """

        state = self.check_permissions(level=1)
        if state != 1:
            return -1

        file_format = Path(file_path).suffix
        # get filepath of current version
        version_number, version_name, thumbnail_name = self.construct_names(file_format)

        abs_version_path = self.get_abs_project_path(self.name, version_name)
        thumbnail_path = self.get_abs_database_path("thumbnails", thumbnail_name)
        Path(abs_version_path).parent.mkdir(parents=True, exist_ok=True)

        # save the file
        output_path = self._standalone_handler.save_as(
            abs_version_path, source_path=file_path
        )

        # generate thumbnail
        # create the thumbnail folder if it doesn't exist
        Path(thumbnail_path).parent.mkdir(parents=True, exist_ok=True)

        # add it to the versions
        extension = Path(output_path).suffix or "Folder"
        self._standalone_handler.text_to_image(extension, thumbnail_path, self._thumbnail_resolution[0], self._thumbnail_resolution[1])
        version_dict = {
            "version_number": version_number,
            "workstation": socket.gethostname(),
            "notes": notes,
            "thumbnail": Path("thumbnails", thumbnail_name).as_posix(),
            "scene_path": Path(self.name, str(version_name)).as_posix(),
            "user": self.guard.user,
            "previews": {},
            "file_format": file_format,
            "dcc_version": "NA",
        }
        version_obj = WorkVersion(self.path, version_dict)
        self._versions.append(version_obj)
        self._apply_versions()
        return version_obj

    def _apply_versions(self):
        """Serialize the version objects and apply it to the settings."""
        self.edit_property("versions",
                           [version.to_dict() for version in self._versions])
        self.apply_settings(force=True)

    def new_version(self, file_format=None, notes="", ignore_checks=True):
        """Create a new version of the work.

        Args:
            file_format (str): The file format of the file.
            notes (str): Notes for the version.
            ignore_checks (bool): If True, skip all pre-checks.

        Returns:
            dict: The version dictionary.
        """

        state = self.check_permissions(level=1)
        if state != 1:
            return -1

        if not ignore_checks:
            # check if there is a mismatch with the current dcc version
            dcc_mismatch = self.check_dcc_version_mismatch()
            if dcc_mismatch:
                LOG.warning(
                    f"The current dcc version ({dcc_mismatch[1]}) does not match with the defined dcc version ({dcc_mismatch[0]})."
                )
                return -1

        # validate file format
        file_format = file_format or self._dcc_handler.formats[0]
        if file_format not in self._dcc_handler.formats:
            raise ValueError("File format is not valid.")

        # get filepath of current version
        version_number, version_name, thumbnail_name = self.construct_names(file_format)

        origin_path = self.get_abs_project_path(self.name, version_name)
        thumbnail_path = self.get_abs_database_path("thumbnails", thumbnail_name)
        Path(origin_path).parent.mkdir(parents=True, exist_ok=True)

        # set the origin path to localizer.
        # self.localize.origin_path = origin_path

        # run pre-save operations defined in the dcc handler
        self._dcc_handler.pre_save()

        # save the file to either project or cache path.
        # output_path = self.localize.output_path
        output_path = self.get_output_path(self.name, version_name)
        if not output_path:
            return -1
        returned_output_path = self._dcc_handler.save_as(output_path)

        # on some occasions the save as method may return a different path.
        # for example, if the file cannot be saved with specified file format,
        # extractor logic may decide to force something else.
        if returned_output_path != output_path:
            version_name = Path(returned_output_path).name  # e.g. "test_v001.ma"
            file_format = Path(returned_output_path).suffix  # e.g. ".ma"

        # generate thumbnail
        # create the thumbnail folder if it doesn't exist
        Path(thumbnail_path).parent.mkdir(parents=True, exist_ok=True)
        self._dcc_handler.generate_thumbnail(thumbnail_path, self._thumbnail_resolution[0], self._thumbnail_resolution[1]) #default thumb resolution: 220 124

        # add it to the versions
        is_localized = self.can_localize()
        version_dict = {
            "version_number": version_number,
            "workstation": socket.gethostname(),
            "notes": notes,
            "thumbnail": Path("thumbnails", thumbnail_name).as_posix(),
            "scene_path": Path(self.name, str(version_name)).as_posix(),
            "user": self.guard.user,
            "previews": {},
            "file_format": file_format,
            "dcc_version": self._dcc_handler.get_dcc_version(),
        }
        if is_localized:
            version_dict["localized"] = is_localized
            version_dict["localized_path"] = output_path
        version_obj = WorkVersion(self.path, version_dict)
        self._versions.append(version_obj)
        self._apply_versions()
        self._dcc_handler.post_save()
        return version_obj

    def construct_names(
        self, file_format, version_number=None, thumbnail_extension=".jpg"
    ):
        """Construct a name for the work version.

        Args:
            file_format (str): The file format of the file.
            version_number (int, optional): The version number.
                If not given, iterated on top of the last version.
            thumbnail_extension (str, optional): The extension of the thumbnail
                file.

        Returns:
            tuple: (version_number, version_name, thumbnail_name)
        """
        version_number = version_number or self.get_last_version() + 1
        version_name = f"{self._name}_v{version_number:03d}{file_format}"
        thumbnail_name = (
            f"{self._name}_v{version_number:03d}_thumbnail{thumbnail_extension}"
        )
        return version_number, version_name, thumbnail_name

    def load_version(self, version_number, force=False, **kwargs):
        """Load the given version of the work.

        Args:
            version_number (int): Version number.
            force (bool, optional): If True, force open the file.
            **kwargs: Additional arguments to pass to the dcc handler.
        """
        version_obj = self.get_version(version_number)
        if version_obj:
            abs_path = version_obj.get_resolved_path()
            self._dcc_handler.open(abs_path, force=force)
        return

    def import_version(self, version_number, element_type=None, ingestor=None):
        """Import the given version of the work to the scene.

        Args:
            version_number (int): Version number.
            element_type (str, optional): Element type of the version.
            ingestor (str, optional): Ingestor to use.
        """
        # work files does not have element types. This is for publish files.
        _element_type = element_type or "source"
        ingestor = ingestor or "source"
        version_obj = self.get_version(version_number)
        if version_obj:
            abs_path = version_obj.get_resolved_path()
            _ingest_obj = self._dcc_handler.ingests[ingestor]()
            # feed the metadata from the parent subproject
            _ingest_obj.metadata = self.get_metadata(self.parent_task)
            _ingest_obj.namespace = self.name
            _ingest_obj.category = self.category
            _ingest_obj.ingest_path = abs_path
            _ingest_obj.bring_in()

    def reference_version(self, version_number, element_type=None, ingestor=None):
        """Reference the given version of the work to the scene.

        Args:
            version_number (int): Version number.
            element_type (str, optional): Element type of the version.
            ingestor (str, optional): Ingestor to use.
        """
        # work files does not have element types. This is for publish files.
        _element_type = element_type or "source"
        ingestor = ingestor or "source"
        version_obj = self.get_version(version_number)
        if version_obj:
            # relative_path = version_obj.scene_path
            # abs_path = self.get_abs_project_path(relative_path)
            abs_path = version_obj.get_resolved_path()
            _ingest_obj = self._dcc_handler.ingests[ingestor]()
            _ingest_obj.metadata = self.get_metadata(self.parent_task)
            _ingest_obj.namespace = self.name
            _ingest_obj.category = self.category
            _ingest_obj.ingest_path = abs_path
            _ingest_obj.reference()

    def check_destroy_permissions(self):
        """Check the permissions for deleting the work.

        Users can only delete their own works. Admins can delete any work.
        If there is a publish of the work, only Admins can delete the work.

        Returns:
            Tuple[bool, str]: (state, message)
        """
        if self.check_permissions(level=3) == -1:
            if self.publish.versions:
                # if there is a publish, only admins can delete the work
                msg = "This work has published versions. Only admins can delete it."
                LOG.warning(msg)
                return False, msg
            if self.guard.user != self._creator:
                msg = (
                    "You do not have the permission to delete this work.\n"
                    "Only admins can delete other users' works."
                )
                LOG.warning(msg)
                return False, msg
            else:
                # check creators for all versions
                for version in self._versions:
                    if version.user != self.guard.user:
                        msg = (
                            "You do not have the permission to delete this work.\n"
                            "There are other versions created by other user(s).\n"
                            "Only admins can delete other users' works."
                        )
                        LOG.warning(msg)
                        return False, msg
        return True, ""

    def destroy(self):
        """Delete the work AND all its versions AND PUBLISHES.

        CAUTION: This is a destructive operation. Use with caution.

        Returns:
            tuple: (state(int), message(str)): 1 if the operation is
                successful, -1 otherwise. A message is returned as well.
        """
        state, msg = self.check_destroy_permissions()
        if not state:
            return -1, msg

        if self.publish.versions:
            self.publish.destroy()

        for version in self.versions:
            version.move_to_purgatory()

        # finally move the database file
        db_destination = Path(self.get_resolved_purgatory_path(), self.settings_file.name)
        utils.move(self.settings_file.as_posix(), db_destination.as_posix())
        return 1, "success"

    def check_owner_permissions(self, version_number):
        """Check the permissions for 'owner' and 'admin-only' actions.

        Users can only delete their own versions.
        Admins can delete any version. If there is a publish of the version,
        only Admins can delete the version.

        Args:
            version_number (int): Version number.

        Returns:
            Tuple[bool, str]: (state, message)

        """
        version_obj = self.get_version(version_number)
        if not version_obj:
            LOG.warning(f"Version {version_number} does not exist.")
            return False, "Version does not exist."
        if self.check_permissions(level=3) == -1:
            if self.guard.user != version_obj.user:
                msg = (
                    "You do not have the permissions for this action.\n"
                    "Only admins and version owners are allowed."
                )
                LOG.warning(msg)
                return False, msg
        return True, ""

    def delete_version(self, version_number):
        """Delete the given version of the work.

        Args:
            version_number (int): Version number.

        Returns:
            tuple: (state(int), message(str)): 1 if the operation is
                successful, -1 otherwise. A message is returned as well.
        """

        state, msg = self.check_owner_permissions(version_number)
        if not state:
            return -1, msg
        version_obj = self.get_version(version_number)
        if version_obj:
            version_obj.move_to_purgatory()

            # remove the version from the versions list
            self._versions.remove(version_obj)
            self._apply_versions()
        return 1, msg

    def __generate_thumbnail_paths(self, version_obj, override_extension=None):
        """Return the thumbnail paths of the given version.

        Args:
            version_obj (dict): Version dictionary.
            override_extension (str, optional): Override the extension of the
                thumbnail.
        """
        # if there is no previous thumbnail, generate a new one
        extension = (
            override_extension
            or Path(version_obj.get("thumbnail", "noThumb.jpg")).suffix
        )
        _number, _name, thumbnail_name = self.construct_names(
            version_obj.get("file_format", ""),
            version_obj.get("version_number"),
            thumbnail_extension=extension,
        )
        relative_path = Path("thumbnails", thumbnail_name).as_posix()
        abs_path = self.get_abs_database_path(relative_path)
        Path(abs_path).parent.mkdir(parents=True, exist_ok=True)
        return relative_path, abs_path

    def replace_thumbnail(self, version_number, new_thumbnail_path=None):
        """Replace the thumbnail of the given version.
        Args:
            version_number (int): Version number.
            new_thumbnail_path (str): Path to the thumbnail image.
                    If not given, a new thumbnail will be generated.

        Returns:
            int: 1 if successful, -1 if failed.
        """
        state, _msg = self.check_owner_permissions(version_number)
        if not state:
            return -1

        version_obj = self.get_version(version_number)
        override_suffix = (
            Path(new_thumbnail_path).suffix if new_thumbnail_path else None
        )
        target_relative_path, target_absolute_path = self.__generate_thumbnail_paths(
            version_obj, override_extension=override_suffix
        )

        if not new_thumbnail_path:
            self._dcc_handler.generate_thumbnail(target_absolute_path, self._thumbnail_resolution[0], self._thumbnail_resolution[1]) #default thumb resolution: 220 124
            version_obj["thumbnail"] = target_relative_path
        else:
            shutil.copy(new_thumbnail_path, target_absolute_path)
            version_obj["thumbnail"] = target_relative_path

        self.apply_settings()
        return 1

    def check_dcc_version_mismatch(self):
        """Check if there is a mismatch with the current and defined dcc versions.

        Returns:
            tuple or bool: a tuple of defined dcc version and current dcc
                version. Otherwise returns False.
        """
        # first try to get the current dcc version from scene. If not found, do not proceed.
        current_dcc = self._dcc_handler.get_dcc_version()
        if not current_dcc:
            return False  # In this case we assume there is no need for dcc check
        metadata_key = f"{self.guard.dcc.lower()}_version"
        # if a dcc version defined in metadata, use that. Otherwise use the current dcc version.
        defined_dcc_version = (
            self.get_metadata(self.parent_task, metadata_key) or self.dcc_version
        )
        if defined_dcc_version in ["NA", "", current_dcc]:
            return False
        return defined_dcc_version, current_dcc
