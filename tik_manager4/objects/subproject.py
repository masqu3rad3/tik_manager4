import os
from tik_manager4.core import filelog
from tik_manager4.objects.entity import Entity
from tik_manager4.objects.category import Category

log = filelog.Filelog(logname=__name__, filename="tik_manager4")

class Subproject(Entity):
    def __init__(self, name=""):
        super(Subproject, self).__init__()

        self._name = name
        self._sub_projects = {}
        self._categories = {}
        self._resolution = None
        self._fps = None

    @property
    def subs(self):
        return self._sub_projects

    @property
    def categories(self):
        return self._categories

    @property
    def resolution(self):
        return self._resolution

    @resolution.setter
    def resolution(self, val):
        if type(val) == tuple or list:
            self._resolution = val
        else:
            raise Exception("%s is not a valid resolution. must be list or tuple." % val)

    @property
    def fps(self):
        return self._fps

    @fps.setter
    def fps(self, val):
        self._fps = val

    def get_sub_tree(self, sub=None):
        """
        Gets the subproject data recursively

        Args:
            sub: (Subproject Object) Starts from this subproject if defined.

        Returns:
            (dictionary) sub-project data recursively

        """

        sub = sub or self
        data = {
            "id": self.id,
            "name": self.name,
            "path": self.path,
            "resolution": self._resolution,
            "fps": self._fps,
            "categories": list(sub.categories.keys()),
            "subs": [sub.get_sub_tree(sub=sub) for sub in sub.subs.values()],
        }
        return data

    def add_sub_project(self, name):
        if name in self._sub_projects.keys():
            log.warning("{0} already exist in sub-projects of {1}".format(name, self._name))
            return 0
        sub_pr = Subproject(name=name)
        sub_pr.resolution = self.resolution
        sub_pr.fps = self.fps
        sub_pr._relative_path = os.path.join(self._relative_path, name)
        self._sub_projects[name] = sub_pr
        return sub_pr

    def add_category(self, name):
        category = Category(name=name)
        self._categories[name] = category
        return category
