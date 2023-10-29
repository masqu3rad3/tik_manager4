# pylint: disable=super-with-arguments
# pylint: disable=consider-using-f-string
import pathlib
from tik_manager4.core.settings import Settings
from tik_manager4.objects.entity import Entity
from tik_manager4 import dcc


class Publish(Settings, Entity):
    _dcc_handler = dcc.Dcc()

    def __init__(self, absolute_path, name=None, path=None):
        super(Publish, self).__init__()
        self.settings_file = absolute_path

        self._name = self.get_property("name") or name
        self._creator = self.get_property("creator") or self.guard.user
        self._category = self.get_property("category") or None
        self._dcc = self.get_property("dcc") or self.guard.dcc
        self._publish_id = self.get_property("publish_id") or self._id
        self._task_name = self.get_property("task_name") or None
        self._task_id = self.get_property("task_id") or None
        self._relative_path = self.get_property("path") or path
        self._software_version = self.get_property("softwareVersion") or None
        self._elements = self.get_property("elements") or []
        # self._is_promoted = self.get_property("isPromoted") or False
        self.modified_time = None  # to compare and update if necessary

        # get the current folder path
        _folder = pathlib.Path(self.settings_file).parent
        promoted_file = _folder / "promoted.json"
        self._promoted_object = Settings(promoted_file)

    def is_promoted(self):
        """Check the 'promoted' file in the publish folder. If the content is matching with the publish id, return True"""
        _id = self._promoted_object.get_property("publish_id", default=None)
        return _id == self._publish_id

    def promote(self):
        """Promote the publish editing the promoted.json"""
        _data = {
            "publish_id": self._publish_id,
            "name": self._name,
            "path": self._relative_path,
        }
        self._promoted_object.set_data(_data)
        self._promoted_object.apply_settings()



