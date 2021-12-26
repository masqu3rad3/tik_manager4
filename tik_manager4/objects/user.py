import os
from tik_manager4.core.settings import Settings
from tik_manager4.ui import feedback

FEED = feedback.Feedback()


DEFAULT_USER_SETTINGS = {
    "globalFavorites": True,
    "colorCoding": {
        "Maya": "rgb(81, 230, 247, 255)",
        "3dsMax": "rgb(150, 247, 81, 255)",
        "Houdini": "rgb(247, 172, 81, 255)",
        "Nuke": "rgb(246, 100, 100, 255)",
        "Photoshop": "rgb(60, 60, 250, 255)",
        "": "rgb(0, 0, 0, 0)"
    },
    "executables": {
        "image_exec": "",
        "imageSeq_exec": "",
        "video_exec": "",
        "obj_exec": "",
        "fbx_exec": "",
        "alembic_exec": ""
    },
    "extraColumns": [
        "Date"
    ],
    "commonFolder": "",

}


class User(object):
    def __init__(self):
        super(User, self).__init__()
        self.settings = Settings()
        self.states = Settings()
        self.user_directory = None

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
        # set the default keys for missing ones
        for key, val in DEFAULT_USER_SETTINGS.items():
            if not self.settings.get_property(key=key):
                self.settings.add_property(key=key, val=val)

        # check the validity of common folder
        if not os.path.isdir(self.settings.get_property("commonFolder")):
            FEED.pop_info(title="Set Common Directory", text="Common Directory is not defined. "
                                                             "Press Continue to select Common Directory",
                          button_label="Continue")
            common_dir = FEED.browse_directory()
            self.settings.edit_property("commonFolder", common_dir)
        self.settings.apply_settings()
        return 1

#
# class UserSettings(Settings):
#     def __init__(self, settings_file):
#         super(UserSettings, self).__init__()
#         self.settings_file = settings_file
#         self._validate_data()
#
#     def _validate_data(self):
#         """Makes sure the user settings data is intact"""
#         # set the default keys for missing ones
#         for key, val in DEFAULT_USER_SETTINGS.items():
#             if not self.get_property(key=key):
#                 self.add_property(key=key, val=val)
#         self.apply_settings()
#         return 1
#
#     @property
#     def is_global_favorites(self):
#         return self.get_property("globalFavorites")
#
#     @is_global_favorites.setter
#     def is_global_favorites(self, val):
#         self.edit_property("globalFavorites", bool(val))