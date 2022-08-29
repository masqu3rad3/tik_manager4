import socket
from tik_manager4.core.settings import Settings
from tik_manager4.objects.entity import Entity
from tik_manager4 import dcc

class Work(Settings, Entity):
    _dcc_handler = dcc.Dcc()
    def __init__(self, absolute_path,
                 name=None,
                 path=None
                 ):
        super(Work, self).__init__()
        self.settings_file = absolute_path

        self._name = self.get_property("name") or name
        self._creator = self.get_property("creator") or self._guard.user
        self._dcc = self.get_property("dcc") or self._guard.dcc
        self._versions = self.get_property("versions") or []
        self._reference_id = self.get_property("referenceID") or None
        self._relative_path = self.get_property("path") or path
        self._software_version = self.get_property("softwareVersion") or None
        self.modified_time = None # to compare and update if necessary


    def version_count(self):
        return len(self._versions)

    def new_version(self, **kwargs):
        # get filepath of current version
        _version_name = "{0}_{1}_v{2}".format(self._name, self._creator, str(self.version_count()+1).zfill(3))
        _current_version_path = self.get_abs_project_path()
        _thumbnail_path = self.get_abs_database_path("thumbnails", "{0}_thumbnail.jpg")
        self._io.folder_check(_current_version_path)

        # save the file
        # TODO file save function
        self._dcc_handler.save_as(_current_version_path)

        # generate thumbnail
        # TODO thumbnail function

        # add it to the versions
        _version = {
            "workstation": socket.gethostname(),
            "thumbnail": "",
            "relative_path": self._relative_path,
            "note": "",
            "user": self._guard.user,
            "preview": "",
        }
        self._versions.append(_version)
        self.edit_property("versions", self._versions)
        self.apply_settings()





