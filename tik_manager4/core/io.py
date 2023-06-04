"""I/O Class Module to handle all read/write operations
:created: 19/04/2020
:author: Arda Kutlu <ardakutlu@gmail.com>
"""
import os
import json
from tik_manager4.core import filelog
from tik_manager4.external.filelock import FileLock, Timeout

log = filelog.Filelog(logname=__name__, filename="tik_manager")


class IO(dict):
    # def __init__(self, file_name=None, folder_name=None, root_path=None, file_path=None):
    def __init__(self, file_path=None):
        super(IO, self).__init__()
        self.valid_extensions = [".json", ".ttask", ".twork", ".tpub"]
        self.default_extension = ".json"
        if file_path:
            self.file_path = file_path

    @property
    def file_path(self):
        return self["file_path"]

    @file_path.setter
    def file_path(self, new_path):
        name, ext = os.path.splitext(new_path)
        directory, _ = os.path.split(new_path)
        if not ext:
            log.error("IO module needs to know the extension")
            raise Exception
        if ext not in self.valid_extensions:
            log.error("IO maya_modules does not support this extension (%s)" % ext)
            raise Exception
        self["file_path"] = self.folder_check(new_path)
        # else:
        #     self["file_path"] = os.path.join(self.root_path, self.folder_name, new_path)

    def read(self, file_path=None):
        file_path = file_path if file_path else self.file_path
        return self._load_json(file_path)

    def write(self, data, file_path=None):
        file_path = file_path if file_path else self.file_path
        _lock_path = "{}.lock".format(file_path)
        lock = FileLock(_lock_path, timeout=5)
        try:
            lock.acquire()
            self._dump_json(data, file_path)
        except Timeout:
            raise ValueError("File is locked by another process")
        finally:
            lock.release()
            return file_path




    @staticmethod
    def _load_json(file_path):
        """Loads the given json file"""
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    return data
            except ValueError:
                log.error("Corrupted file => %s" % file_path)
                raise
        else:
            msg = "File does not exist => %s" % file_path
            log.error(msg)
            raise Exception(msg)

    @staticmethod
    def file_exists(file_path):
        return os.path.isfile(file_path)

    @staticmethod
    def _dump_json(data, file_path):
        """Saves the data to the json file"""
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def folder_check(check_path):
        """Checks if the folder exists, creates it if doesnt"""
        base_folder = os.path.split(check_path)[0]  # in case it is a file path

        if not os.path.isdir(os.path.normpath(base_folder)):
            os.makedirs(os.path.normpath(base_folder))
        return check_path

    def get_modified_time(self):
        """Get the modified time of the file"""
        return os.path.getmtime(self.file_path)
