"""Preview Module."""

import platform
import subprocess
from pathlib import Path
from typing import List, Tuple

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

# TODO:  Move the preview functions from work object here and make it available to be used by work and publishes (or maybe more)

class Preview:
    """Preview class."""
    def __init__(self, preview_context, work_object, settings=None):
        """Initialize the Preview object.

        Args:
            preview_context (PreviewContext): The preview context.
            work_object (WorkObject): The work object.
            settings (dict, optional): Additional settings. Defaults to None.
        """
        self.context = preview_context
        self.work = work_object
        self._settings = settings or {}
        self._path = None

        self._folder = self.work.get_abs_project_path("previews")
        Path(self._folder).mkdir(parents=True, exist_ok=True)

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
        camera_code = self.work.dcc_handler.get_scene_cameras()[self.context.camera]
        abs_path = self.work.dcc_handler.generate_preview(
            full_name,
            self._folder,
            camera_code=camera_code,
            resolution=self.context.resolution,
            frame_range=self.context.frame_range,
            settings=self._settings,
        )
        if not abs_path:
            LOG.error("Preview generation failed.")
            return False

        suffix = Path(abs_path).suffix
        if self._settings.get("PostConversion", False) and suffix != ".mp4":
            ffmpeg = self._check_ffmpeg()
            if ffmpeg:
                abs_path = self._convert_preview(abs_path, ffmpeg, overwrite=True)
            else:
                LOG.warning("FFMPEG not found. Skipping conversion.")

        relative_path = Path("previews") / Path(abs_path).name
        version = self.work.get_version(self.context.version_number)
        preview_data = {nice_name: relative_path.as_posix()}

        if "previews" in version.keys():
            version["previews"].update(preview_data)
        else:
            version["previews"] = preview_data
        self.work.apply_settings(force=True)
        if show_after:
            utils.execute(abs_path)
        return True

    def _verify_context(self):
        """Verify the preview context."""

        if not self.context.camera:
            LOG.error("Camera not set.")
            return False

        if not self.context.version_number:
            LOG.error("Version number not set.")
            return False
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
            self.work.name,
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
            fps = self.work.dcc_handler.get_scene_fps()
            # the incoming _file_path needs to have %04d in it in order to be recognized as a sequence
            flag_start = [ffmpeg, "-r", str(fps), "-i", str(_file_path)]
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
