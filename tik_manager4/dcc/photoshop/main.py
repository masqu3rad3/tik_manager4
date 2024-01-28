from pathlib import Path
from win32com.client import Dispatch
import winreg

from tik_manager4.dcc.main_core import MainCore
from tik_manager4.dcc.photoshop import validate
from tik_manager4.dcc.photoshop import extract
from tik_manager4.dcc.photoshop import ingest

# test dispatch
# psApp = Dispatch("Photoshop.Application")


class Dcc(MainCore):
    """Photoshop DCC class"""

    name = "Photoshop"
    formats = [".psd", ".psb"]
    preview_enabled = False
    validations = validate.classes
    extracts = extract.classes
    ingests = ingest.classes
    def __init__(self):
        super().__init__()

        self.com_link = Dispatch("Photoshop.Application")
        # self.com_link = self.get_dispatch("Photoshop.Application")

    def get_dispatch(self, key_prefix="Photoshop.Application"):
        """Get the Photoshop dispatch object."""
        # first try only the prefix
        try:
            com_link = Dispatch(key_prefix)
            return com_link
        except: # pylint: disable=bare-except
            pass

        keys = self.get_photoshop_registry_keys(prefix=key_prefix)

        for key in keys:
            try:
                com_link = Dispatch(key)
                return com_link
            except: # pylint: disable=bare-except
                pass

    @staticmethod
    def get_photoshop_registry_keys(prefix):
        # prefix = "Photoshop.Application"
        keys = []
        hive = winreg.HKEY_CLASSES_ROOT
        subkey = ""

        try:
            with winreg.OpenKey(hive, subkey) as key:
                idx = 0
                while True:
                    subkey_name = winreg.EnumKey(key, idx)
                    if subkey_name.startswith(prefix):
                        keys.append(subkey_name)
                    idx += 1
        except FileNotFoundError:
            pass  # Handle the case where the registry key doesn't exist
        except Exception as e:
            pass
        return keys

    # @staticmethod
    # def get_photoshop_registry_keys():
    #     photoshop_keys = []
    #     try:
    #         # Open the registry key
    #         key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "Photoshop.Application")
    #
    #         # Enumerate all subkeys
    #         index = 0
    #         while True:
    #             try:
    #                 subkey = winreg.EnumKey(key, index)
    #                 if subkey.startswith("Photoshop.Application"):
    #                     photoshop_keys.append(subkey)
    #                 index += 1
    #             except OSError:
    #                 break
    #
    #         # Close the registry key
    #         winreg.CloseKey(key)
    #
    #     except Exception as e:
    #         print(f"Error accessing registry: {e}")
    #
    #     return photoshop_keys

    # def getPhotoshopDispatchName(self, excludes=None):
    #     """Get the name of the Photoshop dispatch object."""
    #
    #     name = "Photoshop.Application"
    #     classBase = "SOFTWARE\\Classes\\"
    #     try:
    #         if excludes and name in excludes:
    #             raise Exception()
    #
    #         winreg.OpenKey(
    #             winreg.HKEY_LOCAL_MACHINE,
    #             classBase + name,
    #             0,
    #             winreg.KEY_READ | winreg.KEY_WOW64_64KEY,
    #         )
    #     except:
    #         classKey = winreg.OpenKey(
    #             winreg.HKEY_LOCAL_MACHINE,
    #             classBase,
    #             0,
    #             winreg.KEY_READ | winreg.KEY_WOW64_64KEY,
    #         )
    #         try:
    #             i = 0
    #             keyName = None
    #             while True:
    #                 classNameKey = winreg.EnumKey(classKey, i)
    #                 if excludes and classNameKey in excludes:
    #                     i += 1
    #                     continue
    #
    #                 if classNameKey.startswith("Photoshop.Application."):
    #                     if keyName:
    #                         try:
    #                             if float(classNameKey.replace("Photoshop.Application.", "")) > float(keyName.replace("Photoshop.Application.", "")):
    #                                 keyName = classNameKey
    #                         except:
    #                             pass
    #                     else:
    #                         keyName = classNameKey
    #
    #                 elif keyName:
    #                     return keyName
    #
    #                 i += 1
    #         except WindowsError:
    #             pass
    #
    #     else:
    #         return name


    def save_as(self, file_path):
        """Save the current scene as a new file.

        Args:
            file_path (str): Path to the file to save.
        """
        # get the format from the file path
        format = Path(file_path).suffix
        if format not in Dcc.formats:
            raise ValueError(f"Unsupported file format: {format}")

        if format == ".psd":
            active_doc = self.com_link.Application.ActiveDocument
            save_options = Dispatch("Photoshop.PhotoshopSaveOptions")
            active_doc.SaveAs(file_path, save_options, False) # False means its not saving as a copy.

        elif format == ".psb":
            desc19 = Dispatch("Photoshop.ActionDescriptor")
            desc20 = Dispatch("Photoshop.ActionDescriptor")
            desc20.PutBoolean(self.com_link.StringIDToTypeID('maximizeCompatibility'), True)
            desc19.PutObject(
                self.com_link.CharIDToTypeID('As  '), self.com_link.CharIDToTypeID('Pht8'), desc20)
            desc19.PutPath(self.com_link.CharIDToTypeID('In  '), file_path)
            desc19.PutBoolean(self.com_link.CharIDToTypeID('LwCs'), True)
            self.com_link.ExecuteAction(self.com_link.CharIDToTypeID('save'), desc19, 3)

        return file_path

    def open(self, file_path, force=True, **extra_arguments):
        """Load the given file.

        Args:
            file_path (str): Path to the file to load.
        """
        # import pdb
        # pdb.set_trace()
        print("file_path: ", file_path)
        self.com_link.Open(file_path)

    def get_scene_file(self):
        """Get the current scene file.

        Returns:
            str: Path to the current scene file.
        """
        try:
            active_document = self.com_link.Application.ActiveDocument
            doc_name = active_document.name
            doc_path = active_document.path
            return str(Path(doc_path, doc_name))
        except: # pylint: disable=bare-except
            return ""

    def generate_thumbnail(self, file_path, width, height):
        """Generate a thumbnail for the given file."""
        self.com_link.Preferences.RulerUnits = 1
        active_document = self.com_link.Application.ActiveDocument
        duplicate_document = active_document.Duplicate("thumbnail_copy", True)
        duplicate_document.bitsPerChannel = 8
        ratio = float(duplicate_document.Width) / float(duplicate_document.Height)

        if ratio <= (float(width) / float(height)):
            new_width = height * ratio
            new_height = height
        else:
            new_width = width
            new_height = width / ratio

        duplicate_document.ResizeImage(new_width, new_height)
        duplicate_document.ResizeCanvas(width, height)

        # save the thumbnail
        save_options = Dispatch("Photoshop.JPEGSaveOptions")
        save_options.EmbedColorProfile = True
        save_options.FormatOptions = 1  # => psStandardBaseline
        save_options.Matte = 1  # => No Matte
        save_options.Quality = 6
        active_document.SaveAs(file_path, save_options, True)
        duplicate_document.Close(2) # 2 means without saving...
        return file_path

    def get_dcc_version(self):
        """Get the version of the DCC."""
        return str(self.com_link.Version)