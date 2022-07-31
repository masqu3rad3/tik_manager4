from tik_manager4 import dcc


class Guard(object):
    _user = None
    _permission_level = 0
    _authenticated = False
    _project_root = None
    _database_root = None
    _dcc = None

    @classmethod
    def set_dcc(cls, dcc_name):
        cls._dcc = dcc_name

    @property
    def dcc(self):
        return self._dcc or dcc.NAME

    @classmethod
    def set_user(cls, user):
        cls._user = user

    @property
    def user(self):
        return self._user

    @classmethod
    def set_permission_level(cls, level):
        cls._permission_level = level

    @property
    def permission_level(self):
        return self._permission_level

    @classmethod
    def set_authentication_status(cls, state):
        cls._authenticated = state

    @property
    def is_authenticated(self):
        return self._authenticated

    @classmethod
    def set_project_root(cls, root):
        cls._project_root = root

    @property
    def project_root(self):
        return self._project_root

    @classmethod
    def set_database_root(cls, root):
        cls._database_root = root

    @property
    def database_root(self):
        return self._database_root
