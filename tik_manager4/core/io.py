"""I/O Module to handle read/write operations."""

from pathlib import Path
import json
from json.decoder import JSONDecodeError
from tik_manager4.core import filelog
from tik_manager4.external import filelock as fl

LOG = filelog.Filelog(logname=__name__)


class IO:
    """Handler class for read/write operations."""

    def __init__(self, file_path=None):
        """Initializes the IO class."""
        super().__init__()
        self.valid_extensions = [".json", ".ttask", ".twork", ".tpub"]
        self.default_extension = ".json"
        self._string_path = None
        self._path_obj = None
        if file_path:
            self.file_path = file_path

    @property
    def file_path(self):
        """Return the file path."""
        return self._string_path

    @file_path.setter
    def file_path(self, new_path):
        """Set the new file path.

        Args:
            new_path (str): The new file path.

        Raises:
            ValueError: If the extension is not supported
                        or not provided.
        """
        self._path_obj = Path(new_path)
        ext = self._path_obj.suffix

        if not ext:
            LOG.error("IO module needs to know the extension")
            raise ValueError("IO module needs to know the extension")
        if ext not in self.valid_extensions:
            msg = f"IO module does not support this extension ({ext})"
            LOG.error(msg)
            raise ValueError(msg)
        self._path_obj.parent.mkdir(parents=True, exist_ok=True)
        self._string_path = str(self._path_obj)

    def read(self, file_path=None):
        """Read the given file and return the data.

        Args:
            file_path (str): The file path to read from.

        Raises:
            FileNotFoundError: If the file does not exist.

        Returns:
            dict: The data read from the file.
        """
        _path_obj = Path(file_path) if file_path else self._path_obj
        if _path_obj.is_file():
            return self._load_json(str(_path_obj))
        msg = f"File does not exist => {str(_path_obj)}"
        LOG.error(msg)
        raise FileNotFoundError(msg)

    def write(self, data, file_path=None):
        """Write the given data to the file.

        Args:
            data (dict): The data to write.
            file_path (str): The file path to write to.

        Raises:
            fl.Timeout: If the file is locked by another process.
        """
        _path_obj = Path(file_path) if file_path else self._path_obj
        _lock_path = f"{str(_path_obj)}.lock"
        lock = fl.FileLock(_lock_path, timeout=3)
        try:
            lock.acquire()
            self._dump_json(data, str(_path_obj))
        except fl.Timeout as exc:
            raise fl.Timeout("File is locked by another process") from exc

    @staticmethod
    def _load_json(file_path):
        """Load the given json file.

        Args:
            file_path (str): The file path to load.
        """
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                return data
        except (ValueError, JSONDecodeError) as exc:
            msg = f"Corrupted file => {file_path}"
            LOG.error(msg)
            raise Exception(msg) from exc

    @staticmethod
    def file_exists(file_path):
        """Check if the file exists.

        Args:
            file_path (str): The file path to check.
        """
        print(f"Checking if file exists: {file_path}")
        print(f"Checking if file exists: {file_path}")
        print(f"Checking if file exists: {file_path}")
        print(f"Checking if file exists: {file_path}")
        print(f"Checking if file exists: {file_path}")
        print(f"Checking if file exists: {file_path}")
        return Path(file_path).is_file()

    @staticmethod
    def _dump_json(data, file_path):
        """Save the data to the json file.

        Args:
            data (dict): The data to save.
            file_path (str): The file path to save.
        """
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

    def get_modified_time(self):
        """Get the modified time of the file"""
        return self._path_obj.lstat().st_mtime
