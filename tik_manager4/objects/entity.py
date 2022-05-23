import uuid
from tik_manager4.objects.guard import Guard

class Entity(object):
    # _user = User()
    _guard = Guard()

    def __init__(self, name="", uid=None):
        self._id = uid
        self._relative_path = ""
        self._name = name
        self.type = "entity"
        # self._user = User()

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
        return self._relative_path.replace("\\","/")

    @path.setter
    def path(self, val):
        self._relative_path = val

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        self._name = val

    @property
    def permission_level(self):
        return self._guard.permission_level

    @property
    def is_authenticated(self):
        return self._guard.is_authenticated

    # def testing(self):
    #     print(self._guard.permission_level)
    #     print(self._guard.is_authenticated)
    #     return(self._guard.permission_level, self._guard.is_authenticated)


