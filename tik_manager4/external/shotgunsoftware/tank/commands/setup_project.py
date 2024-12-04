# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from __future__ import print_function

import os
import textwrap
import traceback

from .action_base import Action
from . import core_localize
from ..errors import TankError
from ..util import shotgun
from ..util import ShotgunPath
from ..util import is_linux, is_macos, is_windows
from . import constants
from .. import pipelineconfig_utils
from ..util.filesystem import ensure_folder_exists

from .setup_project_core import run_project_setup
from .setup_project_params import ProjectSetupParameters
from .interaction import YesToEverythingInteraction
from tank_vendor.shotgun_api3.lib import sgsix
from tank_vendor.six.moves import input


class SetupProjectAction(Action):
    """
    Action that sets up a new Toolkit Project.

    This is the standard command that is exposed via the setup_project tank command
    and API equivalent.
    """

    def __init__(self):
        """
        Constructor
        """
        Action.__init__(
            self,
            "setup_project",
            Action.GLOBAL,
            "Sets up a new project with the Flow Production Tracking Toolkit.",
            "Configuration",
        )

        # this method can be executed via the API
        self.supports_api = True

        self.parameters = {}

        self.parameters["check_storage_path_exists"] = {
            "description": (
                "Check that the path to the storage exists. "
                "this is enabled by default but can be turned "
                "off in order to deal with certain expert "
                "level use cases relating to UNC paths. for "
                "example, if your storage is set to be "
                "'\\\\PROJECTS', this location cannot be "
                "validated to exist and this option needs to "
                "be used."
            ),
            "default": True,
            "type": "bool",
        }

        self.parameters["force"] = {
            "description": (
                "Enabling this flag allows you to run the set up project on "
                "projects which have already been previously set up. "
            ),
            "default": False,
            "type": "bool",
        }

        self.parameters["project_id"] = {
            "description": "PTR id for the project you want to set up.",
            "default": None,
            "type": "int",
        }

        self.parameters["project_folder_name"] = {
            "description": (
                "Name of the folder which you want to be the root "
                "point of the created project. If a project already "
                "exists, this parameter must reflect the name of the "
                "top level folder of the project."
            ),
            "default": None,
            "type": "str",
        }

        self.parameters["config_uri"] = {
            "description": "The configuration to use when setting up this "
            "project. This can be a path on disk to a directory containing "
            "a config, a path to a git bare repo (e.g. a git repo path "
            "which ends with .git) or '%s' to fetch the default config "
            "from the toolkit app store." % (constants.DEFAULT_CFG,),
            "default": constants.DEFAULT_CFG,
            "type": "str",
        }

        self.parameters["install_mode"] = {
            "description": "The type of installation to perform. Either 'centralized' or 'distributed'",
            "default": "centralized",
            "type": "str",
        }

        # note how the current platform's default value is None in order to make that required
        self.parameters["config_path_mac"] = {
            "description": (
                "The path on disk where the configuration should be "
                "installed on Macosx."
            ),
            "default": (None if is_macos() else ""),
            "type": "str",
        }

        self.parameters["config_path_win"] = {
            "description": (
                "The path on disk where the configuration should be "
                "installed on Windows."
            ),
            "default": (None if is_windows() else ""),
            "type": "str",
        }

        self.parameters["config_path_linux"] = {
            "description": (
                "The path on disk where the configuration should be "
                "installed on Linux."
            ),
            "default": (None if is_linux() else ""),
            "type": "str",
        }

        # Special setting used by older versions of the PTR desktop app
        # to handle auto-installing the site configuration at startup.
        self.parameters["auto_path"] = {
            "description": "Deprecated. Do not use this! --- "
            "Expert setting. Setting this to true means that a blank "
            "path entry is written to the PTR site pipeline "
            "configuration. This can be used in conjunction with "
            "a localized core to create a site configuration which "
            "can have different locations on different machines. It "
            "is then up to the bootstrap logic of the code that "
            "starts up toolkit to determine where to go look for the "
            "configuration. When setting this to true, you typically "
            "only need to specify the path to the current operating "
            "system configuration.",
            "default": False,
            "type": "bool",
        }

    def run_noninteractive(self, log, parameters):
        """
        Tank command API accessor.
        Called when someone runs a tank command through the core API.

        :param log: std python logger
        :param parameters: dictionary with tank command parameters
        """
        # validate params and seed default values
        computed_params = self._validate_parameters(parameters)

        # connect to shotgun
        sg = self._shotgun_connect(log)

        # create a parameters class
        params = ProjectSetupParameters(log, sg)

        # tell it which core to pick up. For the tank command, we just base it off the
        # currently running API
        curr_core_path = pipelineconfig_utils.get_path_to_current_core()
        core_roots = pipelineconfig_utils.resolve_all_os_paths_to_core(curr_core_path)
        params.set_associated_core_path(
            core_roots["linux2"], core_roots["win32"], core_roots["darwin"]
        )

        # specify which config to use
        params.set_config_uri(
            computed_params["config_uri"], computed_params["check_storage_path_exists"]
        )

        # set expert auto path setting
        params.set_auto_path_mode(computed_params["auto_path"])

        # set mode
        if computed_params["install_mode"] == "centralized":
            params.set_distribution_mode(ProjectSetupParameters.CENTRALIZED_CONFIG)
        elif computed_params["install_mode"] == "distributed":
            params.set_distribution_mode(ProjectSetupParameters.DISTRIBUTED_CONFIG)
        else:
            raise ValueError("Invalid install_mode parameter specified.")

        # set the project
        params.set_project_id(computed_params["project_id"], computed_params["force"])
        params.set_project_disk_name(computed_params["project_folder_name"])

        # set the config path
        if params.get_distribution_mode() == ProjectSetupParameters.CENTRALIZED_CONFIG:
            # specify paths
            params.set_configuration_location(
                computed_params["config_path_linux"],
                computed_params["config_path_win"],
                computed_params["config_path_mac"],
            )

        # run overall validation of the project setup
        params.pre_setup_validation()

        # and finally carry out the setup
        run_project_setup(log, sg, params)

        if params.get_distribution_mode() == ProjectSetupParameters.CENTRALIZED_CONFIG:

            config_path = params.get_configuration_location(sgsix.platform)

            # if the new project's config has a core descriptor, then we should
            # localize it to use that version of core. alternatively, if the current
            # core being used is localized, then localize the new config with it.
            if pipelineconfig_utils.has_core_descriptor(
                config_path
            ) or pipelineconfig_utils.is_localized(curr_core_path):

                log.info("Localizing Core...")
                core_localize.do_localize(
                    log,
                    self._shotgun_connect(log),
                    config_path,
                    YesToEverythingInteraction(),  # don't prompt
                )

    def run_interactive(self, log, args):
        """
        Tank command accessor

        :param log: std python logger
        :param args: command line args
        """

        if len(args) not in [0, 1]:
            raise TankError("Syntax: setup_project [--no-storage-check] [--force]")

        check_storage_path_exists = True
        force = False

        if len(args) == 1 and args[0] == "--no-storage-check":
            check_storage_path_exists = False
            log.info(
                "no-storage-check mode: Will not verify that the storage exists. This "
                "can be useful if the storage is pointing directly at a server via a "
                "Windows UNC mapping."
            )

        if len(args) == 1 and args[0] == "--force":
            force = True
            log.info(
                "force mode: Projects already set up with Toolkit can be set up again."
            )

        elif len(args) == 1 and args[0] not in ["--no-storage-check", "--force"]:
            raise TankError("Syntax: setup_project [--no-storage-check] [--force]")
            check_storage_path_exists = False

        # connect to shotgun
        sg = self._shotgun_connect(log)

        # create a parameters class
        params = ProjectSetupParameters(log, sg)

        # tell it which core to pick up. For the tank command, we just base it off the
        # currently running API
        curr_core_path = pipelineconfig_utils.get_path_to_current_core()
        core_roots = pipelineconfig_utils.resolve_all_os_paths_to_core(curr_core_path)
        params.set_associated_core_path(
            core_roots["linux2"], core_roots["win32"], core_roots["darwin"]
        )

        # now ask which config to use. Download if necessary and examine
        config_uri = self._select_template_configuration(log, sg)

        # allow the user to map storages required by the configuration
        self._map_storages(params, config_uri, log, sg)

        # now try to load the config
        params.set_config_uri(config_uri, check_storage_path_exists)

        # ask which project to operate on
        project_id = self._select_project(log, sg, force)
        params.set_project_id(project_id, force)

        # ask the user to confirm the folder name
        self._get_project_folder_name(log, sg, params)

        # now ask the user where the config should go
        self._get_disk_location(log, params)

        # run overall validation of the project setup
        params.pre_setup_validation()

        # print overview
        self._emit_project_setup_summary(log, params)

        # check if user wants to continue
        if not self._confirm_continue(log):
            raise TankError("Installation Aborted.")

        # and finally carry out the setup
        run_project_setup(log, sg, params)

        config_path = params.get_configuration_location(sgsix.platform)

        # if the new project's config has a core descriptor, then we should
        # localize it to use that version of core. alternatively, if the current
        # core being used is localized, then localize the new core with it.
        if pipelineconfig_utils.has_core_descriptor(
            config_path
        ) or pipelineconfig_utils.is_localized(curr_core_path):

            log.info("Localizing Core...")
            core_localize.do_localize(
                log,
                self._shotgun_connect(log),
                config_path,
                YesToEverythingInteraction(),  # don't prompt
            )

        # display readme etc.
        readme_content = params.get_configuration_readme()
        if len(readme_content) > 0:
            log.info("")
            log.info("README file for template:")
            for line in readme_content:
                print(line)

        log.info("")
        log.info("We recommend that you now run 'tank updates' to get the latest")
        log.info("versions of all apps and engines for this project.")
        log.info("")
        log.info(
            "For more Apps, Support, Documentation and the Toolkit Community, go to"
        )
        log.info("https://developer.shotgridsoftware.com")
        log.info("")

    def _shotgun_connect(self, log):
        """
        Connects to Shotgun.

        :returns: Shotgun API Instance.
        :raises: TankError on failure.
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

    def _confirm_continue(self, log):
        """
        Called when the logic needs an interactive session to issue a "ok to continue" prompt

        :returns: true or false
        """
        evaluated_value = None
        while evaluated_value is None:
            val = input("Continue with project setup (Yes/No)? [Yes]: ")
            if val == "" or val.lower().startswith("y"):
                evaluated_value = True
            elif val.lower().startswith("n"):
                evaluated_value = False
            else:
                log.error("Please answer Yes, y, no, n or press ENTER for yes!")

        return evaluated_value

    def _select_template_configuration(self, log, sg):
        """
        Ask the user which config to use. Returns a config uri string.

        :param log: python logger
        :param sg: Shotgun API instance

        :returns: config uri string
        """
        log.info("")
        log.info("")
        log.info("------------------------------------------------------------------")
        log.info("Which configuration would you like to associate with this project?")

        primary_pcs = sg.find(
            constants.PIPELINE_CONFIGURATION_ENTITY,
            [["code", "is", constants.PRIMARY_PIPELINE_CONFIG_NAME]],
            ["code", "project", "mac_path", "windows_path", "linux_path"],
        )

        if len(primary_pcs) > 0:
            log.info("")
            log.info(
                "You can use the configuration from an existing project as a "
                "template for this new project. All settings, apps and folder "
                "configuration settings will be copied over to your new project. "
                "The following configurations were found: "
            )
            log.info("")
            for ppc in primary_pcs:
                # As of 6.0.2, pipeline configurations can be project less, so skip those
                if ppc.get("project") is None:
                    continue

                pc_path = ppc.get(ShotgunPath.get_shotgun_storage_key())
                if pc_path is None or pc_path == "":
                    # this Toolkit config does not exist on a disk that is reachable from this os
                    log.info(
                        "   %s: No valid config found for this OS!"
                        % ppc.get("project").get("name")
                    )
                else:
                    config_path = os.path.join(pc_path, "config")
                    log.info(
                        "   %s: '%s'" % (ppc.get("project").get("name"), config_path)
                    )

            log.info("")
            log.info(
                "If you want to use any of the configs listed about for your new project, "
                "just type in its path when prompted below."
            )

        log.info("")
        log.info(
            "You can use the Default Configuration for your new project.  "
            "The default configuration is a good sample config, demonstrating "
            "a typical basic setup of the Flow Production Tracking Toolkit using the "
            "latest apps and engines. This will be used by default if you just "
            "hit enter below."
        )
        log.info("")
        log.info(
            "If you have a configuration stored somewhere on disk, you can "
            "enter the path to this config and it will be used for the "
            "new project."
        )
        log.info("")
        log.info(
            "You can also enter an url pointing to a git repository. Toolkit will then "
            "clone this repository and base the config on its content."
        )
        log.info("")

        config_name = input("[%s]: " % constants.DEFAULT_CFG).strip()
        if config_name == "":
            config_name = constants.DEFAULT_CFG
        return config_name

    def _select_project(self, log, sg, show_initialized_projects):
        """
        Returns the project id and name for a project for which setup should be done.
        Will request the user to input console input to select project.

        :param log: python logger
        :param sg: Shotgun API instance
        :param show_initialized_projects: Should alrady initialized projects be displayed in the listing?

        :returns: project_id
        """

        filters = [
            ["name", "is_not", "Template Project"],
            ["sg_status", "is_not", "Archive"],
            ["sg_status", "is_not", "Lost"],
            ["archived", "is_not", True],
        ]

        if show_initialized_projects == False:
            # not force mode. Only show non-set up projects
            filters.append(["tank_name", "is", None])

        projs = sg.find(
            "Project", filters, ["id", "name", "sg_description", "tank_name"]
        )

        if len(projs) == 0:
            raise TankError(
                "Sorry, no projects found! All projects seem to have already been "
                "set up with the Flow Production Tracking Toolkit. If you are an expert "
                "user and want to run the setup on a project which already has been "
                "set up, run the setup_project command with a --force option."
            )

        if show_initialized_projects:
            log.info("")
            log.info("")
            log.info(
                "Below are all active projects, including ones that have been set up:"
            )
            log.info(
                "--------------------------------------------------------------------"
            )
            log.info("")

        else:
            log.info("")
            log.info("")
            log.info(
                "Below are all projects that have not yet been set up with Toolkit:"
            )
            log.info(
                "-------------------------------------------------------------------"
            )
            log.info("")

        for x in projs:
            # helper that formats a single project
            desc = x.get("sg_description")
            if desc is None:
                desc = "[No description]"

            # chop a long description
            if len(desc) > 50:
                desc = "%s..." % desc[:50]

            log.info("[%2d] %s" % (x.get("id"), x.get("name")))
            if x.get("tank_name"):
                log.info("Note: This project has already been set up.")
            log.info("     %s" % desc)
            log.info("")

        log.info("")
        answer = input(
            "Please type in the id of the project to connect to or ENTER to exit: "
        )
        if answer == "":
            raise TankError("Aborted by user.")
        try:
            project_id = int(answer)
        except:
            raise TankError("Please enter a number!")

        if project_id not in [x["id"] for x in projs]:
            raise TankError("Id %d was not found in the list of projects!" % project_id)

        return project_id

    def _get_project_folder_name(self, log, sg, params):
        """
        Given a project entity in Shotgun (name, id), decide where the project data
        root should be on disk. This will verify that the selected folder exists
        in each of the storages required by the configuration. It will prompt the user
        and can create these root folders if required (with open permissions).

        :param log: python logger
        :param sg: Shotgun API instance
        :param params: ProjectSetupParameters instance which holds the project setup parameters.
        :returns: The project disk name which is selected, this name may
                  include slashes if the selected location is multi-directory.
        """

        suggested_folder_name = params.get_default_project_disk_name()

        log.info("")
        log.info("")
        log.info("")
        log.info(
            "Now you need to tell Toolkit where you are storing the data for this project."
        )
        log.info(
            "The selected Toolkit config utilizes the following Local Storages, as "
        )
        log.info("defined in the PTR Site Preferences:")
        log.info("")
        for storage_name in params.get_required_storages():
            current_os_path = params.get_storage_path(storage_name, sgsix.platform)
            log.info(" - %s: '%s'" % (storage_name, current_os_path))

        # first, display a preview
        log.info("")
        log.info("Each of the above locations need to have a data folder which is ")
        log.info(
            "specific to this project. These folders all need to be named the same thing."
        )
        log.info("They also need to exist on disk.")
        log.info("For example, if you named the project '%s', " % suggested_folder_name)
        log.info("the following folders would need to exist on disk:")
        log.info("")
        for storage_name in params.get_required_storages():
            proj_path = params.preview_project_path(
                storage_name, suggested_folder_name, sgsix.platform
            )
            log.info(" - %s: %s" % (storage_name, proj_path))

        log.info("")

        # now ask for a value and validate
        while True:
            log.info("")
            proj_name = input(
                "Please enter a folder name [%s]: " % suggested_folder_name
            ).strip()
            if proj_name == "":
                proj_name = suggested_folder_name

            # validate the project name
            try:
                params.validate_project_disk_name(proj_name)
            except TankError as e:
                # bad project name!
                log.error("Invalid project name: %s" % e)
                # back to beginning
                continue

            log.info("...that corresponds to the following data locations:")
            log.info("")
            storages_valid = True
            for storage_name in params.get_required_storages():

                proj_path = params.preview_project_path(
                    storage_name, proj_name, sgsix.platform
                )

                if os.path.exists(proj_path):
                    log.info(" - %s: %s [OK]" % (storage_name, proj_path))
                else:

                    # try to create the folders
                    try:

                        old_umask = os.umask(0)
                        try:
                            os.makedirs(proj_path, 0o777)
                        finally:
                            os.umask(old_umask)

                        log.info(" - %s: %s [Created]" % (storage_name, proj_path))
                        storages_valid = True
                    except Exception as e:
                        log.error(" - %s: %s [Not created]" % (storage_name, proj_path))
                        log.error("   Please create path manually.")
                        log.error("   Details: %s" % e)
                        storages_valid = False

            log.info("")

            if storages_valid:
                # looks like folders exist on disk

                val = input("Paths look valid. Continue? (Yes/No)? [Yes]: ")
                if val == "" or val.lower().startswith("y"):
                    break
            else:
                log.info(
                    "Please make sure that folders exist on disk for your project name!"
                )

        params.set_project_disk_name(proj_name)

    def _get_disk_location(self, log, params):
        """
        Ask the user where the pipeline configuration should be located on disk.

        :param log: python logger
        :param params: ProjectSetupParameters instance which holds the project setup parameters.
        """

        log.info("")
        log.info("")
        log.info(
            "Now it is time to decide where the configuration for this project should go. "
        )
        log.info("Typically, this is in a software install area where you keep ")
        log.info("all your Toolkit code and configuration. We will suggest defaults ")
        log.info("based on your current install.")

        log.info("")
        log.info("You can press ENTER to accept the default value or to skip.")

        default_config_locations = self._get_default_configuration_location(log, params)

        linux_path = self._ask_location(
            log, default_config_locations["linux2"], "Linux"
        )
        windows_path = self._ask_location(
            log, default_config_locations["win32"], "Windows"
        )
        macosx_path = self._ask_location(
            log, default_config_locations["darwin"], "Macosx"
        )

        params.set_configuration_location(linux_path, windows_path, macosx_path)

    def _get_default_configuration_location(self, log, params):
        r"""
        Returns default suggested location for configurations.
        Returns a dictionary with sys.platform style keys linux2/win32/darwin, e.g.

        { "darwin": "/foo/bar/project_name",
          "linux2": "/foo/bar/project_name",
          "win32" : "c:\foo\bar\project_name"}

        :param log: python logger
        :param params: project setup params object
        :returns: dictionary with paths
        """

        # figure out the config install location. There are three cases to deal with
        # - 0.13 style layout, where they all sit together in an install location
        # - 0.12 style layout, where there is a tank folder which is the studio location
        #   and each project has its own folder.
        # - installing off a localized core api, meaning that there is no obvious
        #   relationship between the config location and the core location

        location = {"darwin": None, "linux2": None, "win32": None}

        # Get the path to the storage we want to use when calculating the default
        # location for the installed config.
        # Multi-root configurations require a storage named "primary" so we base
        # our default on that. If only a single storage is available, we just use it.
        storage_names = params.get_required_storages()
        default_storage_name = params.default_storage_name

        # There is no default storage name for a config that doesn't use roots, like
        # tk-config-basic, so we should skip storage detection.
        if default_storage_name:
            primary_local_path = params.get_storage_path(
                default_storage_name, sgsix.platform
            )
        else:
            primary_local_path = None

        curr_core_path = pipelineconfig_utils.get_path_to_current_core()
        core_locations = pipelineconfig_utils.resolve_all_os_paths_to_core(
            curr_core_path
        )

        if pipelineconfig_utils.is_localized(curr_core_path):
            # the API we are using to run the setup from was localized. This means
            # that the API will not be shared between projects and with something
            # like the PTR desktop app workflow, the core API is installed in a
            # system location like %APPDATA% or ~/Library.
            # So we cannot use that as a default. In this case, simply don't provide
            # a default parameter.
            pass

        elif core_locations[sgsix.platform] is None:
            # edge case: the shared core location that we are trying to install from
            # is not set up to work with this operating system. In that case, skip
            # default generation
            pass

        elif (
            primary_local_path is not None
            and os.path.abspath(
                os.path.join(core_locations[sgsix.platform], "..")
            ).lower()
            == primary_local_path.lower()
        ):
            # ok the parent of the install root matches the primary storage - means OLD STYLE (pre core 0.12)
            #
            # in this setup, we would have the following structure:
            # /studio              <--- primary storage
            # /studio/tank         <--- core API install
            # /studio/project      <--- project data location
            # /studio/project/tank <--- toolkit configuation location

            if params.get_project_path(primary_storage_name, "darwin"):
                location["darwin"] = "%s/tank" % params.get_project_path(
                    primary_storage_name, "darwin"
                )

            if params.get_project_path(primary_storage_name, "linux2"):
                location["linux2"] = "%s/tank" % params.get_project_path(
                    primary_storage_name, "linux2"
                )

            if params.get_project_path(primary_storage_name, "win32"):
                location["win32"] = "%s\\tank" % params.get_project_path(
                    primary_storage_name, "win32"
                )

        else:
            # Core v0.12+ style setup - this is what is our default recommended setup
            # here, the project data is treated as a completely separate thing.
            #
            # typical new style setup (not showing project data locations)
            # /software/studio <-- core API install
            #
            # /software/proj_a  <-- project configuration
            # /software/proj_b  <-- project configuration
            # /software/proj_c  <-- project configuration
            #
            # In this case, we can determine the location of /software/studio by looking
            # at the location of the running code.
            # we then suggest a configuration relative to this

            # get the project name on disk - note that this may contain slashes
            project_name_chunks = params.get_project_disk_name().split(
                "/"
            )  # ['multi', 'tier', 'name']

            # note: linux_install_root.startswith("/") handles the case where the config file says "undefined"

            if core_locations["linux2"]:
                chunks = core_locations["linux2"].split(
                    "/"
                )  # e.g. /software/studio -> ['', 'software', 'studio']
                chunks.pop()  # pop the studio bit (e.g ['', 'software'])
                chunks.extend(project_name_chunks)  # append project name
                location["linux2"] = "/".join(chunks)

            if core_locations["darwin"]:
                chunks = core_locations["darwin"].split(
                    "/"
                )  # e.g. /software/studio -> ['', 'software', 'studio']
                chunks.pop()  # pop the studio bit (e.g ['', 'software'])
                chunks.extend(project_name_chunks)  # append project name
                location["darwin"] = "/".join(chunks)

            if core_locations["win32"]:
                # split path into chunks
                # e.g. c:\software\studio -> ['c:', 'software', 'studio']
                # e.g. \\myserver\mymount\software\studio -> ['', '', 'myserver', 'mymount', 'software', 'studio']
                chunks = core_locations["win32"].split("\\")
                chunks.pop()  # pop the studio bit
                chunks.extend(project_name_chunks)  # append project name
                location["win32"] = "\\".join(chunks)

        return location

    def _ask_location(self, log, default, os_nice_name):
        """
        Helper method - asks the user where to put a pipeline config.

        :param log: python logger
        :param default: default value
        :param os_nice_name: A display name for an operating system
        :returns: A path determined by the user
        """
        curr_val = default

        if curr_val is None:
            val = input("%s : " % os_nice_name)
            if val == "":
                log.info(
                    "Skipping. This Pipeline configuration will not support %s."
                    % os_nice_name
                )
            else:
                curr_val = val.strip()

        else:
            val = input("%s [%s]: " % (os_nice_name, curr_val))
            if val != "":
                curr_val = val.strip()
        return curr_val

    def _emit_project_setup_summary(self, log, params):
        """
        Emit project summary to the given logger

        :param log: python logger object
        :param params: Parameters object which holds gathered project settings
        """
        log.info("")
        log.info("")
        log.info("Project Creation Summary:")
        log.info("-------------------------")
        log.info("")
        log.info(
            "You are about to set up the Flow Production Tracking Toolkit "
            "for Project %s - %s "
            % (params.get_project_id(), params.get_project_disk_name())
        )
        log.info("The following items will be created:")
        log.info("")
        log.info("* A PTR Pipeline configuration will be created:")
        log.info("  - on Macosx:  '%s'" % params.get_configuration_location("darwin"))
        log.info("  - on Linux:   '%s'" % params.get_configuration_location("linux2"))
        log.info("  - on Windows: '%s'" % params.get_configuration_location("win32"))
        log.info("")
        log.info("* The Pipeline configuration will use the following Core API:")
        log.info("  - on Macosx:  '%s'" % params.get_associated_core_path("darwin"))
        log.info("  - on Linux:   '%s'" % params.get_associated_core_path("linux2"))
        log.info("  - on Windows: '%s'" % params.get_associated_core_path("win32"))
        log.info("")
        log.info("NOTE: If the installed configuration contains a ")
        log.info("      core_api.yml file, the version of core specified in ")
        log.info("      that file will be localized after project setup is ")
        log.info("      complete.")
        log.info("")

    def _map_storages(self, params, config_uri, log, sg):
        """
        Present the user with information about the storage roots defined by
        the configuration. Allows them to map a root to an existing local
        storage in PTR.

        :param params: Project setup params instance
        :param config_uri: A config uri
        :param log: python logger object
        :param sg: Shotgun API instance
        """

        # query all storages that exist in PTR
        storages = sg.find(
            "LocalStorage",
            filters=[],
            fields=["code", "id", "linux_path", "mac_path", "windows_path"],
            order=[{"field_name": "code", "direction": "asc"}],
        )

        # build lookups by name and id
        storage_by_id = {}
        storage_by_name = {}
        for storage in storages:
            # store lower case names so we can do case insensitive comparisons
            storage_name = storage["code"].lower()
            storage_id = storage["id"]
            storage_by_id[storage_id] = storage
            storage_by_name[storage_name] = storage

        # present a summary of storages that exist in PTR
        log.info("")
        log.info("The following local storages exist in Flow Production Tracking:")
        log.info("")
        for storage in sorted(storages, key=lambda s: s["code"]):
            self._print_storage_info(storage, log)

        # get all roots required by the supplied config uri
        required_roots = params.validate_config_uri(config_uri)
        log.info(
            "This configuration requires %s storage root(s)." % len(required_roots)
        )
        log.info("")
        log.info("For each storage root, enter the name of the local storage ")
        log.info("above you wish to use.")
        log.info("")

        # a list of tuples we'll use to map a root name to a storage name
        mapped_roots = []

        # loop over required storage roots
        for (root_name, root_info) in required_roots.items():

            log.info("%s" % (root_name,))
            log.info("-" * len(root_name))

            # format the description so that it wraps nicely
            description = root_info.get("description")

            if description:
                wrapped_desc_lines = textwrap.wrap(description)
                for line in wrapped_desc_lines:
                    log.info("  %s" % (line,))
            log.info("")

            # make a best guess as to which storage to use
            suggested_storage = None

            # see if a shotgun storage id is defined in the root info.
            root_sg_id = root_info.get("shotgun_id")
            if root_sg_id in storage_by_id:
                storage_name = storage_by_id[root_sg_id]["code"]
                # shotgun id defined explicitly for this root
                log.info(
                    "Press ENTER to use the explicit mapping to the '%s' "
                    "storage as defined in the configuration." % (storage_name,)
                )
                log.info("")
                suggested_storage = storage_name

            # does name match an existing storage?
            elif root_name.lower() in storage_by_name:
                log.info(
                    "Press ENTER to use the storage wth the same name as the " "root."
                )
                log.info("")
                # get the actual name by indexing into the storage dict
                suggested_storage = storage_by_name[root_name.lower()]["code"]

            if suggested_storage:
                suggested_storage_display = " [%s]: " % (suggested_storage,)
            else:
                suggested_storage_display = ": "

            # ask the user which storage to associate with this root
            storage_to_use = input(
                "Which local storage would you like to associate root '%s'%s"
                % (root_name, suggested_storage_display)
            ).strip()

            if storage_to_use == "" and suggested_storage:
                storage_to_use = suggested_storage

            # match case insensitively
            if storage_to_use.lower() in storage_by_name:
                storage_to_use = storage_by_name[storage_to_use.lower()]["code"]
                storage = storage_by_name[storage_to_use.lower()]
            else:
                raise TankError("Please enter a valid storage name!")

            log.info("")
            log.info(
                "Accepted mapping: root '%s' ==> local storage '%s':"
                % (root_name, storage_to_use)
            )
            log.info("")

            # if the selected storage does not have a valid path for the current
            # operating system, prompt the user for a path to create/use
            current_os_key = ShotgunPath.get_shotgun_storage_key()
            current_os_path = storage.get(current_os_key)

            if not current_os_path:
                # the current os path for the selected storage is not populated.
                # prompt the user and update the path in PTR.
                current_os_path = input(
                    "Please enter a path for this storage on the current OS: "
                )

                if not current_os_path:
                    raise TankError("A path is required for the current OS.")

                if not os.path.isabs(current_os_path):
                    raise TankError("An absolute path is required for the current OS.")

                # try to create the path on disk
                try:
                    ensure_folder_exists(current_os_path)
                except Exception as e:
                    raise TankError(
                        "Unable to create the folder on disk.\n"
                        "Error: %s\n%s" % (e, traceback.format_exc())
                    )

                # update the storage in PTR.
                log.info("Updating the local storage in PTR...")
                log.info("")
                update_data = sg.update(
                    "LocalStorage", storage["id"], {current_os_key: current_os_path}
                )

                storage[current_os_key] = update_data[current_os_key]

            mapped_roots.append((root_name, storage_to_use))

        # ---- now we've mapped the roots, and they're all valid, we need to
        #      update the root information on the core wizard

        for (root_name, storage_name) in mapped_roots:

            root_info = required_roots[root_name]
            storage_data = storage_by_name[storage_name.lower()]

            # populate the data defined prior to mapping
            updated_storage_data = root_info

            # update the mapped shotgun data
            updated_storage_data["shotgun_storage_id"] = storage_data["id"]
            updated_storage_data["linux_path"] = str(storage_data["linux_path"])
            updated_storage_data["mac_path"] = str(storage_data["mac_path"])
            updated_storage_data["windows_path"] = str(storage_data["windows_path"])

            # now update the core wizard's root info
            params.update_storage_root(config_uri, root_name, updated_storage_data)

        log.info("")

    def _print_storage_info(self, storage, log):
        """
        Given a dict of local storage info, print the name and paths
        """

        linux_path = storage.get("linux_path") or ""
        mac_path = storage.get("mac_path") or ""
        windows_path = storage.get("windows_path") or ""

        storage_name = storage["code"]

        log.info(storage_name)
        log.info("-" * len(storage_name))
        log.info("    Linux: %s" % (linux_path,))
        log.info("      Mac: %s" % (mac_path,))
        log.info("  Windows: %s" % (windows_path,))
        log.info("")
