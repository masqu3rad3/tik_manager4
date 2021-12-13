import uuid

class Entity(object):
    def __init__(self):
        self._id = None
        self._relative_path = ""
        self._name = ""

    def __str__(self):
        return self._name

    @property
    def id(self):
        return self._id or uuid.uuid1().time_low

    @property
    def path(self):
        return self._relative_path

    @path.setter
    def path(self, val):
        self._relative_path = val

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        self._name = val


