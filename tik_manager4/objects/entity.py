import uuid

class Entity(object):
    def __init__(self, name="", uid=None):
        self._id = uid
        self._path = ""
        self._name = name

    @property
    def id(self):
        if not self._id:
            self._id = uuid.uuid1().time_low
        return self._id

    @id.setter
    def id(self, val):
        self._id = val

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, val):
        self._path = val

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        self._name = val


