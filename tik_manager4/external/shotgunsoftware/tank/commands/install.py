# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from ..errors import TankError
from . import console_utils
from .action_base import Action
from . import util
from . import constants


class InstallAppAction(Action):
    """
    Action for installing an app
    """

    def __init__(self):
        Action.__init__(
            self,
            "install_app",
            Action.TK_INSTANCE,
            "Adds a new app to your configuration.",
            "Configuration",
        )

        # this method can be executed via the API
        self.supports_api = True

        self.parameters = {}

        self.parameters["environment"] = {
            "description": "Name of environment to install into.",
            "default": None,
            "type": "str",
        }

        self.parameters["engine_instance"] = {
            "description": "Name of the engine instance to install into.",
            "default": None,
            "type": "str",
        }

        self.parameters["preserve_yaml"] = {
            "description": (
                "Enable alternative yaml parser that better preserves "
                "yaml structure and comments"
            ),
            "default": True,
            "type": "bool",
        }

        self.parameters["app_uri"] = {
            "description": (
                "Address to app to install. If you specify the name of "
                "an app (e.g. tk-multi-loader), toolkit will try to download "
                "it from the PTR App Store. Alternatively, you can also "
                "specify the path to a bare git repo, for example in github. "
                "For more info, see the help for the install_app commmand."
            ),
            "default": None,
            "type": "str",
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

        return self._run(
            log,
            computed_params["environment"],
            computed_params["engine_instance"],
            computed_params["app_uri"],
            computed_params["preserve_yaml"],
        )

    def run_interactive(self, log, args):
        """
        Tank command accessor

        :param log: std python logger
        :param args: command line args
        """
        (use_legacy_parser, args) = util.should_use_legacy_yaml_parser(args)
        preserve_yaml = not use_legacy_parser

        if len(args) != 3:

            log.info(
                "This command adds an app to an existing environment and engine. "
                "You can either add apps from the Toolkit App Store, git or directly from disk."
            )
            log.info("")
            log.info("Adding an app from local disk (for developers)")
            log.info("----------------------------------------------")
            log.info("")
            log.info(
                "This is useful when you start development of a new app. We recommend that you "
                "base your new apps on our default starter app, located in github:"
            )
            log.info("")
            log.info("https://github.com/shotgunsoftware/tk-multi-starterapp")
            log.info("")
            log.info(
                "Download it to a local folder, either by forking it or simply by downloading "
                "the code. We now recommend that you decide which base frameworks to use, "
                "and update the info.yml manifest accordingly. "
                "Next, add it to a toolkit environment using the install_app command. The "
                "command will ensure that all required frameworks and parameters are correctly "
                "downloaded and populated:"
            )
            log.info("")
            log.info("> tank install_app environment_name engine_name /path/on/disk")
            log.info("")
            log.info(
                "For more information about app development, see "
                "https://help.autodesk.com/view/SGDEV/ENU/?contextId=PG_SGTK_DEVELOPER_APP"
            )
            log.info("")
            log.info("")

            log.info("Adding an app from git or github")
            log.info("--------------------------------")
            log.info("")
            log.info(
                "You can also install apps directly from git or github. Toolkit will "
                "read a git repository's list of tags, try to interpret them as version numbers, and "
                "install the tag with the highest version number. Later on, when you run "
                "the 'tank updates' command, it will automatically detect if there are tags "
                "with higher version number than the currently installed and prompt you to "
                "update."
            )
            log.info("")
            log.info(
                "We strongly recommend that your tags following the Semantic Version "
                "numbering scheme when working with Toolkit. You can read more about it "
                "here: http://semver.org"
            )
            log.info("")
            log.info("To install an app from git, use the following syntax:")
            log.info("> tank install_app environment_name engine_name git-repo")
            log.info("")
            log.info(
                "The git_repo part is a repository location that can be understood by git. "
                "Examples include: "
            )
            log.info(" - /path/to/repo.git")
            log.info(" - user@remotehost:/path_to/repo.git")
            log.info(" - git://github.com/manneohrstrom/tk-hiero-publish.git")
            log.info(" - https://github.com/manneohrstrom/tk-hiero-publish.git")
            log.info("")
            log.info("")

            log.info("Adding an App from the Toolkit App Store")
            log.info("----------------------------------------")
            log.info("")
            log.info(
                "The standard mechanism through which apps and engines are distributed "
                "is the Toolkit App Store. Items in the App Store are part of the official "
                "toolkit distribution and have gone through our quality control process. "
                "To see all apps and engines in the Toolkit App Store, navigate here:"
            )
            log.info("")
            log.info(
                "https://help.autodesk.com/view/SGDEV/ENU/?contextId=PC_TOOLKIT_APPS"
            )
            log.info("")
            log.info("To install an app store app, use the following syntax:")
            log.info("> tank install_app environment_name engine_name app_name")
            log.info("")
            log.info(
                "For example, to install the loader app into the shell engine in the "
                "Asset environment:"
            )
            log.info("> tank install_app Asset tk-shell tk-multi-loader")
            log.info("")
            log.info("")
            log.info("Comment and structure preserving mode")
            log.info("-------------------------------------")
            log.info("")
            log.info(
                "If you add a %s flag, the original, non-structure-preserving "
                "yaml parser will be used. This parser was used by default in core v0.17.x "
                "and below." % constants.LEGACY_YAML_PARSER_FLAG
            )
            log.info("")
            log.info("")
            log.info(
                "Handy tip: For a list of existing environments, engines and apps, "
                "run the 'tank app_info' command."
            )
            log.info("")

            return

        env_name = args[0]
        engine_instance_name = args[1]
        app_name = args[2]

        self._run(log, env_name, engine_instance_name, app_name, preserve_yaml)

    def _run(self, log, env_name, engine_instance_name, app_name, preserve_yaml):

        log.info("")
        log.info("Welcome to the Flow Production Tracking App installer!")
        log.info(
            "Installing into environment %s and engine %s."
            % (env_name, engine_instance_name)
        )

        try:
            env = self.tk.pipeline_configuration.get_environment(
                env_name, writable=True
            )
            env.set_yaml_preserve_mode(preserve_yaml)
        except Exception as e:
            raise TankError(
                "Environment '%s' could not be loaded! Error reported: %s"
                % (env_name, e)
            )

        # make sure the engine exists in the environment
        if engine_instance_name not in env.get_engines():
            raise TankError(
                "Environment %s has no engine named %s!"
                % (env_name, engine_instance_name)
            )

        if app_name.endswith(".git"):
            # this is a git location!
            # run descriptor factory method
            log.info("Connecting to git...")
            location = {"type": "git", "path": app_name}
            app_descriptor = self.tk.pipeline_configuration.get_latest_app_descriptor(
                location
            )
            log.info(
                "Latest tag in repository '%s' is %s."
                % (app_name, app_descriptor.version)
            )

        elif "/" in app_name or "\\" in app_name:
            # this is a local path on disk, meaning that we should set up a dev descriptor!
            log.info("Looking for a locally installed app in '%s'..." % app_name)
            location = {"type": "dev", "path": app_name}
            app_descriptor = self.tk.pipeline_configuration.get_app_descriptor(location)

        else:
            # this is an app store app!
            log.info("Connecting to the Toolkit App Store...")
            location = {"type": "app_store", "name": app_name}
            app_descriptor = self.tk.pipeline_configuration.get_latest_app_descriptor(
                location
            )
            log.info(
                "Latest approved App Store Version is %s." % app_descriptor.version
            )

        # note! Some of these methods further down are likely to pull the apps local
        # in order to do deep introspection. In order to provide better error reporting,
        # pull the apps local before we start
        if not app_descriptor.exists_local():
            log.info("Downloading, hold on...")
            app_descriptor.download_local()

        # now assume a convention where we will name the app instance that we create in the environment
        # the same as the short name of the app
        app_instance_name = app_descriptor.system_name

        # check so that there is not an app with that name already!
        if app_instance_name in env.get_apps(engine_instance_name):
            raise TankError(
                "Engine %s already has an app named %s!"
                % (engine_instance_name, app_instance_name)
            )

        # now make sure all constraints are okay
        try:
            console_utils.check_constraints_for_item(
                app_descriptor, env, engine_instance_name
            )
        except TankError as e:
            raise TankError("Cannot install: %s" % e)

        # okay to install!

        # ensure that all required frameworks have been installed

        # find the file where our app is being installed
        # when adding new items, we always add them to the root env file
        fw_location = env.disk_location
        console_utils.ensure_frameworks_installed(
            log, self.tk, fw_location, app_descriptor, env, self._interaction_interface
        )

        # create required shotgun fields
        app_descriptor.ensure_shotgun_fields_exist(self.tk)

        # run post install hook
        app_descriptor.run_post_install(self.tk)

        # find the name of the engine
        engine_system_name = env.get_engine_descriptor(engine_instance_name).system_name

        # now get data for all new settings values in the config
        params = console_utils.get_configuration(
            log,
            self.tk,
            app_descriptor,
            None,
            self._interaction_interface,
            engine_system_name,
        )

        # next step is to add the new configuration values to the environment
        env.create_app_settings(engine_instance_name, app_instance_name)
        env.update_app_settings(
            engine_instance_name, app_instance_name, params, app_descriptor.get_dict()
        )

        log.info("App Installation Complete!")
        if app_descriptor.documentation_url:
            log.info("For documentation, see %s" % app_descriptor.documentation_url)
        log.info("")
        log.info("")


class InstallEngineAction(Action):
    """
    Action for installing an engine.
    """

    def __init__(self):
        Action.__init__(
            self,
            "install_engine",
            Action.TK_INSTANCE,
            "Adds a new engine to your configuration.",
            "Configuration",
        )

        # this method can be executed via the API
        self.supports_api = True

        self.parameters = {}

        self.parameters["environment"] = {
            "description": "Name of environment to install into.",
            "default": None,
            "type": "str",
        }

        self.parameters["preserve_yaml"] = {
            "description": (
                "Enable alternative yaml parser that better preserves "
                "yaml structure and comments"
            ),
            "default": True,
            "type": "bool",
        }

        self.parameters["engine_uri"] = {
            "description": (
                "Address to engine to install. If you specify the name of "
                "an engine (e.g. tk-maya), toolkit will try to download "
                "it from the PTR App Store. Alternatively, you can also "
                "specify the path to a bare git repo, for example in github. "
                "For more info, see the help for the install_engine commmand."
            ),
            "default": None,
            "type": "str",
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

        return self._run(
            log,
            True,
            computed_params["environment"],
            computed_params["engine_uri"],
            computed_params["preserve_yaml"],
        )

    def run_interactive(self, log, args):
        """
        Tank command accessor

        :param log: std python logger
        :param args: command line args
        """
        (use_legacy_parser, args) = util.should_use_legacy_yaml_parser(args)
        preserve_yaml = not use_legacy_parser

        if len(args) != 2:

            log.info(
                "This command adds an engine to an existing environment. "
                "You can either add engines from the Toolkit App Store or from git source control."
            )
            log.info("")
            log.info("")

            log.info("Adding an engine from local disk (for developers)")
            log.info("-------------------------------------------------")
            log.info("")
            log.info(
                "This is useful when you start development of a new engine. "
                "Set up some starter code on disk (for example by cloning "
                "an existing engine) and then run the install_engine command:"
            )
            log.info("")
            log.info("> tank install_engine environment_name /path/on/disk")
            log.info("")
            log.info("")

            log.info("Adding an engine from git or github")
            log.info("-----------------------------------")
            log.info("")
            log.info(
                "You can also install engines directly from git or github. Toolkit will "
                "read a git repository's list of tags, try to interpret them as version numbers, and "
                "install the tag with the highest version number. Later on, when you run "
                "the 'tank updates' command, it will automatically detect if there are tags "
                "with higher version number than the currently installed and prompt you to "
                "update."
            )
            log.info("")
            log.info(
                "We strongly recommend that your tags following the Semantic Version "
                "numbering scheme when working with Toolkit. You can read more about it "
                "here: http://semver.org"
            )
            log.info("")
            log.info("To install an engine from git, use the following syntax:")
            log.info("> tank install_engine environment_name git-repo")
            log.info("")
            log.info(
                "The git_repo part is a repository location that can be understood by git. "
                "Examples include: "
            )
            log.info(" - /path/to/repo.git")
            log.info(" - user@remotehost:/path_to/repo.git")
            log.info(" - git://github.com/manneohrstrom/tk-hiero-publish.git")
            log.info(" - https://github.com/manneohrstrom/tk-hiero-publish.git")
            log.info("")
            log.info("")

            log.info("Adding an engine from the Toolkit App Store")
            log.info("-------------------------------------------")
            log.info("")
            log.info(
                "The standard mechanism through which apps and engines are distributed "
                "is the Toolkit App Store. Items in the App Store are part of the official "
                "toolkit distribution and have gone through our quality control process. "
                "To see all apps and engines in the Toolkit App Store, navigate here:"
            )
            log.info("")
            log.info(
                "https://help.autodesk.com/view/SGDEV/ENU/?contextId=PC_TOOLKIT_APPS"
            )
            log.info("")
            log.info("To install an app store engine, use the following syntax:")
            log.info("> tank install_engine environment_name engine_name")
            log.info("")
            log.info(
                "For example, to install the houdini engine into the Asset environment:"
            )
            log.info("> tank install_engine Asset tk-houdini")
            log.info("")
            log.info("Comment and structure preserving mode")
            log.info("-------------------------------------")
            log.info("")
            log.info(
                "If you add a %s flag, the original, non-structure-preserving "
                "yaml parser will be used. This parser was used by default in core v0.17.x "
                "and below." % constants.LEGACY_YAML_PARSER_FLAG
            )
            log.info("")
            log.info("")
            log.info(
                "Handy tip: For a list of existing environments, engines and apps, "
                "run the 'tank app_info' command."
            )
            log.info("")

            return

        env_name = args[0]
        engine_name = args[1]

        self._run(log, env_name, engine_name, preserve_yaml)

    def _run(self, log, env_name, engine_name, preserve_yaml):
        """
        Actual execution payload
        """

        log.info("")
        log.info("")
        log.info("Welcome to the Flow Production Tracking Toolkit Engine installer!")
        log.info("")

        try:
            env = self.tk.pipeline_configuration.get_environment(
                env_name, writable=True
            )
            env.set_yaml_preserve_mode(preserve_yaml)
        except Exception as e:
            raise TankError(
                "Environment '%s' could not be loaded! Error reported: %s"
                % (env_name, e)
            )

        if engine_name.endswith(".git"):
            # this is a git location!
            # run descriptor factory method
            log.info("Connecting to git...")
            location = {"type": "git", "path": engine_name}
            engine_descriptor = self.tk.pipeline_configuration.get_latest_engine_descriptor(
                location
            )
            log.info(
                "Latest tag in repository '%s' is %s."
                % (engine_name, engine_descriptor.version)
            )

        elif "/" in engine_name or "\\" in engine_name:
            # this is a local path on disk, meaning that we should set up a dev descriptor!
            log.info("Looking for a locally installed engine in '%s'..." % engine_name)
            location = {"type": "dev", "path": engine_name}
            engine_descriptor = self.tk.pipeline_configuration.get_engine_descriptor(
                location
            )

        else:
            # this is an app store app!
            log.info("Connecting to the Toolkit App Store...")
            location = {"type": "app_store", "name": engine_name}
            engine_descriptor = self.tk.pipeline_configuration.get_latest_engine_descriptor(
                location
            )
            log.info(
                "Latest approved App Store Version is %s." % engine_descriptor.version
            )

        log.info("")

        # now assume a convention where we will name the engine instance that we create in the environment
        # the same as the short name of the engine
        engine_instance_name = engine_descriptor.system_name

        # check so that there is not an app with that name already!
        if engine_instance_name in env.get_engines():
            raise TankError(
                "Engine %s already exists in environment %s!"
                % (engine_instance_name, env)
            )

        # now make sure all constraints are okay
        try:
            console_utils.check_constraints_for_item(engine_descriptor, env)
        except TankError as e:
            raise TankError("Cannot install: %s" % e)

        # okay to install!

        # ensure that all required frameworks have been installed
        # find the file where our app is being installed
        # when adding new items, we always add them to the root env file
        fw_location = env.disk_location
        console_utils.ensure_frameworks_installed(
            log,
            self.tk,
            fw_location,
            engine_descriptor,
            env,
            self._interaction_interface,
        )

        # note! Some of these methods further down are likely to pull the apps local
        # in order to do deep introspection. In order to provide better error reporting,
        # pull the apps local before we start
        if not engine_descriptor.exists_local():
            log.info("Downloading, hold on...")
            engine_descriptor.download_local()
            log.info("")

        # create required shotgun fields
        engine_descriptor.ensure_shotgun_fields_exist(self.tk)

        # run post install hook
        engine_descriptor.run_post_install(self.tk)

        # now get data for all new settings values in the config
        params = console_utils.get_configuration(
            log, self.tk, engine_descriptor, None, self._interaction_interface, None
        )

        # next step is to add the new configuration values to the environment
        env.create_engine_settings(engine_instance_name)
        env.update_engine_settings(
            engine_instance_name, params, engine_descriptor.get_dict()
        )

        log.info("")
        log.info("")
        log.info("Engine Installation Complete!")
        log.info("")
        if engine_descriptor.documentation_url:
            log.info("For documentation, see %s" % engine_descriptor.documentation_url)
        log.info("")
        log.info("")
