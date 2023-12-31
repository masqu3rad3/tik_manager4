# pylint: disable=super-with-arguments
# pylint: disable=consider-using-f-string
import socket
import platform
import subprocess
from pathlib import Path
from tik_manager4.core import utils
from tik_manager4.core.settings import Settings
from tik_manager4.core import filelog
from tik_manager4.objects.entity import Entity
from tik_manager4.objects.publish import Publish

# from tik_manager4.objects.publish import PublishVersion
from tik_manager4 import dcc

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")

class Work(Settings, Entity):
    _dcc_handler = dcc.Dcc()
    object_type = "work"

    def __init__(self, absolute_path, name=None, path=None):
        super(Work, self).__init__()
        self.settings_file = Path(absolute_path)

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

    @property
    def state(self):
        """Return the state of the work."""
        return self._state

    @property
    def dcc(self):
        """Return the dcc of the work."""
        return self._dcc

    @property
    def dcc_version(self):
        """Return the dcc version of the work."""
        return self._dcc_version

    @property
    def id(self):
        """Return the id of the work."""
        return self._work_id

    @property
    def task_id(self):
        """Return the id of the task."""
        return self._task_id

    @property
    def task_name(self):
        """Return the name of the task."""
        return self._task_name

    @property
    def creator(self):
        """Return the creator of the work."""
        return self._creator

    @property
    def category(self):
        """Return the category of the work."""
        return self._category

    @property
    def versions(self):
        """Return the versions of the work."""
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
        # First try to get the last version from the versions list. If not found, return 0.
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
        version_number, version_name, thumbnail_name = self.construct_names(file_format)

        abs_version_path = self.get_abs_project_path(self.name, version_name)
        thumbnail_path = self.get_abs_database_path("thumbnails", thumbnail_name)
        Path(abs_version_path).parent.mkdir(parents=True, exist_ok=True)

        # save the file
        output_path = self._dcc_handler.save_as(abs_version_path)

        # on some occasions the save as method may return a different path.
        # for example, if the file cannot be saved with specified file format,
        # extractor logic may decide to force something else.
        if output_path != abs_version_path:
            version_name = Path(output_path).name # e.g. "test_v001.ma"
            file_format = Path(output_path).suffix # e.g. ".ma"


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
        return version

    def make_preview(
        self, version_number, camera, resolution, frame_range, label=None, settings=None
    ):
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
            if settings.get("PostConversion", False):
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
        # TODO: Format validation

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
        # change the extension to mp4
        output_file = _file_path.with_suffix(".mp4")

        # deal with the existing output
        if output_file.exists():
            if overwrite:
                output_file.unlink()
            else:
                return

        flag_start = [ffmpeg, "-i", str(_file_path)]

        full_flag_list = (
            flag_start
            + presetLUT["videoCodec"].split()
            + presetLUT["compression"].split()
            + presetLUT["audioCodec"].split()
            + presetLUT["resolution"].split()
            + presetLUT["foolproof"].split()
            + [str(output_file)]
        )

        if platform.system() == "Windows":
            subprocess.check_call(full_flag_list, shell=False)
        else:
            subprocess.check_call(full_flag_list)
        _file_path.unlink()
        return str(output_file)

    def _check_ffmpeg(self):
        """Checks if the FFMPEG present in the system"""
        if platform.system() == "Windows":
            # get the ffmpeg.exe from the parallel folder 'external'
            parent_folder = Path(__file__).parent.parent
            ffmpeg_folder = parent_folder / "external" / "ffmpeg"
            ffmpeg = ffmpeg_folder / "ffmpeg.exe"
            if not ffmpeg.exists():
                return False
            else:
                return ffmpeg
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
        """Resolve the preview name."""
        # get rid of the namespace
        camera = camera.split(":")[-1]
        if not label:
            nice_name = [camera]
        else:
            nice_name = [camera, label]

        full_name = nice_name + [self._name, f"v{version:03d}"]
        return "_".join(nice_name), "_".join(full_name)

    def construct_names(self, file_format):
        """Construct a name for the work version.

        Args:
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

    def import_version(self, version_number, element_type=None, ingestor=None):
        """Import the given version of the work to the scene."""
        # work files does not have element types. This is for publish files.
        _element_type = element_type or "source"
        ingestor = ingestor or "source"
        version_obj = self.get_version(version_number)
        if version_obj:
            relative_path = version_obj.get("scene_path")
            abs_path = self.get_abs_project_path(relative_path)
            _ingest_obj = self._dcc_handler.ingests[ingestor]()
            _ingest_obj.category = self.category
            _ingest_obj.file_path = abs_path
            _ingest_obj.bring_in()

    def reference_version(self, version_number, element_type=None, ingestor=None):
        """Reference the given version of the work to the scene."""
        # work files does not have element types. This is for publish files.
        _element_type = element_type or "source"
        ingestor = ingestor or "source"
        version_obj = self.get_version(version_number)
        if version_obj:
            relative_path = version_obj.get("scene_path")
            abs_path = self.get_abs_project_path(relative_path)
            _ingest_obj = self._dcc_handler.ingests[ingestor]()
            _ingest_obj.category = self.category
            _ingest_obj.file_path = abs_path
            _ingest_obj.reference()

    def delete_work(self):
        """Delete the work."""
        # TODO: implement this. This should move the work to the purgatory.
        pass
