"""Gets the settings from a json file.
Edits, adds and applies it if there are changes.
"""
from copy import deepcopy
from tik_manager4.core import io


class Settings():
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
        self._time_stamp = None
        self._fallback = None
        if file_path:
            self.settings_file = file_path

    @property
    def date_modified(self):
        # convert the _time_stamp to a readable date

        return self._time_stamp

    @property
    def settings_file(self):
        return self._filePath

    @settings_file.setter
    def settings_file(self, file_path):
        """Sets the settings file path"""
        self._filePath = file_path
        self._io.file_path = file_path
        if self._io.file_exists(file_path):
            self._time_stamp = self._io.get_modified_time()
            self.initialize(self._io.read())

    def reload(self):
        """Reloads the settings from file"""
        self.settings_file = self._filePath
        return self._currentValue

    @property
    def keys(self):
        """Returns all keys in the current data"""
        return list(self._currentValue.keys())

    @property
    def values(self):
        """Returns all values in the current data"""
        return list(self._currentValue.values())

    @property
    def properties(self):
        """Return the current dictionary data."""
        return self._currentValue

    def is_modified(self):
        """Checks if the file has been modified since initialization"""
        return not bool(self._io.get_modified_time() == self._time_stamp)

    def initialize(self, data):
        """Initializes the settings data"""
        data = data or {}
        self._originalValue = {}
        self._currentValue = {}
        self._currentValue.update(data)
        self._originalValue = deepcopy(self._currentValue)

    def update(self, data, add_missing_keys=False):
        """Updates the settings data"""
        if isinstance(data, Settings):
            data = data.get_data()
        if not add_missing_keys:
            self._currentValue.update((k, data[k]) for k in self._currentValue.keys() & data.keys())
        else:
            self._currentValue.update(data)

    def is_settings_changed(self):
        """Checks if the settings changed since initialization"""
        return not (self._currentValue == self._originalValue)

    def apply_settings(self, force=False):
        """Applies the changed settings and writes it to file"""
        if not self.is_settings_changed() and not force:
            return False
        self._originalValue = deepcopy(self._currentValue)
        self._io.write(self._originalValue)
        self._time_stamp = self._io.get_modified_time()
        return True

    def reset_settings(self):
        """Revert back the unsaved changes to the original state."""
        self._currentValue = deepcopy(self._originalValue)

    def edit_property(self, key, val):
        """Update the property key with given value."""
        self._currentValue.update({key: val})

    def edit_sub_property(self, sub_keys, new_val):
        """Edit nested properties."""
        val = self._currentValue
        for key in sub_keys[:-1]:
            val = val[key]

        # Assign a new value to the final key
        val[sub_keys[-1]] = new_val

    def add_property(self, key, val, force=True):
        """Create a property key with given value."""
        if key in self._currentValue and not force:
            return False
        self._currentValue.update({key: val})
        return True

    def delete_property(self, key):
        """Deletes the given property key"""
        self._currentValue.pop(key)

    def get_property(self, key, default=None):
        """Returns the value of the property key"""
        return self._currentValue.get(key, default)

    def get(self, key, default=None):
        """Duplicate of get_property for situations where it may be present with dict items."""
        return self._currentValue.get(key, default)

    def get_sub_property(self, sub_keys):
        """Return the value of the sub property key."""
        val = self._currentValue
        for key in sub_keys:
            val = val[key]
        return val

    def set_data(self, data):
        """Feed the raw data directly."""
        self._currentValue = data

    def get_data(self):
        """Return the whole current data."""
        return self._currentValue

    def set_fallback(self, file_path):
        """Use this file in case the file_path is not found."""
        self._fallback = file_path
        if not self._io.file_exists(self._filePath):
            self.use_fallback()

    def use_fallback(self):
        """Use the fallback file."""
        if self._fallback:
            self.initialize(self._io.read(self._fallback))
            self.apply_settings(force=True)
    def __str__(self):
        # return the type of the class and the current data
        return f"{type(self).__name__}({self._currentValue})"
    def __repr__(self):
        return str(self._currentValue)