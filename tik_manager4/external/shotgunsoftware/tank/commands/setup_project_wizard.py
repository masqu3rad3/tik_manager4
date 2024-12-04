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
from distutils.version import StrictVersion

from .action_base import Action
from . import core_localize
from ..util import shotgun
from ..util import ShotgunPath
from ..util import is_linux, is_macos, is_windows
from ..errors import TankError
from .. import pipelineconfig_utils

from .setup_project_core import run_project_setup
from .setup_project_params import ProjectSetupParameters
from .interaction import YesToEverythingInteraction
from tank_vendor.shotgun_api3.lib import sgsix


class SetupProjectFactoryAction(Action):
    """
    Special handling of Project setup.

    This is a more complex alternative to the simple setup_project command.

    This class exposes a setup_project_factory command to the API only (no tank command support)
    which returns a factory command object which can then in turn construct project setup wizard instances which
    can be used to build interactive wizard-style project setup processes.

    it is used like this:

    >>> import tank
    # create our factory object
    >>> factory = tank.get_command("setup_project_factory")
    # the factory can spit out set up wizards
    >>> setup_wizard = factory.execute({})
    # now set up various parameters etc on the project wizard
    # this can be an interactive process which includes validation etc.
    >>> wizard.set_parameters(....)
    # lastly, execute the actual setup.
    >>> wizard.execute()

    """

    def __init__(self):
        Action.__init__(
            self,
            "setup_project_factory",
            Action.GLOBAL,
            (
                "Returns a factory object which can be used to construct setup wizards. These wizards "
                "can then be used to run an interactive setup process."
            ),
            "Configuration",
        )

        # no tank command support for this one because it returns an object
        self.supports_tank_command = False

        # this method can be executed via the API
        self.supports_api = True

        self.parameters = {}

    def run_interactive(self, log, args):
        """
        Tank command accessor

        :param log: std python logger
        :param args: command line args
        """
        raise TankError("This Action does not support command line access")

    def run_noninteractive(self, log, parameters):
        """
        Tank command API accessor.
        Called when someone runs a tank command through the core API.

        :param log: std python logger
        :param parameters: dictionary with tank command parameters
        """
        # connect to shotgun
        sg = self._shotgun_connect(log)
        # return a wizard object
        return SetupProjectWizard(log, sg)

    def _shotgun_connect(self, log):
        """
        Connects to Shotgun.

        :returns: Shotgun API handle.
        :raises: TankError on failure
        """

        # now connect to shotgun
        try:
            log.info("Connecting to Flow Production Tracking...")
            sg = shotgun.create_sg_connection()
            sg_version = ".".join([str(x) for x in sg.server_info["version"]])
            log.debug("Connected to target PTR server! (v%s)" % sg_version)
        except Exception as e:
            raise TankError("Could not connect to PTR server: %s" % e)

        return sg


class SetupProjectWizard(object):
    """
    A class which wraps around the project setup functionality in toolkit.
    """

    def __init__(self, log, sg):
        """
        Constructor.
        """
        self._log = log
        self._sg = sg
        self._params = ProjectSetupParameters(self._log, self._sg)

    def set_progress_callback(self, cb):
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
        self._params.set_progress_callback(cb)

    def set_project(self, project_id, force=False):
        """
        Specify which project that should be set up.

        :param project_id: Shotgun id for the project that should be set up.
        :param force: Allow for the setting up of existing projects.
        """
        self._params.set_project_id(project_id, force)

    def set_use_centralized_mode(self):
        """
        Specifies that the setup should creat a centralized config
        """
        self._params.set_distribution_mode(ProjectSetupParameters.CENTRALIZED_CONFIG)

    def set_use_distributed_mode(self):
        """
        Specifies that the setup should create a distributed config.
        """
        self._params.set_distribution_mode(ProjectSetupParameters.DISTRIBUTED_CONFIG)

    def validate_config_uri(self, config_uri):
        r"""
        Validates a configuration template to check if it is compatible with the current Shotgun setup.
        This will download the configuration, validate it to ensure that it is compatible with the
        constraints (versions of core and shotgun) of this system.

        If locating, downloading, or validating the configuration fails, exceptions will be raised.

        Once the configuration exists and is compatible, the storage situation is reviewed against shotgun.
        A dictionary with a breakdown of all storages required by the configuration is returned:

        {
          "primary" : { "description": "This is where work files and scene publishes are located.",
                        "exists_on_disk": False,
                        "defined_in_shotgun": True,
                        "shotgun_id": 12,
                        "darwin": "/mnt/data",
                        "win32": "z:\mnt\data",
                        "linux2": "/mnt/data"},

          "textures" : { "description": "All texture are located on this storage",
                         "exists_on_disk": False,
                         "defined_in_shotgun": False,
                         "shotgun_id": None,
                         "darwin": None,
                         "win32": None,
                         "linux2": None}

          "renders" : { "description": None,
                        "exists_on_disk": False,
                        "defined_in_shotgun": True,
                        "darwin": None,
                        "win32": "z:\mnt\renders",
                        "linux2": "/mnt/renders"}
        }

        The main dictionary is keyed by storage name. It will contain one entry
        for each local storage which is required by the configuration template.
        Each sub-dictionary in turn contains the following items:

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

        :param config_uri: Configuration uri representing the location of a config
        :returns: dictionary with storage data, see above.
        """
        return self._params.validate_config_uri(config_uri)

    def set_config_uri(self, config_uri):
        """
        Validate and set a configuration uri to use with this setup wizard.

        In order to proceed with further functions, such as setting a project name,
        the config uri needs to be set.

        Exceptions will be raise if the configuration is not valid.
        Use the validate_config_uri() to check.

        :param config_uri: string describing a path on disk, a github uri or the name of an app store config.
        """
        self._params.set_config_uri(config_uri)

    def update_storage_root(self, config_uri, root_name, storage_data):
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

        :param config_uri: A config uri
        :param root_name: The name of a root to update.
        :param storage_data: A dctionary
        :return:
        """
        self._params.update_storage_root(config_uri, root_name, storage_data)

    def get_config_metadata(self):
        """
        Returns a metadata dictionary for the config that has been associated with the wizard.
        Returns a dictionary with information. Currently returns the following keys:

        - display_name: The display name for the configuration, e.g. 'Default Config'
        - description: A short description of the configuraiton.
        - readme: readme content associated with the config, in the form of list of strings.
                  if no readme exists, an empty list is returned.

        :returns: dictionary with display_name, readme and description keys
        """
        d = {}
        d["display_name"] = self._params.get_configuration_display_name()
        d["description"] = self._params.get_configuration_description()
        d["readme"] = self._params.get_configuration_readme()
        return d

    def get_default_project_disk_name(self):
        """
        Returns a default project name from toolkit.

        Before you call this method, a config and a project must have been set.

        This will execute hooks etc and given the selected project id will
        return a suggested project name.

        :returns: string with a suggested project name
        """
        return self._params.get_default_project_disk_name()

    def validate_project_disk_name(self, project_disk_name):
        """
        Validate the project disk name.
        Raises Exceptions if the project disk name is not valid.

        :param project_disk_name: string with a project name.
        """
        self._params.validate_project_disk_name(project_disk_name)

    def preview_project_paths(self, project_disk_name):
        r"""
        Return preview project paths given a project name.

        { "primary": { "darwin": "/foo/bar/project_name",
                       "linux2": "/foo/bar/project_name",
                       "win32" : "c:\foo\bar\project_name"},
          "textures": { "darwin": "/textures/project_name",
                        "linux2": "/textures/project_name",
                        "win32" : "c:\textures\project_name"}}

        The operating systems are enumerated using sys.platform jargon.
        If a path doesn't have a valid storage path defined in Shotgun,
        it will be returned as None. If the project name is not valid,
        None values will be returned for all paths.

        It is recommended that you execute validate_project_disk_name()
        to check the validity of the project name prior to executing this
        method.

        :param project_disk_name: string with a project name.
        :returns: Dictionary, see above.
        """
        return_data = {}
        for s in self._params.get_required_storages():
            return_data[s] = {}
            return_data[s]["darwin"] = self._params.preview_project_path(
                s, project_disk_name, "darwin"
            )
            return_data[s]["win32"] = self._params.preview_project_path(
                s, project_disk_name, "win32"
            )
            return_data[s]["linux2"] = self._params.preview_project_path(
                s, project_disk_name, "linux2"
            )

        return return_data

    def set_project_disk_name(self, project_disk_name, create_folders=True):
        """
        Set the desired name of the project. May raise exception if the name is not valid.
        By default, this method also attempts to ensure that folders exists for all
        storages associated with this configuration and project name.

        It is recommended that you execute validate_project_disk_name()
        to check the validity of the project name prior to executing this
        method.

        :param project_disk_name: string with a project name
        :param create_folders: if set to true, the wizard will attempt to create project root folders
                               if these don't already exist.
        """

        # by default, the wizard will also try to help out with the creation of
        # the project root folder if it doesn't already exist!
        if create_folders:

            # make sure name is valid before starting to create directories...
            self._params.validate_project_disk_name(project_disk_name)
            self._log.debug("Will try to create project folders on disk...")
            for s in self._params.get_required_storages():

                # get the full path
                proj_path = self._params.preview_project_path(
                    s, project_disk_name, sgsix.platform
                )

                if not os.path.exists(proj_path):
                    self._log.info("Creating project folder '%s'..." % proj_path)
                    old_umask = os.umask(0)
                    try:
                        os.makedirs(proj_path, 0o777)
                    finally:
                        os.umask(old_umask)
                    self._log.debug("...done!")

                else:
                    self._log.debug(
                        "Storage '%s' - project folder '%s' - already exists!"
                        % (s, proj_path)
                    )

        # lastly, register the name in shotgun
        self._params.set_project_disk_name(project_disk_name)

    def get_default_configuration_location(self):
        r"""
        Returns default suggested install location for configurations.
        Returns a dictionary with sys.platform style keys linux2/win32/darwin, e.g.

        { "darwin": "/foo/bar/project_name",
          "linux2": None,
          "win32" : "c:\foo\bar\project_name"}

        :returns: dictionary with paths or None
        """
        # the logic here is as follows:
        # 1. if the config comes from an existing project, base the config location on this
        # 2. if not, find the most recent primary pipeline config and base location on this
        # 3. failing that (meaning no projects have been set up ever) return None

        # now check the shotgun data
        new_proj_disk_name = self._params.get_project_disk_name()  # e.g. 'foo/bar_baz'
        new_proj_disk_name_win = new_proj_disk_name.replace(
            "/", "\\"
        )  # e.g. 'foo\bar_baz'

        data = self._params.get_configuration_shotgun_info()

        if not data:
            # we are not based on an existing project. Instead pick the last primary config
            # that is using storages (e.g. has got tank_name set)
            data = self._sg.find_one(
                "PipelineConfiguration",
                [
                    ["code", "is", "primary"],
                    ["project.Project.tank_name", "is_not", ""],
                ],
                [
                    "id",
                    "mac_path",
                    "windows_path",
                    "linux_path",
                    "project",
                    "project.Project.tank_name",
                ],
                [{"field_name": "created_at", "direction": "desc"}],
            )

        if not data:
            # there are no primary configurations registered. This means that we are setting up
            # our very first project and cannot really suggest any config locations
            self._log.debug(
                "No configs available to generate preview config values. Returning None."
            )
            suggested_defaults = {"darwin": None, "linux2": None, "win32": None}

        elif data["project.Project.tank_name"] is None:
            # the project we are basing this setup on did not use storages
            suggested_defaults = {"darwin": None, "linux2": None, "win32": None}

        else:
            # now take the pipeline config paths, and try to replace the current project name
            # in these paths by the new project name
            self._log.debug(
                "Basing config values on the following PTR pipeline config: %s" % data
            )

            # get the project path for this project
            old_project_disk_name = data[
                "project.Project.tank_name"
            ]  # e.g. 'foo/bar_baz'
            old_project_disk_name_win = old_project_disk_name.replace(
                "/", "\\"
            )  # e.g. 'foo\bar_baz'

            # now replace the project path in the pipeline configuration
            suggested_defaults = {"darwin": None, "linux2": None, "win32": None}

            # go through each pipeline config path, try to find the project disk name as part of this
            # path. if that exists, replace with the new project disk name
            # here's the logic:
            #
            # project name:     'my_proj'
            # new project name: 'new_proj'
            #
            # pipeline config: /mnt/configs/my_proj/configz -> /mnt/configs/new_proj/configz
            #
            # if the project name isn't found as part of the config path, none is returned
            #
            # pipeline config: /mnt/configs/myproj/configz -> None
            #
            if data["mac_path"] and old_project_disk_name in data["mac_path"]:
                suggested_defaults["darwin"] = data["mac_path"].replace(
                    old_project_disk_name, new_proj_disk_name
                )

            if data["linux_path"] and old_project_disk_name in data["linux_path"]:
                suggested_defaults["linux2"] = data["linux_path"].replace(
                    old_project_disk_name, new_proj_disk_name
                )

            if (
                data["windows_path"]
                and old_project_disk_name_win in data["windows_path"]
            ):
                suggested_defaults["win32"] = data["windows_path"].replace(
                    old_project_disk_name_win, new_proj_disk_name_win
                )

        return suggested_defaults

    def validate_configuration_location(self, linux_path, windows_path, macosx_path):
        """
        Validates a potential location for the pipeline configuration.
        Raises exceptions in case the validation fails.

        :param linux_path: Path on linux
        :param windows_path: Path on windows
        :param macosx_path: Path on mac
        """
        self._params.validate_configuration_location(
            linux_path, windows_path, macosx_path
        )

    def set_configuration_location(self, linux_path, windows_path, macosx_path):
        """
        Specifies where the pipeline configuration should be located.

        :param linux_path: Path on linux
        :param windows_path: Path on windows
        :param macosx_path: Path on mac
        """
        self._params.set_configuration_location(linux_path, windows_path, macosx_path)

    def get_core_settings(self):
        """
        Calculates core API associations for the new project.

        Returns a data structure on the following form:

        { "localize": True,
          "using_runtime": False,
          "core_path: { "linux2": "/path/to/core",
                        "darwin": "/path/to/core",
                        "win32": None }
          "pipeline_config": { "type": "PipelineConfiguration",
                               "id": 12,
                               "code": "primary",
                               "project": {"id": 123, "type": "Project", "name": "big buck bunny"},
                               "project.Project.tank_name": "big_buck_bunny"
                               }
        }

        Below is a summary of the various return parameters:

        localize - If set to True, the localize boolean indicates that the core API will be 'baked in' to the
                   project configuration to form an autonomous (localized) setup which doesn't depend on
                   any other locations on disk. In this case, the core_path data represents the location from
                   where the core API will be obtained. In this case, the only path in the core_path which
                   is relevant  will be the one that corresponds to the current operating system.

        using_runtime - If set to true, this indicates that the core used for the setup will be picked up
                        from the currently executing core API.

        pipeline_config - If the core is picked up from an existing pipeline configuration in Shotgun, this
                          parameter will hold a dictionary with various shotgun values representing the
                          pipeline configuration and its associated project. If the core used to create the project
                          is not associated with an existing pipeline configuration, None is returned.

        core_path - If localize is set to False, the configuration will share an API and it will be picked up
                    from the location indicated in the core_path parameter. In this case, a None value for a path
                    indicates that this platform will not be supported and the project will not be able to execute
                    on that platform unless further configuration adjustments are carried out.

        :returns: dictionary, see above for details.
        """

        # first, work out which version of the core we should be associate the new project with.
        # this logic follows a similar pattern to the default config generation.
        #
        # If the config template is a project in shotgun, use its core.
        # If this core is localized, then localize this project too
        #
        # Otherwise, fall back on the currently executing core API. Always localize in this case.

        # the defaults is to localize and pick up current core API
        curr_core_path = pipelineconfig_utils.get_path_to_current_core()

        try:
            core_path_object = pipelineconfig_utils.resolve_all_os_paths_to_core(
                curr_core_path
            )
        except TankError:
            self._log.debug(
                "Unable to resolve all OS paths for the current tk-core path. Forging ahead with "
                "only the current OS's core location."
            )

            # We really only the current OS path to continue with the project setup
            # anyway, so we'll fall back on that if we're in a situation where the
            # config doesn't contain an install_locations.yml file, which is the
            # most likely situation we'd be in here. That's an intentional omission
            # from baked configurations, as an example, and we don't want to stop
            # project setups if the process is being run from an environment running
            # from a baked config.
            if is_linux():
                path_args = [None, os.path.expandvars(curr_core_path), None]
            elif is_macos():
                path_args = [None, None, os.path.expandvars(curr_core_path)]
            elif is_windows():
                path_args = [os.path.expandvars(curr_core_path), None, None]
            else:
                msg = "Unsupported OS detected: %s" % sgsix.platform
                raise TankError(msg)

            core_path_object = ShotgunPath(*path_args).as_system_dict()

        return_data = {
            "localize": True,
            "using_runtime": True,
            "core_path": core_path_object,
            "pipeline_config": None,
        }

        # first try to get shotgun pipeline config data from the config template
        data = self._params.get_configuration_shotgun_info()

        if data:
            self._log.debug(
                "Will try to inherit core from the config template: %s" % data
            )

            # get the right path field from the config
            pipeline_config_root_path = data[ShotgunPath.get_shotgun_storage_key()]

            if pipeline_config_root_path and os.path.exists(pipeline_config_root_path):
                # looks like this exists - try to resolve its core API location

                core_api_root = pipelineconfig_utils.get_core_path_for_config(
                    pipeline_config_root_path
                )

                if core_api_root:
                    # core api resolved correctly. Let's try to base our core on this config.
                    self._log.debug(
                        "Will use pipeline configuration here: %s"
                        % pipeline_config_root_path
                    )
                    self._log.debug(
                        "This has an associated core here: %s" % core_api_root
                    )
                    return_data["using_runtime"] = False
                    return_data["pipeline_config"] = data
                    return_data[
                        "core_path"
                    ] = pipelineconfig_utils.resolve_all_os_paths_to_core(core_api_root)

                    # finally, check the logic for localization:
                    # if this core that we have found and resolved is localized,
                    # we localize the new project as well.
                    if pipelineconfig_utils.is_localized(pipeline_config_root_path):
                        return_data["localize"] = True
                    else:
                        return_data["localize"] = False
                else:
                    self._log.warning(
                        "Cannot locate the Core API associated with the configuration in '%s'. "
                        "As a fallback, the currently executing Toolkit Core API will "
                        "be used." % pipeline_config_root_path
                    )

            else:
                self._log.warning(
                    "You are basing your new project on an existing configuration ('%s'), however "
                    "the configuration does not exist on disk. As a fallback, the currently executing "
                    "Toolkit Core API will be used." % pipeline_config_root_path
                )

        return return_data

    def pre_setup_validation(self):
        """
        Performs basic validation checks on all the specified data together.
        This method should be executed prior to running the setup projet logic to ensure
        that the process will succeed.
        """
        self._params.pre_setup_validation()

    def set_default_core(self):
        """
        Sets the desired core API to use. These values should be present for
        pre_setup_validation.

        If a core has been provided by core_api.yml in the configuration, this
        will take precedence.
        """
        # get core logic
        core_settings = self.get_core_settings()

        # ok - we are good to go! Set the core to use
        self._params.set_associated_core_path(
            core_settings["core_path"]["linux2"],
            core_settings["core_path"]["win32"],
            core_settings["core_path"]["darwin"],
        )

    def _get_server_version(self, connection):
        """
        Retrieves the server version from the connection.

        :param connection: Connection we want the server version from.

        :returns: Tuple of (major, minor) versions.
        """
        sg_major_ver = connection.server_info["version"][0]
        sg_minor_ver = connection.server_info["version"][1]
        sg_patch_ver = connection.server_info["version"][2]

        return StrictVersion("%d.%d.%d" % (sg_major_ver, sg_minor_ver, sg_patch_ver))

    def _is_session_based_authentication_supported(self):
        """
        Returns if a site needs to be configured with a script user or if the new
        human user based authentication for Toolkit will work with it.

        :returns: If the site is not compatible with the new authentication code,
            returns True, False otherwise.
        """
        # First version to support human based authentication for all operations was
        # 6.0.2.
        if self._get_server_version(self._sg) >= StrictVersion("6.0.2"):
            return True
        else:
            return False

    def execute(self):
        """
        Execute the actual setup process.
        """
        self._log.debug("Start preparing for project setup!")

        # get core logic
        core_settings = self.get_core_settings()
        self.set_default_core()

        # Do validation
        self.pre_setup_validation()

        # and finally carry out the setup
        run_project_setup(self._log, self._sg, self._params)

        if (
            self._params.get_distribution_mode()
            == ProjectSetupParameters.CENTRALIZED_CONFIG
        ):

            # ---- check if we should run the localization afterwards

            # note - when running via the wizard, toolkit script credentials are
            # stripped out as the core is copied across as part of a localization if
            # the site we are configuring supports the authentication module, ie,
            # Shotgun 6.0.2 and greater.

            # this is primarily targeting the PTR desktop app, meaning that even if
            # the PTR desktop app's site configuration contains script credentials,
            # these are not propagated into newly created toolkit projects.

            config_path = self._params.get_configuration_location(sgsix.platform)

            # if the new project's config has a core descriptor, then we should
            # localize it to use that version of core. alternatively, if the current
            # core being used is localized (as returned via `get_core_settings`),
            # then localize the new core with it.
            if (
                pipelineconfig_utils.has_core_descriptor(config_path)
                or core_settings["localize"]
            ):
                core_localize.do_localize(
                    self._log,
                    self._sg,
                    config_path,
                    YesToEverythingInteraction(),  # don't prompt
                )
