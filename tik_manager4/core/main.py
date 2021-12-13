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

        #db io instances
        self.smCommonFolder_io = None
        self.smProjects_io = None
        self.smUser_io = None


        self._home_dir = self._get_home_dir()
        self._common_dir = self._get_common_dir()
        if not self._common_dir:
            raise Exception("Tik Manager requires the Common Directory to work")

        self._dcc = dcc.dcc.NAME
        self._project = self._get_project()
        self._user = self._get_user()

    @property
    def dcc(self):
        return self._dcc

    @property
    def project(self):
        return self._project

    @property
    def user(self):
        return self._user

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
        """Returns the common directory (or tries to set if not defined)"""

        _database = os.path.join(self._home_dir, "smCommonFolder.json")
        self.smCommonFolder_io = io.IO(file_path=_database)
        common_dir = self.smCommonFolder_io.read()
        if not common_dir:
            FEED.pop_info(title="Set Common Directory", text="Common Directory is not defined. "
                                                             "Press Continue to select Common Directory",
                          button_label="Continue")
            common_dir = FEED.browse_directory()
            self.smCommonFolder_io.write(common_dir)
        return common_dir

    def _get_project(self):
        """Returns the current defined project in database if any"""

        _database = os.path.join(self._home_dir, "smProjects.json")
        self.smProjects_io = io.IO(file_path=_database)
        data = self.smProjects_io.read()
        if data:
            return data.get_property(self._dcc, None)

    def _get_user(self):
        """Returns the current user or sets it as 'generic' if no user data"""

        _database = os.path.join(self._home_dir, "smUser.json")
        self.smUser_io = io.IO(file_path=_database)
        data = self.smUser_io.read()
        if not data:
            data = "Generic"
            self.smUser_io.write(data)
        return data







