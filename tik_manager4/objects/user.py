import hashlib
from pathlib import Path
from tik_manager4.core import filelog
from tik_manager4.core import utils
from tik_manager4.core.settings import Settings
from tik_manager4.objects.commons import Commons
from tik_manager4.objects.guard import Guard
from tik_manager4.ui.dialog import feedback

log = filelog.Filelog(logname=__name__, filename="tik_manager4")

FEED = feedback.Feedback()


class User(object):
    _guard = Guard()

    def __init__(self, common_directory=None):
        super(User, self).__init__()
        self.settings = Settings()
        self.bookmarks = Settings()
        self.resume = Settings()
        self.user_directory = None
        self.common_directory = (
            common_directory  # this is only for programmatically set the commons
        )
        self.commons = None

        self._active_user = None
        self._validate_user_data()

    @property
    def is_authenticated(self):
        return bool(self._guard.is_authenticated)

    @property
    def permission_level(self):
        return self._guard.permission_level

    @property
    def bookmark_names(self):
        """Return the bookmark names"""
        return [Path(x).name for x in self.get_project_bookmarks()]
        # return [os.path.basename(x) for x in self.get_project_bookmarks()]

    @property
    def last_project(self):
        """Returns the last project"""
        return self.resume.get_property("project")

    @last_project.setter
    def last_project(self, value):
        """Sets the last project"""
        self.resume.edit_property("project", value)

    @property
    def last_subproject(self):
        """Returns the last subproject"""
        return self.resume.get_property("subproject")

    @last_subproject.setter
    def last_subproject(self, value):
        """Sets the last subproject"""
        self.resume.edit_property("subproject", value)

    @property
    def last_task(self):
        """Returns the last task"""
        return self.resume.get_property("task")

    @last_task.setter
    def last_task(self, value):
        """Sets the last task"""
        self.resume.edit_property("task", value)

    @property
    def last_category(self):
        """Returns the last category"""
        return self.resume.get_property("category")

    @last_category.setter
    def last_category(self, value):
        """Sets the last category"""
        self.resume.edit_property("category", value)

    @property
    def last_work(self):
        """Returns the last category"""
        return self.resume.get_property("work")

    @last_work.setter
    def last_work(self, value):
        """Sets the last category"""
        self.resume.edit_property("work", value)

    @property
    def last_version(self):
        """Returns the last version"""
        return self.resume.get_property("version")

    @last_version.setter
    def last_version(self, value):
        """Sets the last version"""
        self.resume.edit_property("version", value)

    @property
    def expanded_subprojects(self):
        """Return the expanded states of subprojects."""
        return self.resume.get_property("expanded_subprojects", [])

    @expanded_subprojects.setter
    def expanded_subprojects(self, value):
        """Set the expanded states of subprojects."""
        self.resume.edit_property("expanded_subprojects", value)

    @property
    def split_sizes(self):
        """Get the split sizes to apply to the main UI"""
        return self.resume.get_property("split_sizes", [])

    @split_sizes.setter
    def split_sizes(self, value):
        """Set the split size values."""
        self.resume.edit_property("split_sizes", value)

    @property
    def visible_columns(self):
        """Get the column visibilities."""
        return self.resume.get_property("visible_columns", {})

    @visible_columns.setter
    def visible_columns(self, value):
        """Set the column visibilities."""
        self.resume.edit_property("visible_columns", value)

    @classmethod
    def __set_authentication_status(cls, state):
        # cls._authenticated = state
        cls._guard.set_authentication_status(state)

    @classmethod
    def __set_permission_level(cls, level):
        # cls._permission_level = level
        cls._guard.set_permission_level(level)

    @classmethod
    def __set_category_definitions(cls, category_definitions):
        cls._guard.set_category_definitions(category_definitions)

    @classmethod
    def __set_asset_categories(cls, asset_categories):
        cls._guard.set_asset_categories(asset_categories)

    @classmethod
    def __set_shot_categories(cls, shot_categories):
        cls._guard.set_shot_categories(shot_categories)

    @classmethod
    def __set_null_categories(cls, empty_categories):
        cls._guard.set_null_categories(empty_categories)

    def _validate_user_data(self):
        """Finds or creates user directories and files"""

        _user_root = utils.get_home_dir()
        # self.user_directory = str((Path(_user_root, "TikManager4").mkdir(exist_ok=True)))
        _user_dir = Path(_user_root, "TikManager4")
        _user_dir.mkdir(exist_ok=True)
        self.user_directory = str(_user_dir)
        # self.user_directory = os.path.normpath(os.path.join(_user_root, "TikManager4"))
        # if not os.path.isdir(os.path.normpath(self.user_directory)):
        #     os.makedirs(os.path.normpath(self.user_directory))
        self.settings.settings_file = str(Path(self.user_directory, "userSettings.json"))
        # self.settings.settings_file = os.path.join(
        #     self.user_directory, "userSettings.json"
        # )
        self.bookmarks.settings_file = str(Path(self.user_directory, "bookmarks.json"))
        # self.bookmarks.settings_file = os.path.join(
        #     self.user_directory, "bookmarks.json"
        # )
        self.resume.settings_file = str(Path(self.user_directory, "resume.json"))
        # self.resume.settings_file = os.path.join(self.user_directory, "resume.json")

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
        self.settings.edit_property("commonFolder", self.common_directory)
        self.settings.apply_settings()

        self.commons = Commons(self.common_directory)
        self.__set_category_definitions(self.commons.category_definitions)

        # set the default keys for missing ones
        for key, val in self.commons.user_settings.get_property(
            "userPreferences"
        ).items():
            if not self.settings.get_property(key=key):
                self.settings.add_property(key=key, val=val)

        for key, val in self.commons.user_settings.get_property("bookmarks").items():
            if not self.bookmarks.get_property(key=key):
                self.bookmarks.add_property(key=key, val=val)


        for key, val in self.commons.user_settings.get_property("resume").items():
            if not self.resume.get_property(key=key):
                self.resume.add_property(key=key, val=val)

        # set the active user
        active_user = self.resume.get_property("user")
        state, msg = self.set(active_user, save_to_db=False)
        if state == -1:
            self.set("Generic", save_to_db=False)

        self.settings.apply_settings()
        self.bookmarks.apply_settings()
        self.resume.apply_settings()
        return 1

    def get(self):
        """Returns the currently active user"""
        return self._active_user

    def set(self, user_name, password=None, save_to_db=True, clear_db=False):
        """Sets the active user to the session"""
        # check if the user exists in common database
        if user_name in self.commons.get_users():
            if password is not None:  # try to authenticate the active user
                if self.check_password(user_name, password):
                    self.__set_authentication_status(True)
                else:
                    return -1, log.warning(
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
            if save_to_db:
                # self.bookmarks.edit_property("activeUser", self._active_user)
                self.resume.edit_property("user", self._active_user)
                _d_hash = self.__hash_pass(
                    "{0}{1}".format(
                        self._active_user,
                        self.commons.users.get_property(self._active_user).get("pass"),
                    )
                )
                self.resume.edit_property("user_dhash", _d_hash)
                self.resume.apply_settings()
            if clear_db:
                self.resume.edit_property("user", None)
                self.resume.edit_property("user_dhash", None)
                self.resume.apply_settings()
            self.__set_permission_level(
                self.commons.check_user_permission_level(user_name)
            )
            return user_name, "Success"
        else:
            return -1, log.warning(
                "User %s cannot set because it does not exist in commons database"
            )

    def authenticate(self, password):
        if self.check_password(self._active_user, password):
            self.__set_authentication_status(True)
            return 1, "Success"
        else:
            self.__set_authentication_status(False)
            return -1, log.warning(
                "Wrong password provided for user %s" % self._active_user
            )

    def create_new_user(
        self,
        new_user_name,
        new_user_initials,
        new_user_password,
        permission_level,
        active_user_password=None,
    ):
        """Creates a new user and stores it in database"""

        # first check the permissions of active user
        if self.permission_level < 3:
            return -1, log.warning(
                "User %s has no permission to create new users" % self._active_user
            )

        # Don't allow non-authenticated users to go further

        if active_user_password:
            self.authenticate(active_user_password)

        if not self.is_authenticated:
            return -1, log.warning(
                "Active user is not authenticated or the password is wrong"
            )

        if new_user_name in self.commons.users.keys:
            return -1, log.error("User %s already exists. Aborting" % new_user_name)
        user_data = {
            "initials": new_user_initials,
            "pass": self.__hash_pass(new_user_password),
            "permissionLevel": self.__clamp_level(permission_level),
        }
        self.commons.users.add_property(new_user_name, user_data)
        self.commons.users.apply_settings()
        return 1, "Success"

    def delete_user(self, user_name, active_user_password=None):
        """Removes the user from database"""
        # first check the permissions of active user
        if self.permission_level < 3:
            return -1, log.warning(
                "User %s has no permission to delete users" % self._active_user
            )

        # Don't allow non-authenticated users to go further
        if active_user_password:
            self.authenticate(active_user_password)
        if not self.is_authenticated:
            return -1, log.warning(
                "Active user is not authenticated or the password is wrong"
            )

        if user_name == "Admin":
            return -1, log.warning("Admin User cannot be deleted")
        if user_name == "Generic":
            return -1, log.warning("Generic User cannot be deleted")

        if user_name not in self.commons.users.keys:
            return -1, log.error("User %s does not exist. Aborting" % user_name)
        self.commons.users.delete_property(user_name)
        self.commons.users.apply_settings()
        return 1, "Success"

    @staticmethod
    def __clamp_level(level):
        """Clamps the level between 0-3 and makes sure its integer"""
        return max(0, min(int(level), 3))

    def change_permission_level(self, user_name, new_level, active_user_password=None):
        # first check the permissions of active user
        if self.permission_level < 3:
            msg = (
                "User %s has no permission to change permission level of other users"
                % self._active_user
            )
            return -1, log.warning(msg)
            # Don't allow non-authenticated users to go further
        if active_user_password:
            self.authenticate(active_user_password)
        if not self.is_authenticated:
            return -1, log.warning(
                "Active user is not authenticated or the password is wrong"
            )

        if user_name == "Admin":
            return -1, log.warning("Admin permission levels cannot be altered")
        if user_name == "Generic":
            return -1, log.warning("Generic User permission levels cannot be altered")

        if user_name not in self.commons.users.keys:
            return -1, log.error("User %s does not exist. Aborting" % user_name)

        user_data = self.commons.users.get_property(user_name)
        user_data["permissionLevel"] = self.__clamp_level(new_level)
        self.commons.users.edit_property(user_name, user_data)
        self.commons.users.apply_settings()
        return 1, "Success"

    def change_user_password(self, old_password, new_password, user_name=None):
        """Change the user password.
        It only changes the active user, a.k.a needs to be logged in"""
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
            return -1, log.error("Old password for %s does not match" % user_name)

    def check_password(self, user_name, password):
        """checks the given password against the hashed password"""
        hashed_pass = self.__hash_pass(password)
        if self.commons.users.get_property(user_name).get("pass", "") == hashed_pass:
            return True
        else:
            return False

    @staticmethod
    def __hash_pass(password):
        """Hashes the password"""
        return hashlib.sha1(str(password).encode("utf-8")).hexdigest()

    def get_project_bookmarks(self):
        """Returns the user bookmarked projects as list of dictionaries"""
        return self.bookmarks.get_property("bookmarkedProjects")

    def add_project_bookmark(self, project_path):
        """Add a new project bookmark to the user bookmarks"""
        bookmark_list = self.bookmarks.get_property("bookmarkedProjects")
        if project_path not in bookmark_list:
            bookmark_list.append(project_path)
            self.bookmarks.apply_settings()
            return 1
        else:
            log.warning("Project %s already exists in bookmarks" % project_path)
            return -1

    def delete_project_bookmark(self, project_path):
        """Delete a project bookmark from the user bookmarks"""
        bookmark_list = self.bookmarks.get_property("bookmarkedProjects")
        if project_path in bookmark_list:
            bookmark_list.remove(project_path)
            self.bookmarks.apply_settings()
            return 1
        else:
            log.warning("Project %s doesn't exist in bookmarks" % project_path)
            return -1

    def add_recent_project(self, path):
        recents_list = self.bookmarks.get_property("recentProjects")
        if path in recents_list:
            recents_list.remove(path)
        recents_list.append(path)
        if len(recents_list) > 10:
            recents_list.pop(0)
        self.bookmarks.apply_settings(force=True)

    def get_recent_projects(self):
        return self.bookmarks.get_property("recentProjects")

