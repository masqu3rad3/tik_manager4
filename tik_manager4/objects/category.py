from tik_manager4.objects.entity import Entity

class Category(Entity):
    def __init__(self, name=""):
        super(Category, self).__init__()
        # self._id = uuid.uuid1().time_low
        # self._relative_path = ""
        self._name = name
        self._base_scenes = {}

    @property
    def base_scenes(self):
        return self._base_scenes

    def scan_base_scenes(self):
        pass






