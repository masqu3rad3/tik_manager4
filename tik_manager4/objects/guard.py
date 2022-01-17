
class Guard(object):
    _permission_level = 0
    _authenticated = False

    @classmethod
    def set_permission_level(cls, level):
        cls._permission_level = level

    @property
    def permission_level(self):
        return self._permission_level

    @classmethod
    def set_authentication_status(cls, state):
        cls._authenticated = state

    @property
    def is_authenticated(self):
        return self._authenticated
