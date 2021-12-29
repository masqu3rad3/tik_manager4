import os
from tik_manager4.core import filelog
from tik_manager4.objects.entity import Entity
from tik_manager4.objects.category import Category

log = filelog.Filelog(logname=__name__, filename="tik_manager4")


class Subproject(Entity):
    def __init__(self, resolution=None, fps=None, *args, **kwargs):

        self._fps = fps
        self._resolution = resolution
        super(Subproject, self).__init__(*args, **kwargs)

        self._sub_projects = {}
        self._categories = []

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

    def get_sub_tree(self):
        visited = []
        queue = []

        # start with the initial dictionary with self subproject
        all_data = {
            "id": self.id,
            "name": self.name,
            "path": self.path,
            "resolution": self._resolution,
            "fps": self._fps,
            "categories": [category.name for category in self.categories],
            "subs": [],  # this will be filled with the while loop
        }

        # add the initial dictionary and self into the queue
        # Each queue item is a list.
        # first element is the dictionary point and second is the subproject object
        queue.append([all_data, self])

        while queue:
            current = queue.pop(0)
            parent = current[0]
            sub = current[1]

            for neighbour in list(sub.subs.values()):
                if neighbour not in visited:
                    # print(neighbour.path)
                    sub_data = {
                        "id": neighbour.id,
                        "name": neighbour.name,
                        "path": neighbour.path,
                        "resolution": neighbour.resolution,
                        "fps": neighbour.fps,
                        # "categories": list(neighbour.categories.keys()),
                        "categories": [category.name for category in neighbour.categories],
                        "subs": [],  # this will be filled with the while loop
                    }
                    parent["subs"].append(sub_data)

                    # visited.append([sub_data, neighbour])
                    visited.append(neighbour)
                    queue.append([sub_data, neighbour])

        return all_data

    def set_sub_tree(self, data):
        """
        Creates the subproject from the data dictionary.
        This is for building back the hierarchy from json data

        """
        visited = []
        queue = []
        self.id = data.get("id", None)
        self._name = data.get("name", None)
        self._path = data.get("path", None)
        self._resolution = data.get("resolution", None)
        self._fps = data.get("fps", None)
        _ = [self.add_category(x) for x in data.get("categories", [])]

        # append the subproject object and pointer for json as a queue element
        queue.append([self, data.get("subs", [])])

        while queue:
            current = queue.pop(0)
            sub = current[0]
            data_position = current[1]

            for neighbour in data_position:
                if neighbour not in visited:
                    # print(neighbour.path)
                    _id = neighbour.get("id", None)
                    _name = neighbour.get("name", None)
                    _path = neighbour.get("path", None)
                    _resolution = neighbour.get("resolution", None)
                    _fps = neighbour.get("fps", None)
                    _categories = neighbour.get("categories", [])
                    sub_project = sub.add_sub_project(_name, resolution=_resolution,
                                                      fps=_fps, uid=_id)
                    # define the path and categories separately
                    # TODO Categories and path can be overrides for Subproject class
                    sub_project._path = _path
                    _ = [sub_project.add_category(x) for x in _categories]

                    visited.append(neighbour)
                    queue.append([sub_project, neighbour.get("subs", [])])

    def add_sub_project(self, name, resolution=None, fps=None, uid=None):
        """
        Creates a subproject object
        Args:
            name: (String) Name of the subproject
            resolution: (Tuple or List) If not provided, derives it from the parent subproject
            fps:  (Tuple or List) If not provided, derives it from the parent subproject
            uid: (integer) entity unique integer id
        Returns:
            <Subproject class>

        """

        if name in self._sub_projects.keys():
            log.warning("{0} already exist in sub-projects of {1}".format(name, self._name))
            return 0

        # inherit the resolution and fps if not overriden
        resolution = resolution or self.resolution
        fps = fps or self.fps

        # TODO Currently the overriden uid is not getting checked if it is really unique or not
        sub_pr = Subproject(name=name, resolution=resolution, fps=fps, uid=uid)
        sub_pr._path = os.path.join(self._path, name)
        self._sub_projects[name] = sub_pr
        return sub_pr

    def add_category(self, name):
        """Creates a new category (step) underneath"""

        category = Category(name=name)
        self._categories.append(category)
        return category

    def create_folders(self, root, sub=None):
        """Creates folders for subprojects and categories below this starting from 'root' path"""
        sub = sub or self
        folder = os.path.join(root, sub.path)
        if not os.path.exists(folder):
            os.makedirs(folder)
        # unfortunately python 2.x does not support  exist_ok argument...
        for category in sub.categories:
            _f = os.path.join(folder, category.name)
            if not os.path.exists(_f):
                os.makedirs(_f)
        _ = [sub.create_folders(root, sub=sub) for sub in sub.subs.values()]
