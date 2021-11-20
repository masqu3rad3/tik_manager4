"""Gets the settings from a json file. Edits, adds and applies it if there are changes"""


from tik_manager4.core import io

class Settings(object):
    def __init__(self, file_path=None):
        super(Settings, self).__init__()
        self._io = io.IO()
        self._filePath = None
        self._properties = []

        if file_path:
            self.file_path = file_path

    @property
    def file_path(self):
        return self._filePath

    @file_path.setter
    def file_path(self, file_path):
        # self.clear()
        self._filePath = file_path
        self._io.file_path = file_path
        self.initialize(self._io.read())

    @property
    def all_properties(self):
        return self._properties

    def initialize(self, data):
        self._properties = []
        if not data:
            return
        for key, val in data.items():
            self._properties.append(key)
            command = "self.{0}=Property(val=val)".format(key)
            exec(command)

    def is_changed(self):
        """Check if the settings changed since initialization"""
        for pro in self._properties:
            if exec("self.{0}.is_modified".format(pro)):
                return True
        return False

    def apply(self):
        apply_dict = {}
        for pro in self._properties:
            apply_dict[pro] = eval("self.{0}.commit()".format(pro))
        self._io.write(apply_dict)

    def reset(self):
        for pro in self._properties:
            exec("self.{0}.restore()".format(pro))

    def edit(self, key, val):
        command = "self.{0}.set(val)".format(key)
        exec(command)

    def add(self, key, val):
        self._properties.append(key)
        command = "self.{0}=Property(val=val)".format(key)
        exec(command)

    def delete(self, key):
        self._properties.remove(key)

class Property(object):
    def __init__(self, val=None):
        super(Property, self).__init__()
        self._originalValue = val
        self._currentValue = val

    def set(self, val):
        self._currentValue = val

    def get(self):
        return self._currentValue

    def is_modified(self):
        return True if self._originalValue != self._currentValue else False

    def restore(self):
        self._currentValue = self._originalValue
        return self._currentValue

    def commit(self):
        self._originalValue = self._currentValue
        return self._originalValue