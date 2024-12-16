"""Preview Module."""

import platform
import subprocess
from pathlib import Path
from typing import List, Tuple

from tik_manager4.core.constants import ObjectType
from tik_manager4.core import filelog
from tik_manager4.core import utils

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")

class PreviewContext:
    """Data class to hold the preview context."""
    def __init__(self,
                 enabled=True,
                 camera=None,
                 label=None,
                 resolution=None,
                 frame_range=None,
                 version_number=None):
        """Initialize the PreviewContext object."""
        self._enabled: bool = enabled
        self._camera: str = camera
        self._label: str = label
        self._resolution: List[int] = resolution
        self._frame_range: Tuple[int, int] = frame_range
        self._version_number: int = version_number

    @property
    def enabled(self):
        """Preview context enabled."""
        return self._enabled

    def set_enabled(self, value):
        """Set the enabled state.

        Args:
            value (bool): The enabled state.
        """
        self._enabled = value

    @property
    def camera(self):
        """Preview context camera."""
        return self._camera

    def set_camera(self, value):
        """Set the camera.

        Args:
            value (str): The camera name.
        """
        self._camera = value

    @property
    def label(self):
        """Preview context label."""
        return self._label

    def set_label(self, value):
        """Set the label.

        Args:
            value (str): The label.
        """
        self._label = value

    @property
    def resolution(self):
        """Preview context resolution."""
        return self._resolution

    def set_resolution(self, value):
        """Set the resolution.

        Args:
            value (list, tuple): The resolution.
        """
        self._resolution = value

    @property
    def frame_range(self):
        """Preview context frame range."""
        return self._frame_range

    def set_frame_range(self, value):
        """Set the frame range.

        Args:
            value (list, tuple): The frame range.
        """
        self._frame_range = value

    @property
    def version_number(self):
        """Preview context version number."""
        return self._version_number

    def set_version_number(self, value):
        """Set the version number.

        Args:
            value (int): The version number.
        """
        self._version_number = value

    @staticmethod
    def get_default_camera(cameras):
        """Convenience function to get the default camera with priority."""
        # Define the priority list
        priority_list = ['front', 'back', 'top', 'bottom', 'persp']

        # Filter out cameras that are not in the priority list
        filtered_cameras = [cam for cam in cameras if cam not in priority_list]

        # If there are cameras not in the priority list, return the first one
        if filtered_cameras:
            return filtered_cameras[0]

        # If 'persp' is in the list, return it
        if 'persp' in cameras:
            return 'persp'

        # Otherwise, return the first camera in the list
        return cameras[0]

class Preview:
    """Preview class."""
    def __init__(self, preview_context, database_object, settings=None, message_callback=None):
        """Initialize the Preview object.

        Args:
            preview_context (PreviewContext): The preview context.
            database_object (WorkObject): The Work object. or PublishVersion
            settings (dict, optional): Additional settings. Defaults to None.
            message_callback (function, optional): The message callback function. Defaults to None.
        """

        self.context = preview_context
        self.database_obj = database_object
        self._settings = settings or {}
        self._path = None
        self._message_callback = message_callback or LOG.info

        self._folder = self.database_obj.get_abs_project_path("previews")
        Path(self._folder).mkdir(parents=True, exist_ok=True)

    def set_message_callback(self, callback):
        """Set the message callback function.

        Args:
            callback (function): The message callback function.
        """
        if callback:
            self._message_callback = callback
        else:
            # if there is no message callback, use stdout
            self._message_callback = LOG.info

    @property
    def settings(self):
        """Preview settings."""
        return self._settings

    @settings.setter
    def settings(self, value):
        """Set the preview settings.

        Args:
            value (dict): The preview settings.
        """
        self._settings = value

    def generate(self, show_after=True):
        """Generate the preview."""
        if not self._verify_context():
            return False

        nice_name, full_name = self.resolve_preview_name()

        # camera code can be a node, path, uuid or name depending on the dcc
        camera_code = self.database_obj.dcc_handler.get_scene_cameras()[self.context.camera]
        abs_path = self.database_obj.dcc_handler.generate_preview(
            full_name,
            self._folder,
            camera_code=camera_code,
            resolution=self.context.resolution,
            range=self.context.frame_range,
            settings=self._settings,
        )
        if not abs_path:
            self._message_callback("Preview generation failed.")
            LOG.error("Preview generation failed.")
            return False

        suffix = Path(abs_path).suffix
        if self._settings.get("PostConversion", False) and suffix != ".mp4":
            self._message_callback("Converting the preview to MP4 format.")
            ffmpeg = self._check_ffmpeg()
            if ffmpeg:
                abs_path = self._convert_preview(abs_path, ffmpeg, overwrite=True)
            else:
                self._message_callback("FFMPEG not found. Skipping conversion.")
                LOG.warning("FFMPEG not found. Skipping conversion.")

        relative_path = Path("previews") / Path(abs_path).name

        preview_data = {nice_name: relative_path.as_posix()}

        self._message_callback("Registering preview data.")
        self.register_data(preview_data)

        if show_after:
            utils.execute(abs_path)
        return abs_path

    def register_data(self, preview_data):
        """Register the preview data to the database object."""
        if self.database_obj.object_type == ObjectType.WORK:
            # if this is a work object, we need to update the specific version dictionary.
            version = self.database_obj.get_version(self.context.version_number)
            if "previews" in version.keys():
                version["previews"].update(preview_data)
            else:
                version["previews"] = preview_data
            self.database_obj.apply_settings(force=True)
        elif self.database_obj.object_type == ObjectType.PUBLISH_VERSION:
            # PublishVersion object has no version number, so we update the previews directly
            # Unlike the work objects version, this is a Tik Settings class.
            self.database_obj.add_property("previews", preview_data)
            self.database_obj.apply_settings(force=True)

    def _verify_context(self):
        """Verify the preview context."""

        if not self.context.camera:
            LOG.error("Camera not set.")
            return False

        # work object requires version number
        if self.database_obj.object_type == ObjectType.WORK:
            if not self.context.version_number:
                LOG.error("Version number not set. Work object requires version number.")
                return False
        elif self.database_obj.object_type == ObjectType.PUBLISH_VERSION:
            self.context.set_version_number(self.database_obj.version)
        return True

    def resolve_preview_name(self):
        """Resolve the preview name.

        Returns:
            tuple: The nice name and the full name tags.
        """
        camera = self.context.camera.split(":")[-1]
        if not self.context.label:
            nice_name = [camera]
        else:
            nice_name = [camera, self.context.label]

        full_name_tags = (nice_name + [
            self.database_obj.name,
            f"v{self.context.version_number:03d}"
        ])
        return "_".join(nice_name), "_".join(full_name_tags)

    def _check_ffmpeg(self) -> str or bool:
        """Check if the FFMPEG is installed or accessible."""
        if platform.system() == "Windows":
            # get the ffmpeg.exe from the parallel folder 'external'
            parent_folder = Path(__file__).parent.parent
            ffmpeg_folder = parent_folder / "external" / "ffmpeg"
            ffmpeg = ffmpeg_folder / "ffmpeg.exe"
            if not ffmpeg.exists():
                return False
            return str(ffmpeg)
        else:
            try:
                _verify = subprocess.call(
                    ["ffmpeg", "-version"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                return "ffmpeg"
            except OSError:
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
        preset_lut = {
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
                return None
        # if the suffix is in compatible videos, use the video conversion settings
        if not is_image_seq:
            flag_start = [ffmpeg, "-i", str(_file_path)]
        else:
            # get the frame rate from dcc
            fps = self.database_obj.dcc_handler.get_scene_fps()
            # the incoming _file_path needs to have %04d in it in order to be recognized as a sequence
            flag_start = [ffmpeg, "-r", str(fps), "-start_number", str(self.context.frame_range[0]), "-i", str(_file_path)]
            # remove the digits section from the file name e.g. test_v001.0001.jpg -> test_v001.jpg
            output_file_str = str(output_file).replace(output_file.suffixes[0], "")
        full_flag_list = (
            flag_start
            + preset_lut["videoCodec"].split()
            + preset_lut["compression"].split()
            + preset_lut["audioCodec"].split()
            + preset_lut["resolution"].split()
            + preset_lut["foolproof"].split()
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
