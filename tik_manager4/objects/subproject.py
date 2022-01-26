import os
import shutil

from fnmatch import fnmatch
from tik_manager4.core import filelog
from tik_manager4.objects.entity import Entity
from tik_manager4.objects.category import Category

# from tik_manager4.objects.guard import Guard


log = filelog.Filelog(logname=__name__, filename="tik_manager4")


class Subproject(Entity):
    # _guard = Guard()
    def __init__(self, resolution=None, fps=None, *args, **kwargs):

        self.__fps = fps
        self.__resolution = resolution
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
        return self.__resolution

    # @resolution.setter
    # def resolution(self, val):
    #     state, msg = self._check_permissions(level=2)
    #     if state != 1:
    #         return -1, msg
    #     if type(val) == tuple or list:
    #         self.__resolution = val
    #     else:
    #         raise Exception("%s is not a valid resolution. must be list or tuple." % val)

    @property
    def fps(self):
        return self.__fps

    # @fps.setter
    # def fps(self, val):
    #     self._fps = val

    def set_resolution(self, val):
        state, msg = self._check_permissions(level=2)
        if state != 1:
            return -1, log.warning(msg)
        if type(val) == tuple or list:
            self.__resolution = val
            return 1, "Success"
        else:
            raise Exception("%s is not a valid resolution. must be list or tuple." % val)

    def set_fps(self, val):
        state, msg = self._check_permissions(level=2)
        if state != 1:
            return -1, log.warning(msg)
        if type(val) == int or float:
            self.__fps = val
            return 1, "Success"
        else:
            raise Exception("%s is not a valid fps value. must be int or float." % val)

    def get_sub_tree(self):
        visited = []
        queue = []

        # start with the initial dictionary with self subproject
        all_data = {
            "id": self.id,
            "name": self.name,
            "path": self.path,
            "resolution": self.resolution,
            "fps": self.fps,
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
                        # "resolution": neighbour.resolution,
                        # "fps": neighbour.fps,
                        # "categories": list(neighbour.categories.keys()),
                        "categories": [category.name for category in neighbour.categories],
                        "subs": [],  # this will be filled with the while loop
                    }
                    if neighbour.resolution != self.resolution:
                        sub_data["resolution"] = neighbour.resolution
                    if neighbour.fps != self.fps:
                        sub_data["fps"] = neighbour.fps
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
        self._relative_path = data.get("path", None)
        self.__resolution = data.get("resolution", None)
        self.__fps = data.get("fps", None)
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
                    _relative_path = neighbour.get("path", None)
                    # _resolution = neighbour.get("resolution", None)
                    # resolution and fps is getting inherited from parent entity if not overridden
                    _resolution = neighbour.get("resolution", self.resolution)
                    # _fps = neighbour.get("fps", None)
                    _fps = neighbour.get("fps", self.fps)
                    _categories = neighbour.get("categories", [])
                    # sub_project = sub.add_sub_project(_name, resolution=_resolution,
                    #                                   fps=_fps, uid=_id)
                    sub_project = sub.__build_sub_project(_name, _resolution, _fps, _id)
                    # define the path and categories separately
                    # TODO Categories and path can be overrides for Subproject class
                    sub_project._relative_path = _relative_path
                    _ = [sub_project.add_category(x) for x in _categories]

                    visited.append(neighbour)
                    queue.append([sub_project, neighbour.get("subs", [])])

    def __build_sub_project(self, name, resolution, fps, uid):
        """Builds the sub-project inside class."""

        sub_pr = Subproject(name=name, resolution=resolution, fps=fps, uid=uid)
        sub_pr.path = os.path.join(self.path, name)
        self._sub_projects[name] = sub_pr
        return sub_pr

    def _check_permissions(self, level=2):
        """Checks the user permissions for project related tasks. Default required level is 2"""

        if self.permission_level < level:
            return -1, log.warning("This user does not have permissions for this action")

        if not self.is_authenticated:
            return -1, log.warning("User is not authenticated")
        return 1, "Success"

    def add_sub_project(self, name, resolution=None, fps=None, uid=None):
        """
        Adds a sub project. Creates the folder structure and requires permissions

        """

        state, msg = self._check_permissions(level=2)
        if state != 1:
            return -1, msg
        # adding sub-projects requires level 2 permissions
        # if self.permission_level < 2:
        #     return -1, log.warning("This user does not have permissions for this action")
        #
        # if not self.is_authenticated:
        #     return -1, log.warning("User is not authenticated")

        if name in self._sub_projects.keys():
            return -1, log.warning("{0} already exist in sub-projects of {1}".format(name, self._name))
            # return 0

        # inherit the resolution and fps if not overriden
        resolution = resolution or self.resolution
        fps = fps or self.fps

        return self.__build_sub_project(name, resolution, fps, uid)

        # # TODO Currently the overriden uid is not getting checked if it is really unique or not
        # sub_pr = Subproject(name=name, resolution=resolution, fps=fps, uid=uid)
        # # sub_pr._relative_path = os.path.join(self._relative_path, name)
        # sub_pr.path = os.path.join(self.path, name)
        # self._sub_projects[name] = sub_pr
        # return sub_pr

    def find_sub_by_id(self, uid):
        queue = list(self.subs.values())
        while queue:
            current = queue.pop(0)
            if current.id == uid:
                return current
            else:
                queue.extend(list(current.subs.values()))
        log.warning("Requested uid does not exist")


    def find_sub_by_path(self, path):
        if path == "":  # this is root
            return self
        queue = list(self.subs.values())
        while queue:
            current = queue.pop(0)
            if current.path == path:
                return current
            else:
                queue.extend(list(current.subs.values()))
        log.warning("Requested path does not exist")

    def find_subs_by_wildcard(self, wildcard):
        subs = []
        queue = list(self.subs.values())
        visited = []
        while queue:
            current = queue.pop(0)
            # print(current.name)
            if fnmatch(current.path, wildcard):
                # yield current
                subs.append(current)
            if current not in visited:
                queue.extend(list(current.subs.values()))
            else:
                visited.append(current)
        return subs

    def get_uid_by_path(self, path):
        sub = self.find_sub_by_path(path)
        if sub:
            return sub.id
        else:
            return -1

    def get_uid_by_id(self, uid):
        sub = self.find_sub_by_id(uid)
        if sub:
            return sub.id
        else:
            return -1

    def _remove_sub_project(self, uid=None, path=None):
        "Removes the sub project from the object but not from the database"

        if not uid and not path:
            return -1, log.error("Deleting sub project requires at least an id or path ")

        # print("***")
        # print(user_object.get_active_user())
        # print(user_object.permission_level)
        # print(user_object.permission_level)
        # if user_object.permission_level < 3:
        #     print("anan")
        #     return -1, log.warning("User %s does not have delete permissions" % user_object.get_active_user())
        # print("bacin")
        # if not user_object.is_authenticated:
        #     return -1, log.warning("User is not authenticated")
        # first find the subproject to be deleted
        if uid:
            kill_sub = self.find_sub_by_id(uid)
        else:
            kill_sub = self.find_sub_by_path(path)

        if not kill_sub:
            return -1, log.warning("Subproject cannot be found")

        path = kill_sub.path
        parent_path = os.path.dirname(kill_sub.path) or ""
        parent_sub = self.find_sub_by_path(parent_path)
        del parent_sub.subs[kill_sub.name]

        # # blast database folders
        # shutil.rmtree()

        log.warning("delete_sub_project is wip")

    def add_category(self, name):
        """Creates a new category (step) underneath"""

        category = Category(name=name)
        self._categories.append(category)
        return category

    def _delete_folders(self, root, sub=None):
        sub = sub or self
        folder = os.path.join(root, sub.path)
        shutil.rmtree(folder)

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

    # def testing(self):
    #     print(self._guard.permission_level)
    #     print(self._guard.is_authenticated)
    #     return(self._guard.permission_level, self._guard.is_authenticated)
