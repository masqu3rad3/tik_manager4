import socket
from tik_manager4.core.settings import Settings
from tik_manager4.objects.entity import Entity

class Work(Settings, Entity):
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

    def new_version(self):
        # get filepath of current version
        _current_version_path = self.get_abs_project_path()
        self._io.folder_check(_current_version_path)

        # save the file
        # TODO file save function

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





