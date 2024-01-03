from pathlib import Path
import logging

from pymxs import runtime as rt
import qtmax


from tik_manager4.dcc.main_core import MainCore
from tik_manager4.dcc.max import validate
from tik_manager4.dcc.max import extract
from tik_manager4.dcc.max import ingest


LOG = logging.getLogger(__name__)


class Dcc(MainCore):
    name = "Max"
    formats = [".max"]
    preview_enabled = True  # Whether or not to enable the preview in the UI
    validations = validate.classes
    extracts = extract.classes
    ingests = ingest.classes

    @staticmethod
    def get_main_window():
        """Get the main window."""
        # return QtWidgets.QWidget.find(rt.windows.getMAXHWND())
        return qtmax.GetQMaxMainWindow()

    @staticmethod
    def save_scene():
        """Save the current scene."""
        rt.execute("max file save")

    @staticmethod
    def save_as(file_path):
        """
        Saves the file to the given path
        Args:
            file_path: (String) File path that will be written
            file_format: (String) File format

        Returns: (String) File path

        """
        rt.saveMaxFile(file_path)
        return file_path

    @staticmethod
    def save_prompt():
        """Pop up the save prompt."""
        rt.execute("max file saveas")
        return True # returning True is mandatory for the save prompt to work

    @staticmethod
    def open(file_path, force=True, **extra_arguments):
        """
        Opens the given file path
        Args:
            file_path: (String) File path to open
            force: (Bool) if true any unsaved changes on current scene will be lost
            **extra_arguments: Compatibility arguments for other DCCs

        Returns: None

        """
        rt.loadMaxFile(file_path)

    @staticmethod
    def get_ranges():
        """Get the viewport ranges."""
        r_ast = float(rt.animationRange.start)
        r_min = float(rt.animationRange.start)
        r_max = float(rt.animationRange.end)
        r_aet = float(rt.animationRange.end)
        return [r_ast, r_min, r_max, r_aet]

    @staticmethod
    def set_ranges(range_list):
        """
        Set the timeline ranges.

        Args:
            range_list: list of ranges as [<animation start>, <user min>, <user max>,
                                            <animation end>]

        Returns: None

        """
        rt.animationRange = rt.interval(range_list[0], range_list[-1])

    @staticmethod
    def is_modified():
        """Check if the scene has unsaved changes."""
        return rt.getSaveRequired()

    @staticmethod
    def get_scene_file():
        """Get the current scene file."""
        if rt.maxFilePath and rt.maxFileName:
            return str(Path(rt.maxFilePath, rt.maxFileName))
        else:
            return ""

    @staticmethod
    def get_current_frame():
        """Return current frame in timeline.
        If dcc does not have a timeline, returns None.
        """
        slider_time = rt.sliderTime
        return slider_time.frame

    def generate_thumbnail(self, file_path, width, height):
        """
        Grabs a thumbnail from the current scene
        Args:
            file_path: (String) File path to save the thumbnail
            width: (Int) Width of the thumbnail
            height: (Int) Height of the thumbnail

        Returns: None

        """

        grab = rt.gw.getViewportDib()
        ratio = float(grab.width) / float(grab.height)

        if ratio <= (float(width) / float(height)):
            new_width = height * ratio
            new_height = height
        else:
            new_width = width
            new_height = width / ratio

        resize_frame = rt.bitmap(new_width, new_height, color=rt.color(0, 0, 0))
        rt.copy(grab, resize_frame)
        thumb_frame = rt.bitmap(width, height, color=rt.color(0, 0, 0))
        x_offset = (width - resize_frame.width) * 0.5
        y_offset = (height - resize_frame.height) * 0.5

        rt.pasteBitmap(resize_frame, thumb_frame, rt.point2(0, 0), rt.point2(x_offset, y_offset))
        thumb_frame.filename = file_path
        rt.save(thumb_frame)
        rt.close(thumb_frame)

        return file_path

    @staticmethod
    def get_scene_cameras():
        """Return NAMES of all the cameras in the scene."""
        # Get all nodes in the scene
        all_nodes = rt.rootNode.children
        # Filter nodes to get only cameras
        cameras = [node for node in all_nodes if rt.isKindOf(node, rt.camera)]
        _dict = {}
        for cam in cameras:
            _dict[cam.name] = cam
        # add the perspective as an option
        _dict["persp"] = ""
        return _dict

    @staticmethod
    def get_current_camera():
        """Return the current camera in the scene."""
        active_cam_node = rt.getActiveCamera()
        if active_cam_node:
            return active_cam_node.name, active_cam_node
        else:
            return "persp", ""

    @staticmethod
    def generate_preview(name, folder, camera_code, resolution, range, settings=None):
        """
        Create a preview from the current scene
        Args:
            name: (String) Name of the preview
            folder: (String) Folder to save the preview
            camera_code: (String) Camera code. In Max, this is camera node obj..
            resolution: (list) Resolution of the preview
            range: (list) Range of the preview
            settings: (dict) Global Settings dictionary
        """

        settings = settings or {
            "DisplayFieldChart": False,
            "DisplayGateMask": False,
            "DisplayFilmGate": False,
            "DisplayFilmOrigin": False,
            "DisplayFilmPivot": False,
            "DisplayResolution": False,
            "DisplaySafeAction": False,
            "DisplaySafeTitle": False,
            "DisplayAppearance": "smoothShaded",
            "ClearSelection": True,
            "ShowFrameNumber": True,
            "ShowFrameRange": True,
            "CrfValue": 23,
            "Format": "video",
            "PostConversion": True,
            "ShowFPS": True,
            "PolygonOnly": True,
            "Percent": 100,
            "DisplayTextures": True,
            "ShowGrid": False,
            "ShowSceneName": False,
            "UseDefaultMaterial": False,
            "ViewportAsItIs": False,
            "HudsAsItIs": False,
            "WireOnShaded": False,
            "Codec": "png",
            "ShowCategory": False,
            "Quality": 100,
        }

        extension = "avi"

        # get the current values
        original_values = {
            "width": rt.renderWidth,
            "height": rt.renderHeight,
            "selection": rt.getCurrentSelection(),
        }

        # change the render settings temporarily
        rt.renderWidth = resolution[0]
        rt.renderHeight = resolution[1]

        display_geometry = bool(settings["PolygonOnly"])
        display_shapes = not bool(settings["PolygonOnly"])
        display_lights = not bool(settings["PolygonOnly"])
        display_cameras = not bool(settings["PolygonOnly"])
        display_helpers = not bool(settings["PolygonOnly"])
        display_particles = not bool(settings["PolygonOnly"])
        display_bones = not bool(settings["PolygonOnly"])
        display_grid = bool(settings["ShowGrid"])
        display_frame_nums = bool(settings["ShowFrameNumber"])
        percent_size = settings["Percent"]
        render_level = (
            rt.execute("#litwireframe")
            if settings["WireOnShaded"]
            else rt.execute("#smoothhighlights")
        )
        if settings["ClearSelection"]:
            rt.clearSelection()

        file_path = Path(folder) / f"{name}.{extension}"
        rt.createPreview(
            filename=str(file_path),
            percentSize=percent_size,
            dspGeometry=display_geometry,
            dspShapes=display_shapes,
            dspLights=display_lights,
            dspCameras=display_cameras,
            dspHelpers=display_helpers,
            dspParticles=display_particles,
            dspBones=display_bones,
            dspGrid=display_grid,
            dspFrameNums=display_frame_nums,
            rndLevel=render_level,
            autoPlay=not settings["PostConversion"],
        )

        # restore the original values
        rt.renderWidth = original_values["width"]
        rt.renderHeight = original_values["height"]
        rt.select(original_values["selection"])

        return file_path

    @staticmethod
    def get_dcc_version():
        """Return the DCC major version."""
        return rt.maxversion()[0]

    @staticmethod
    def get_scene_fps():
        """Return the current FPS value set by DCC. None if not supported."""
        return rt.framerate

    def set_scene_fps(self, fps_value):
        """
        Set the FPS value in DCC if supported.
        Args:
            fps_value: (integer) fps value

        Returns: None

        """
        range = self.get_ranges()
        rt.framerate = fps_value
        self.set_ranges(range)
