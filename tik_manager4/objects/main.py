"""Main Module for the Tik Manager"""

from pathlib import Path
import sys
from tik_manager4.core import filelog, settings, utils
from tik_manager4.objects import user, project
from tik_manager4 import dcc
from tik_manager4.ui.Qt import (
    QtWidgets,
)  # Only for browsing if the common folder is not defined

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)


class Main():
    """Main Tik Manager class. Handles User and Project related functions."""

    # set the dcc to the guard object
    dcc = dcc.Dcc()
    log = filelog.Filelog(logname=__name__, filename="tik_manager4")


    def __init__(self, common_folder=None):
        """Initialize."""
        # set either the latest project or the default one
        # always make sure the default project exists, in case of urgent fall back
        self.user = user.User(common_directory=common_folder)
        self.project = project.Project()
        self.project.guard.set_dcc(dcc.NAME)
        self.project.guard.set_commons(self.user.commons)

        default_project = Path(utils.get_home_dir(), "TM4_default")
        # default_project = os.path.join(utils.get_home_dir(), "TM4_default")

        if not (default_project / "tikDatabase" / "project_structure.json").exists():
            self._create_default_project()

        _project = default_project
        if self.user.get_recent_projects():
            recent_projects = self.user.get_recent_projects()
            # try to find the last project that exists
            for _project in reversed(recent_projects):
                if Path(_project, "tikDatabase", "project_structure.json").exists():
                    break

        self.set_project(str(_project))

    def _create_default_project(self):
        """Create a default project. Protected method."""
        # this does not require any permissions
        _project_path = Path(utils.get_home_dir(), "TM4_default")
        _database_path = _project_path / "tikDatabase"
        _database_path.mkdir(parents=True, exist_ok=True)
        _structure_file = _database_path / "project_structure.json"
        if _structure_file.exists():
            return

        structure_data = self.user.commons.structures.get_property("empty") or {
            "name": "TM4_default",
            "path": "",
            "resolution": [1920, 1080],
            "fps": 25,
            "mode": "root",
            "subs": [],
        }
        structure_data["name"] = "TM4_default"

        # create structure database file
        structure = settings.Settings(file_path=_structure_file)
        structure.set_data(structure_data)
        structure.apply_settings()

        project_obj = project.Project()  # this will be temporary
        project_obj._set(_project_path)

        # create an initial main task under the root
        categories = list(project_obj.guard.category_definitions.properties.keys())
        _main_task = project_obj.add_task("main", categories=categories)

    def create_project(
        self,
        path,
        structure_template="empty",
        structure_data=None,
        set_after_creation=True,
        **kwargs
    ):
        """Create a new project."""
        if self.user.permission_level < 3:
            self.log.warning("This user does not have rights to perform this action")
            return -1
        if not self.user.is_authenticated:
            self.log.warning("User is not authenticated")
            return -1
        database_path = Path(path, "tikDatabase")
        database_path.mkdir(parents=True, exist_ok=True)
        structure_file = database_path / "project_structure.json"
        if structure_file.exists():
            self.log.warning("Project already exists. Aborting")
            return -1
        project_name = Path(path).name
        if structure_data:
            structure_data = structure_data
        else:
            structure_data = self.user.commons.structures.get_property(
                structure_template
            )
        if not structure_data:
            self.log.warning("Structure template %s is not defined. Creating empty project")
            structure_data = {
                "name": project_name,
                "path": "",
                "mode": "root",
                "subs": [],
            }
        # override defined keys
        structure_data["name"] = project_name
        structure_data.update(kwargs)

        # create structure database file
        structure = settings.Settings(file_path=structure_file)
        structure.set_data(structure_data)
        structure.apply_settings()
        # define a project object to validate data and create folders

        project_obj = project.Project()  # this will be temporary
        project_obj._set(path)
        project_obj.create_folders(project_obj.absolute_path)
        project_obj.create_folders(project_obj.database_path)
        project_obj.save_structure()  # This makes sure IDs are getting saved

        categories = list(project_obj.guard.category_definitions.properties.keys())
        _main_task = project_obj.add_task("main", categories=categories)

        if set_after_creation:
            self.set_project(path)
        return 1

    def set_project(self, absolute_path):
        """Set the current project."""
        if not Path(absolute_path).exists():
            self.log.error("Project Path does not exist. Aborting")
            return -1
        self.project._set(absolute_path)
        # add to recent projects
        self.user.add_recent_project(absolute_path)
        self.user.last_project = absolute_path
        self.dcc.set_project(absolute_path)
