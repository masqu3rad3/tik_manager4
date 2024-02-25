"""Template module for publishing"""

from pathlib import Path
import importlib
from tik_manager4.core import filelog
from tik_manager4.core.settings import Settings
from tik_manager4.objects.metadata import Metadata


LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")


class ExtractCore:
    """Core class for extracting elements from the scene."""
    nice_name: str = ""
    color: tuple = (255, 255, 255)  # RGB
    exposed_settings: dict = {}
    global_exposed_settings: dict = {}
    optional: bool = False
    bundled: bool =False

    def __init__(self):
        # get the module name as name
        # self._name = None
        self._extension: str = ""
        self._extract_folder: str = ""
        self._category: str = ""
        self._state = "idle"
        self._extract_name = ""
        self._enabled: bool = True
        self._message: str = ""
        # self._bundled: bool = False # if bundled, the extract will be a folder
        self._metadata: Metadata
        self.category_functions = {}
        self.global_settings = Settings()
        self.global_settings.set_data(self.global_exposed_settings)
        self.settings: dict = {}
        # create settings objects from the default settings
        for key, value in self.exposed_settings.items():
            _settings = Settings()
            _settings.set_data(value)
            self.settings[key] = _settings


    def __init_subclass__(cls, **kwargs):
        # Get the base name of the file without the extension using pathlib
        module = importlib.import_module(cls.__module__)
        module_file_path = Path(module.__file__).resolve()
        module_name = module_file_path.stem
        # Set the 'name' variable in the subclass
        cls.name = module_name
        super().__init_subclass__(**kwargs)

    @property
    def enabled(self):
        """Return the enabled state of the extractor."""
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        """Set the enabled state of the extractor."""
        self._enabled = enabled

    @property
    def extract_name(self):
        """Return the name of the extracted file."""
        return self._extract_name

    @extract_name.setter
    def extract_name(self, name):
        """Set the name of the extracted file."""
        self._extract_name = name

    @property
    def extension(self):
        """Return the extension of the extracted file."""
        return self._extension

    @extension.setter
    def extension(self, extension):
        """Set the extension of the extracted file."""
        self._extension = extension

    @property
    def extract_folder(self):
        """Return the folder path where the extracted file will be saved."""
        return self._extract_folder

    @extract_folder.setter
    def extract_folder(self, folder_path):
        """Set the folder path where the extracted file will be saved."""
        _folder_path_obj = Path(folder_path)
        _folder_path_obj.mkdir(parents=True, exist_ok=True)
        self._extract_folder = str(_folder_path_obj)

    @property
    def category(self):
        """Return the category which will rules."""
        return self._category

    @category.setter
    def category(self, category):
        """Set the category which will rules."""
        # TODO some validation here
        self._category = category

    @property
    def state(self):
        """Return the state of the extractor."""
        return self._state

    @property
    def message(self):
        """Return the message of the extractor."""
        return self._message

    @property
    def metadata(self):
        """Return the metadata of the extractor."""
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        """Set the metadata of the extractor."""
        # if any of the setting keys are in the metadata, set the value of the setting
        for global_key in self.global_settings.keys:
            if metadata.exists(global_key):
                self.global_settings.edit_property(global_key, metadata.get_value(global_key))

        for category_key in self.settings:
            for setting_key in self.settings[category_key].keys:
                if metadata.exists(setting_key):
                    self.settings[category_key].edit_property(setting_key, metadata.get_value(setting_key))
        self._metadata = metadata

    def extract(self):
        """Execute the extract."""
        func = self.category_functions.get(self.category, self._extract_default)
        try:
            func()
            self._state = "success"
        except Exception as exc:  # pylint: disable=broad-except
            # print the FULL STACK TRACEBACK
            LOG.exception(exc)
            LOG.error(f"Error while extracting {self.name} to {self.extract_folder}")
            self._state = "failed"
            self._message = str(exc)

    def _extract_default(self):
        """Extract for any non-specified category."""
        pass

    def resolve_output(self):
        """Resolve the output path."""
        if self.bundled:
            output_path = Path(self.extract_folder) / f"{self.name.upper()}_{self._extract_name}"
        else:
            output_path = Path(self.extract_folder) / f"{self.name.upper()}_{self._extract_name}{self.extension}"
        return str(output_path)
