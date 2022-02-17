from tik_manager4.objects.entity import Entity
from tik_manager4.objects.basescene import BaseScene

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
        pass

    def add_base_scene(self):
        pass






