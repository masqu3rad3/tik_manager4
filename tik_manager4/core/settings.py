"""Gets the settings from a json file. Edits, adds and applies it if there are changes"""
from copy import deepcopy
from tik_manager4.core import io


class Settings(object):
    """
    Generic Settings class to hold read and compare dictionary data
    """
    def __init__(self, file_path=None):
        super(Settings, self).__init__()
        self._io = io.IO()
        self._filePath = None
        self._properties = []
        self._originalValue = {}
        self._currentValue = {}
        if file_path:
            self.settings_file = file_path

    @property
    def settings_file(self):
        return self._filePath

    @settings_file.setter
    def settings_file(self, file_path):
        self._filePath = file_path
        self._io.file_path = file_path
        if self._io.file_exists(file_path):
            self.initialize(self._io.read())

    @property
    def all_properties(self):
        return self._currentValue.keys()

    def initialize(self, data):
        """Initializes the settings data"""
        data = data or {}
        self._originalValue.clear()
        self._currentValue.clear()
        self._originalValue.update(data)
        self._currentValue.update(data)

    def is_settings_changed(self):
        """Checks if the settings changed since initialization"""
        return not (self._currentValue == self._originalValue)

    def apply_settings(self):
        """Applies the changed settings and writes it to file"""
        if self.is_settings_changed():
            self._originalValue = deepcopy(self._currentValue)
            self._io.write(self._originalValue)

    def reset_settings(self):
        """Reverts back the unsaved changes to the original state"""
        self._currentValue = deepcopy(self._originalValue)

    def edit_property(self, key, val):
        """Updates the property key with given value"""
        self._currentValue.update({key: val})

    def add_property(self, key, val):
        """Creates a property key with given value"""
        self._currentValue.update({key: val})

    def delete_property(self, key):
        """Deletes the given property key"""
        self._currentValue.pop(key)

    def get_property(self, key):
        """Returns the value of the property key"""
        return self._currentValue.get(key, None)

    def set_data(self, data):
        """Feeds the raw data directly"""
        self._currentValue = data

    def get_data(self):
        """Returns the whole current data"""
        return self._currentValue