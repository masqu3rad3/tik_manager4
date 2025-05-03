# pylint: disable=super-with-arguments
"""Publish object module."""


from pathlib import Path

from tik_manager4.objects.version import PromotedVersion
from tik_manager4.core.constants import ObjectType
from tik_manager4.objects.version import PublishVersion, LiveVersion
from tik_manager4.mixins.localize import LocalizeMixin
from tik_manager4.core import filelog

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")


class Publish(LocalizeMixin):
    """Class to represent a publish.

    Publish objects are created from the work objects. Publishes are the
    final versions of the works. Publishes are not editable.
    This class is not represented by a file. Publish-PublishVersion relationship
    is opposite of Work-WorkVersion relationship.
    PublishVersions have database files, publishes don't.
    """
    object_type = ObjectType.PUBLISH

    def __init__(self, work_object):
        """Initialize the publish object."""
        super(Publish, self).__init__()
        self._dcc_handler = work_object.guard.dcc_handler
        self.work_object = work_object

        self._publish_versions = {}

        self._live_version = None
        self._promoted_version = None

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
    def dcc_handler(self):
        """DCC handler object."""
        return self._dcc_handler

    @property
    def versions(self):
        """Versions of the publish."""
        all_versions = self.all_versions
        return [version for version in all_versions if not version.deleted]

    @property
    def all_versions(self):
        """All versions of the publish, including the deleted ones."""
        self.scan_publish_versions()
        return list(self._publish_versions.values())

    @property
    def version_count(self):
        """Number of publish versions."""
        # return len(self.versions)
        return len(self.all_versions)

    @property
    def state(self):
        """State of the publish."""
        return self.work_object.state

    @property
    def parent_task(self):
        """Parent task of the publish."""
        return self.work_object.parent_task

    @property
    def deleted(self):
        """Return True if the publish is deleted."""
        # if there are no non-deleted versions, the publish is considered deleted
        return not bool(self.versions)

    @property
    def live_version(self):
        """Return the live version."""
        if self._live_version:
            return self._live_version
        return self.get_live_version()

    @property
    def promoted_version(self):
        """Return the promoted version."""
        if self._promoted_version:
            return self._promoted_version
        return self.get_promoted_version()

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
        self.work_object._state = "active" if not self.versions else "published"
        self.work_object.edit_property("state", self.work_object._state)
        self.work_object.apply_settings()

    def get_last_version(self):
        """Return the last publish version."""
        # find the latest publish version
        _publish_version_numbers = [data.version for data in self.all_versions]
        return 0 if not _publish_version_numbers else max(_publish_version_numbers)

    def get_publish_data_folder(self):
        """Return the publish data folder."""
        return self.work_object.get_abs_database_path("publish", self.work_object.name)

    def get_publish_project_folder(self):
        """Return the publish scene folder."""
        return self.work_object.get_abs_project_path("publish", self.work_object.name)

    def get_live_version(self):
        """Get the live version among the published versions."""
        for version in reversed(self._publish_versions.values()):
            if version.is_live():
                return version
        return None

    def get_promoted_version(self):
        """Get the promoted version among the published versions."""
        for version in reversed(self._publish_versions.values()):
            if version.is_promoted():
                return version

    def scan_publish_versions(self):
        """Return the publish versions in the publish folder."""
        # search directory is resolved from the work object
        _search_dir = Path(self.get_publish_data_folder())
        if not _search_dir.exists():
            return {}
        _publish_version_paths = list(_search_dir.glob("*.tpub"))

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

        self._live_version = self.get_live_version()
        self._promoted_version = self.get_promoted_version()

        # check the project settings for the active branches.
        if self.guard.project_settings.get("active_branches", True):
            if self._live_version:
                # Create a LIVE version merging the live version with live data
                # This is a temporary version and not saved to disk.
                live_version = LiveVersion(self._live_version.settings_file)
                live_version._elements = live_version._live_object.get("elements")
                self._publish_versions["live"] = live_version

            if self._promoted_version:
                # Create a PROMOTED version merging the promoted version with promoted data
                # This is a temporary version and not saved to disk.
                promoted_version = PromotedVersion(self._promoted_version.settings_file)
                promoted_version._elements = promoted_version._live_object.get("elements")
                self._publish_versions["promoted"] = promoted_version

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

    def load_version(
        self, version_number, force=False, element_type="source", read_only=False
    ):
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
                abs_path = version_obj.get_resolved_path(relative_path)
                suffix = Path(abs_path).suffix
                self._dcc_handler.open(abs_path, force=force)
                if not read_only:
                    self.work_object.new_version(
                        notes=f"Auto Saved from publish version {version_obj.version}",
                        file_format=suffix,
                    )
            else:
                raise ValueError(
                    f"{element_type} element cannot be found in the publish version."
                )

    def import_version(
        self, version_number, element_type=None, ingestor=None, sequential=False
    ):
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
            abs_path = version_obj.get_resolved_path(relative_path)
            _func = self._dcc_handler.ingests.get(ingestor, None)
            if not _func:
                raise ValueError(f"Element type not supported: {element_type}")
            _import_obj = _func()
            _import_obj.sequential = sequential
            _import_obj.metadata = self.work_object.get_metadata(
                self.work_object.parent_task
            )
            _import_obj.namespace = self.name
            _import_obj.category = self.work_object.category
            _import_obj.ingest_path = (
                abs_path  # This path can be a folder if its a bundled type.
            )
            _import_obj.bring_in()

    def reference_version(
        self, version_number, element_type=None, ingestor=None, sequential=False
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
            abs_path = version_obj.get_resolved_path(relative_path)
            _func = self._dcc_handler.ingests.get(ingestor, None)
            if not _func:
                raise ValueError(f"Element type not supported: {element_type}")
            _import_obj = _func()
            _import_obj.sequential = sequential
            _import_obj.category = self.work_object.category
            _import_obj.metadata = self.work_object.get_metadata(
                self.work_object.parent_task
            )
            _import_obj.namespace = self.name
            _import_obj.ingest_path = abs_path
            _import_obj.reference()

    def import_bundle_piece(
        self,
        version_number,
        element_type,
        bundle_piece,
        ingestor_name,
        sequential=False,
    ):
        """Import the bundled piece of the publish to the scene.

        This is a publish specific method.

        Args:
            version_number (int): The version number.
            element_type (str): The element type to import.
            ingestor (str, optional): The ingestor to use. Defaults to None.

        Raises:
            ValueError: If the element type is not given or not supported.
        """
        version_obj = self.get_version(version_number)
        if not version_obj:
            raise ValueError(f"Version {version_number} not found.")
        element = version_obj.get_element_by_type(element_type)
        if not element:
            raise ValueError(f"Element type not found: {element_type}")
        if not element.get("bundled"):
            raise ValueError(f"Element type is not bundled: {element_type}")
        bundle_piece = element["bundle_info"].get(bundle_piece)
        if not bundle_piece:
            raise ValueError(f"Bundle piece not found: {bundle_piece}")
        abs_path = version_obj.get_resolved_path(element["path"], bundle_piece["path"])
        _func = self._dcc_handler.ingests.get(ingestor_name, None)
        if not _func:
            raise ValueError(f"{ingestor_name} is not a valid ingestor.")

        _import_obj = _func()
        _import_obj.sequential = sequential
        _import_obj.metadata = self.work_object.get_metadata(
            self.work_object.parent_task
        )
        _import_obj.category = self.work_object.category
        _import_obj.ingest_path = abs_path
        _import_obj.bring_in()

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

        for publish_obj in self.versions:
            state, msg = publish_obj.move_to_purgatory()
            if not state:
                return -1, msg

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

        state, msg = version_obj.move_to_purgatory()
        if not state:
            return -1, msg

        # remove the publish version from the publish versions
        return 1, "success"

    def resurrect(self, dont_resurrect_versions=False):
        """Resurrect the publishes stalk.

        By default this brings back the LAST publish version from purgatory.

        Args:
            dont_resurrect_versions (bool, optional): If True, the versions of
                the publish will not be resurrected. Defaults to False.

        Returns:
            tuple: (state(int), message(str)): 1 if the operation is
                successful, -1 otherwise. A message is returned as well.
        """
        # if the upstream work is deleted, first resurrect the work (and everything above)
        if self.work_object.deleted:
            state = self.work_object.resurrect()
            if state == -1:
                return -1

        if not dont_resurrect_versions:
            # resurrect only the last version. This is because we dont want any versionless works.
            self.all_versions[-1].resurrect()
        return 1