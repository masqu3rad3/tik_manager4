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

        self._name = name
        self._creator = self.guard.user
        self._category = None
        self._dcc = self.guard.dcc
        self._publish_id = self._id
        self._version = 1
        self._work_version = None
        self._task_name = None
        self._task_id = None
        self._relative_path = path
        self._dcc_version = None
        self._elements = []

        self.modified_time = None  # to compare and update if necessary

        self.init_properties()

        # get the current folder path
        _folder = pathlib.Path(self.settings_file).parent
        promoted_file = _folder / "promoted.json"
        self._promoted_object = Settings(promoted_file)

    def init_properties(self):
        """Initialize the properties of the publish."""
        self._name = self.get_property("name", self._name)
        self._creator = self.get_property("creator", self._creator)
        self._category = self.get_property("category", self._category)
        self._dcc = self.get_property("dcc", self._dcc)
        self._publish_id = self.get_property("publish_id", self._publish_id)
        self._version = self.get_property("version", self._version)
        self._work_version = self.get_property("work_version", self._work_version)
        self._task_name = self.get_property("task_name", self._task_name)
        self._task_id = self.get_property("task_id", self._task_id)
        self._relative_path = self.get_property("path", self._relative_path)
        self._dcc_version = self.get_property("dcc_version", self._dcc_version)
        self._elements = self.get_property("elements", self._elements)



    @property
    def creator(self):
        """Return the creator of the publish."""
        return self._creator

    @property
    def category(self):
        """Return the category of the publish."""
        return self._category

    @property
    def dcc(self):
        """Return the dcc of the publish."""
        return self._dcc

    @property
    def dcc_version(self):
        """Return the dcc version of the publish."""
        return self._dcc_version

    @property
    def publish_id(self):
        """Return the publish id of the publish."""
        return self._publish_id

    @property
    def version(self):
        """Return the version of the publish."""
        return self._version

    @property
    def task_name(self):
        """Return the task name of the publish."""
        return self._task_name

    @property
    def task_id(self):
        """Return the task id of the publish."""
        return self._task_id

    @property
    def relative_path(self):
        """Return the relative path of the publish."""
        return self._relative_path

    @property
    def software_version(self):
        """Return the software version of the publish."""
        return self._dcc_version

    @property
    def elements(self):
        """Return the elements of the publish."""
        return self._elements

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



