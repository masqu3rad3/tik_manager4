# pylint: disable=super-with-arguments
# pylint: disable=consider-using-f-string
import os
import socket
import platform
import subprocess
from tik_manager4.core import utils
from tik_manager4.core.settings import Settings
from tik_manager4.core import filelog
from tik_manager4.objects.entity import Entity
from tik_manager4 import dcc

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")

class Work(Settings, Entity):
    _dcc_handler = dcc.Dcc()

    def __init__(self, absolute_path, name=None, path=None):
        super(Work, self).__init__()
        self.settings_file = absolute_path

        self._name = self.get_property("name") or name
        self._creator = self.get_property("creator") or self.guard.user
        self._category = self.get_property("category") or None
        self._dcc = self.get_property("dcc") or self.guard.dcc
        self._versions = self.get_property("versions") or []
        self._work_id = self.get_property("work_id") or self._id
        self._task_name = self.get_property("task_name") or None
        self._task_id = self.get_property("task_id") or None
        self._relative_path = self.get_property("path") or path
        self._software_version = self.get_property("softwareVersion") or None
        # there are 3 states: working, published, omitted
        self._state = self.get_property("state") or "working"
        self.modified_time = None  # to compare and update if necessary

        self._publishes = {}

    @property
    def state(self):
        return self._state

    @property
    def dcc(self):
        return self._dcc

    @property
    def id(self):
        return self._work_id

    @property
    def task_id(self):
        return self._task_id

    @property
    def creator(self):
        return self._creator

    @property
    def publishes(self):
        return self._publishes

    @property
    def versions(self):
        return self._versions

    @property
    def version_count(self):
        """Return the number of versions."""
        return len(self._versions)

    def reload(self):
        """Reload from file"""
        self.__init__(self.settings_file)

    def omit_work(self):
        """Omit the work."""
        self._state = "omitted"
        self.edit_property("state", self._state)
        self.apply_settings()

    def revive_work(self):
        """Revive the work."""
        self._state = "working" if not self.publishes else "published"
        self.edit_property("state", self._state)
        self.apply_settings()

    def get_last_version(self):
        """Return the last version of the work."""
        # First try to get last version from the versions list. If not found, return 0.
        if self._versions:
            return self._versions[-1].get("version_number", self.version_count)
        else:
            return 0

    def get_version(self, version_number):
        """Return the version dictionary by version number."""
        for version in self._versions:
            if version.get("version_number") == version_number:
                return version

    def new_version(self, file_format=None, notes=""):
        """Create a new version of the work."""

        state = self.check_permissions(level=1)
        if state != 1:
            return -1

        # validate file format
        file_format = file_format or self._dcc_handler.formats[0]
        if file_format not in self._dcc_handler.formats:
            raise ValueError("File format is not valid.")

        # get filepath of current version
        _version_number, _version_name, _thumbnail_name = self.construct_names(
            file_format
        )

        _abs_version_path = self.get_abs_project_path(_version_name)
        _thumbnail_path = self.get_abs_database_path("thumbnails", _thumbnail_name)
        self._io.folder_check(_abs_version_path)

        # save the file
        self._dcc_handler.save_as(_abs_version_path)

        # generate thumbnail
        # create the thumbnail folder if it doesn't exist
        self._io.folder_check(_thumbnail_path)
        self._dcc_handler.generate_thumbnail(_thumbnail_path, 100, 100)

        # add it to the versions
        _version = {
            "version_number": _version_number,
            "workstation": socket.gethostname(),
            "notes": notes,
            "thumbnail": os.path.join("thumbnails", _thumbnail_name).replace("\\", "/"),
            "scene_path": os.path.join("", _version_name).replace("\\", "/"),
            "user": self.guard.user,
            "previews": {},
            "file_format": file_format
        }
        self._versions.append(_version)
        self.edit_property("versions", self._versions)
        self.apply_settings(force=True)
        return _version

    def make_preview(self, version_number, camera, resolution, frame_range, label=None, settings=None):
        """Initiate a playblast for the given version.

        Args:
            version_number (int): Version number.
            camera (str): Camera name.
            resolution (list): Resolution of the playblast. [width, height]
            frame_range (list): Range of the playblast. [start_frame, end_frame]
            label (str): Label of the playblast. Optional.
            settings (dict): Settings for the playblast. If not given, default settings will be used.
        Returns (bool): True if successful. False otherwise.
        """

        preview_settings = settings or {}
        _preview_folder = self.get_abs_project_path("previews")
        self._io.folder_check(_preview_folder)

        _nice_name, _full_name = self.resolve_preview_names(version_number, camera, label=label)

        preview_file_abs_path = self._dcc_handler.generate_preview(_full_name, _preview_folder, camera=camera,
                                                                   resolution=resolution, range=frame_range,
                                                                   settings=preview_settings)
        if preview_file_abs_path:
            if settings.get("PostConversion", False):
                ffmpeg = self._check_ffmpeg()
                if ffmpeg:
                    preview_file_abs_path = self._convert_preview(preview_file_abs_path, ffmpeg, overwrite=True)
                else:
                    LOG.warning("FFMPEG not found. Skipping conversion.")

            _relative_path = os.path.join("previews", os.path.basename(preview_file_abs_path)).replace("\\", "/")
            _version = self.get_version(version_number)
            new_preview_data = {
                _nice_name: _relative_path
            }


            if "previews" in _version.keys():
                _version["previews"].update(new_preview_data)
            else:
                _version["previews"] = new_preview_data

            self.apply_settings(force=True)
            utils.execute(preview_file_abs_path)
            return True
        else:
            return False

    def _convert_preview(self, preview_file_abs_path, ffmpeg, overwrite=False):
        # TODO: Format validation

        # get the conversion lut
        presetLUT = {
            "videoCodec": "-c:v libx264 -profile:v baseline -level 3.0 -pix_fmt yuv420p",
            "compression": "-crf 23",
            "foolproof": "-vf scale=ceil(iw/2)*2:ceil(ih/2)*2",
            "speed": "-preset ultrafast",
            "resolution": "",
            "audioCodec": "-c:a aac"
        }

        # set output file
        base, ext = os.path.splitext(preview_file_abs_path)
        output_file = "%s.mp4" % (base)
        # deal with the existing output
        if os.path.isfile(output_file):
            if overwrite:
                os.remove(output_file)
            else:
                return

        flagStart = ["%s" % ffmpeg, "-i", preview_file_abs_path]

        fullFlagList = flagStart + \
                       presetLUT["videoCodec"].split() + \
                       presetLUT["compression"].split() + \
                       presetLUT["audioCodec"].split() + \
                       presetLUT["resolution"].split() + \
                       presetLUT["foolproof"].split() + \
                       [str(output_file)]

        if platform.system() == "Windows":
            subprocess.check_call(fullFlagList, shell=False)
        else:
            subprocess.check_call(fullFlagList)
        os.remove(preview_file_abs_path)
        return output_file

    def _check_ffmpeg(self):
        """Checks if the FFMPEG present in the system"""
        if platform.system() == "Windows":
            # get the ffmpeg.exe from the parallel folder 'external'
            parent_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ffmpeg_folder = os.path.join(parent_folder, "external", "ffmpeg")
            ffmpeg = os.path.join(ffmpeg_folder, "ffmpeg.exe")
            if not os.path.isfile(ffmpeg):
                return False
            else:
                return ffmpeg
        else:
            try:
                v = subprocess.call(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return "ffmpeg"
            except OSError:
                return False

    def resolve_preview_names(self, version, camera, label=None):
        """Resolve the preview name."""
        # get rid of the namespace
        camera = camera.split(":")[-1]
        if not label:
            nice_name = [camera]
        else:
            nice_name = [camera, label]

        full_name = nice_name + [self._name, f"v{version:03d}"]
        return "_".join(nice_name), "_".join(full_name)

    # def make_publish(self, notes, elements=None):
    #     """Create a publish from the currently loaded version on DCC."""
    #
    #     # valid file_format keyword can be collected from main.dcc.formats
    #     state = self.check_permissions(level=1)
    #     if state != 1:
    #         return -1

    def construct_names(self, file_format):
        """Construct a name for the work version.

        Args:
            extension (str): The extension of the file.
            file_format (str): The file format of the file.

        """
        version_number = self.get_last_version() + 1
        version_name = f"{self._name}_v{version_number:03d}{file_format}"
        thumbnail_name = f"{self._name}_v{version_number:03d}_thumbnail.jpg"
        return version_number, version_name, thumbnail_name

    def load_version(self, version_number):
        """Load the given version of the work."""
        version_obj = self.get_version(version_number)
        if version_obj:
            relative_path = version_obj.get("scene_path")
            abs_path = self.get_abs_project_path(relative_path)
            self._dcc_handler.open(abs_path)

    def import_version(self, version_number):
        """Import the given version of the work to the scene."""
        version_obj = self.get_version(version_number)
        if version_obj:
            relative_path = version_obj.get("scene_path")
            abs_path = self.get_abs_project_path(relative_path)
            self._dcc_handler.import_file(abs_path)

    def delete_work(self):
        """Delete the work."""
        # TODO: implement this. This should move the work to the purgatory.
        pass
