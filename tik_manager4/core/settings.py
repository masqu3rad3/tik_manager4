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
        self.initialize(self._io.read())

    @property
    def all_properties(self):
        return self._currentValue.keys()

    def initialize(self, data):
        data = data or {}
        self._originalValue.clear()
        self._currentValue.clear()
        self._originalValue.update(data)
        self._currentValue.update(data)

    def is_settings_changed(self):
        """Check if the settings changed since initialization"""
        return not (self._currentValue == self._originalValue)

    def apply_settings(self):
        self._originalValue = deepcopy(self._currentValue)
        self._io.write(self._originalValue)

    def reset_settings(self):
        self._currentValue = deepcopy(self._originalValue)

    def edit_property(self, key, val):
        self._currentValue.update({key: val})

    def add_property(self, key, val):
        self._currentValue.update({key: val})

    def delete_property(self, key):
        self._currentValue.pop(key)

    def get_property(self, key):
        return self._currentValue.get(key, None)
