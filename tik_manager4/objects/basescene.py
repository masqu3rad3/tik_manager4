from tik_manager4.objects.version import Version


class BaseScene(object):
    def __init__(self, project_path=None, version_folder=None, publish_folder=None):
        super(BaseScene, self).__init__()

        self._projectPath = project_path
        self._versionFolder = version_folder
        self._publishFolder = publish_folder

        self._name = None

        self._type = None
        self._step = None

        self._versions = []
        self._publishes = []

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, val):
        self._type = val

    @property
    def step(self):
        return self._step

    @step.setter
    def step(self, val):
        self._step = val

    def add_version(self, path, user, workstation, note, thumbnail, preview, ranges):
        self._versions.append(Version(path, user, workstation, note, thumbnail, preview, ranges))

    def get_all_versions(self):
        return self._versions

    def get_version(self, id):
        return self._versions[id-1]