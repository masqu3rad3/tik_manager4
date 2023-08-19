# pylint: disable=super-with-arguments
# pylint: disable=consider-using-f-string
from tik_manager4.core.settings import Settings
from tik_manager4.objects.entity import Entity
from tik_manager4 import dcc


class Publish(Settings, Entity):
    _dcc_handler = dcc.Dcc()

    def __init__(self, absolute_path, name=None, path=None):
        super(Publish, self).__init__()
        self.settings_file = absolute_path
