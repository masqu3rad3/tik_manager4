from tik_manager4.objects.basescene import BaseScene

class Project(object):
    def __init__(self):
        self._path = None
        self._name = None
        self._resolution = None
        self._fps = None

        self._base_scenes = []

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._name

    @property
    def resolution(self):
        return self._resolution

    @property
    def fps(self):
        return self._fps


