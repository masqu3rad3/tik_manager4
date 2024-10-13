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
from . import constants
from . import util
from . import console_utils
from .action_base import Action

import os


class SwitchAppAction(Action):
    """
    Action that makes it easy to switch from one descriptor to another
    """

    def __init__(self):
        Action.__init__(
            self,
            "switch_app",
            Action.TK_INSTANCE,
            "Switches an app from one code location to another.",
            "Developer",
        )

    def run_interactive(self, log, args):

        if len(args) < 4:

            log.info(
                "This command allows you to easily switch an app between different "
                "locations. A location defines where toolkit picks and synchrononizes "
                "App versions. It can be either the Toolkit App Store, a version control "
                "system such as Git or a location on disk."
            )
            log.info("")

            log.info("Switching an app to use a raw disk location")
            log.info("--------------------------------------------------")
            log.info(
                "If you want to do app development, it is handy to be able to "
                "take an app in your configuration and tell it to load from a "
                "specific folder on disk. The workflow is that you typically would "
                "start off with a git repository (forked off one of Flow Production Tracking's git "
                "repositories if you are modifying one of the standard toolkit apps). "
                "Then, clone this repo into your local dev area where you intend to "
                "make the actual changes. Now use the switch command to tell toolkit "
                "to use this version of the code."
            )
            log.info("")
            log.info(
                "Note! We advise against using dev locations in your primary configuration "
                "when you want to do development work, start by cloning your primary "
                "pipeline configuration. You can do this by right clicking on it in Flow Production Tracking."
            )
            log.info("")
            log.info("> Syntax:  switch_app environment engine app path")
            log.info(
                "> Example: switch_app Asset tk-maya tk-multi-about /Users/foo/dev/tk-multi-about"
            )
            log.info("")
            log.info("")
            log.info("Switching an app to track a git repository")
            log.info("--------------------------------------------------")
            log.info(
                "If you are using custom made apps or have modified Flow Production Tracking's built in apps "
                "by forking them from github ('https://github.com/shotgunsoftware'), and you "
                "have finished customization, you usually want to switch the app so that it "
                "tracks your git repository instead of the Toolkit App Store. Toolkit will "
                "read the list of tags from the repository and identify version-like tags "
                "(such as 'v0.1.2' or 'v1.2.3.4' and use these to determine which version "
                "is the latest one. If you create a new tag in the repository and then run "
                "the Toolkit update checker, it will detect that a more recent version is "
                "available and prompt you if you want to upgrade."
            )
            log.info("")
            log.info("> Syntax: switch_app environment engine app git_repo")
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
            log.info("Switching an app to track the Toolkit App Store")
            log.info("--------------------------------------------------")
            log.info(
                "If you have been doing development and want to switch back to the "
                "official app store version of an app, you can use the following syntax:"
            )
            log.info("")
            log.info("> Syntax: switch_app environment engine app app_store")
            log.info("> Example: switch_app Asset tk-maya tk-multi-about app_store")
            log.info("")
            log.info("")
            log.info(
                "For a list of environments, engines and apps, run the app_info command."
            )
            log.info("")
            log.info(
                "If you add a %s flag, the original, non-structure-preserving "
                "yaml parser will be used. This parser was used by default in core v0.17.x "
                "and below." % constants.LEGACY_YAML_PARSER_FLAG
            )
            log.info("")
            return

        (use_legacy_parser, args) = util.should_use_legacy_yaml_parser(args)
        preserve_yaml = not use_legacy_parser

        # get parameters
        env_name = args[0]
        engine_instance_name = args[1]
        app_instance_name = args[2]
        path = None
        mode = None

        fourth_param = args[3]

        if fourth_param == "app_store":
            mode = "app_store"
        elif fourth_param.endswith(".git"):
            mode = "git"
            path = fourth_param
        else:
            mode = "dev"
            path = fourth_param

        # find descriptor
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

        # and the app
        apps_for_engine = env.get_apps(engine_instance_name)
        if app_instance_name not in apps_for_engine:
            raise TankError(
                "Environment %s, engine %s has no app named '%s'! "
                "Available app instances are: %s "
                % (
                    env_name,
                    engine_instance_name,
                    app_instance_name,
                    ", ".join(apps_for_engine),
                )
            )

        # get the descriptor
        descriptor = env.get_app_descriptor(engine_instance_name, app_instance_name)

        log.info("")

        if mode == "app_store":
            new_descriptor = self.tk.pipeline_configuration.get_latest_app_descriptor(
                {"type": "app_store", "name": descriptor.system_name}
            )

        elif mode == "dev":
            if not os.path.exists(path):
                raise TankError("Cannot find path '%s' on disk!" % path)

            # run descriptor factory method
            new_descriptor = self.tk.pipeline_configuration.get_app_descriptor(
                {"type": "dev", "path": path}
            )

        elif mode == "git":
            # run descriptor factory method
            new_descriptor = self.tk.pipeline_configuration.get_latest_app_descriptor(
                {"type": "git", "path": path}
            )

        else:
            raise TankError("Unknown mode!")

        # prompt user!
        log.info("")
        log.info("")
        log.info("Current version")
        log.info("------------------------------------")
        for (k, v) in descriptor.get_dict().items():
            log.info(" - %s: %s" % (k.capitalize(), v))

        log.info("")
        log.info("New version")
        log.info("------------------------------------")
        for (k, v) in new_descriptor.get_dict().items():
            log.info(" - %s: %s" % (k.capitalize(), v))

        log.info("")
        if not self._interaction_interface.ask_yn_question("Okay to switch?"):
            log.info("Switch aborted!")
            return

        if not new_descriptor.exists_local():
            log.info("Downloading %s..." % new_descriptor)
            new_descriptor.download_local()

        # create required shotgun fields
        new_descriptor.ensure_shotgun_fields_exist(self.tk)

        # run post install hook
        new_descriptor.run_post_install(self.tk)

        # ensure that all required frameworks have been installed
        # find the file where our item is being installed
        (_, yml_file) = env.find_location_for_app(
            engine_instance_name, app_instance_name
        )

        console_utils.ensure_frameworks_installed(
            log, self.tk, yml_file, new_descriptor, env, self._interaction_interface
        )

        # find the name of the engine
        engine_system_name = env.get_engine_descriptor(engine_instance_name).system_name

        # now get data for all new settings values in the config
        params = console_utils.get_configuration(
            log,
            self.tk,
            new_descriptor,
            descriptor,
            self._interaction_interface,
            engine_system_name,
        )

        # next step is to add the new configuration values to the environment
        env.update_app_settings(
            engine_instance_name, app_instance_name, params, new_descriptor.get_dict()
        )

        log.info("Switch complete!")
