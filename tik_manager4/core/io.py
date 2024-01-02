"""I/O Class Module to handle all read/write operations
:created: 19/04/2020
:author: Arda Kutlu <ardakutlu@gmail.com>
"""

from pathlib import Path
import json
from json.decoder import JSONDecodeError
from tik_manager4.core import filelog
from tik_manager4.external import filelock as fl

LOG = filelog.Filelog(logname=__name__)


class IO():
    def __init__(self, file_path=None):
        super(IO, self).__init__()
        self.valid_extensions = [".json", ".ttask", ".twork", ".tpub"]
        self.default_extension = ".json"
        self._string_path = None
        self._path_obj = None
        if file_path:
            self.file_path = file_path

    @property
    def file_path(self):
        return self._string_path

    @file_path.setter
    def file_path(self, new_path):
        self._path_obj = Path(new_path)
        # _new_path_obj = Path(new_path)
        ext = self._path_obj.suffix

        if not ext:
            LOG.error("IO module needs to know the extension")
            raise Exception
        if ext not in self.valid_extensions:
            LOG.error("IO maya_modules does not support this extension (%s)" % ext)
            raise Exception
        self._path_obj.parent.mkdir(parents=True, exist_ok=True)
        self._string_path = str(self._path_obj)
        # self["file_path"] = self.folder_check(new_path)
        # self["file_path"] = str(_new_path_obj)

    def read(self, file_path=None):
        # file_path = file_path or self._string_path
        _path_obj = Path(file_path) if file_path else self._path_obj
        if _path_obj.is_file():
        # if os.path.isfile(file_path):
            return self._load_json(str(_path_obj))
        else:
            msg = f"File does not exist => {str(_path_obj)}"
            LOG.error(msg)
            raise Exception(msg)

    def write(self, data, file_path=None):
        _path_obj = Path(file_path) if file_path else self._path_obj
        _lock_path = f"{str(_path_obj)}.lock"
        lock = fl.FileLock(_lock_path, timeout=3)
        try:
            lock.acquire()
            self._dump_json(data, str(_path_obj))
        except fl.Timeout:
            raise fl.Timeout("File is locked by another process")

    @staticmethod
    def _load_json(file_path):
        """Loads the given json file"""
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                return data
        except (ValueError, JSONDecodeError):
            LOG.error("Corrupted file => %s" % file_path)
            raise Exception("Corrupted file => %s" % file_path)

    @staticmethod
    def file_exists(file_path):
        return Path(file_path).is_file()

    @staticmethod
    def _dump_json(data, file_path):
        """Saves the data to the json file"""
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

    def get_modified_time(self):
        """Get the modified time of the file"""
        return self._path_obj.lstat().st_mtime
