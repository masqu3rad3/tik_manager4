import os
from tik_manager4.core import filelog, settings
from tik_manager4.objects import user, project

log = filelog.Filelog(logname=__name__, filename="tik_manager4")


class Main(object):
    user = user.User()
    project = project.Project()

    def __init__(self):
        # set either the latest project or the default one
        # always make sure the default project exists, in case of urgent fall back
        default_project = os.path.join(os.path.expanduser("~"), "TM4_default")
        if not os.path.exists(os.path.join(default_project, "tikDatabase", "project_structure.json")):
            self._create_default_project()

        if self.user.get_recent_projects():
            _project = self.user.get_recent_projects()[-1]
        else:
            _project = default_project

        self.project.set(_project)
        self.user.add_recent_project(_project)

    def _create_default_project(self):
        # this does not require any permissions
        _project_path = os.path.join(os.path.expanduser("~"), "TM4_default")
        _database_path = os.path.join(_project_path, "tikDatabase")
        _structure_file = os.path.join(_database_path, "project_structure.json")
        if os.path.exists(_structure_file):
            return
        if not os.path.exists(_database_path):
            os.makedirs(_database_path)

        structure_data = self.user.commons.structures.get_property("empty") or {
            "name": "TM4_default",
            "path": "",
            "resolution": [1920, 1080],
            "fps": 25,
            "categories": [],
            "subs": []
        }
        structure_data["name"] = "TM4_default"

        # create structure database file
        structure = settings.Settings(file_path=_structure_file)
        structure.set_data(structure_data)
        structure.apply_settings()


    def create_project(self, path, structure_template="empty", set_after_creation=True, **kwargs):
        """Creates a new project"""

        if self.user.permission_level < 3:
            log.warning("This user does not have rights to perform this action")
            return -1
        if not self.user.is_authenticated:
            log.warning("User is not authenticated")
            return -1

        database_path = os.path.join(path, "tikDatabase")
        if not os.path.exists(database_path):
            os.makedirs(database_path)

        structure_file = os.path.join(database_path, "project_structure.json")
        if os.path.exists(structure_file):
            log.warning("Project already exists. Aborting")
            return -1

        project_name = os.path.basename(path)
        structure_data = self.user.commons.structures.get_property(structure_template)

        if not structure_data:
            log.warning("Structure template %s is not defined. Creating empty project")
            structure_data = {
                              "name": project_name,
                              "path": "",
                              "resolution": [1920, 1080],
                              "fps": 25,
                              "categories": [],
                              "subs": []
                            }

        # override defined keys
        structure_data["name"] = project_name
        structure_data.update(kwargs)

        # create structure database file
        structure = settings.Settings(file_path=structure_file)
        structure.set_data(structure_data)
        structure.apply_settings()

        # define a project object to validate data and create folders
        if set_after_creation:
            project_obj = self.project # our main project
        else:
            project_obj = project.Project() # this will be temporary

        project_obj.set(path)
        project_obj.create_folders(project_obj.absolute_path)
        project_obj.create_folders(project_obj.database_path)
        return 1

    # def set_project(self):
