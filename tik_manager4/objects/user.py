"""User module for Tik Manager 4."""

import hashlib
from pathlib import Path
from tik_manager4.core.constants import ObjectType
from tik_manager4.core import filelog
from tik_manager4.core import utils
from tik_manager4.core.settings import Settings
from tik_manager4.objects.commons import Commons
from tik_manager4.objects.guard import Guard

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")

try:
    from tik_manager4.ui.dialog import feedback
    FEED = feedback.Feedback()
except Exception as exc: # pylint: disable=broad-except
    from tik_manager4.core import cli
    FEED = cli.FeedbackCLI()

class UserSettings(Settings):
    """Customized settings for the User class."""
    def apply_settings(self, force=False):
        """Apply the settings to the file."""
        if self._current_value.get("commonFolder", "") != self._original_value.get("commonFolder", ""):
            FEED.pop_info(title="Restart Required", text="Changing the common folder requires a restart of the application.")
        super().apply_settings(force=force)


class User:
    """User class to handle user data and permissions."""
    object_type = ObjectType.USER
    _guard = Guard()

    def __init__(self, common_directory=None):
        """Initializes the User class."""
        super().__init__()
        self.bookmarks = Settings()
        self.resume = Settings()
        self.localization = Settings()
        self.settings = UserSettings()
        self.user_directory = None
        self.common_directory = (
            common_directory  # this is only for programmatically set the commons
        )
        self.commons = None

        self._active_user = None
        self._validate_user_data()

    @property
    def name(self):
        """Active User Name."""
        return self._active_user

    @property
    def email(self):
        """Active User Email."""
        return self.commons.users.get_property(self._active_user).get("email")

    @property
    def is_authenticated(self):
        """Authentication Status for the active user."""
        return bool(self._guard.is_authenticated)

    @property
    def permission_level(self):
        """Permission Level of the active user."""
        return self._guard.permission_level

    def check_permissions(self, level):
        """Checks the user permissions for project actions.

        Args:
            level (int): Permission level to be checked against.

        Returns:
            int: 1 if the user has the permission, -1 otherwise.
        """
        if self.permission_level < level:
            LOG.warning("This user does not have permissions for this action")
            return -1

        if not self.is_authenticated:
            LOG.warning("User is not authenticated")
            return -1
        return 1

    @property
    def bookmark_names(self):
        """Names of the user bookmarks."""
        return [Path(x).name for x in self.get_project_bookmarks()]

    @property
    def last_project(self):
        """The last project interacted with."""
        return self.resume.get_property("project")

    @last_project.setter
    def last_project(self, value):
        """Set the last project.

        Args:
            value (str): The project name.
        """
        self.resume.edit_property("project", value)

    @property
    def last_subproject(self):
        """The last subproject interacted with."""
        return self.resume.get_property("subproject")

    @last_subproject.setter
    def last_subproject(self, value):
        """Sets the last subproject.

        Args:
            value (str): The subproject name.
        """
        self.resume.edit_property("subproject", value)

    @property
    def last_task(self):
        """The last task interacted with."""
        return self.resume.get_property("task")

    @last_task.setter
    def last_task(self, value):
        """Set the last task.

        Args:
            value (str): The task name.
        """
        self.resume.edit_property("task", value)

    @property
    def last_category(self):
        """The last category interacted with."""
        return self.resume.get_property("category")

    @last_category.setter
    def last_category(self, value):
        """Set the last category.

        Args:
            value (str): The category name.
        """
        self.resume.edit_property("category", value)

    @property
    def last_work(self):
        """The last category interacted with."""
        return self.resume.get_property("work")

    @last_work.setter
    def last_work(self, value):
        """Set the last category.

        Args:
            value (str): The category name.
        """
        self.resume.edit_property("work", value)

    @property
    def last_version(self):
        """The last version interacted with."""
        return self.resume.get_property("version")

    @last_version.setter
    def last_version(self, value):
        """Set the last version.

        Args:
            value (str): The version name.
        """
        self.resume.edit_property("version", value)

    @property
    def expanded_subprojects(self):
        """The expansion states of subprojects."""
        return self.resume.get_property("expanded_subprojects", [])

    @expanded_subprojects.setter
    def expanded_subprojects(self, value):
        """Set the expanded states of subprojects.

        Args:
            value (list): List of expanded subprojects.
        """
        self.resume.edit_property("expanded_subprojects", value)

    @property
    def split_sizes(self):
        """The split sizes to apply to the main UI."""
        return self.resume.get_property("split_sizes", [])

    @split_sizes.setter
    def split_sizes(self, value):
        """Set the split size values.

        Args:
            value (list): List of split sizes.
        """
        self.resume.edit_property("split_sizes", value)

    @property
    def visible_columns(self):
        """The column visibilities."""
        return self.resume.get_property("visible_columns", {})

    @visible_columns.setter
    def visible_columns(self, value):
        """Set the column visibilities.

        Args:
            value (dict): Dictionary of column visibilities.
        """
        self.resume.edit_property("visible_columns", value)

    @property
    def column_sizes(self):
        """Column sizes."""
        return self.resume.get_property("column_sizes", {})

    @column_sizes.setter
    def column_sizes(self, value):
        """Set the column sizes.

        Args:
            value (dict): Dictionary of column sizes.
        """
        self.resume.edit_property("column_sizes", value)

    @property
    def main_window_state(self):
        """Retrieve the geometric position and scale of the main window."""
        # calculate the default size and position for the center of the screen
        # if the property does not exist, the window should be on the center of the screen


        return self.resume.get_property("main_window_state", None)


    @main_window_state.setter
    def main_window_state(self, value):
        """Store the geometric position and scale of the main window.

        Args:
            value (dict): Dictionary of window state.
        """
        self.resume.edit_property("main_window_state", value)

    @property
    def ui_elements(self):
        """The GUI elements."""
        return self.resume.get_property("ui_elements", {})

    @ui_elements.setter
    def ui_elements(self, value):
        """Set the GUI elements.

        Args:
            value (dict): Dictionary of GUI elements.
        """
        self.resume.edit_property("ui_elements", value)

    @classmethod
    def __set_authentication_status(cls, state):
        """Sets the authentication status of the user.

        Args:
            state (bool): The authentication status.
        """
        cls._guard.set_authentication_status(state)

    @classmethod
    def __set_permission_level(cls, level):
        """Sets the permission level for the current user.

        Args:
            level (int): The permission level.
        """
        cls._guard.set_permission_level(level)

    @classmethod
    def __set_category_definitions(cls, category_definitions):
        """Sets the category definitions.

        Args:
            category_definitions: The category definitions.

        Returns:

        """
        cls._guard.set_category_definitions(category_definitions)

    def _validate_user_data(self):
        """Find or create user directories and files.

        Returns:
            int: 1 if successful.

        Raises:
            Exception: If the commons directory is not valid.
        """

        _user_root = utils.get_home_dir()
        _user_dir = Path(_user_root, "TikManager4")
        _user_dir.mkdir(exist_ok=True)
        self.user_directory = str(_user_dir)
        self.settings.settings_file = str(
            Path(self.user_directory, "user_settings.json")
        )
        self.bookmarks.settings_file = str(Path(self.user_directory, "bookmarks.json"))
        self.resume.settings_file = str(Path(self.user_directory, "resume.json"))
        self.localization.settings_file = str(Path(self.user_directory, "localization.json"))
        # Check if the common folder defined in the user settings
        self.common_directory = self.common_directory or self.settings.get_property(
            "commonFolder"
        )

        if not self.common_directory or not Path(self.common_directory).is_dir():
            # if it is not overridden while creating the object ask it from the user
            if not self.common_directory:
                FEED.pop_info(
                    title="Set Commons Directory",
                    text="Commons Directory is not defined. "
                    "Press Continue to select Commons Directory",
                    button_label="Continue",
                )
                self.common_directory = FEED.browse_directory()
            assert (
                self.common_directory
            ), "Commons Directory must be defined to continue"
            if not Path(self.common_directory).is_dir():
                answer = FEED.pop_question(
                    title="Commons Directory does not exist",
                    text=f"Defined Commons Directory does not exist. \n{self.common_directory}"
                    f"Do you want to define a new Commons Directory?",
                    buttons=["yes", "cancel"],
                )
                if answer == "yes":
                    self.common_directory = FEED.browse_directory()
                else:
                    raise Exception("Commons Directory does not exist. Exiting...")
        self.settings.edit_property("commonFolder", self.common_directory)
        self.settings.add_property(
            "user_templates_directory", self.user_directory, force=False
        )
        self.settings.add_property("alembic_viewer", "", force=False)
        self.settings.add_property("usd_viewer", "", force=False)
        self.settings.add_property("fbx_viewer", "", force=False)
        self.settings.add_property("image_viewer", "", force=False)
        self.settings.add_property("sequence_viewer", "", force=False)
        self.settings.add_property("video_player", "", force=False)
        self.settings.apply_settings()

        self.commons = Commons(self.common_directory)
        if not self.commons.is_valid:
            answer = FEED.pop_question(
                title="Commons Directory is not valid",
                text="Commons Directory doesn't contain all of the necessary "
                "files and it is write protected.\n"
                "Do you want to define a new Commons Directory?",
                buttons=["yes", "cancel"],
            )
            if answer == "yes":
                self.common_directory = FEED.browse_directory()
                self.commons = Commons(self.common_directory)
                self.settings.edit_property("commonFolder", self.common_directory)
                self.settings.apply_settings()
            else:
                raise Exception("Commons Directory is not valid. Exiting...")
        self.__set_category_definitions(self.commons.category_definitions)

        for key, val in self.commons.user_defaults.get_property("bookmarks").items():
            if not self.bookmarks.get_property(key=key):
                self.bookmarks.add_property(key=key, val=val)

        for key, val in self.commons.user_defaults.get_property("resume").items():
            if not self.resume.get_property(key=key):
                self.resume.add_property(key=key, val=val)

        # set the active user
        active_user = self.resume.get_property("user")
        state, _msg = self.set(active_user, save_to_db=False)
        if state == -1:
            self.set("Generic", save_to_db=False)

        self.settings.apply_settings()
        self.bookmarks.apply_settings()
        self.resume.apply_settings()
        return 1

    def get(self):
        """Return the currently active user."""
        return self._active_user

    def set(self, user_name, password=None, save_to_db=True, clear_db=False):
        """Set the active user to the session.

        Args:
            user_name (str): The user name.
            password (str, optional): The password. If not provided, the user
                will be authenticated with the hash in the database.
            save_to_db (bool, optional): If True, a hash of the user name and
                password will be saved to the database for auto-login.
            clear_db (bool, optional): If True the hash will be cleared from
                the database.

        Returns:
            tuple: (1, "Success") if successful, (-1, LOG.warning) otherwise.
        """
        # check if the user exists in common database
        if user_name not in self.commons.get_users():
            return -1, LOG.warning(
                f"User {self._active_user} cannot set because "
                f"it does not exist in commons database"
            )
        if password is not None:  # try to authenticate the active user
            if self.check_password(user_name, password):
                self.__set_authentication_status(True)
            else:
                return -1, LOG.warning(
                    "Wrong password provided for user %s" % user_name
                )
        elif self.resume.get_property("user_dhash") == self.__hash_pass(
            "{0}{1}".format(
                user_name, self.commons.users.get_property(user_name).get("pass")
            )
        ):
            self.__set_authentication_status(True)
        else:
            self.__set_authentication_status(
                False
            )  # make sure it is not authenticated if no password
        self._active_user = user_name
        self._guard.set_user(self._active_user)
        self.resume.edit_property("user", self._active_user)
        if save_to_db:
            _d_hash = self.__hash_pass(
                "{0}{1}".format(
                    self._active_user,
                    self.commons.users.get_property(self._active_user).get("pass"),
                )
            )
            self.resume.edit_property("user_dhash", _d_hash)
        if clear_db:
            self.resume.edit_property("user_dhash", None)
        self.resume.apply_settings()
        self.__set_permission_level(
            self.commons.check_user_permission_level(user_name)
        )
        return user_name, "Success"


    def authenticate(self, password):
        """Authenticate the active user with the given password.

        Args:
            password (str): The password.

        Returns:
            tuple: (1, "Success") if successful, (-1, LOG.warning) otherwise.
        """
        if self.check_password(self._active_user, password):
            self.__set_authentication_status(True)
            return 1, "Success"
        self.__set_authentication_status(False)
        return -1, LOG.warning(
            "Wrong password provided for user %s" % self._active_user
        )

    def create_new_user(
        self,
        new_user_name,
        new_user_initials,
        new_user_password,
        permission_level,
        active_user_password=None,
        email=None,
    ):
        """Create a new user and stores it in database.

        Args:
            new_user_name (str): The new user name.
            new_user_initials (str): The new user initials.
            new_user_password (str): The new user password.
            permission_level (int): The permission level.
            active_user_password (str, optional): The password of the
                active user.
            email (str, optional): The email address of the user.

        Returns:
            tuple: (1, "Success") if successful, (-1, LOG.warning) otherwise.
        """

        # first check the permissions of active user
        if self.permission_level < 3:
            return -1, LOG.warning(
                f"User {self._active_user} has no permission to create new users"
            )

        # Don't allow non-authenticated users to go further

        if active_user_password:
            self.authenticate(active_user_password)

        if not self.is_authenticated:
            return -1, LOG.warning(
                "Active user is not authenticated or the password is wrong"
            )

        if new_user_name in self.commons.users.keys:
            return -1, LOG.error("User %s already exists. Aborting" % new_user_name)
        email = email or ""
        user_data = {
            "initials": new_user_initials,
            "pass": self.__hash_pass(new_user_password),
            "permissionLevel": self.__clamp_level(permission_level),
            "email": email
        }
        self.commons.users.add_property(new_user_name, user_data)
        self.commons.users.apply_settings()
        return 1, "Success"

    def delete_user(self, user_name, active_user_password=None):
        """Remove the user from database.

        Args:
            user_name (str): The user name.
            active_user_password (str, optional): The password of the
                active user. If not provided, the user will be authenticated
                with the hash in the database.

        Returns:
            tuple: (1, "Success") if successful, (-1, LOG.warning) otherwise.
        """
        # first check the permissions of active user
        if self.permission_level < 3:
            return -1, LOG.warning(
                "User %s has no permission to delete users" % self._active_user
            )

        # Don't allow non-authenticated users to go further
        if active_user_password:
            self.authenticate(active_user_password)
        if not self.is_authenticated:
            return -1, LOG.warning(
                "Active user is not authenticated or the password is wrong"
            )

        if user_name == "Admin":
            return -1, LOG.warning("Admin User cannot be deleted")
        if user_name == "Generic":
            return -1, LOG.warning("Generic User cannot be deleted")

        if user_name not in self.commons.users.keys:
            return -1, LOG.error("User %s does not exist. Aborting" % user_name)
        self.commons.users.delete_property(user_name)
        self.commons.users.apply_settings()
        return 1, "Success"

    @staticmethod
    def __clamp_level(level):
        """Clamp the level between 0-3 and makes sure its integer."""
        return max(0, min(int(level), 3))

    def change_permission_level(self, user_name, new_level, active_user_password=None):
        """Change the permission level of a user.

        Args:
            user_name (str): The user name.
            new_level (int): The new permission level.
            active_user_password (str, optional): The password of the
                active user. If not provided, the user will be authenticated
                with the hash in the database.

        Returns:
            tuple: (1, "Success") if successful, (-1, LOG.warning) otherwise.
        """
        # first check the permissions of active user
        if self.permission_level < 3:
            msg = (
                "User %s has no permission to change permission level of other users"
                % self._active_user
            )
            return -1, LOG.warning(msg)
            # Don't allow non-authenticated users to go further
        if active_user_password:
            self.authenticate(active_user_password)
        if not self.is_authenticated:
            return -1, LOG.warning(
                "Active user is not authenticated or the password is wrong"
            )

        if user_name == "Admin":
            return -1, LOG.warning("Admin permission levels cannot be altered")
        if user_name == "Generic":
            return -1, LOG.warning("Generic User permission levels cannot be altered")

        if user_name not in self.commons.users.keys:
            return -1, LOG.error("User %s does not exist. Aborting" % user_name)

        user_data = self.commons.users.get_property(user_name)
        user_data["permissionLevel"] = self.__clamp_level(new_level)
        self.commons.users.edit_property(user_name, user_data)
        self.commons.users.apply_settings()
        return 1, "Success"

    def change_user_password(self, old_password, new_password, user_name=None):
        """Change the user password.

        It only changes the active user, a.k.a needs to be logged in.

        Args:
            old_password (str): The old password.
            new_password (str): The new password.
            user_name (str, optional): The user name. If not provided, the
                active user will be used.
        """
        user_name = user_name or self._active_user
        if self.__hash_pass(old_password) == self.commons.users.get_property(
            user_name
        ).get("pass"):
            self.commons.users.get_property(user_name)["pass"] = self.__hash_pass(
                new_password
            )
            self.commons.users.apply_settings()
            return 1, "Success"
        else:
            return -1, LOG.error("Old password for %s does not match" % user_name)

    def check_password(self, user_name, password):
        """Check the given password against the hashed password.

        Args:
            user_name (str): The user name.
            password (str): The password.

        Returns:
            bool: True if the password is correct, False otherwise.
        """
        hashed_pass = self.__hash_pass(password)
        if self.commons.users.get_property(user_name).get("pass", "") == hashed_pass:
            return True
        else:
            return False

    @staticmethod
    def __hash_pass(password):
        """Hash the password.

        Args:
            password (str): The password.

        Returns:
            str: The hashed password.
        """
        return hashlib.sha1(str(password).encode("utf-8")).hexdigest()

    def get_project_bookmarks(self):
        """Return the user bookmarked projects as list of dictionaries."""
        return self.bookmarks.get_property("bookmarkedProjects")

    def add_project_bookmark(self, project_path):
        """Add a new project bookmark to the user bookmarks.

        Args:
            project_path (str): The project path.

        Returns:
            int: 1 if successful, -1 otherwise.
        """
        bookmark_list = self.bookmarks.get_property("bookmarkedProjects")
        if project_path not in bookmark_list:
            bookmark_list.append(project_path)
            self.bookmarks.apply_settings()
            return 1
        else:
            LOG.warning("Project %s already exists in bookmarks" % project_path)
            return -1

    def delete_project_bookmark(self, project_path):
        """Delete a project bookmark from the user bookmarks.

        Args:
            project_path (str): The project path.

        Returns:
            int: 1 if successful, -1 otherwise.
        """
        bookmark_list = self.bookmarks.get_property("bookmarkedProjects")
        if project_path not in bookmark_list:
            LOG.warning("Project %s doesn't exist in bookmarks" % project_path)
            return -1
        bookmark_list.remove(project_path)
        self.bookmarks.apply_settings()
        return 1

    def add_recent_project(self, path):
        """Add a project to the recent projects list.

        Args:
            path (str): The project path.

        Returns:
            int: 1 if successful, -1 otherwise.
        """
        recent_list = self.bookmarks.get_property("recentProjects")
        if path in recent_list:
            recent_list.remove(path)
        recent_list.append(path)
        if len(recent_list) > 10:
            recent_list.pop(0)
        self.bookmarks.apply_settings(force=True)

    def get_recent_projects(self):
        """Return the list of recent projects."""
        return self.bookmarks.get_property("recentProjects")

    def add_recent_commons(self, commons_path):
        """Add the commons path to the recent commons list."""
        commons_list = self.bookmarks.get_property("recentCommons")
        if commons_path in commons_list:
            commons_list.remove(commons_path)
        commons_list.append(commons_path)
        if len(commons_list) > 10:
            commons_list.pop(0)
        self.bookmarks.apply_settings(force=True)

    def get_recent_commons(self):
        """Return the list of recent commons."""
        return self.bookmarks.get_property("recentCommons")