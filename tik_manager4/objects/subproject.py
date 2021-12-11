import os

class Subproject(object):
    def __init__(self, name=""):
        super(Subproject, self).__init__()

        self._relative_path = ""
        self._name = name
        self._sub_projects = []
        self._base_scenes = []

    def __str__(self):
        return self._name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        self._name = val

    @property
    def relative_path(self):
        return self._relative_path

    @relative_path.setter
    def relative_path(self, val):
        self._relative_path = val

    @property
    def sub_projects(self):
        return self._sub_projects

    def add_sub_project(self, name):
        sub_pr = Subproject(name=name)
        sub_pr._relative_path = os.path.join(self._relative_path, name)
        self._sub_projects.append(sub_pr)
        pass

    def scan_base_scenes(self):
        """Finds the base scenes defined in the database"""
        # if not self._path:
        #     msg = "Project path is not available"
        #     log.warning(msg)
        #     return 0
        # TODO WIP
        pass

