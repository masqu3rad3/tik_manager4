

class BaseScene(object):
    def __init__(self):
        super(BaseScene, self).__init__()

        self._version_list = []
        self._published_version = None

    @property
    def version_count(self):
        return len(self._version_list)

    def add_version(self):
        pass

    def save_version(self):
        pass

    def load_version(self, version):
        pass

    def publish(self, version):
        pass



class Version(object):
    def __init__(self, path=None, user=None):
        super(Version, self).__init__()

        self._relative_path = path
        self._user = user
