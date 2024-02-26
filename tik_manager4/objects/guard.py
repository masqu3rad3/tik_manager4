"""Global object that holds the state of the application."""

class Guard():
    _user = None
    _permission_level = 0
    _authenticated = False
    _project_root = None
    _database_root = None
    _dcc = None
    _last_error = None
    _last_warning = None
    _last_info = None
    _category_definitions = None
    _asset_categories = []
    _shot_categories = []
    _null_categories = []
    project_settings = None
    preview_settings = None
    commons = None
    _dcc_handler = None

    @classmethod
    def set_commons(cls, commons):
        """Set the commons object"""
        cls.commons = commons

    @classmethod
    def set_project_settings(cls, project_settings):
        """Set the project settings object"""
        cls.project_settings = project_settings

    @classmethod
    def set_preview_settings(cls, preview_settings):
        """Set the preview settings object"""
        cls.preview_settings = preview_settings

    @classmethod
    def set_dcc(cls, dcc_name):
        cls._dcc = dcc_name

    @property
    def dcc(self):
        return self._dcc

    @property
    def dcc_handler(self):
        return self._dcc_handler

    @classmethod
    def set_dcc_handler(cls, handler):
        cls._dcc_handler = handler

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

    @classmethod
    def set_category_definitions(cls, definitions):
        cls._category_definitions = definitions

    @property
    def category_definitions(self):
        return self._category_definitions
