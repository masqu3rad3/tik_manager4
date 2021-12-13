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

    def get_sub_tree(self):
        data = {
            "id": self.id,
            "name": self.name,
            "path": self.path,
            "categories": self.categories,
            "subs": [],
        }
        # subs = self._sub_projects
        for _, sub in self._sub_projects.items():
            subdata={}
            subdata["id"] = sub.id
            subdata["name"] = sub.name
            subdata["path"] = sub.path
            subdata["categories"] = sub.categories
            subdata["subs"] = [sub.get_sub_tree() for x in sub.subs]
            data["subs"].append(subdata)
        return data
    # def get_project_tree(self):
    #     data = {}
    #     subs = self._sub_projects
    #     while subs != []:
    #         for x in subs:
    #             data[x]
    #             yield x.name
    #             subs = x._sub_projects
    #     return data
    #     pass

    # def get_sub_project_data(self, recursive=False):
    #     if recursive:
    #         pass
    #     else:
    #
    #     data = {}
    #     for sub in self._sub_projects:


    def get_sub_project_names(self, recursive=False):
        # if recursive:
        #     data = []
        #     subs = self._sub_projects
        #     while subs != []:
        #         sub_data = []
        #         for x in subs:
        #             sub_data.append(x)

        if recursive:
            subs = self._sub_projects
            while subs != []:
                for x in subs:
                    yield x.name
                    subs = x._sub_projects
        return [sub.name for sub in self._sub_projects]

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

    def scan_base_scenes(self):
        """Finds the base scenes defined in the database"""
        # if not self._path:
        #     msg = "Project path is not available"
        #     log.warning(msg)
        #     return 0
        # TODO WIP
        pass

