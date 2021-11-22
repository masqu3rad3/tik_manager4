import os

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





class Version(object):
    def __init__(self, path=None, user=None, workstation=None, note=None, thumbnail=None, preview=None, ranges=None):
        super(Version, self).__init__()

        self._relative_path = path
        self._user = user
        self._workstation = workstation
        self._note = note
        self._thumbnail = thumbnail
        self._preview = preview or {}
        self._ranges = ranges

class Publish(object):
    def __init__(self, path=None):
        super(Publish, self).__init__()

        self._relative_path = path


# class BaseScene(object):
#     def __init__(self):
#         super(BaseScene, self).__init__()
#
#         self._version_list = []
#         self._published_version = None
#
#     @property
#     def version_count(self):
#         return len(self._version_list)
#
#     def add_version(self):
#         pass
#
#     def save_version(self):
#         pass
#
#     def load_version(self, version):
#         pass
#
#     def publish(self, version):
#         pass
#
#
#
# class Version(object):
#     def __init__(self, path=None, user=None):
#         super(Version, self).__init__()
#
#         self._relative_path = path
#         self._user = user
