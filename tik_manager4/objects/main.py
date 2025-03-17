"""Main Module for the Tik Manager"""

import http.client
import json
from pathlib import Path
import uuid

from tik_manager4.core import filelog, settings, utils
from tik_manager4.core.constants import ValidationState, ValidationResult
from tik_manager4.objects import user, project, purgatory
from tik_manager4 import dcc
from tik_manager4 import management
from tik_manager4.external.packaging.version import Version
import tik_manager4._version as version
# the reload is necessary to make sure the dcc is reloaded
# this makes sure when different dcc's are used in the same python session
# for example, Maya and trigger.
from importlib import reload
reload(dcc)


class Main:
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
        self.project.guard.set_dcc_handler(self.dcc)
        self.project.guard.set_commons(self.user.commons)
        self.project.guard.set_localize_settings(self.user.localization)
        self.all_dcc_extensions = dcc.EXTENSION_DICT
        self.purgatory = purgatory.Purgatory(self)

        self.default_project = Path(utils.get_home_dir(), "TM4_default")

        if not (self.default_project / "tikDatabase" / "project_structure.json").exists():
            self._create_default_project()

        _project = self.default_project.as_posix()
        if self.user.get_recent_projects():
            recent_projects = self.user.get_recent_projects()
            # try to find the last project that exists
            for _project in reversed(recent_projects):
                if Path(_project, "tikDatabase", "project_structure.json").exists():
                    break

        self.set_project(str(_project))

        self.globalize_management_platform()

        self.dcc.collect_common_plugins()

    def fallback_to_default_project(self):
        """Fallback to the default project."""
        if self.default_project.exists():
            self.set_project(self.default_project.as_posix())
        else:
            self._create_default_project()
            self.set_project(self.default_project.as_posix())

    def globalize_management_platform(self):
        """Globalize the management platform."""
        management_platform = self.project.settings.get("management_platform", None)
        if management_platform:
            self.project.guard.set_management_handler(
                management.platforms[management_platform](self))
        else:
            self.project.guard.set_management_handler(None)

    def _create_default_project(self):
        """Create a default project."""
        # this does not require any permissions
        _project_path = Path(utils.get_home_dir(), "TM4_default")
        _database_path = _project_path / "tikDatabase"
        _database_path.mkdir(parents=True, exist_ok=True)
        _structure_file = _database_path / "project_structure.json"
        if _structure_file.exists():
            return False

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
        project_obj._set(_project_path.as_posix())

        # create an initial main task under the root
        categories = list(project_obj.guard.category_definitions.properties.keys())
        _main_task = project_obj.add_task("main", categories=categories)
        return True

    def create_project(
        self,
        path,
        structure_template="empty",
        structure_data=None,
        set_after_creation=True,
        locked_commons=True,
        **kwargs
    ):
        """Create a new project.

        Args:
            path (str): The path to create the project.
            structure_template (str): The name of the structure template to use.
            structure_data (dict): The structure data to use. If not provided,
                    The structure template name will be used to get the data from
                    the common database.
            set_after_creation (bool): If True, the project
                will be set after creation.
            locked_commons (bool): If True, the project will be locked to the
                current commons.

        Returns:
            int: 1 if successful, -1 if not.
        """
        path_obj = Path(path)
        if self.user.permission_level < 3:
            self.log.warning("This user does not have rights to perform this action")
            return -1
        if not self.user.is_authenticated:
            self.log.warning("User is not authenticated")
            return -1
        # database_path = Path(path, "tikDatabase")
        database_path = path_obj / "tikDatabase"
        database_path.mkdir(parents=True, exist_ok=True)
        structure_file = database_path / "project_structure.json"
        if structure_file.exists():
            self.log.warning("Project already exists. Aborting")
            return -1
        project_name = path_obj.name

        structure_data = structure_data or self.user.commons.structures.get_property(
            structure_template
        )

        # if the structure data is still not defined use a default empty structure
        if not structure_data:
            self.log.warning(f"Structure template {structure_template} is "
                             f"not defined. Creating empty project")
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

        project_obj = project.Project()  # this will be temporary
        project_obj._set(path_obj.as_posix())
        project_obj.create_folders(project_obj.absolute_path)
        project_obj.create_folders(project_obj.database_path)
        project_obj.save_structure()  # This makes sure IDs are getting saved

        categories = list(project_obj.guard.category_definitions.properties.keys())
        _main_task = project_obj.add_task("main", categories=categories)

        if locked_commons:
            # first make sure that the commons have an id.
            if not self.user.commons.id:
                self.user.commons.management_settings.add_property(
                    "commons_id", str(uuid.uuid1().hex))
                self.user.commons.management_settings.apply_settings()
            project_obj.settings.add_property("commons_id", self.user.commons.id)
            project_obj.settings.add_property("commons_name", self.user.commons.name)
            project_obj.settings.apply_settings(force=True)

        self.globalize_management_platform()

        if set_after_creation:
            self.set_project(path_obj.as_posix())
        return 1

    def can_set_project(self, absolute_path) -> ValidationResult:
        """Check if the project is valid.

        Args:
            absolute_path (str): The absolute path to the project.

        Returns:
            object: ValidationResult object.
        """
        if not Path(absolute_path).exists():
            msg = "Project Path does not exist. Aborting"
            self.log.error(msg)
            return ValidationResult(ValidationState.ERROR, msg, allow_proceed=False)
        if not Path(absolute_path, "tikDatabase", "project_structure.json").exists():
            if self.user.permission_level < 3:
                msg = "The selected folder is not a Tik Manager project, and you do not have the necessary privileges to set it as one. Action cannot be completed."
                self.log.error(msg)
                return ValidationResult(ValidationState.ERROR, msg, allow_proceed=False)
            msg = "The selected folder is not currently defined as a Tik Manager project. If you proceed, the necessary database files and folder structure will be created, and this folder will be designated as a Tik Manager project.\n\nDo you want to continue?"
            self.log.warning(msg)
            return ValidationResult(ValidationState.WARNING, msg, allow_proceed=True)
        return ValidationResult(ValidationState.SUCCESS, "Success")

    def set_project(self, absolute_path):
        """Set the current project.

        Args:
            absolute_path (str): The absolute path to the project.

        Returns:
            int: 1 if successful, -1 if not.
        """
        # pylint: disable=protected-access
        validation: ValidationResult = self.can_set_project(absolute_path)
        if validation.state != ValidationState.SUCCESS and not validation.allow_proceed:
            return False, validation.message

        state, msg = self.project._set(absolute_path, commons_id=self.user.commons.id) # pylint: disable=protected-access
        if not state:
            self.fallback_to_default_project()
            self.log.error(msg)
            return False, msg

        # add to recent projects
        self.user.add_recent_project(absolute_path)
        self.user.last_project = absolute_path
        self.dcc.set_project(absolute_path)
        self.globalize_management_platform()
        return True, "Success"

    def add_project_as_structure_template(self, template_name=None):
        """Add the current project as a new structure template."""
        # check for the permission level
        if self.user.permission_level < 3:
            self.log.warning("This user does not have rights to perform this action")
            return False

        current_structure = self.project.structure.copy_data()
        # go through the structure and remove the ids
        filtered_structure = utils.remove_key(current_structure, "id")
        filtered_structure["name"] = template_name

        self.user.commons.structures.add_property(template_name, filtered_structure)
        self.user.commons.structures.apply_settings()

        return True

    def collect_template_paths(self):
        """Collect all template files from common, project and user folders.

        Returns:
            list: [project_templates, common_templates, user_templates]
        """
        # if the dcc is standalone, collect all applicable extensions from the extension dictionary
        # otherwise, collect the extensions from the dcc object
        if self.dcc.name.lower() == "standalone":
            extensions = [ext for ext_list in self.all_dcc_extensions.values() for ext in ext_list]
        else:
            extensions = self.dcc.formats
        user_templates = [p for p in Path(self.user.settings.get("user_templates_directory")).rglob("*.*") if
                          p.suffix in extensions]
        project_templates = [p for p in Path(self.project.absolute_path).joinpath("_templates").rglob("*.*") if
                             p.suffix in extensions]
        common_templates = [p for p in Path(self.user.common_directory).joinpath("_templates").rglob("*.*") if
                            p.suffix in extensions]

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
        """Resolve the DCC name from the extension.

        Args:
            extension (str): The file extension.

        Returns:
            str: The DCC name.
        """
        for key, value in self.all_dcc_extensions.items():
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

    def get_management_handler(self, platform_name=None):
        """Resolve the management handler.

        Args:
            platform_name (str, optional): The name of the platform.
                if the platform name is not matching to the current one,
                a new handler will be created.
        """
        msg = "Success"
        defined_handler = self.project.guard.management_handler
        if defined_handler:
            if defined_handler.name == platform_name:
                if defined_handler.is_authenticated:
                    return defined_handler, msg
                _sg, msg = defined_handler.authenticate()
                if not _sg:
                    self.log.error(msg)
                    return None, msg
                return defined_handler, msg
            # if we are requesting a different platform than the defined one
            # Create a new loose handler
            handler = (management.platforms[platform_name](self))
            _sg, msg = handler.authenticate()
            return handler, msg

        # if there is no defined handler, create a new one
        project_defined_platform = self.project.settings.get("management_platform")
        if platform_name:
            handler = management.platforms[platform_name](self)
            _sg, msg = handler.authenticate()
            return handler, msg
        if project_defined_platform:
            handler = management.platforms[project_defined_platform](self)
            self.project.guard.set_management_handler(handler)
            _sg, msg = handler.authenticate()
            return handler, msg
        msg = "No management platform defined or provided."
        self.log.warning(msg)
        return None, msg


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
        """Get all the links in a dictionary.

        Returns:
            dict: Dictionary with the link names and the links.
        """
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
        """Get the windows installer download url.

        Returns:
            str: The download url or None.
        """
        assets = self._dict.get("assets")
        for asset in assets:
            if asset.get("name").endswith(".exe"):
                return asset.get("browser_download_url")
        return None

    @property
    def mac_installer(self):
        """Get the mac installer download url.

        Returns:
            str: The download url or None.
        """
        assets = self._dict.get("assets")
        for asset in assets:
            if asset.get("name").endswith(".dmg"):
                return asset.get("browser_download_url")
        return None

    @property
    def debian_installer(self):
        """Get the linux installer download url.

        Returns:
            str: The download url or None.
        """
        assets = self._dict.get("assets")
        for asset in assets:
            if asset.get("name").endswith(".deb"):
                return asset.get("browser_download_url")
        return None

    @property
    def redhat_installer(self):
        """Get the linux installer download url.

        Returns:
            str: The download url or None.
        """
        assets = self._dict.get("assets")
        for asset in assets:
            if asset.get("name").endswith(".rpm"):
                return asset.get("browser_download_url")
        return None

    @property
    def tarball(self):
        """Return the tarball."""
        return self._dict.get("tarball_url")

    @property
    def zipball(self):
        """Return the zipball."""
        return self._dict.get("zipball_url")

    @property
    def is_newer(self):
        """Check if the current version is newer than the installed version."""
        return self._version > self._current_version

    @property
    def release_notes(self):
        """Return the release notes."""
        return self._dict.get("body")
