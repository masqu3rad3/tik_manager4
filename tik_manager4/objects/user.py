import os
from tik_manager4.core.settings import Settings
from tik_manager4.objects.commons import Commons
from tik_manager4.ui import feedback

FEED = feedback.Feedback()


class User(object):
    def __init__(self, commons_directory=None):
        super(User, self).__init__()
        self.settings = Settings()
        self.states = Settings()
        self.user_directory = None
        self.common_directory = commons_directory  # this is only for programmatically set the commons
        self.commons = None

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

        self.settings.apply_settings()
        return 1


