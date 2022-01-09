import hashlib
import logging
import os
from tik_manager4.core import filelog
from tik_manager4.core.settings import Settings
from tik_manager4.objects.commons import Commons
from tik_manager4.ui import feedback

log = filelog.Filelog(logname=__name__, filename="tik_manager4")

FEED = feedback.Feedback()


class User(object):
    _authenticated = False
    _permission_level = 0

    def __init__(self, commons_directory=None):
        super(User, self).__init__()
        self.settings = Settings()
        self.bookmarks = Settings()
        self.states = Settings()  # is this necessary anymore??
        self.user_directory = None
        self.common_directory = commons_directory  # this is only for programmatically set the commons
        self.commons = None

        self._active_user = None
        # self._password_authenticated = False
        self._validate_user_data()

    @property
    def directory(self):
        return self.user_directory

    @property
    def is_authenticated(self):
        return bool(self._authenticated)

    @property
    def permission_level(self):
        return self._permission_level

    @classmethod
    def __set_authentication_status(cls, state):
        cls._authenticated = state

    @classmethod
    def __set_permission_level(cls, level):
        cls._permission_level = level

    def _validate_user_data(self):
        """Finds or creates user directories and files"""

        _user_root = os.path.expanduser('~')
        self.user_directory = os.path.normpath(os.path.join(_user_root, "TikManager4"))
        if not os.path.isdir(os.path.normpath(self.user_directory)):
            os.makedirs(os.path.normpath(self.user_directory))
        self.settings.settings_file = os.path.join(self.user_directory, "userSettings.json")
        self.bookmarks.settings_file = os.path.join(self.user_directory, "bookmarks.json")

        # Check if the common folder defined in the user settings
        self.common_directory = self.common_directory or self.settings.get_property("commonFolder")
        if not self.common_directory or not os.path.isdir(self.common_directory):
            # if it is not overridden while creating the object ask it from the user
            if not self.common_directory:
                FEED.pop_info(title="Set Commons Directory", text="Commons Directory is not defined. "
                                                                  "Press Continue to select Commons Directory",
                              button_label="Continue")
                self.common_directory = FEED.browse_directory()
            assert self.common_directory, "Commons Directory must be defined to continue"
        self.settings.edit_property("commonFolder", self.common_directory)
        self.settings.apply_settings()

        self.commons = Commons(self.common_directory)

        # set the default keys for missing ones
        for key, val in self.commons.manager.get_property("defaultUserSettings").items():
            if not self.settings.get_property(key=key):
                self.settings.add_property(key=key, val=val)

        for key, val in self.commons.manager.get_property("defaultBookmarks").items():
            if not self.bookmarks.get_property(key=key):
                self.bookmarks.add_property(key=key, val=val)

        # set the active user
        active_user = self.bookmarks.get_property("activeUser")
        state, msg = self.set_active_user(active_user, save_to_db=False)
        if state == -1:
            self.set_active_user("Generic", save_to_db=False)
        # if active_user not in self.commons.get_users():
        #     active_user = "Generic"
        # self.set_active_user(active_user, save_to_db=False)

        self.settings.apply_settings()
        self.bookmarks.apply_settings()
        return 1

    def get_active_user(self):
        """Returns the currently active user"""
        return self._active_user

    def set_active_user(self, user_name, password=None, save_to_db=True):
        """Sets the active user to the session"""

        # check if the user exists in common database
        if user_name in self.commons.get_users():
            if password is not None:  # try to authenticate the active user
                if self.check_password(user_name, password):
                    self.__set_authentication_status(True)
                else:
                    return -1, log.warning("Wrong password provided for user %s" % user_name)
            else:
                self.__set_authentication_status(False)  # make sure it is not authenticated if no password
            self._active_user = user_name
            if save_to_db:
                self.bookmarks.edit_property("activeUser", self._active_user)
            self.__set_permission_level(self.commons.check_user_permission_level(user_name))
            return user_name, "Success"
        else:
            return -1, log.warning("User %s cannot set because it does not exist in commons database")

    def authenticate(self, password):
        if self.check_password(self._active_user, password):
            self.__set_authentication_status(True)
            return 1, "Success"
        else:
            self.__set_authentication_status(False)
            return -1, log.warning("Wrong password provided for user %s" % self._active_user)

    def create_new_user(self, new_user_name, new_user_initials, new_user_password, permission_level,
                        active_user_password=None):
        """Creates a new user and stores it in database"""

        # first check the permissions of active user - Creating new user requires level 3 permissions
        if self.permission_level < 3:
            return -1, log.warning("User %s has no permission to create new users" % self._active_user)

        # Don't allow non-authenticated users to go further

        if active_user_password:
            self.authenticate(active_user_password)

        if not self.is_authenticated:
            return -1, log.warning("Active user is not authenticated or the password is wrong")

        if new_user_name in self.commons.users.all_properties:
            return -1, log.error("User %s already exists. Aborting" % new_user_name)
        user_data = {
            "initials": new_user_initials,
            "pass": self.__hash_pass(new_user_password),
            "permissionLevel": self.__clamp_level(permission_level)
        }
        self.commons.users.add_property(new_user_name, user_data)
        self.commons.users.apply_settings()
        return 1, "Success"

    def delete_user(self, user_name, active_user_password=None):
        """Removes the user from database"""
        # first check the permissions of active user - Creating new user requires level 3 permissions
        if self.permission_level < 3:
            return -1, log.warning("User %s has no permission to delete users" % self._active_user)

        # Don't allow non-authenticated users to go further
        if active_user_password:
            self.authenticate(active_user_password)
        if not self.is_authenticated:
            return -1, log.warning("Active user is not authenticated or the password is wrong")

        if user_name == "Admin":
            return -1, log.warning("Admin User cannot be deleted")
        if user_name == "Generic":
            return -1, log.warning("Generic User cannot be deleted")

        if user_name not in self.commons.users.all_properties:
            return -1, log.error("User %s does not exist. Aborting" % user_name)
        self.commons.users.delete_property(user_name)
        self.commons.users.apply_settings()
        return 1, "Success"

    @staticmethod
    def __clamp_level(level):
        """Clamps the level between 0-3 and makes sure its integer"""
        return max(0, min(int(level), 3))

    def change_permission_level(self, user_name, new_level, active_user_password=None):
        # first check the permissions of active user - changing permission levels requires level 3 permissions
        if self.permission_level < 3:
            return -1, log.warning("User %s has no permission to change permission level of other users" % self._active_user)
            # Don't allow non-authenticated users to go further
        if active_user_password:
            self.authenticate(active_user_password)
        if not self.is_authenticated:
            return -1, log.warning("Active user is not authenticated or the password is wrong")

        if user_name == "Admin":
            return -1, log.warning("Admin permission levels cannot be altered")
        if user_name == "Generic":
            return -1, log.warning("Generic User permission levels cannot be altered")

        if user_name not in self.commons.users.all_properties:
            return -1, log.error("User %s does not exist. Aborting" % user_name)

        user_data = self.commons.users.get_property(user_name)
        user_data["permissionLevel"] = self.__clamp_level(new_level)
        self.commons.users.edit_property(user_name, user_data)
        self.commons.users.apply_settings()
        return 1, "Success"

    def change_user_password(self, old_password, new_password, user_name=None):
        """Changes the user password. It only changes the active user, aka needs to be logged in"""
        user_name = user_name or self._active_user
        if self.__hash_pass(old_password) == self.commons.users.get_property(user_name).get("pass"):
            self.commons.users.get_property(user_name)["pass"] = self.__hash_pass(new_password)
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

    def add_project_bookmark(self, project_name, path):
        """Adds the given project to the user bookmark database"""

        bookmark_list = self.bookmarks.get_property("bookmarkedProjects")

        all_bookmark_names = [x.get("name") for x in bookmark_list]
        if project_name in all_bookmark_names:
            return -1, log.warning("%s already exists in user bookmarks" % project_name)

        bookmark_list.append({"name": project_name, "path": path})
        self.bookmarks.apply_settings()
        return 1, "%s added to bookmarks" % project_name

    def delete_project_bookmark(self, project_name):
        """Removes the project from user bookmarks"""

        bookmark_list = self.bookmarks.get_property("bookmarkedProjects")

        for nmb, bookmark in enumerate(bookmark_list):
            if bookmark.get("name") == project_name:
                bookmark_list.pop(nmb)
                # self.bookmarks.edit_property("bookmarkedProjects", bookmark_list)
                self.bookmarks.apply_settings()
                return 1, "Success"
        return -1, log.warning("%s doesn't exist in bookmarks. Aborting" % project_name)

    @staticmethod
    def __hash_pass(password):
        """Hashes the password"""
        return hashlib.sha1(str(password).encode('utf-8')).hexdigest()

    def get_project_bookmarks(self):
        """Returns the user bookmarked projects as list of dictionaries"""
        return self.bookmarks.get_property("bookmarkedProjects")

    def add_recent_project(self, path):
        recents_list = self.bookmarks.get_property("recentProjects")
        recents_list.append(path)
        if len(recents_list) > 10:
            recents_list.pop(0)
        self.bookmarks.apply_settings()

    def get_recent_projects(self):
        return self.bookmarks.get_property("recentProjects")

    # TODO Project Repositories