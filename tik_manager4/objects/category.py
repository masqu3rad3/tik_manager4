import os
from glob import glob
from tik_manager4.objects.entity import Entity
from tik_manager4.objects.basescene import BaseScene
from tik_manager4.core import filelog

log = filelog.Filelog(logname=__name__, filename="tik_manager4")

class Category(Entity):
    def __init__(self, name=""):
        super(Category, self).__init__()

        self._name = name
        self._base_scenes = {}
        self.type = "category"

    @property
    def base_scenes(self):
        return self._base_scenes

    def scan_base_scenes(self):
        self._base_scenes.clear()
        _search_dir = os.path.join(self._guard.database_root, self.path)
        _base_scene_paths = glob(os.path.join(_search_dir, '*.tbs'))
        for b_path in _base_scene_paths:
            _basescene = BaseScene(b_path)
            self._base_scenes[_basescene.name] = _basescene

        # return glob(os.path.join(_search_dir, '*.tbs'))

    def add_base_scene(self, name):
        relative_path = os.path.join(self.path, "%s.tbs" % name)
        abs_path = os.path.join(self._guard.database_root, relative_path)
        if os.path.exists(abs_path):
            log.warning("There is a basescene under this category with the same name => %s" % name)
            return
        _basescene = BaseScene(abs_path, name=name, category=self.name)
        _basescene.add_property("name", name)
        _basescene.add_property("creator", self._guard.user)
        _basescene.add_property("category", self.name)
        _basescene.add_property("path", self.path)
        _basescene.add_property("versions", [])
        _basescene.add_property("publishes", [])
        _basescene.add_property("referenceID", None)
        _basescene.apply_settings()





