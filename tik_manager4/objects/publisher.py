# pylint: disable=super-with-arguments
# pylint: disable=consider-using-f-string
"""Publisher Handler module.

This module is responsible for handling the publish process.
"""
import logging
from pathlib import Path

from tik_manager4.core import filelog

from tik_manager4.objects.preview import Preview
from tik_manager4.dcc.standalone import main as standalone
from tik_manager4.objects.publish import PublishVersion
from tik_manager4.objects.guard import Guard

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")


class Publisher:
    """Publisher class to handle the publish process."""

    guard = Guard()

    def __init__(self, project_object):
        """Initialize the Publisher object."""
        self._dcc_handler = self.guard.dcc_handler
        self._project_object = project_object
        self._work_object = None
        self._work_version: int = 0
        self._metadata = None

        # resolved variables
        self._resolved_extractors = {}
        self._resolved_validators = {}
        self._abs_publish_data_folder = None
        self._abs_publish_scene_folder = None
        self._publish_file_name = None
        self._publish_version = None

        # class variables
        self._published_object = None
        self.warnings = []

    @property
    def validators(self):
        """List of resolved validators."""
        return self._resolved_validators

    @property
    def extractors(self):
        """List of resolved extractors."""
        return self._resolved_extractors

    @property
    def work_object(self):
        """The Work object that will be published."""
        return self._work_object

    @property
    def task_object(self):
        """The Task object that will be published."""
        if not self._work_object:
            return None
        return self._work_object.parent_task or \
        self._project_object.find_task_by_id(self._work_object.task_id)

    def resolve(self):
        """Resolve the publish data file name.

        Returns:
            str: The resolved publish data file name.
        """
        self._work_object, self._work_version = self._project_object.get_current_work()

        if not self._work_object:
            LOG.warning("No work object found. Aborting.")
            return False

        self._resolved_extractors = {}
        self._resolved_validators = {}

        self._metadata = self.task_object.metadata

        category_definitions = self._work_object.guard.category_definitions
        category_props = category_definitions.properties.get(
            self._work_object.category, {})

        extracts = category_props.get("extracts", [])
        validations = category_definitions.properties.get(
            self._work_object.category, {}
        ).get("validations", [])

        dcc_extracts = self._dcc_handler.extracts

        for extract, handler in dcc_extracts.items():
            if extract in extracts:
                resolved = handler()
                resolved.category = self._work_object.category
                resolved.metadata = self._metadata
                self._resolved_extractors[extract] = resolved

        # Sort the extractors to match the order in category definitions
        self._resolved_extractors = dict(
            sorted(self._resolved_extractors.items(),
                   key=lambda x: extracts.index(x[0]))
        )

        for validation in validations:
            if validation in list(self._dcc_handler.validations.keys()):
                self._resolved_validators[validation] = self._dcc_handler.validations[
                    validation
                ]()
                self._resolved_validators[validation].metadata = self._metadata

        self._resolved_validators = dict(
            sorted(self._resolved_validators.items(),
                   key=lambda x: validations.index(x[0]))
        )

        latest_publish_version = self._work_object.publish.get_last_version()

        self._abs_publish_data_folder = (
            self._work_object.publish.get_publish_data_folder()
        )
        self._abs_publish_scene_folder = (
            self._work_object.publish.get_publish_project_folder()
        )
        self._publish_version = latest_publish_version + 1
        self._publish_file_name = (
            f"{self._work_object.name}_v{self._publish_version:03d}.tpub"
        )
        return self._publish_file_name

    def reserve(self):
        """Reserve the slot for publish.

        Makes sure that no other process overrides the publish.
        """
        # make sure the publish file is not already exists
        _publish_file_path = (
            Path(self._abs_publish_data_folder) / self._publish_file_name
        )
        if _publish_file_path.exists():
            raise ValueError(f"Publish file already exists. {_publish_file_path}")

        self._published_object = PublishVersion(str(_publish_file_path))

        self._published_object.add_property("name", self._work_object.name)
        self._published_object.add_property("creator", self._work_object.guard.user)
        self._published_object.add_property("category", self._work_object.category)
        self._published_object.add_property("dcc", self._work_object.guard.dcc)
        self._published_object.add_property(
            "publish_id", self._published_object.generate_id()
        )
        self._published_object.add_property("version_number", self._publish_version)
        self._published_object.add_property("work_version", self._work_version)
        self._published_object.add_property("task_name", self._work_object.task_name)
        self._published_object.add_property("task_id", self._work_object.task_id)
        self._published_object.add_property(
            "path", Path(self._work_object.path, "publish").as_posix()
        )
        self._published_object.add_property(
            "dcc_version", self._dcc_handler.get_dcc_version()
        )
        self._published_object.add_property("elements", [])
        self._published_object.init_properties()  # make sure the properties are initialized
        is_localized = self._published_object.can_localize()
        if is_localized:
            self._published_object.add_property("localized", True)
            self._published_object.add_property("localized_path", self._published_object.get_output_path())

        self._published_object.apply_settings()  # make sure the file is created
        self._published_object.init_properties()  # make sure the properties are initialized
        self._published_object._dcc_handler.pre_publish()

    def validate(self):
        """Validate the scene using the resolved validators."""
        for _val_name, val_object in self._resolved_validators.items():
            val_object.validate()

    def write_protect(self, file_or_folder_path):
        """Protect the given file or folder making it read-only.

        Args:
            file_or_folder_path (str): The path to the file or folder.
        """
        path = Path(file_or_folder_path)
        file_list = []
        if path.is_file():
            file_list.append(path)
        elif path.is_dir():
            for _file in path.rglob("*"):
                file_list.append(_file)
        for _file in file_list:
            try:
                _file.chmod(0o444)
            except Exception as e:  # pylint: disable=broad-except
                LOG.warning(f"File protection failed: {_file}")

    def extract_single(self, extract_object):
        """Extract only from the given extract object.

        Args:
            extract_object (Extract): The extract object to extract.
        """
        publish_path = Path(self._published_object.get_output_path(self._work_object.name))
        extract_object.category = self._work_object.category  # define the category
        extract_object.extract_folder = publish_path.as_posix()  # define the extract folder
        extract_object.extract_name = f"{self._work_object.name}"  # define the extract name
        extract_object.version_string = f"v{self._publish_version:03d}"  # define the version string
        extract_object.extract()
        self.write_protect(extract_object.resolve_output())

    def extract(self):
        """Extract the elements.

        Uses all resolved extractors to extract the elements.
        """
        # first save the scene
        self._dcc_handler.save_scene()
        for _extract_type_name, extract_object in self._resolved_extractors.items():
            self.extract_single(extract_object)
            yield extract_object

    def publish(self,
                notes=None,
                preview_context=None,
                message_callback=None,
                management_task_id=None,
                management_task_status_to=None
                ):
        """Finalize the publish by updating the reserved slot.

        Args:
            notes (str, optional): The notes to add to the publish.
            preview_context (PreviewContext, optional): The preview context.
            message_callback (function, optional): The message callback function.
            management_task_id (str, optional): The management task id.
            management_task_status_to (str, optional): When defined, the task
                on management platform will be set to the given value.

        Returns:
            PublishVersion: The published object.
        """
        self.warnings = []
        # use either given message callback function or a generic logging function
        message_callback = message_callback or logging.getLogger(__name__).info
        # collect the validation states and log it into the publish object
        validations = {}
        for validation_name, validation_object in self._resolved_validators.items():
            validations[validation_name] = validation_object.state
        self._published_object.add_property("validations", validations)

        # collect the extracted elements information and add to the publish object
        for _extract_type_name, extract_object in self._resolved_extractors.items():
            if (
                extract_object.state == "failed"
                or extract_object.state == "unavailable"
                or not extract_object.enabled
            ):
                continue
            element = {
                "name": extract_object.nice_name,
                "type": extract_object.name,
                "suffix": extract_object.extension,
                "path": Path(extract_object.resolve_output())
                .relative_to(self._published_object.get_output_path())
                .as_posix(),
                "bundled": extract_object.bundled,
                "bundle_info": extract_object.bundle_info,
                "bundle_match_id": extract_object.bundle_match_id,
            }
            self._published_object._elements.append(element)

        self._published_object.edit_property(
            "elements", self._published_object._elements
        )
        if not notes:
            notes = "[Auto Generated]"
        self._published_object.add_property("notes", notes)

        abs_thumbnail_path = self._generate_thumbnail()

        preview_abs_path = None
        if preview_context:
            message_callback(f"Generating preview")
            try:
                preview_abs_path = self._generate_preview(preview_context, message_callback)
            except Exception as e:  # pylint: disable=broad-except
                message_callback("Preview generation failed.")
                self.warnings.append("Preview generation failed. See the log for details.")
                LOG.error(f"Preview generation failed: {e}")

        if management_task_id:
            management_platform = self._project_object.settings.get(
                "management_platform", "Management Platform")
            message_callback(f"Publishing to {management_platform}")
            try:
                self.publish_to_management(
                    management_task_id,
                    management_task_status_to,
                    description=notes,
                    thumbnail=abs_thumbnail_path,
                    preview=preview_abs_path,
                )
            except Exception as e:  # pylint: disable=broad-except
                msg = f"Publish to {management_platform} failed. See the log for details."
                message_callback(msg)
                self.warnings.append(msg)
                LOG.error(f"Publish to {management_platform} failed: {e}")

        self._published_object.apply_settings(force=True)
        self._published_object.make_live()

        # hook for post publish can be defined in per dcc handler.
        message_callback("Performing post publish operations")
        self._published_object._dcc_handler.post_publish()
        return self._published_object

    def _generate_preview(self, preview_context, message_callback=None):
        """Generate the preview."""
        if not preview_context.enabled:
            return
        preview_handler = Preview(preview_context, self._published_object)
        preview_handler.settings = self._published_object.guard.preview_settings.properties
        preview_handler.set_message_callback(message_callback)
        return preview_handler.generate(show_after=False)

    def _generate_thumbnail(self):
        """Generate the thumbnail."""
        thumbnail_name = f"{self._work_object.name}_v{self._publish_version:03d}.jpg"
        thumbnail_resolution = self._work_object.guard.preview_settings.properties.get("ThumbnailResolution", [220, 124])
        thumbnail_path = self._published_object.get_abs_database_path(
            "thumbnails", thumbnail_name
        )
        Path(thumbnail_path).parent.mkdir(parents=True, exist_ok=True)
        self._dcc_handler.generate_thumbnail(thumbnail_path, *(thumbnail_resolution))
        self._published_object.add_property(
            "thumbnail", Path("thumbnails", thumbnail_name).as_posix()
        )
        return thumbnail_path # abs path

    def discard(self):
        """Discard the reserved slot."""
        # find any extracted files and delete them
        for _extract_type_name, extract_object in self._resolved_extractors.items():
            if extract_object.state == "failed":
                continue
            _extracted_file_path = Path(extract_object.resolve_output())
            if _extracted_file_path.exists():
                # remove the write protection
                _extracted_file_path.chmod(0o777)
                _extracted_file_path.unlink()

        # delete the publish file
        _publish_file_path = (
            Path(self._abs_publish_data_folder) / self._publish_file_name
        )
        if _publish_file_path.exists():
            _publish_file_path.unlink()
        self._published_object = None
        LOG.info("Publish discarded.")

    @property
    def metadata(self):
        """Metadata associated with the parent subproject."""
        return self._metadata

    @property
    def publish_version(self):
        """Resolved publish version."""
        return self._publish_version

    @property
    def publish_name(self):
        """Resolved publish name."""
        return self._publish_file_name

    @property
    def absolute_data_path(self):
        """Resolved absolute data path."""
        return self._abs_publish_data_folder

    @property
    def absolute_scene_path(self):
        """Resolved absolute scene path."""
        return self._abs_publish_scene_folder

    @property
    def relative_data_path(self):
        """Resolved relative path."""
        if self._work_object:
            return (
                Path(self._abs_publish_data_folder)
                .relative_to(self._work_object.guard.project_root)
                .as_posix()
            )
        return None

    @property
    def relative_scene_path(self):
        """Resolved relative path."""
        if self._work_object:
            return (
                Path(self._abs_publish_scene_folder)
                .relative_to(self._work_object.guard.project_root)
                .as_posix()
            )
        return None

    def publish_to_management(self, management_task_id, status, description="", thumbnail=None, preview=None):
        """Publish the data to the management system."""
        entity_type = self.task_object.type
        entity_id = self._work_object.task_id
        path = self.relative_scene_path
        name = self.publish_name
        project_id = self._project_object.settings.get("host_project_id")

        # Check if the thumbnail and preview paths are existing
        if thumbnail and not Path(thumbnail).exists():
            LOG.warning(f"Thumbnail path does not exist: {thumbnail}")
            thumbnail = None

        if preview and not Path(preview).exists():
            LOG.warning(f"Preview path does not exist: {preview}")
            preview = None

        user_email = self.guard.email
        management_version = self.guard.management_handler.publish_version(
            entity_type=entity_type,
            entity_id=entity_id,
            task_id=management_task_id,
            name=name,
            path=path,
            project_id=project_id,
            status=status,
            description=description,
            thumbnail=thumbnail,
            preview=preview,
            email=user_email,
            publish_version=self._publish_version
        )
        self._published_object.edit_property("publish_id", management_version["id"])


    def get_management_tasks(self):
        """Get the management tasks from the platform manager (i.e. Shotgrid).

        This method collects the platform tasks associated with the work
        object and returns them. It is important to note that platform tasks
        are not the same as the tik tasks.
        """
        if not self._work_object:
            LOG.warning("No work object found. Aborting.")
            return []
        # get the id from the project settings
        entity_id = self._work_object.task_id
        entity_type = self.task_object.type
        step = self._work_object.category
        project_id = self._project_object.settings.get("host_project_id")
        # get the tasks from the platform manager
        list_of_tasks = self.guard.management_handler.request_tasks(
            entity_id, entity_type, step, project_id
        )
        return list_of_tasks


class SnapshotPublisher(Publisher):
    """Separate publisher to handle arbitrary file and folder publishing.

    Handles automatically creating a new work version if the current work is
    not there.
    """

    def __init__(self, *args):
        """Initialize the SnapshotPublisher object."""
        super(SnapshotPublisher, self).__init__(args)
        # this overrides the dcc handler which resolved on inherited
        # class to standalone
        self._dcc_handler = standalone.Dcc()

    @property
    def work_object(self):
        """Work object."""
        return self._work_object

    @work_object.setter
    def work_object(self, value):
        """Set the work object.

        Args:
            value (Work): The work object.
        """
        self._work_object = value

    @property
    def work_version(self):
        """Work version."""
        return self._work_version

    @work_version.setter
    def work_version(self, value):
        """Set the work version.

        Args:
            value (int): The work version.
        """
        self._work_version = value

    def resolve(self):
        """Resolve the file name for the snapshot.

        Returns:
            str: The resolved publish file name.
        """

        version_object = self._work_object.get_version(self._work_version)
        relative_path = version_object.scene_path
        abs_path = self._work_object.get_abs_project_path(relative_path)

        # get either the snapshot or snapshot_bundle depending if its a folder or file
        if Path(abs_path).is_dir():
            snapshot_extractor = self._dcc_handler.extracts["snapshot_bundle"]()
        else:
            snapshot_extractor = self._dcc_handler.extracts["snapshot"]()
        snapshot_extractor.category = self._work_object.category  # define the category

        snapshot_extractor.source_path = abs_path
        snapshot_extractor.extension = Path(abs_path).suffix

        self._resolved_extractors = {"snapshot": snapshot_extractor}
        self._resolved_validators = {}

        latest_publish_version = self._work_object.publish.get_last_version()

        self._abs_publish_data_folder = (
            self._work_object.publish.get_publish_data_folder()
        )
        self._abs_publish_scene_folder = (
            self._work_object.publish.get_publish_project_folder()
        )
        self._publish_version = latest_publish_version + 1
        self._publish_file_name = (
            f"{self._work_object.name}_v{self._publish_version:03d}.tpub"
        )
        return self._publish_file_name

    def _generate_thumbnail(self):
        """Generate the thumbnail."""
        thumbnail_name = f"{self._work_object.name}_v{self._publish_version:03d}.png"
        thumbnail_resolution = self._published_object.guard.preview_settings.properties.get("ThumbnailResolution", [220, 124])
        thumbnail_path = self._published_object.get_abs_database_path(
            "thumbnails", thumbnail_name
        )
        Path(thumbnail_path).parent.mkdir(parents=True, exist_ok=True)
        extension = self._resolved_extractors["snapshot"].extension or "Bundle"
        self._dcc_handler.text_to_image(
            extension, thumbnail_path, *(thumbnail_resolution), color="cyan"
        )
        self._published_object.add_property(
            "thumbnail", Path("thumbnails", thumbnail_name).as_posix()
        )
