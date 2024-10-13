# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import tempfile
import uuid

from . import constants

from ..util import StorageRoots
from ..util import sgre as re
from ..util import shotgun
from ..util import filesystem
from ..util import is_windows
from ..util.version import is_version_newer
from ..util.zip import unzip_file, zip_file

from .. import hook
from ..errors import TankError, TankErrorProjectIsSetup
from .. import pipelineconfig_utils
from ..descriptor import create_descriptor, Descriptor

from tank_vendor import yaml

from ..util import ShotgunPath
from tank_vendor.shotgun_api3.lib import sgsix


class ProjectSetupParameters(object):
    """
    Class that holds all the various parameters needed to run a project setup.

    This class allows for various forms of validation and inspection of all the data required
    to set up a project.

    Parameters are typically set in this order:

    - get some information about the configuration
    - set the template configuration you want to use - set_config_uri()

    - set the project id - set_project_id()
    - get a suggested project name - get_default_project_disk_name()
    - set project disk name - set_project_disk_name() (can validate on beforehand using validate_project_disk_name())

    - set the configuration location - set_configuration_location()

    - validate using pre_setup_validation

    - run project setup!
    """

    (CENTRALIZED_CONFIG, DISTRIBUTED_CONFIG) = range(2)

    def __init__(self, log, sg):
        """
        Constructor

        :param log: python logger
        :param sg: shotgun connection
        """

        # set up handles
        self._sg = sg
        self._log = log

        # initialize data members - config
        self._cached_config_templates = {}
        self._config_template = None
        self._config_name = None
        self._config_description = None
        self._config_path = None

        # expert setting auto path mode
        self._auto_path = False

        # distribution mode, e.g. use old xxx_path fields or
        # new descriptor/uploaded config fields when storing
        # stuff on the pipeline config.
        self._distribution_mode = self.CENTRALIZED_CONFIG

        # initialize data members - project
        self._force_setup = False
        self._project_id = None
        self._project_disk_name = None

        # where to pick up the core from
        self._core_path = None

        # progress callback
        self._progress_callback = None

    def set_progress_callback(self, fp):
        """
        Specify a function which should be called during project setup
        whenever there is an update to the progress.

        The callback function should have the following
        signature:

        def callback(chapter_str, percent_progress_int)

        The installer will run through several "chapters" throughout the install
        and each of these will have a separate progress calculation. Some chapters
        are fast and/or difficult to quantify into steps - in this case, the
        percent_progress_int parameter will be passed None. For such chapters,
        the callback will be called only once.

        For chapters which report progress, the callback will be called multiple times,
        each time with an incremented progress. This is an int value in percent.

        For example

        callback("Setting up base storages", None)
        callback("Making folders", None)
        callback("Downloading apps", 1)
        callback("Downloading apps", 21)
        callback("Downloading apps", 56)
        callback("Downloading apps", 93)
        callback("Finalizing", None)

        :param fp: Function object representing a progress callback
        """
        self._progress_callback = fp

    def report_progress_from_installer(self, chapter, progress=None):
        """
        This method is executed from the setup core as it is executing the setup.
        If a progress callback has been defined, this is being called.
        For details, see set_progress_callback()

        :param chapter: String defining the current chapter
        :param progress: Int or None indicating progress, in percent
        """
        if self._progress_callback:
            self._progress_callback(chapter, progress)

    ################################################################################################################
    # Configuration template related logic

    @property
    def default_storage_name(self):
        """
        The name of the default storage.
        """
        return self._config_template.default_storage_name

    def validate_config_uri(self, config_uri):
        r"""
        Validates a configuration template to check if it is compatible with the current Shotgun setup.
        This will download the config, validate it to ensure that it is compatible with the
        constraints (versions of core and shotgun) of this system.

        If locating, downloading, or validating the config fails, exceptions will be raised.

        Once the config exists and is compatible, the storage situation is reviewed against shotgun.
        A dictionary with a breakdown of all storages required by the configuration is returned:

        {
          "primary" : { "description": "Description",
                        "exists_on_disk": False,
                        "defined_in_shotgun": True,
                        "darwin": "/mnt/foo",
                        "win32": "z:\mnt\foo",
                        "linux2": "/mnt/foo"},

          "textures" : { "description": None,
                         "exists_on_disk": False,
                         "defined_in_shotgun": True,
                         "darwin": None,
                         "win32": "z:\mnt\foo",
                         "linux2": "/mnt/foo"}
         }

        :param config_uri: Configuration uri representing the location of a config
        :returns: dictionary with storage data, see above.
        """

        # see if we got it cached
        if config_uri not in self._cached_config_templates:
            # first download, read and parse the configuration template
            # this call may mean downloading stuff from the internet.
            config_template = TemplateConfiguration(config_uri, self._sg, self._log)
            self._cached_config_templates[config_uri] = config_template

        return self._cached_config_templates[config_uri].resolve_storages()

    def set_config_uri(self, config_uri, check_storage_path=True):
        """
        Sets the configuration uri to use for this project.
        As part of this command, a template configuration may be downloaded over the network,
        either from git or from the toolkit app store.
        Raises exceptions in case the configuration is not compatible with the current shotgun setup.

        :param config_uri: Configuration uri representing the location of a config
        :param check_storage_path: Validate that storage paths exists on disk
        """

        # cache, get storage breakdown and run basic validation
        storage_data = self.validate_config_uri(config_uri)

        # now validate storages
        #
        # {
        #   "primary" : { "description": "Description",
        #                 "exists_on_disk": False,
        #                 "defined_in_shotgun": True,
        #                 "darwin": "/mnt/foo",
        #                 "win32": "z:\mnt\foo",
        #                 "linux2": "/mnt/foo"},
        #
        #   "textures" : { "description": None,
        #                  "exists_on_disk": False,
        #                  "defined_in_shotgun": True,
        #                  "darwin": None,
        #                  "win32": "z:\mnt\foo",
        #                  "linux2": "/mnt/foo"}
        #  }

        for storage_name in storage_data:

            if not storage_data[storage_name]["defined_in_shotgun"]:
                raise TankError(
                    "The storage '%s' required by the configuration has not been defined in Flow Production Tracking. "
                    "In order to fix this, please navigate to the Site Preferences in PTR "
                    "and set up a new local file storage." % storage_name
                )

            elif storage_data[storage_name][sgsix.platform] is None:
                raise TankError(
                    "The PTR Local File Storage '%s' does not have a path defined "
                    "for the current operating system!" % storage_name
                )

            elif (
                check_storage_path and not storage_data[storage_name]["exists_on_disk"]
            ):
                local_path = storage_data[storage_name][sgsix.platform]
                raise TankError(
                    "The path on disk '%s' defined in the PTR Local File Storage '%s' does "
                    "not exist!" % (local_path, storage_name)
                )

        # all checks passed! Populate official variables
        # note that the validate_config_uri method cached the config for us
        # so can just assign the object from the cache.
        self._config_template = self._cached_config_templates[config_uri]
        self._storage_data = storage_data

    def get_configuration_display_name(self):
        """
        Returns the display name of the configuration template

        :returns: Configuration display name string, none if not defined
        """
        if self._config_template is None:
            raise TankError("Please specify a configuration template!")

        return self._config_template.get_name()

    def get_configuration_description(self):
        """
        Returns the description of the associated configuration template

        :returns: Configuration description string, None if not defined
        """
        if self._config_template is None:
            raise TankError("Please specify a configuration template!")

        return self._config_template.get_description()

    def get_configuration_shotgun_info(self):
        """
        Returns information about how the config that we are
        using as a template for this project relates to shotgun.

        if we are basing the project on an external configuration,
        None is returned.

        If we are basing the project on an existing project, a dictionary
        with shotgun pipelineconfig information is returned,
        including the fields

        - id
        - code
        - mac_path
        - windows_path
        - linux_path
        - project
        - project.Project.tank_name (the disk name for the project)

        :returns: dict or None if no sg association could be found
        """
        if self._config_template is None:
            raise TankError("Please specify a configuration template!")

        if not self._config_template.is_local_config():
            return False

        field_name = ShotgunPath.get_shotgun_storage_key()

        data = self._sg.find_one(
            "PipelineConfiguration",
            [[field_name, "is", self._config_template.get_pipeline_configuration()]],
            [
                "id",
                "code",
                "mac_path",
                "windows_path",
                "linux_path",
                "project",
                "project.Project.tank_name",
            ],
        )

        return data

    def get_configuration_readme(self):
        """
        Returns the contents of a configuration README file, if such a file
        exists.

        :returns: list of strings or empty list if readme doesn't exist
        """
        if self._config_template is None:
            raise TankError("Please specify a configuration template!")

        return self._config_template.get_readme_content()

    def get_required_storages(self):
        """
        Returns a list of storage names which are required for this project.

        :returns: list of strings
        """
        if self._config_template is None:
            raise TankError("Please specify a configuration template!")

        return list(self._storage_data.keys())

    def get_storage_description(self, storage_name):
        """
        Returns the description of a storage required by a configuration

        :param storage_name: Storage name
        :returns: Storage description string, None if not defined
        """
        if self._config_template is None:
            raise TankError("Please specify a configuration template!")

        if storage_name not in self._storage_data:
            raise TankError(
                "Configuration template does not contain a storage with name '%s'!"
                % storage_name
            )

        return self._storage_data.get(storage_name).get("description")

    def get_storage_shotgun_id(self, storage_name):
        """
        Given a storage name as defined in the configuration roots, return the
        corresponding shotgun id as defined in Shotgun. If no PTR storage can
        be correlated, return None.
        """
        return self._storage_data.get(storage_name, {}).get("shotgun_id")

    def get_storage_path(self, storage_name, platform):
        """
        Returns the storage root path given a platform and a storage, as defined in Shotgun
        Note that this path has not been cleaned up, and may for example contain slashes at the end.

        :param storage_name: Storage name
        :param platform: operating system, sys.platform syntax
        :returns: path
        """
        if self._config_template is None:
            raise TankError("Please specify a configuration template!")

        if storage_name not in self._storage_data:
            raise TankError(
                "Configuration template does not contain a storage with name '%s'!"
                % storage_name
            )

        return self._storage_data.get(storage_name).get(
            sgsix.normalize_platform(platform)
        )

    def update_storage_root(self, config_uri, root_name, storage_data):
        """
        Given a required storage root name, update the template config's storage
        root information. See the corresponding template config method for more
        info.
        """
        self._cached_config_templates[config_uri].update_storage_root(
            root_name, storage_data
        )

    def upload_configuration(self, pipeline_config_id):
        """
        Zips up and then uploads the configuration to Shotgun.

        :param int pipeline_config_id: Pipeline configuration id to upload to.
        """
        if self._config_template is None:
            raise TankError("Please specify a configuration template!")

        # compose a filename for the zip file that will be uploaded to PTR
        # this will also be the name that is displayed on the attachment in PTR
        zip_filename = "%s.zip" % (self._config_template.version or "config")

        # create a folder name which will be the folder which everything is
        # contained inside if you unzip the configuration
        folder_name = "config_%s" % (self._config_template.version or "unversioned")

        # create a temp area where we can do our zipping
        temp_root = os.path.join(tempfile.gettempdir(), uuid.uuid4().hex)
        filesystem.ensure_folder_exists(temp_root)
        temp_zip = os.path.join(tempfile.gettempdir(), temp_root, zip_filename)
        temp_config = os.path.join(tempfile.gettempdir(), temp_root, folder_name)

        self._log.debug("Packaging up configuration...")

        try:
            # copy the configuration to the temp folder so we can update it.
            self._config_template.copy_configuration(temp_config)

            # update the roots.yml file in the config to
            # match the storage selections we have made in the wizard
            # e.g. link up a storage name e.g. 'primary' in the config
            # against a local storage id in Shotgun.
            #
            # Note: We don't write any paths to the roots.yml -
            # these are resolved at bootstrap time.
            roots_data = {}
            for storage_name in self.get_required_storages():

                # for distributed configs, we don't include any paths
                roots_data[storage_name] = {
                    "windows_path": None,
                    "linux_path": None,
                    "mac_path": None,
                }

                # if this is the default storage,
                # ensure it is explicitly marked in the roots file
                if (
                    self.default_storage_name
                    and storage_name == self.default_storage_name
                ):
                    roots_data[storage_name]["default"] = True

                # if there is a PTR local storage associated with this root, make sure
                # it is explicit in the the roots file. this allows roots to exist that
                # are not named the same as the storage in PTR
                sg_storage_id = self.get_storage_shotgun_id(storage_name)
                if sg_storage_id is not None:
                    roots_data[storage_name]["shotgun_storage_id"] = sg_storage_id

            storage_roots = StorageRoots.from_metadata(roots_data)
            storage_roots.write(self._sg, temp_config, storage_roots)

            # clean up some system files
            filesystem.safe_delete_folder(os.path.join(temp_config, "tk-metadata"))

            # zip up
            zip_file(temp_config, temp_zip)

            self._log.debug("Uploading confguration to Flow Production Tracking...")
            self._sg.upload(
                constants.PIPELINE_CONFIGURATION_ENTITY,
                pipeline_config_id,
                temp_zip,
                field_name=constants.PIPELINE_CONFIGURATION_UPLOAD_FIELD,
            )
        finally:
            filesystem.safe_delete_folder(temp_root)

    def create_configuration(self, target_path):
        """
        Sets up the associated template configuration. Copies files.

        :param target_path: Location where the config should be set up.
        """
        if self._config_template is None:
            raise TankError("Please specify a configuration template!")

        return self._config_template.create_configuration(target_path)

    ################################################################################################################
    # Project related logic

    def set_project_id(self, project_id, force=False):
        """
        Sets the project id and validates that this id is valid.

        :param project_id: Shotgun project id. Passing None means we are configuring the site
                           configuration.
        :param force: If true, existing projects can be overwritten
        """
        if project_id is not None:
            proj = self._sg.find_one(
                "Project", [["id", "is", project_id]], ["name", "tank_name"]
            )

            if proj is None:
                raise TankError(
                    "Could not find a project with id %s!" % self._project_id
                )

            # if force is false then tank_name must be empty
            if (
                self.get_auto_path_mode() == False
                and force == False
                and proj["tank_name"] is not None
            ):
                raise TankErrorProjectIsSetup()

        self._project_id = project_id
        self._force_setup = force

    def get_default_project_disk_name(self):
        """
        Returns the default folder name for a project

        :returns: project name string. This may contain slashes if the project name spans across
                  more than one folder.
        """

        if self._project_id is None:
            raise TankError("No project id specified!")

        # see if there is a hook to procedurally evaluate this
        project_name_hook = shotgun.get_project_name_studio_hook_location()
        if os.path.exists(project_name_hook):
            # custom hook is available!
            suggested_folder_name = hook.execute_hook(
                project_name_hook, parent=None, sg=self._sg, project_id=self._project_id
            )
        else:
            # construct a valid name - replace white space with underscore and lower case it.
            proj = self._sg.find_one(
                "Project", [["id", "is", self._project_id]], ["name"]
            )
            suggested_folder_name = re.sub(r"\W", "_", proj.get("name")).lower()

        return suggested_folder_name

    def validate_project_disk_name(self, project_name):
        """
        Validates that the given project disk name is valid.
        Raises exceptions in case the name is not valid.

        :param project_name: project disk name
        """
        if project_name.startswith("/"):
            raise TankError("A project disk name cannot start with a slash!")

        if project_name.endswith("/"):
            raise TankError("A project disk name cannot end with a slash!")

        # basic validation of folder name
        # note that the value can contain slashes and span across multiple folders
        if re.match(r"^[\./a-zA-Z0-9_-]+$", project_name) is None:
            raise TankError(
                "Invalid project folder '%s'! Please use alphanumerics, "
                "underscores and dashes." % project_name
            )

    def preview_project_path(self, storage_name, project_name, platform):
        """
        Returns a full project path for a given storage. Returns None if the project name is not valid.
        A configuration template must have been specified prior to executing this command.
        The path returned may not exist on disk but never ends with a path separator.

        :param storage_name: Name of storage for which to preview the project path
        :param project_name: Project disk name to preview
        :param platform: Os platform as a string, sys.platform style (e.g. linux2/win32/darwin)

        :returns: full path
        """
        if self._config_template is None:
            raise TankError("Please specify a configuration template!")

        # basic validation of project name
        try:
            self.validate_project_disk_name(project_name)
        except TankError:
            # validation failed!
            return None

        # get the storage path
        storage_path = self.get_storage_path(storage_name, platform)

        if storage_path is None:
            return None

        # get rid of any trailing slashes
        storage_path = storage_path.rstrip("/\\")
        # append the project name
        storage_path += "/%s" % project_name
        # note that project name can be 'foo/bar' with a forward slash for all platforms
        # Fixes any slashes that might be in the wrong direction.
        if platform == "win32":
            # ensure back slashes all the way
            storage_path = storage_path.replace("/", "\\")
        else:
            # ensure slashes all the way
            storage_path = storage_path.replace("\\", "/")

        return storage_path

    def set_project_disk_name(self, project_name):
        """
        Sets a project disk name to use for this configuration.
        May raise exception if the name is not valid.

        :param project_name: name of project
        """
        self.validate_project_disk_name(project_name)
        self._project_disk_name = project_name

    def get_project_id(self):
        """
        Returns the project id for the project to be set up.

        :returns: Shotgun project id as int or None if the id is not set.
        """
        return self._project_id

    def get_force_setup(self):
        """
        Should setup be forced?

        :returns: a boolean flag indicating whether the setup should be forced or not.
        """
        return self._force_setup

    def get_project_disk_name(self):
        """
        Returns the disk name to be given to the project. This may be a simple name
        "test_project" or may contain slashes "test/project" for project names
        which span across multiple folder levels, however it never starts or ends
        with a slash.

        :returns: project name as a string
        """
        if self._project_disk_name is None:
            raise TankError("No project name specified!")

        return self._project_disk_name

    def get_project_path(self, storage_name, platform):
        """
        Returns the project path given a platform and a storage. Can be None for undefined storages.
        The path returned may not exist on disk but never ends with a path separator.

        :param storage_name: Name of storage for which to preview the project path
        :param platform: Os platform as a string, sys.platform style (e.g. linux2/win32/darwin)

        :returns: full path
        """
        if self._project_disk_name is None:
            raise TankError("No project name specified!")

        if self._config_template is None:
            raise TankError("Please specify a configuration template!")

        return self.preview_project_path(
            storage_name, self._project_disk_name, platform
        )

    ################################################################################################################
    # Configuration template related logic

    def set_auto_path_mode(self, status):
        """
        Defines if auto-path should be on or off.
        Auto-path means that the pipeline configuration entry in
        Shotgun does not actually encode the path to where the configuration
        is located on disk - this is instead purely kept on the disk side

        :param status: boolean indicating if auto path should be used
        """
        self._auto_path = status

    def get_auto_path_mode(self):
        """
        Returns the auto-path status. See set_auto_path for details.

        :returns: boolean indicating if auto path should be used
        """
        return self._auto_path

    def set_distribution_mode(self, mode):
        """
        Controls whether the setup should be deployed as a
        centralized or distributed configuration.

        :param mode: Pass ProjectSetupParameters.CENTRALIZED_CONFIG|DISTRIBUTED_CONFIG
        """
        self._distribution_mode = mode

    def get_distribution_mode(self):
        """
        Returns whether the setup should be deployed as a
        centralized or distributed configuration.

        :returns: ProjectSetupParameters.CENTRALIZED_CONFIG|DISTRIBUTED_CONFIG
        """
        return self._distribution_mode

    def validate_configuration_location(self, linux_path, windows_path, macosx_path):
        """
        Performs basic I/O checks to ensure that the given configuration location is valid.
        Raises exceptions in case of validation problems.

        :param linux_path: Path on linux
        :param windows_path: Path on windows
        :param macosx_path: Path on mac
        """

        config_path = {}
        config_path["linux2"] = linux_path
        config_path["win32"] = windows_path
        config_path["darwin"] = macosx_path

        # validate that the config name contains valid characters. The range of valid characters
        # is similar to the one used to validate the project name.
        CONFIG_NAME_VALIDATION_REGEX = "^[a-zA-Z0-9_-]+$"

        # for paths which are not None and not empty, validate their name.
        # (note how we don't use os.path.sep because we have to check
        #  windows paths on a linux system and vice versa).
        if linux_path and linux_path != "":
            base_name = linux_path.split("/")[-1]
            if re.match(CONFIG_NAME_VALIDATION_REGEX, base_name) is None:
                raise TankError(
                    "Invalid Linux configuration folder name '%s'! Please use alphanumerics, "
                    "underscores and dashes." % base_name
                )

        if windows_path and windows_path != "":
            base_name = windows_path.split("\\")[-1]
            if re.match(CONFIG_NAME_VALIDATION_REGEX, base_name) is None:
                raise TankError(
                    "Invalid Windows configuration folder name '%s'! Please use alphanumerics, "
                    "underscores and dashes." % base_name
                )

        if macosx_path and macosx_path != "":
            base_name = macosx_path.split("/")[-1]
            if re.match(CONFIG_NAME_VALIDATION_REGEX, base_name) is None:
                raise TankError(
                    "Invalid Mac configuration folder name '%s'! Please use alphanumerics, "
                    "underscores and dashes." % base_name
                )

        # get the location of the configuration
        config_path_current_os = config_path[sgsix.platform]

        if config_path_current_os is None or config_path_current_os == "":
            raise TankError(
                "Please specify a configuration path for your current operating system!"
            )

        # validate that the config location is not taken
        if os.path.exists(config_path_current_os):
            # pipeline config location already exists -
            # make sure it doesn't already contain an install
            if os.path.exists(
                os.path.join(config_path_current_os, "install")
            ) or os.path.exists(os.path.join(config_path_current_os, "config")):
                raise TankError(
                    "Looks like the location '%s' already contains a "
                    "configuration!" % config_path_current_os
                )
            # also make sure it has right permissions
            if not os.access(config_path_current_os, os.W_OK | os.R_OK | os.X_OK):
                raise TankError(
                    "The permissions setting for '%s' is too strict. The current user "
                    "cannot create files or folders in this location."
                    % config_path_current_os
                )

        else:
            # path does not exist!
            # make sure parent path exists and is writable
            # (the setup process will create the path automatically)
            #
            # however, ensure that the parent path exists
            parent_config_path_current_os = os.path.dirname(config_path_current_os)

            if not os.path.exists(parent_config_path_current_os):
                raise TankError(
                    "The folder '%s' does not exist! Please create "
                    "it before proceeding!" % parent_config_path_current_os
                )

            # and make sure we can create a folder in it
            if not os.access(
                parent_config_path_current_os, os.W_OK | os.R_OK | os.X_OK
            ):
                raise TankError(
                    "Cannot create a project configuration in location '%s'! "
                    "The permissions setting for the parent folder '%s' "
                    "is too strict. The current user "
                    "cannot create folders in this location. Please create the "
                    "project configuration folder by hand and then re-run the project "
                    "setup." % (config_path_current_os, parent_config_path_current_os)
                )

    def set_configuration_location(self, linux_path, windows_path, macosx_path):
        """
        Sets the desired path to a pipeline configuration.
        Paths can be None, indicating that the path is not defined on a platform.

        :param linux_path: Path on linux
        :param windows_path: Path on windows
        :param macosx_path: Path on mac
        """

        # validate
        self.validate_configuration_location(linux_path, windows_path, macosx_path)

        # and set member variables
        self._config_path = {}
        self._config_path["linux2"] = linux_path
        self._config_path["win32"] = windows_path
        self._config_path["darwin"] = macosx_path

    def get_configuration_location(self, platform):
        """
        Returns the path to the configuration for a given platform.
        The path returned has not been validated and may not be correct nor exist.

        :param platform: Os platform as a string, sys.platform style (e.g. linux2/win32/darwin)
        :returns: path to pipeline configuration.
        """
        if self._config_path is None:
            raise TankError("No configuration location has been set!")

        return self._config_path[sgsix.normalize_platform(platform)]

    ################################################################################################################
    # Accessing which core API to use

    def set_associated_core_path(self, linux_path, windows_path, macosx_path):
        """
        Sets the desired core API to use.
        Paths can be None, indicating that the path is not defined on a platform.

        :param linux_path: Path on linux
        :param windows_path: Path on windows
        :param macosx_path: Path on mac
        """

        # and set member variables
        self._core_path = {}
        self._core_path["linux2"] = linux_path
        self._core_path["win32"] = windows_path
        self._core_path["darwin"] = macosx_path

    def get_associated_core_path(self, platform):
        """
        Return the location of the currently running API, given an os platform.
        Note that values returned can be none in case the core API location
        has not been defined on a platform.

        :param platform: Os platform as a string, sys.platform style (e.g. linux/win32/darwin)
        :returns: path to pipeline configuration.
        """
        return self._core_path[sgsix.normalize_platform(platform)]

    ################################################################################################################
    # Validation

    def pre_setup_validation(self):
        """
        Performs basic validation checks on all the specified data together.
        This method should be executed prior to running the setup projet logic to ensure
        that the process will succeed.
        """

        if self._core_path is None:
            raise TankError("Need to define a core location!")

        if self._core_path[sgsix.platform] is None:
            raise TankError(
                "The core API you are trying to use in conjunction with this project "
                "has not been set up to operate on the current operating system. Please update "
                "the install_location.yml file and try again."
            )

        # make sure all parameters have been specified
        if self._config_template is None:
            raise TankError("Configuration template has not been specified!")

        if (
            self._distribution_mode == self.CENTRALIZED_CONFIG
            and self._config_path is None
        ):
            raise TankError(
                "Path to the target configuration install has not been specified!"
            )

        if self._project_disk_name is None:
            raise TankError("Project disk name has not been specified!")

        # ensure an uploaded_config field exists if we are doing a distributed cfg
        if self._distribution_mode == self.DISTRIBUTED_CONFIG:
            # if the fields don't exist in shotgun, the fields will be not be returned
            field_data = self._sg.schema_field_read("PipelineConfiguration")
            if "uploaded_config" not in field_data:
                raise TankError(
                    "PTR site is missing a PipelineConfiguration.uploaded_config "
                    "field, required for distributed configs to work correctly. Please update to "
                    "a more recent version of Flow Production Tracking."
                )
        else:
            # checks for centralized config

            # make sure that the storage location is not the same folder
            # as the pipeline config location. That will confuse tank.
            config_path_current_os = self.get_configuration_location(sgsix.platform)
            for storage_name in self.get_required_storages():

                # get the project path for this storage
                # note! at this point, the storage root has been checked and exists on disk.
                project_path_local_os = self.get_project_path(
                    storage_name, sgsix.platform
                )

                if config_path_current_os == project_path_local_os:
                    raise TankError(
                        "Your configuration location '%s' has been set to the same "
                        "as one of the storage locations. This is not supported!"
                        % config_path_current_os
                    )

        # validate the local storages
        for storage_name in self.get_required_storages():

            # get the project path for this storage
            # note! at this point, the storage root has been checked and exists on disk.
            project_path_local_os = self.get_project_path(storage_name, sgsix.platform)

            if not os.path.exists(project_path_local_os):
                raise TankError(
                    "The Project path %s for storage %s does not exist on disk! "
                    "Please create it and try again!"
                    % (project_path_local_os, storage_name)
                )

        # check if the config template has required minimum core version and make sure that
        # the core we are trying to marry up with the config is recent enough
        required_core_version = self._config_template.get_required_core_version()
        if required_core_version:

            # now figure out the version of the desired API
            api_location = self.get_associated_core_path(sgsix.platform)
            curr_core_version = pipelineconfig_utils.get_core_api_version(api_location)

            if is_version_newer(required_core_version, curr_core_version):
                raise TankError(
                    "This configuration requires Toolkit Core version %s "
                    "but you are running version %s"
                    % (required_core_version, curr_core_version)
                )
            else:
                self._log.debug(
                    "Config requires Toolkit Core %s. "
                    "You are running %s which is fine."
                    % (required_core_version, curr_core_version)
                )


class TemplateConfiguration(object):
    """
    Functionality for handling installation and validation of tank configs.
    This class abstracts download and resolve of various config URLs, such as

    - app store based configs
    - git based configs
    - file system configs
    - configs copied across from other projects

    The constructor is initialized with a config_uri which can have the following syntax:

    - toolkit app store syntax:    tk-config-default
    - git syntax (ends with .git): git@github.com:shotgunsoftware/tk-config-default.git
                                   https://github.com/shotgunsoftware/tk-config-default.git
                                   /path/to/bare/repo.git
    - file system location:        /path/to/config

    For the app store, the config is downloaded and unpacked into the project location
    For the file system uri, the config folder is copied into the project location
    For git, the git repo is cloned into the config location, therefore being a live repository
    to which changes later on can be pushed or pulled.
    """

    _LOCAL = "local"

    def __init__(self, config_uri, sg, log):
        """
        Constructor

        :param config_uri: location of config (see constructor docs for details)
        :param sg: Shotgun site API instance
        :param log: Log channel
        """
        self._sg = sg
        self._log = log

        # now extract the cfg and validate
        old_umask = os.umask(0)
        try:
            (self._cfg_folder, self._version, self._config_mode) = self._process_config(
                config_uri
            )
        finally:
            os.umask(old_umask)
        self._config_uri = config_uri

        # load the required storage roots for the config
        self._storage_roots = StorageRoots.from_config(self._cfg_folder)

        # if the file doesn't exist, create some defaults. if the file does
        # exist, we'll assume that the intention is not to define any storage
        # roots, as is the case with the basic and site config.
        if not os.path.exists(self._storage_roots.roots_file):
            self._storage_roots.populate_defaults()

        # ensure a default root can be determined from the required roots
        if self._storage_roots.required_roots and not self._storage_roots.default:
            raise TankError(
                "Looks like your configuration has required storage roots but "
                "does not specify a default root. You can mark a storage root "
                "as default in your config's '%s' folder by adding a `default: "
                "true` key/value pair to a storage's definition."
                % (self._storage_roots.STORAGE_ROOTS_FILE_PATH,)
            )

        # see if there is a readme file
        self._readme_content = []
        readme_file = os.path.join(self._cfg_folder, "README")
        if os.path.exists(readme_file):
            fh = open(readme_file)
            for line in fh:
                self._readme_content.append(line.strip())
            fh.close()

        # validate that we are running recent enough versions of core and shotgun
        info_yml = os.path.join(self._cfg_folder, constants.BUNDLE_METADATA_FILE)
        if not os.path.exists(info_yml):
            self._manifest = {}
            self._log.warning(
                "Could not find manifest file %s. "
                "Project setup will proceed without validation." % info_yml
            )
        else:
            # check manifest
            try:
                file_data = open(info_yml)
                try:
                    self._manifest = yaml.load(file_data, Loader=yaml.FullLoader)
                finally:
                    file_data.close()
            except Exception as e:
                raise TankError(
                    "Cannot load configuration manifest '%s'. Error: %s" % (info_yml, e)
                )

            # perform checks
            if "requires_shotgun_version" in self._manifest:
                # there is a sg min version required - make sure we have that!

                required_version = self._manifest["requires_shotgun_version"]

                # get the version for the current sg site as a string (1.2.3)
                sg_version_str = ".".join(
                    [str(x) for x in self._sg.server_info["version"]]
                )

                if is_version_newer(required_version, sg_version_str):
                    raise TankError(
                        "This configuration requires PTR version %s "
                        "but you are running version %s"
                        % (required_version, sg_version_str)
                    )
                else:
                    self._log.debug(
                        "Config requires PTR %s. "
                        "You are running %s which is fine."
                        % (required_version, sg_version_str)
                    )

    ################################################################################################
    # Helper methods

    def _create_git_descriptor(self, git_uri):
        """
        Given a config git uri, create a descriptor object
        to be used for the project setup.

        :param git_uri: Git repository uri for config
        :return: :class:`sgtk.descriptor.Descriptor` object.
        """
        # the default logic when passing a git url to the project
        # setup is to return back the last commit on master.
        return create_descriptor(
            self._sg,
            Descriptor.CONFIG,
            {"type": "git_branch", "path": git_uri, "branch": "master"},
            resolve_latest=True,
            local_fallback_when_disconnected=False,
        )

    def _process_config_zip(self, zip_path):
        """
        unpacks a zip config into a temp location.

        :param zip_path: path to zip file to unpack
        :returns: tmp location on disk where config now resides
        """
        # unzip into temp location
        self._log.debug("Unzipping configuration and inspecting it...")
        zip_unpack_tmp = os.path.join(tempfile.gettempdir(), uuid.uuid4().hex)
        unzip_file(zip_path, zip_unpack_tmp, auto_detect_bundle=True)
        template_items = os.listdir(zip_unpack_tmp)
        for item in ["core", "env", "hooks"]:
            if item not in template_items:
                raise TankError(
                    "Config zip '%s' is missing a %s folder!" % (zip_path, item)
                )
        self._log.debug("Configuration looks valid!")

        return zip_unpack_tmp

    def _process_config_dir(self, dir_path):
        """
        Validates that the directory contains a tank config
        """
        template_items = os.listdir(dir_path)
        for item in ["core", "env", "hooks"]:
            if item not in template_items:
                raise TankError(
                    "Config location '%s' missing a %s folder!" % (dir_path, item)
                )
        self._log.debug("Configuration looks valid!")
        return dir_path

    def _process_config(self, config_uri):
        """
        Looks at the starter config string and tries to convert it into a folder
        Returns a path to a config.

        - toolkit app store syntax:    tk-config-default
        - git syntax (ends with .git): git@github.com:shotgunsoftware/tk-config-default.git
                                       https://github.com/shotgunsoftware/tk-config-default.git
                                       /path/to/bare/repo.git
        - file system location:        /path/to/config

        :param config_uri: config path of some kind (git/appstore/configured_project)
        :returns: tuple with (tmp_path_to_config, config_type) where config_type is configured_project/zip/git/app_store
        """
        # three cases:
        # tk-config-xyz
        # /path/to/file.zip
        # /path/to/folder
        if config_uri.endswith(".git"):
            # this is a git repository!
            self._log.info("Hang on, loading configuration from git...")
            descriptor = self._create_git_descriptor(config_uri)
            descriptor.ensure_local()
            return descriptor.get_path(), descriptor.version, "git"

        elif os.path.sep in config_uri:
            # probably a file path!
            if os.path.exists(config_uri):
                # either a folder or zip file!
                if config_uri.endswith(".zip"):
                    self._log.info("Hang on, unzipping configuration...")
                    return self._process_config_zip(config_uri), None, "zip"
                else:
                    self._log.info("Hang on, loading configuration...")
                    return self._process_config_dir(config_uri), None, self._LOCAL
            else:
                raise TankError("File path %s does not exist on disk!" % config_uri)

        elif config_uri.startswith("tk-"):
            # app store!
            self._log.info("Hang on, loading configuration from the app store...")

            descriptor = create_descriptor(
                self._sg,
                Descriptor.CONFIG,
                {"type": "app_store", "name": config_uri},
                resolve_latest=True,
                local_fallback_when_disconnected=False,
            )
            descriptor.ensure_local()
            return descriptor.get_path(), descriptor.version, "app_store"

        else:
            raise TankError("Don't know how to handle config '%s'" % config_uri)

    ################################################################################################
    # Public interface

    @property
    def default_storage_name(self):
        """
        The default storage name for this template configuration.
        """
        return self._storage_roots.default

    @property
    def version(self):
        """
        Version number string for this config or none if no version is defined.
        """
        return self._version

    def resolve_storages(self):
        r"""
        Validate that the roots exist in shotgun. Communicates with Shotgun.

        Returns the root paths from shotgun for each storage.

        {
          "primary" : { "description": "Description",
                        "exists_on_disk": False,
                        "defined_in_shotgun": True,
                        "shotgun_id": 12,
                        "darwin": "/mnt/foo",
                        "win32": "z:\mnt\foo",
                        "linux2": "/mnt/foo"},

          "textures" : { "description": None,
                         "exists_on_disk": False,
                         "defined_in_shotgun": True,
                         "shotgun_id": 14,
                         "darwin": None,
                         "win32": "z:\mnt\foo",
                         "linux2": "/mnt/foo"}
        }

        The main dictionary is keyed by storage name. It will contain one entry
        for each local storage which is required by the configuration template.
        Each sub-dictionary contains the following items:

        - description: Description what the storage is used for. This comes from the
          configuration template and can be used to help a user to explain the purpose
          of a particular storage required by a configuration.
        - defined_in_shotgun: If false, no local storage with this name exists in Shotgun.
        - shotgun_id: If defined_in_shotgun is True, this will contain the entity id for
          the storage. If defined_in_shotgun is False, this will be set to none.
        - darwin/win32/linux: Paths to storages, as defined in Shotgun. These values can be
          None if a storage has not been defined.
        - exists_on_disk: Flag if the path defined for the current operating system exists on
          disk or not.

        :returns: dictionary with storage breakdown, see example above.
        """

        # a dictionary of info to return
        storage_info = {}

        # do the storage lookup and mapping in PTR
        (local_storage_lookup, unmapped_roots) = self._storage_roots.get_local_storages(
            self._sg
        )

        default_storage_name = self._storage_roots.default

        # process each required storage root and populate the info dict
        for root_name, root_info in self._storage_roots:

            # description
            storage_info[root_name] = {"description": root_info.get("description")}

            # default
            if default_storage_name and default_storage_name == root_name:
                storage_info[root_name]["default"] = True

            # path key defaults
            for key in StorageRoots.PLATFORM_KEYS:
                storage_info[root_name][key] = root_info.get(key)

            if root_name in unmapped_roots:
                # not mapped to a storage in PTR
                storage_info[root_name]["shotgun_id"] = None
                storage_info[root_name]["defined_in_shotgun"] = False
                storage_info[root_name]["exists_on_disk"] = False
            else:
                # mapped to a PTR storage
                local_storage = local_storage_lookup[root_name]

                storage_info[root_name]["defined_in_shotgun"] = True
                storage_info[root_name]["shotgun_id"] = local_storage["id"]

                # populate the platform path keys
                storage_info[root_name]["darwin"] = local_storage["mac_path"]
                storage_info[root_name]["linux2"] = local_storage["linux_path"]
                storage_info[root_name]["win32"] = local_storage["windows_path"]

                sg_path = ShotgunPath.from_shotgun_dict(local_storage)

                # see if the current os path is defined
                local_path = sg_path.current_os

                if not local_path or not os.path.exists(local_path):
                    # no path defined or it doesn't exist
                    storage_info[root_name]["exists_on_disk"] = False
                else:
                    # path exists!
                    storage_info[root_name]["exists_on_disk"] = True

        return storage_info

    def get_required_core_version(self):
        """
        Returns the required core version, as a string

        :returns: str, e.g. 'v0.2.3' or None if not defined
        """
        return self._manifest.get("requires_core_version")

    def get_name(self):
        """
        Returns the display name of this config, as defined in the manifest

        :returns: string
        """
        return self._manifest.get("display_name")

    def get_uri(self):
        """
        Returns the config URI associated with this config

        :returns: string
        """
        return self._config_uri

    def is_local_config(self):
        """
        Returns if the configuration is on the local disk.

        :returns: True if the configuration is on the local disk, False otherwise.
        """
        return self._config_mode == self._LOCAL

    def get_pipeline_configuration(self):
        """
        Resolves the potential pipeline configuration based on the configuration uri. Potential is employed here because
        there's no guarantee this folder is actually part of a pipeline configuration.

        :returns: Path to the pipeline configuration associated with the configuration uri.

        :raises TankError: This exception is raised when the configuration was pulled from GitHub, AppStore or zip file,
            since no pipeline configuration can be associated with these.
        """
        if not self.is_local_config():
            raise TankError(
                "Cannot resolve pipeline configuration for '%s' because it doesn't belong to an existing project!"
                % self._config_uri
            )

        # The config uri points to the config folder inside the pipeline configuration, so we'll have to step out
        # for this one.
        return os.path.split(self._config_uri)[0]

    def get_readme_content(self):
        """
        Get associated readme content as a list.
        If not readme exists, an empty list is returned

        :returns: list of strings
        """
        return self._readme_content

    def get_description(self):
        """
        Returns the description of the config, as defined in the manifest

        :returns string
        """
        return self._manifest.get("description")

    @filesystem.with_cleared_umask
    def copy_configuration(self, target_path):
        """
        Copies the configuration to the given path.
        If the target_path does not exist, it will be created.

        :param target_path: Path where config will be copied
        """
        # copy the config from its source location into place
        filesystem.copy_folder(self._cfg_folder, target_path)

    @filesystem.with_cleared_umask
    def create_configuration(self, target_path):
        """
        Creates the configuration folder in the target path

        :param target_path: Path where config will be copied
        """
        if self._config_mode == "git":
            descriptor = self._create_git_descriptor(self._config_uri)
            descriptor.copy(target_path)

        else:
            # copy the config from its source location into place
            filesystem.copy_folder(self._cfg_folder, target_path)

    def update_storage_root(self, root_name, storage_data):
        r"""
        Given a required storage root name, update the template config's storage
        root information.

        The data is in the same form as the required roots dictionary stored in
        the config's root.yml file. Example::

            {
                "description": "A top-level root folder for production data...",
                "mac_path": "/shotgun/prod",
                "linux_path": "/shotgun/prod",
                "windows_path": "C:\shotgun\prod",
                "default": True,
                "shotgun_storage_id": 1,
            }

        Not all fields are required to be specified. Only the supplied fields
        will be updated on the existing storage data.

        :param root_name: The name of a root to update.
        :param storage_data: A dctionary
        :return:
        """
        self._storage_roots.update_root(root_name, storage_data)
