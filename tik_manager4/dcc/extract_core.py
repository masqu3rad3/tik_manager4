"""Template module for publishing"""

from pathlib import Path
import importlib
from tik_manager4.core import filelog
from tik_manager4.core.settings import Settings


LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")


class ExtractCore:
    """Core class for extracting elements from the scene."""

    nice_name: str = ""
    color: tuple = (255, 255, 255)  # RGB
    default_settings: dict = {}
    optional: bool = False

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
        self._bundled: bool = False # if bundled, the extract will be a folder
        self.category_functions = {}
        self.settings = {}
        for key, value in self.default_settings.items():
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
    def bundled(self):
        """Return the bundled state of the extractor."""
        return self._bundled

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
        if self._bundled:
            output_path = Path(self.extract_folder) / self._extract_name
        else:
            output_path = Path(self.extract_folder) / f"{self._extract_name}{self.extension}"
        return str(output_path)
