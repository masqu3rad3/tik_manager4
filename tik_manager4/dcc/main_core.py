"""Template class for all available DCC commands.
These commands will be overriden in DCCs.
"""
import pathlib

class MainCore():
    name = ""
    preview_enabled = True
    validations = []
    extracts = []
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
    def reference(file_path, namespace):
        """
        References a file
        Args:
            file_path: (String) the file path to be referenced
            namespace: (String) namespace for uniqueness

        Returns: (List) Referenced nodes

        """
        pass

    @staticmethod
    def import_file(file_path, **extra_arguments):
        """
        Imports the given file to the current scene
        Args:
            file_path: (String) File path to be imported
            **extra_arguments: Compatibility arguments

        Returns: (List) Imported nodes

        """
        pass

    @staticmethod
    def import_obj(file_path, **extra_arguments):
        """
        Imports wavefront obj files
        Args:
            file_path: (String) File path to be imported
            **extra_arguments: Compatibility arguments

        Returns: (List) Imported nodes

        """
        pass

    @staticmethod
    def import_abc(file_path, **extra_arguments):
        """
        Imports alembic files
        Args:
            file_path: (String) File path to be imported
            **extra_arguments: Compatibility arguments

        Returns: (List) Imported nodes

        """
        pass

    @staticmethod
    def import_fbx(file_path, **extra_arguments):
        """
        Imports fbx files
        Args:
            file_path: (String) File path to be imported
            **extra_arguments: Compatibility arguments

        Returns: (List) Imported nodes

        """
        pass

    @staticmethod
    def export_obj(file_path, **extra_arguments):
        """
        Exports wavefront obj files
        Args:
            file_path: (String) Export location
            **extra_arguments: Compatibility arguments

        Returns: None

        """
        pass

    @staticmethod
    def export_abc(file_path, **extra_arguments):
        """
        Exports alembic files
        Args:
            file_path: (String) Export location
            **extra_arguments: Compatibility arguments

        Returns: None

        """
        pass

    @staticmethod
    def export_fbx(file_path, **extra_arguments):
        """
        Exports fbx files
        Args:
            file_path: (String) Export location
            **extra_arguments: Compatibility arguments

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
        pass

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
        """
        Grabs a thumbnail from the current scene
        Args:
            file_path: (String) File path to save the thumbnail
            width: (Int) Width of the thumbnail
            height: (Int) Height of the thumbnail

        Returns: (String) File path of the thumbnail (None if not supported)

        """
        return None

    @staticmethod
    def generate_preview(name, folder, camera=None, resolution=None, settings_file=None):
        """
        Create a preview from the current scene
        Args:
            file_path: (String) File path to save the preview

        Returns: (String) File path of the preview

        """
        pass

    @staticmethod
    def get_dcc_version():
        """Returns the current DCC version"""
        pass

    @staticmethod
    def test():
        """Test function"""
        print("TESTING")

    # TODO: validation methods for checking the existence and read/write permmisions
