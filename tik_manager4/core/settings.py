"""Module to handle settings data."""
from copy import deepcopy
from tik_manager4.core import io


class Settings:
    """Generic Settings class to hold read and compare dictionary data."""

    def __init__(self, file_path=None):
        """Initializes the Settings class."""
        super().__init__()
        self._io = io.IO()
        self._filepath = None
        self._properties = []
        self._original_value = {}
        self._current_value = {}
        self._time_stamp = None
        self._fallback = None
        if file_path:
            self.settings_file = file_path

    @property
    def date_modified(self):
        """Return the date modified of the settings file."""
        return self._time_stamp

    @property
    def settings_file(self):
        """Return the settings file path."""
        return self._filepath

    @settings_file.setter
    def settings_file(self, file_path):
        """Set the settings file path."""
        self._filepath = file_path
        self._io.file_path = file_path
        if self._io.file_exists(file_path):
            self._time_stamp = self._io.get_modified_time()
            self.initialize(self._io.read())

    def reload(self):
        """Reload the settings from file."""
        self.settings_file = self._filepath
        return self._current_value

    @property
    def keys(self):
        """Return all keys in the current data."""
        return list(self._current_value.keys())

    @property
    def values(self):
        """Return all values in the current data."""
        return list(self._current_value.values())

    @property
    def properties(self):
        """Return the current dictionary data."""
        return self._current_value

    def is_modified(self):
        """Check if the file has been modified since initialization."""
        return not bool(self._io.get_modified_time() == self._time_stamp)

    def initialize(self, data):
        """Initialize the settings data.

        Args:
            data (dict): The data to initialize the settings with.
        """
        data = data or {}
        self._original_value = {}
        self._current_value = {}
        self._current_value.update(data)
        self._original_value = deepcopy(self._current_value)

    def update(self, data, add_missing_keys=False):
        """Update the settings data.

        Args:
            data (dict): The data to update the settings with.
            add_missing_keys (bool): Whether to add missing keys or not.
        """
        if isinstance(data, Settings):
            data = data.get_data()
        if not add_missing_keys:
            self._current_value.update(
                (key, data[key]) for key in self._current_value.keys()
                & data.keys())
        else:
            self._current_value.update(data)

    def is_settings_changed(self):
        """Check if the settings changed since initialization."""
        return not self._current_value == self._original_value

    def apply_settings(self, force=False):
        """Apply the changed settings and writes it to file.

        Args:
            force (bool): Whether to force write the settings or not.

        Returns:
            bool: True if the settings were written to file, False otherwise.
        """
        if not self.is_settings_changed() and not force:
            return False
        self._original_value = deepcopy(self._current_value)
        self._io.write(self._original_value)
        self._time_stamp = self._io.get_modified_time()
        return True

    def reset_settings(self):
        """Revert back the unsaved changes to the original state."""
        self._current_value = deepcopy(self._original_value)

    def edit_property(self, key, val):
        """Update the property key with given value.

        Args:
            key (str): The property key to update.
            val (any): The value to update the key with.
        """
        self._current_value.update({key: val})

    def edit_sub_property(self, sub_keys, new_val):
        """Edit nested properties.

        Args:
            sub_keys (list): The list of keys to traverse the nested properties.
            new_val (any): The new value to assign to the final key.
        """
        val = self._current_value
        for key in sub_keys[:-1]:
            val = val[key]

        # Assign a new value to the final key
        val[sub_keys[-1]] = new_val

    def add_property(self, key, val, force=True):
        """Create a property key with given value.

        Args:
            key (str): The property key to create.
            val (any): The value to assign to the key.
            force (bool): Whether to force create the key or not.

        Returns:
            bool: True if the key was created, False otherwise.
        """
        if key in self._current_value and not force:
            return False
        self._current_value.update({key: val})
        return True

    def delete_property(self, key):
        """Delete the given property key."""
        self._current_value.pop(key)

    def get_property(self, key, default=None):
        """Return the value of the property key.

        Args:
            key (str): The key to get the value of.
            default (any): The default value to return if the key is not found.

        Returns:
            any: The value of the key.
        """
        return self._current_value.get(key, default)

    def get(self, key, default=None):
        """Duplicate of get_property for situations where it may be present with dict items.

        Args:
            key (str): The key to get the value of.
            default (any): The default value to return if the key is not found.
        """
        return self._current_value.get(key, default)

    def get_sub_property(self, sub_keys):
        """Return the value of the sub property key.

        Args:
            sub_keys (list): The list of keys to traverse the nested properties.

        Returns:
            any: The value of the final key.
        """
        val = self._current_value
        for key in sub_keys:
            val = val[key]
        return val

    def set_data(self, data):
        """Feed the raw data directly.

        Args:
            data (dict): The data to set.
        """
        self._current_value = data

    def get_data(self):
        """Return the whole current data."""
        return self._current_value

    def set_fallback(self, file_path):
        """Use the given file in case the file_path is not found.

        Args:
            file_path (str): The file path to use as fallback.
        """
        self._fallback = file_path
        if not self._io.file_exists(self._filepath):
            self.use_fallback()

    def use_fallback(self):
        """Use the fallback file."""
        if self._fallback:
            self.initialize(self._io.read(self._fallback))
            self.apply_settings(force=True)
    def __str__(self):
        """Return the type of the class and the current data."""
        return f"{type(self).__name__}({self._current_value})"
    def __repr__(self):
        """Return the type of the class and the current data."""
        return str(self._current_value)
