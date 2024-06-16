"""Main Module for the Tik Manager"""

import http.client
import json
from pathlib import Path
import sys
from tik_manager4.core import filelog, settings, utils
from tik_manager4.objects import user, project
from tik_manager4 import dcc
from tik_manager4.external.packaging.version import Version
import tik_manager4._version as version
# the reload is necessary to make sure the dcc is reloaded
# this makes sure when different dcc's are used in the same python session
# for example, Maya and trigger.
from importlib import reload
reload(dcc)
from tik_manager4.ui.Qt import (
    QtWidgets,
)  # Only for browsing if the common folder is not defined

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)


class Main():
    """Main Tik Manager class. Handles User and Project related functions."""
    # set the dcc to the guard object
    dcc = dcc.Dcc()
    # dcc = dcc.get_dcc_class()
    log = filelog.Filelog(logname=__name__, filename="tik_manager4")


    def __init__(self, common_folder=None):
        """Initialize."""
        # set either the latest project or the default one
        # always make sure the default project exists, in case of urgent fall back
        self.user = user.User(common_directory=common_folder)
        self.project = project.Project()
        self.project.guard.set_dcc(dcc.NAME)
        self.project.guard.set_dcc_handler(self.dcc)
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

    def collect_template_paths(self):
        """Collect all template files from common, project and user folders."""
        # if the dcc is standalone, collect all applicable extensions from the extension dictionary
        # otherwise, collect the extensions from the dcc object
        if self.dcc.name.lower() == "standalone":
            extensions = [ext for ext_list in dcc.EXTENSION_DICT.values() for ext in ext_list]
        else:
            extensions = self.dcc.formats
        user_templates = [p for p in Path(self.user.settings.get("user_templates_directory")).rglob("*.*") if
                          p.suffix in extensions]
        project_templates = [p for p in Path(self.project.absolute_path).joinpath("_templates").rglob("*.*") if
                             p.suffix in extensions]
        common_templates = [p for p in Path(self.user.common_directory).joinpath("_templates").rglob("*.*") if
                            p.suffix in extensions]
        # user_templates = list(Path(self.user.settings.get("user_templates_directory")).rglob("*.*"))
        # project_templates = list((Path(self.project.absolute_path)/"_templates").rglob("*.*"))
        # common_templates = list((Path(self.user.common_directory)/"_templates").rglob("*.*"))

        return project_templates + common_templates + user_templates

    def get_template_names(self):
        """Get the names of the templates."""
        all_templates = self.collect_template_paths()
        return list(set([template.stem for template in all_templates]))

    def get_template_path_by_name(self, name):
        """Gets the template file by name.

        Resolution order is project > common > user.

        Args:
            name (str): Name of the template.

        Returns:
            tuple: Dcc Name, Path to the template file.
        """
        all_templates = self.collect_template_paths()
        for template_path in all_templates:
            if template_path.stem == name:
                dcc_name = self.__resolve_dcc_name_from_extension(template_path.suffix)
                return dcc_name, template_path.as_posix()

        return None, None

    def __resolve_dcc_name_from_extension(self, extension):
        """Resolve the DCC name from the extension."""
        for key, value in dcc.EXTENSION_DICT.items():
            if extension in value:
                return key
        # for anything else, return standalone
        return "standalone"

    def get_latest_release(self):
        """Get the latest release version from the github repository.

        Returns:
            ReleaseObject: Release object with version and download links.
        """
        conn = http.client.HTTPSConnection("api.github.com")

        headers = {
            "User-Agent": "MyApp"  # GitHub requires a User-Agent header
        }

        try:
            conn.request("GET", "/repos/masqu3rad3/tik_manager4/releases/latest", headers=headers)
            response = conn.getresponse()

            if response.status != 200:
                self.log.error(f"Error: Unable to fetch data, status code: {response.status}")
                return None

            data = response.read().decode('utf-8')
            release_info = json.loads(data)

            return ReleaseObject(release_info)

        except ConnectionError:
            self.log.error("Connection error to github. Check your internet connection")
            return None

        finally:
            conn.close()


class ReleaseObject:
    """Data class for the update object."""
    def __init__(self, github_dict):
        """Initialize."""
        self._dict = github_dict
        self._version = Version(self._dict.get("tag_name"))
        self._current_version = Version(version.__version__)

    @property
    def name(self):
        """Get the name."""
        return self._dict.get("name")

    @property
    def version(self):
        """Get the version."""
        return self._version

    def collect_links(self):
        """Get all the links in a dictionary."""
        link_sources = {
            "Windows Installer": self.windows_installer,
            "Mac Installer": self.mac_installer,
            "Debian Linux": self.debian_installer,
            "Redhat Linux": self.redhat_installer,
            "Tarball": self.tarball,
            "Zipball": self.zipball
        }

        return {name: link for name, link in link_sources.items() if link}

    @property
    def windows_installer(self):
        """Get the windows installer download url."""
        assets = self._dict.get("assets")
        for asset in assets:
            if asset.get("name").endswith(".exe"):
                return asset.get("browser_download_url")
        return None

    @property
    def mac_installer(self):
        """Get the mac installer download url."""
        assets = self._dict.get("assets")
        for asset in assets:
            if asset.get("name").endswith(".dmg"):
                return asset.get("browser_download_url")
        return None

    @property
    def debian_installer(self):
        """Get the linux installer download url."""
        assets = self._dict.get("assets")
        for asset in assets:
            if asset.get("name").endswith(".deb"):
                return asset.get("browser_download_url")
        return None

    @property
    def redhat_installer(self):
        """Get the linux installer download url."""
        assets = self._dict.get("assets")
        for asset in assets:
            if asset.get("name").endswith(".rpm"):
                return asset.get("browser_download_url")
        return None

    @property
    def tarball(self):
        """Get the tarball."""
        return self._dict.get("tarball_url")

    @property
    def zipball(self):
        """Get the zipball."""
        return self._dict.get("zipball_url")

    @property
    def is_newer(self):
        """Check if the current version is newer than the installed version."""
        return self._version > self._current_version

    @property
    def release_notes(self):
        """Return the release notes."""
        return self._dict.get("body")


