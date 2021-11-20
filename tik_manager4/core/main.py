import os

from tik_manager4 import dcc
from tik_manager4.core import io

from tik_manager4.ui import feedback

FEED = feedback.Feedback()

## Where are we?


## Which Project?


class Main(object):
    def __init__(self):
        super(Main, self).__init__()

        self._home_dir = self._get_home_dir()
        self._common_dir = self._get_common_dir()
        if not self._common_dir:
            raise Exception("Tik Manager requires the Common Directory to work")

        self._dcc = dcc.dcc.NAME
        self._project = self._get_project()
        self._user = None

    def _get_home_dir(self):
        """Returns Documents Directory"""
        dir = os.path.expanduser('~')
        if not "Documents" in dir:
            dir = os.path.join(dir, "Documents")
        tik_manager4_folder = os.path.normpath(os.path.join(dir, "TikManager4"))
        if not os.path.exists(tik_manager4_folder):
            os.makedirs(tik_manager4_folder)
        return tik_manager4_folder

    def _get_common_dir(self):
        _database = os.path.join(self._home_dir, "smCommonFolder.json")
        _io = io.IO(file_path=_database)
        common_dir = _io.read()
        if not common_dir:
            common_dir = FEED.browse_directory()
            _io.write(common_dir)
        return common_dir

    def _get_project(self):
        _database = os.path.join(self._home_dir, "smProjects.json")
        _io = io.IO(file_path=_database)
        data = _io.read()
        if data:
            return data.get(self._dcc, None)



