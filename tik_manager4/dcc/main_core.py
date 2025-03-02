"""Template class for all available DCC commands.
These commands will be overriden in DCCs.
"""
# import importlib
from tik_manager4.core import utils
import inspect
from tik_manager4.dcc.extract_core import ExtractCore
from tik_manager4.dcc.validate_core import ValidateCore
from tik_manager4.dcc.ingest_core import IngestCore
from tik_manager4.dcc.extension_core import ExtensionCore
from tik_manager4.objects import guard

class MainCore():
    name = ""
    formats = []
    preview_enabled = True
    validations = {}
    extracts = {}
    ingests = {}
    extensions = {}
    custom_launcher = False
    guard = guard.Guard()

    # def __init__(self):
    #     """Initialize the class."""
    #

    @classmethod
    def add_validation(cls, key, value):
        """Add a validation to the validations dictionary."""
        cls.validations[key] = value

    @classmethod
    def add_extract(cls, key, value):
        """Add an extract to the extracts dictionary."""
        cls.extracts[key] = value

    @classmethod
    def add_ingest(cls, key, value):
        """Add an ingest to the ingests dictionary."""
        cls.ingests[key] = value

    @classmethod
    def add_extension(cls, key, value):
        """Add an extension to the extensions dictionary."""
        cls.extensions[key] = value

    @staticmethod
    def pre_publish():
        """Actions to be done before publishing."""
        pass

    @staticmethod
    def post_publish():
        """Actions to be done after publishing."""
        pass

    @staticmethod
    def pre_save():
        """Actions to be done before saving."""
        pass

    @staticmethod
    def post_save():
        """Actions to be done after saving."""
        pass

    @staticmethod
    def pre_open_issues():
        """Checks to be done before opening a file."""
        pass

    @staticmethod
    def pre_save_issues():
        """Checks to be done before saving a file."""
        pass

    @staticmethod
    def pre_publish_issues():
        """Checks to be done before publishing."""
        pass

    @staticmethod
    def get_main_window():
        """Returns the main window of the DCC"""
        pass

    @staticmethod
    def save_scene():
        """Saves the current file"""
        pass

    @staticmethod
    def save_as(file_path):
        """
        Saves the file to the given path
        Args:
            file_path: (String) File path that will be written
            file_format: (String) File format
            **extra_arguments: Compatibility arguments

        Returns:

        """
        pass

    @staticmethod
    def save_prompt():
        """Pop up the save prompt."""
        pass

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
        pass

    @staticmethod
    def get_ranges():
        """Get the viewport ranges.
        Returns: (list) [<absolute range start>, <user range start>, <user range end>,
        <absolute range end>
        """
        pass

    @staticmethod
    def set_ranges(range_list):
        """Set the timeline ranges.

        Args:
            range_list: list of ranges as [<animation start>, <user min>, <user max>,
            <animation end>]

        Returns: None

        """
        pass

    @staticmethod
    def set_project(file_path):
        """
        Sets the project path
        Args:
            file_path: (String) File path to set as project

        Returns: None

        """
        pass

    @staticmethod
    def is_modified():
        """Returns True if the scene has unsaved changes"""
        False

    @staticmethod
    def get_scene_file():
        """Gets the current loaded scene file"""
        pass

    @staticmethod
    def get_project():
        """Return currently set project by dcc.
        If dcc does not support project management, return None.
        """
        return None

    @staticmethod
    def get_current_frame():
        """Return current frame in timeline.
        If dcc does not have a timeline, return None.
        """
        return None

    @staticmethod
    def get_current_selection():
        """Returns current selection or None if it is not supported"""
        return None

    @staticmethod
    def get_scene_fps():
        """Return the current FPS value set by DCC. None if not supported."""
        return None

    @staticmethod
    def set_scene_fps(fps_value):
        """
        Set the FPS value in DCC if supported.
        Args:
            fps_value: (integer) fps value

        Returns: None

        """
        pass

    @staticmethod
    def get_scene_cameras():
        """
        Return all the cameras in the scene.
        Returns: (list) List of camera names
        """
        pass

    @staticmethod
    def generate_thumbnail(file_path, width, height):
        """Generate a thumbnail for the given file path."""
        pass


    @staticmethod
    def generate_preview(name, folder, camera_code, resolution, range, settings=None):
        """
        Create a preview from the current scene
        Args:
            name: (String) Name of the preview
            folder: (String) Folder to save the preview
            camera_code: (String) Camera code. In Maya, this is the UUID of the camera transform node.
            resolution: (list) Resolution of the preview
            range: (list) Range of the preview
            settings: (dict) Global Settings dictionary
        """
        pass

    @staticmethod
    def get_dcc_version():
        """Returns the current DCC version"""
        pass

    @staticmethod
    def test():
        """Test function"""
        pass

    @staticmethod
    def launch():
        """Open main menu with DCC custom commands."""
        pass

    def collect_common_plugins(self):
        """Collect common plugins for the DCC"""
        extract_module_files = self.guard.commons.collect_common_modules(self.name.lower(), "extract")
        ingests_module_files = self.guard.commons.collect_common_modules(self.name.lower(), "ingest")
        validations_module_files = self.guard.commons.collect_common_modules(self.name.lower(), "validation")
        extensions_module_files = self.guard.commons.collect_common_modules(self.name.lower(), "extension")

        extract_classes = self.collect_classes(extract_module_files, module_type = ExtractCore)
        ingest_classes = self.collect_classes(ingests_module_files, module_type = IngestCore)
        validation_classes = self.collect_classes(validations_module_files, module_type = ValidateCore)
        extension_classes = self.collect_classes(extensions_module_files, module_type = ExtensionCore)

        for key, value in extract_classes.items():
            self.add_extract(key, value)
        for key, value in ingest_classes.items():
            self.add_ingest(key, value)
        for key, value in validation_classes.items():
            self.add_validation(key, value)
        for key, value in extension_classes.items():
            self.add_extension(key, value)

    @staticmethod
    def collect_classes(file_paths, module_type: object):
        """Collect classes from modules in the given directory."""
        classes = {}

        exceptions = ["__init__.py"]

        for mod in file_paths:
            file_name = mod.name
            if file_name not in exceptions and not file_name.startswith("_"):
                module_name = mod.stem
                module = utils.import_from_path(module_name, mod.as_posix())

                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj,
                                                           module_type) and obj != module_type:
                        classes[module_name] = obj

        return classes