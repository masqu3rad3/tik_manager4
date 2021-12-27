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

    def set_sub_tree(self, data, sub=None):
        """
        Creates the subproject from the data dictionary.
        This is for building back the hierarchy from json data

        """
        sub = sub or self
        sub.id = data.get("id", None)
        sub._name = data.get("name", None)
        sub._path = data.get("path", None)
        sub._resolution = data.get("resolution", None)
        sub._fps = data.get("fps", None)
        _ = [sub.add_category(x) for x in data.get("categories", [])]
        for sub_pr_data in data.get("subs", []):
            sub = sub.add_sub_project(sub_pr_data.get("name", None))
            self.set_sub_tree(sub_pr_data, sub=sub)

    def add_sub_project(self, name, resolution=None, fps=None):
        """
        Creates a subproject object
        Args:
            name: (String) Name of the subproject
            resolution: (Tuple or List) If not provided, derives it from the parent subproject
            fps:  (Tuple or List) If not provided, derives it from the parent subproject

        Returns:
            <Subproject class>

        """

        if name in self._sub_projects.keys():
            log.warning("{0} already exist in sub-projects of {1}".format(name, self._name))
            return 0
        sub_pr = Subproject(name=name)
        sub_pr.resolution = resolution or self.resolution
        sub_pr.fps = fps or self.fps
        sub_pr._relative_path = os.path.join(self._relative_path, name)
        self._sub_projects[name] = sub_pr
        return sub_pr

    def add_category(self, name):
        """Creates a new category (step) underneath"""

        category = Category(name=name)
        self._categories[name] = category
        return category
