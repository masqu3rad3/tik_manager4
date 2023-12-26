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

    def __init__(self):
        # get the module name as name
        # self._name = None
        self._extension: str = ""
        self._extract_folder: str = ""
        self._category: str = ""
        self._status = "idle"
        self._extract_name = ""
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
    def extract_name(self):
        return self._extract_name

    @extract_name.setter
    def extract_name(self, name):
        self._extract_name = name

    @property
    def extension(self):
        return self._extension

    @extension.setter
    def extension(self, extension):
        self._extension = extension

    @property
    def extract_folder(self):
        return self._extract_folder

    @extract_folder.setter
    def extract_folder(self, folder_path):
        _folder_path_obj = Path(folder_path)
        _folder_path_obj.mkdir(parents=True, exist_ok=True)
        self._extract_folder = str(_folder_path_obj)

    @property
    def category(self):
        """Return the category which will rules."""
        return self._category

    @category.setter
    def category(self, category):
        # TODO some validation here
        self._category = category

    @property
    def state(self):
        return self._status

    def extract(self):
        func = self.category_functions.get(self.category, self._extract_default)
        try:
            func()
            self._status = "success"
        except Exception as exc:  # pylint: disable=broad-except
            LOG.error(exc)
            LOG.error(f"Error while extracting {self.name} to {self.extract_folder}")
            self._status = "failed"

    def _extract_default(self):
        """Extract method for any non-specified category"""
        pass

    def resolve_output(self):
        """Resolve the output path"""
        output_path = (
            Path(self.extract_folder) / f"{self._extract_name}{self.extension}"
        )
        return str(output_path)
