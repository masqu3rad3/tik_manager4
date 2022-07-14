import os
from glob import glob
from tik_manager4.objects.entity import Entity
from tik_manager4.objects.basescene import BaseScene
from tik_manager4.core import filelog

log = filelog.Filelog(logname=__name__, filename="tik_manager4")

class Category(Entity):
    def __init__(self, name="", *args, **kwargs):
        super(Category, self).__init__(*args, **kwargs)

        self._name = name
        self._basescenes = []
        self.type = "category"

    @property
    def basescenes(self):
        return self._basescenes

    def scan_basescenes(self):
        self._basescenes.clear()
        _search_dir = os.path.join(self._guard.database_root, self.path)
        _base_scene_paths = glob(os.path.join(_search_dir, '*.tbs'))
        for b_path in _base_scene_paths:
            self._basescenes.append(BaseScene(b_path))

        # return glob(os.path.join(_search_dir, '*.tbs'))

    def add_base_scene(self, name, dcc):
        """Creates a base scene under the category"""
        relative_path = os.path.join(self.path, "%s.tbs" % name)
        abs_path = os.path.join(self._guard.database_root, relative_path)
        if os.path.exists(abs_path):
            log.warning("There is a basescene under this category with the same name => %s" % name)
            return
        _basescene = BaseScene(abs_path, name=name, category=self.name)
        _basescene.add_property("name", name)
        _basescene.add_property("creator", self._guard.user)
        _basescene.add_property("category", self.name)
        _basescene.add_property("dcc", dcc)
        _basescene.add_property("versions", [])
        _basescene.add_property("publishes", [])
        _basescene.add_property("referenceID", None)
        _basescene.apply_settings()
        return _basescene





