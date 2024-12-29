"""Bundle extract for multiple playblasts."""

from pathlib import Path

from maya import cmds

from tik_manager4.dcc.extract_core import ExtractCore
from tik_manager4.external.fileseq import filesequence as fileseq
from tik_manager4.dcc.maya import utils
from tik_manager4.dcc.maya import panels


class Preview(ExtractCore):
    """Extract multiple playblasts from Maya scene."""

    nice_name = "Multi Preview"
    color = (0, 255, 255)
    bundled = True
    order = -1

    def __init__(self):
        _ranges = utils.get_ranges()
        # these are the exposed settings in the UI
        global_exposed_settings = {
            "cameras": {
                "display_name": "Cameras",
                "type": "list",
                "value": self.collect(),
            },
            "start_frame": {
                "display_name": "Start Frame",
                "type": "integer",
                "value": _ranges[0],
            },
            "end_frame": {
                "display_name": "End Frame",
                "type": "integer",
                "value": _ranges[3],
            },
            "resolution": {
                "display_name": "Resolution",
                "type": "vector2Int",
                "value": [1920, 1080],
            },
            "file_format": {
                "display_name": "Format",
                "type": "combo",
                "items": ["jpg", "png", "iff", "tga"],
                "value": "jpg",
            },
            "display_huds": {
                "display_name": "Display HUDs",
                "type": "boolean",
                "value": False,
            },
        }

        super().__init__(global_exposed_settings=global_exposed_settings)

    @staticmethod
    def collect():
        """Collect the cameras in the scene ending with _previewCam."""
        all_camera_shapes = cmds.ls(type="camera")
        all_camera_transforms = [
            cmds.listRelatives(cam, parent=True, fullPath=True)[0]
            for cam in all_camera_shapes
        ]
        # exclude the default cameras
        _exclude_cameras = ["front", "persp", "side", "top"]
        exclude_dag_list = [cmds.ls(x, type="transform", long=True)[0] for x in _exclude_cameras]
        preview_cameras = [
            # cam for cam in all_camera_transforms if cam.endswith("_previewCam")
            cam for cam in all_camera_transforms if cam not in exclude_dag_list
        ]
        return preview_cameras

    def _extract_default(self):
        """Extract playblasts from Maya scene."""
        cameras = self.global_settings.get("cameras")
        _bundle_info = {}
        if not cameras:
            self.bundle_info = {}
            return

        _str_directory = self.resolve_output()
        bundle_directory = Path(_str_directory)
        bundle_directory.mkdir(parents=True, exist_ok=True)

        start_frame = self.global_settings.get("start_frame")
        end_frame = self.global_settings.get("end_frame")
        resolution = self.global_settings.get("resolution")
        compression = self.global_settings.get("file_format")
        display_huds = self.global_settings.get("display_huds")

        f_handler = fileseq.FileSequence("")

        for camera in cameras:
            pb_panel = panels.PanelManager(camera, resolution, inherit=True)
            pb_panel.hud = display_huds

            cmds.select(camera)
            nice_name = camera.split("|")[-1].replace(":", "_")
            file_path_without_extension = bundle_directory / f"{nice_name}"
            cmds.playblast(
                format="image",
                filename=file_path_without_extension.as_posix(),
                widthHeight=resolution,
                percent=100,
                compression=compression,
                quality=100,
                forceOverwrite=True,
                viewer=False,
                offScreen=True,
                offScreenViewportUpdate=True,
                activeEditor=False,
                editorPanelName=pb_panel.panel,
                startTime=start_frame,
                endTime=end_frame,
            )

            pb_panel.kill()

            # get the file sequence
            seq = f_handler.findSequencesOnDisk(
                f"{file_path_without_extension.as_posix()}.@.{compression}"
            )[0]

            _bundle_info[file_path_without_extension.stem] = {
                "extension": f".{compression}",
                "path": seq.format(),
                "sequential": True,
            }

        # explicitly set the bundle_info property
        self.bundle_info = _bundle_info
