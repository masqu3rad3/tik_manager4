"""Module to communicate with other modules regarding the application state."""

class Guard:
    """Global object that holds the state of the application."""
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
    _metadata_definitions = None
    _asset_categories = []
    _shot_categories = []
    _null_categories = []
    project_settings = None
    preview_settings = None
    commons = None
    _dcc_handler = None
    _management_handler = None

    @classmethod
    def set_commons(cls, commons):
        """Set the commons object.

        Args:
            commons (Commons): The commons object.
        """
        cls.commons = commons

    @classmethod
    def set_project_settings(cls, project_settings):
        """Set the project settings object.

        Args:
            project_settings (Settings): The project settings object.
        """
        cls.project_settings = project_settings

    @classmethod
    def set_preview_settings(cls, preview_settings):
        """Set the preview settings object.

        Args:
            preview_settings (Settings): The preview settings object.
        """
        cls.preview_settings = preview_settings

    @classmethod
    def set_dcc(cls, dcc_name):
        """Set the DCC name.

        Args:
            dcc_name (str): The name of the DCC.
        """
        cls._dcc = dcc_name

    @property
    def dcc(self):
        """Return the DCC name."""
        return self._dcc

    @property
    def dcc_handler(self):
        """Return the DCC handler object."""
        return self._dcc_handler

    @classmethod
    def set_dcc_handler(cls, handler):
        """Set the DCC handler object.

        Args:
            handler (object): The DCC handler object.
        """
        cls._dcc_handler = handler

    @property
    def management_handler(self):
        """Return the management handler object."""
        return self._management_handler

    @classmethod
    def set_management_handler(cls, handler):
        """Set the management handler object.

        Args:
            handler (object): The management handler object.
        """
        cls._management_handler = handler

    @classmethod
    def set_user(cls, user):
        """Set the user object.

        Args:
            user (User): The user object.
        """
        cls._user = user

    @property
    def user(self):
        """Return the user object."""
        return self._user

    @classmethod
    def set_permission_level(cls, level):
        """Set the permission level for the current user."""
        cls._permission_level = level

    @property
    def permission_level(self):
        """Return the permission level of the user."""
        return self._permission_level

    @classmethod
    def set_authentication_status(cls, state):
        """Set the authentication status of the user.

        Args:
            state (bool): The authentication status.
        """
        cls._authenticated = state

    @property
    def is_authenticated(self):
        """Return the authentication status of the user."""
        return self._authenticated

    @classmethod
    def set_project_root(cls, root):
        """Set the project root path.

        Args:
            root (str): The project root path.
        """
        cls._project_root = root

    @property
    def project_root(self):
        """Return the project root path."""
        return self._project_root

    @classmethod
    def set_database_root(cls, root):
        """Set the database root path.

        Args:
            root (str): The database root path.
        """
        cls._database_root = root

    @property
    def database_root(self):
        """Return the database root path."""
        return self._database_root

    @classmethod
    def set_category_definitions(cls, definitions):
        """Set the category definitions.

        Args:
            definitions (Settings): The category definitions.
        """
        cls._category_definitions = definitions

    @property
    def category_definitions(self):
        """Return the category definitions."""
        return self._category_definitions

    @classmethod
    def set_metadata_definitions(cls, definitions):
        """Set the metadata definitions.

        Args:
            definitions (Settings): The metadata definitions.
        """
        cls._metadata_definitions = definitions

    @property
    def metadata_definitions(self):
        """Return the metadata definitions."""
        return self._metadata_definitions