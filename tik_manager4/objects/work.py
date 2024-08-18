# pylint: disable=super-with-arguments
# pylint: disable=consider-using-f-string
"""Module for Work object."""

import socket
import shutil
import platform
import subprocess
from pathlib import Path
from tik_manager4.core import utils
from tik_manager4.dcc.standalone.main import Dcc as StandaloneDcc
from tik_manager4.core.settings import Settings
from tik_manager4.core import filelog
from tik_manager4.objects.entity import Entity
from tik_manager4.objects.publish import Publish

# from tik_manager4.objects.publish import PublishVersion
# from tik_manager4 import dcc

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")


class Work(Settings, Entity):
    """Work object to handle works and publishes."""

    _standalone_handler = StandaloneDcc()
    object_type = "work"

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
        # there are 3 states: working, published, omitted
        self._parent_task = parent_task
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
        self._versions = self.get_property("versions", [])
        self._work_id = self.get_property("work_id", self._id)
        self._task_name = self.get_property("task_name", self._task_name)
        self._task_id = self.get_property("task_id")
        self._relative_path = self.get_property("path", self._relative_path)
        self._software_version = self.get_property("softwareVersion")
        self._state = self.get_property("state", self._state)
        if self._state == "working" and self.publish.versions:
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
        self._state = "working"
        self.edit_property("state", self._state)
        self.apply_settings()

    def get_last_version(self):
        """Return the last version of the work."""
        # First try to get the last version from the versions list. If not found, return 0.
        if self._versions:
            return self._versions[-1].get("version_number", self.version_count)
        else:
            return 0

    def get_version(self, version_number):
        """Return the version dictionary by version number.

        Args:
            version_number (int): Version number.
        """
        for version in self._versions:
            if version.get("version_number") == version_number:
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
        self._standalone_handler.text_to_image(extension, thumbnail_path, 220, 124)
        version = {
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
        self._versions.append(version)
        self.edit_property("versions", self._versions)
        self.apply_settings(force=True)
        return version

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

        abs_version_path = self.get_abs_project_path(self.name, version_name)
        thumbnail_path = self.get_abs_database_path("thumbnails", thumbnail_name)
        Path(abs_version_path).parent.mkdir(parents=True, exist_ok=True)

        self._dcc_handler.pre_save()
        # save the file
        output_path = self._dcc_handler.save_as(abs_version_path)

        # on some occasions the save as method may return a different path.
        # for example, if the file cannot be saved with specified file format,
        # extractor logic may decide to force something else.
        if output_path != abs_version_path:
            version_name = Path(output_path).name  # e.g. "test_v001.ma"
            file_format = Path(output_path).suffix  # e.g. ".ma"

        # generate thumbnail
        # create the thumbnail folder if it doesn't exist
        Path(thumbnail_path).parent.mkdir(parents=True, exist_ok=True)
        self._dcc_handler.generate_thumbnail(thumbnail_path, 220, 124)

        # add it to the versions
        version = {
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
        self._versions.append(version)
        self.edit_property("versions", self._versions)
        self.apply_settings(force=True)

        self._dcc_handler.post_save()
        return version

    def make_preview(
        self, version_number, camera, resolution, frame_range, label=None, settings=None
    ):
        """Initiate a playblast for the given version.

        Args:
            version_number (int): Version number.
            camera (str): Camera name.
            resolution (list): Resolution of the playblast. [width, height]
            frame_range (list): Range of the playblast.
                [start_frame, end_frame]
            label (str): Label of the playblast. Optional.
            settings (dict): Settings for the playblast.
                If not given, default settings will be used.

        Returns:
            bool: True if successful, False otherwise.
        """

        preview_settings = settings or {}
        preview_folder = self.get_abs_project_path("previews")
        Path(preview_folder).mkdir(parents=True, exist_ok=True)

        nice_name, full_name = self.resolve_preview_names(
            version_number, camera, label=label
        )

        # camera code can be a node, path, uuid or name depending on the dcc
        camera_code = self._dcc_handler.get_scene_cameras()[camera]
        preview_file_abs_path = self._dcc_handler.generate_preview(
            full_name,
            preview_folder,
            camera_code=camera_code,
            resolution=resolution,
            range=frame_range,
            settings=preview_settings,
        )
        if preview_file_abs_path:
            suffix = Path(preview_file_abs_path).suffix
            if settings.get("PostConversion", False) and suffix != ".mp4":
                ffmpeg = self._check_ffmpeg()
                if ffmpeg:
                    preview_file_abs_path = self._convert_preview(
                        preview_file_abs_path, ffmpeg, overwrite=True
                    )
                else:
                    LOG.warning("FFMPEG not found. Skipping conversion.")

            relative_path = Path("previews") / Path(preview_file_abs_path).name
            version = self.get_version(version_number)
            new_preview_data = {nice_name: str(relative_path)}

            if "previews" in version.keys():
                version["previews"].update(new_preview_data)
            else:
                version["previews"] = new_preview_data

            self.apply_settings(force=True)
            utils.execute(preview_file_abs_path)
            return True
        else:
            return False

    def _convert_preview(self, preview_file_abs_path, ffmpeg, overwrite=False):
        """Convert the preview file to a compatible format.

        Args:
            preview_file_abs_path (str): Absolute path of the preview file.
            ffmpeg (str): Path to the ffmpeg executable.
            overwrite (bool): If True, overwrite the existing file.

        Returns:
            str: Absolute path of the converted file.
        """

        compatible_videos = [".avi", ".mov", ".mp4", ".flv", ".webm", ".mkv"]
        compatible_images = [".tga", ".jpg", ".exr", ".png", ".pic"]

        # get the conversion lut
        presetLUT = {
            "videoCodec": "-c:v libx264 -profile:v baseline -level 3.0 -pix_fmt yuv420p",
            "compression": "-crf 23",
            "foolproof": "-vf scale=ceil(iw/2)*2:ceil(ih/2)*2",
            "speed": "-preset ultrafast",
            "resolution": "",
            "audioCodec": "-c:a aac",
        }

        # set output file
        _file_path = Path(preview_file_abs_path)
        is_image_seq = _file_path.suffix in compatible_images
        # change the extension to mp4
        output_file = _file_path.with_suffix(".mp4")
        output_file_str = str(output_file)

        # deal with the existing output
        if output_file.exists():
            if overwrite:
                output_file.unlink()
            else:
                return
        # if the suffix is in compatible videos, use the video conversion settings
        if not is_image_seq:
            flag_start = [ffmpeg, "-i", str(_file_path)]
        else:
            # get the frame rate from dcc
            fps = self._dcc_handler.get_scene_fps()
            # the incoming _file_path needs to have %04d in it in order to be recognized as a sequence
            flag_start = [ffmpeg, "-r", str(fps), "-i", str(_file_path)]
            # remove the digits section from the file name e.g. test_v001.0001.jpg -> test_v001.jpg
            output_file_str = str(output_file).replace(output_file.suffixes[0], "")
        full_flag_list = (
            flag_start
            + presetLUT["videoCodec"].split()
            + presetLUT["compression"].split()
            + presetLUT["audioCodec"].split()
            + presetLUT["resolution"].split()
            + presetLUT["foolproof"].split()
            + [output_file_str]
        )
        if platform.system() == "Windows":
            subprocess.check_call(full_flag_list, shell=False)
        else:
            subprocess.check_call(full_flag_list)
        if _file_path.suffix in compatible_videos:
            _file_path.unlink()
        # TODO: Delete the file sequences too
        return output_file_str

    def _check_ffmpeg(self):
        """Check if the FFMPEG is installed or accessible."""
        if platform.system() == "Windows":
            # get the ffmpeg.exe from the parallel folder 'external'
            parent_folder = Path(__file__).parent.parent
            ffmpeg_folder = parent_folder / "external" / "ffmpeg"
            ffmpeg = ffmpeg_folder / "ffmpeg.exe"
            if not ffmpeg.exists():
                return False
            else:
                return str(ffmpeg)
        else:
            try:
                v = subprocess.call(
                    ["ffmpeg", "-version"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                return "ffmpeg"
            except OSError:
                return False

    def resolve_preview_names(self, version, camera, label=None):
        """Resolve the preview name.

        Args:
            version (int): Version number.
            camera (str): Camera name.
            label (str, optional): Label for the preview.
        """
        # get rid of the namespace
        camera = camera.split(":")[-1]
        if not label:
            nice_name = [camera]
        else:
            nice_name = [camera, label]

        full_name = nice_name + [self._name, f"v{version:03d}"]
        return "_".join(nice_name), "_".join(full_name)

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
            relative_path = version_obj.get("scene_path")
            abs_path = self.get_abs_project_path(relative_path)
            self._dcc_handler.open(abs_path, force=force)

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
            relative_path = version_obj.get("scene_path")
            abs_path = self.get_abs_project_path(relative_path)
            _ingest_obj = self._dcc_handler.ingests[ingestor]()
            # feed the metadata from the parent subproject
            _ingest_obj.metadata = self.get_metadata(self.parent_task)
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
            relative_path = version_obj.get("scene_path")
            abs_path = self.get_abs_project_path(relative_path)
            _ingest_obj = self._dcc_handler.ingests[ingestor]()
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
                    if version.get("user") != self.guard.user:
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

        CAUTION: This is a destructive operation. Use with care.

        Returns:
            tuple: (state(int), message(str)): 1 if the operation is
                successful, -1 otherwise. A message is returned as well.
        """
        state, msg = self.check_destroy_permissions()
        if not state:
            return -1, msg

        if self.publish.versions:
            self.publish.destroy()

        purgatory_database_dir = Path(self.get_purgatory_database_path())
        purgatory_database_dir.mkdir(parents=True, exist_ok=True)
        purgatory_scene_dir = Path(self.get_purgatory_project_path())
        purgatory_scene_dir.mkdir(parents=True, exist_ok=True)

        purgatory_path = self.get_purgatory_project_path(self.name)
        # if the purgatory path exists, delete it first
        if Path(purgatory_path).exists():
            shutil.rmtree(purgatory_path)
        shutil.move(
            self.get_abs_project_path(self.name),
            purgatory_path,
            copy_function=shutil.copytree,
        )

        thumbnails_dir = Path(self.get_abs_database_path("thumbnails"))
        # collect all thumbnails starting with the work name
        thumbnails = thumbnails_dir.glob(f"{self.name}_*")
        for thumbnail in thumbnails:
            thumb_destination_dir = purgatory_database_dir / "thumbnails"
            thumb_destination_dir.mkdir(parents=True, exist_ok=True)
            thumb_destination_file = thumb_destination_dir / thumbnail.name
            shutil.move(str(thumbnail), str(thumb_destination_file))

        # finally move the database file
        db_destination = purgatory_database_dir / Path(self.settings_file).name
        shutil.move(str(self.settings_file), str(db_destination))
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
            if self.guard.user != version_obj.get("user"):
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
            relative_path = version_obj.get("scene_path")
            abs_path = self.get_abs_project_path(relative_path)
            dest_path = self.get_purgatory_project_path(relative_path)
            # shutil.move(abs_path, dest_path, copy_function=shutil.copytree)
            Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
            if Path(abs_path).exists():
                shutil.move(abs_path, dest_path)

            # move the thumbnail
            thumbnail_relative_path = version_obj.get("thumbnail", None)
            if thumbnail_relative_path:
                thumbnail_abs_path = self.get_abs_database_path(thumbnail_relative_path)
                thumbnail_dest_path = self.get_purgatory_database_path(
                    thumbnail_relative_path
                )
                _thumbnail_dest_path = Path(thumbnail_dest_path)
                _thumbnail_dest_path.parent.mkdir(parents=True, exist_ok=True)
                if Path(thumbnail_abs_path).exists():
                    # first try to delete the thumbnail_dest_path if exists
                    if _thumbnail_dest_path.exists():
                        _thumbnail_dest_path.unlink()
                    shutil.move(
                        thumbnail_abs_path,
                        thumbnail_dest_path,
                        copy_function=shutil.copytree,
                    )

            # remove the version from the versions list
            self._versions.remove(version_obj)
            self.edit_property("versions", self._versions)
            self.apply_settings(force=True)
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
        # version_obj["thumbnail"] = relative_path
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
            self._dcc_handler.generate_thumbnail(target_absolute_path, 220, 124)
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

    # def get_metadata(self, parent_task, key=None):
    #     """Convenience method to get the metadata for work and category objects."""
    #     # if this is a subproject, get the metadata directly from the attribute.
    #     if not parent_task:
    #         return None
    #     parent_sub = parent_task.parent_sub
    #     if not parent_sub:
    #         return None
    #     if key:
    #         return parent_sub.metadata.get_value(key, None)
    #     return parent_sub.metadata