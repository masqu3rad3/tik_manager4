
class Category(object):
    def __init__(self):
        super(Category, self).__init__()
        self._name = ""
        pass

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        self._name = val

