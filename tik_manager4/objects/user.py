import logging
import os
from tik_manager4.core import filelog
from tik_manager4.core.settings import Settings
from tik_manager4.objects.commons import Commons
from tik_manager4.ui import feedback

log = filelog.Filelog(logname=__name__, filename="tik_manager4")

FEED = feedback.Feedback()


class User(object):
    def __init__(self, commons_directory=None):
        super(User, self).__init__()
        self.settings = Settings()
        self.bookmarks = Settings()
        self.states = Settings()  # is this necessary anymore??
        self.user_directory = None
        self.common_directory = commons_directory  # this is only for programmatically set the commons
        self.commons = None

        self._active_user = None
        self._password_authenticated = False
        self._validate_user_data()

    @property
    def directory(self):
        return self.user_directory

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
        if active_user not in self.commons.get_users():
            active_user = "Generic"
        self.set_active_user(active_user, save_to_db=False)

        self.settings.apply_settings()
        self.bookmarks.apply_settings()
        return 1

    def get_active_user(self):
        """Returns the currently active user"""
        return self._active_user

    def set_active_user(self, user_name, password=None, save_to_db=True):
        """Sets the active user to the session"""
        if user_name in self.commons.get_users():
            if password and self.commons.check_password(user_name, password):
                self._password_authenticated = True
            else:
                return -1, log.warning("Wrong password provided for user %s" % user_name)
            self._active_user = user_name
            if save_to_db:
                self.bookmarks.edit_property("activeUser", self._active_user)
            return user_name, "Success"
        else:
            return -1, log.warning("User %s cannot set because it does not exist in commons database")

    def add_project_bookmark(self, project_name, path):
        """Adds the given project to the user bookmark database"""

        bookmark_list = self.bookmarks.get_property("bookmarkedProjects")

        all_bookmark_names = [x.get("name") for x in bookmark_list]
        if project_name in all_bookmark_names:
            return -1, log.warning("Project %s already exists in user bookmarks" % project_name)

        bookmark_list.append({"name": project_name, "path": path})
        self.bookmarks.edit_property(project_name, bookmark_list)
        self.bookmarks.apply_settings()
        return 1, "Project %s added to bookmarks" % project_name

    def delete_project_bookmark(self, project_name):
        """Removes the project from user bookmarks"""

        bookmark_list = self.bookmarks.get_property("bookmarkedProjects")

        for bookmark in bookmark_list:
            if bookmark.get("name") == project_name:
                bookmark_list.pop(bookmark)
                self.bookmarks.edit_property(project_name, bookmark_list)
                return 1, "Project %s removed from bookmarks" % project_name
        return -1, log.warning("Project %s does not exist in bookmarks. Aborting" % project_name)

    # def get_project_bookmarks(self):
    #     """Returns list of dictionaries """
    #     return self.bookmarks.get_property("bookmarkedProjects")
