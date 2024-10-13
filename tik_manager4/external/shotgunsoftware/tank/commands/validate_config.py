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
from .action_base import Action
from ..errors import TankError
from ..platform import validation, bundle


class ValidateConfigAction(Action):
    """
    Action that looks at the config and validates all parameters
    """

    def __init__(self):
        Action.__init__(
            self,
            "validate",
            Action.TK_INSTANCE,
            (
                "Validates your current Configuration to check that all "
                "environments have been correctly configured."
            ),
            "Configuration",
        )

        self.parameters = {}

        self.parameters["envs"] = {
            "description": (
                "A list of environment names to process. If not "
                "specified, process all environments."
            ),
            "type": "list",
            "default": [],
        }

        # this method can be executed via the API
        self.supports_api = True

        self._is_interactive = False

        self._templates = set()
        self._hooks = set()

    def run_noninteractive(self, log, parameters):
        """
        Tank command API accessor.
        Called when someone runs a tank command through the core API.

        :param log: std python logger
        :param parameters: dictionary with tank command parameters
        """

        # validate params and seed default values
        return self._run(log, self._validate_parameters(parameters))

    def run_interactive(self, log, args):
        """
        Tank command accessor

        :param log: std python logger
        :param args: command line args
        """

        self._is_interactive = True

        # currently, environment names are passed in as arguments for
        # validation. Just translate the args to the env list and validate them
        return self._run(log, self._validate_parameters({"envs": args}))

    def _run(self, log, parameters):
        """
        Actual execution payload
        """

        log.info("")
        log.info("")
        log.info(
            "Welcome to the Flow Production Tracking Configuration validator!"
        )
        log.info("")

        log.info("Found the following environments:")
        for x in parameters["envs"]:
            log.info("    %s" % x)
        log.info("")
        log.info("")

        # validate environments
        for env_name in parameters["envs"]:
            if self._terminate_requested:
                break

            log.info("")
            log.info("Environment %s" % env_name)
            log.info("------------------------------------------")

            env = self.tk.pipeline_configuration.get_environment(env_name)
            log.info("Environment path: %s" % (env.disk_location))
            self._process_environment(log, self.tk, env)

        log.info("")
        log.info("")
        log.info("")

        # check templates that are orphaned
        unused_templates = set(self.tk.templates.keys()) - self._templates

        log.info("")
        log.info(
            "------------------------------------------------------------------------"
        )
        log.info(
            "The following templates are not being used directly in any environments:"
        )
        log.info("(they may be used inside complex data structures)")
        for ut in unused_templates:
            log.info(ut)

        log.info("")
        log.info("")
        log.info("")

        # check hooks that are unused
        all_hooks = []
        # get rid of files not ending with .py and strip extension
        for hook in os.listdir(self.tk.pipeline_configuration.get_hooks_location()):
            if hook.endswith(".py"):
                all_hooks.append(hook[:-3])

        unused_hooks = set(all_hooks) - self._hooks

        log.info("")
        log.info("--------------------------------------------------------------------")
        log.info("The following hooks are not being used directly in any environments:")
        log.info("(they may be used inside complex data structures)")
        for uh in unused_hooks:
            log.info(uh)

        log.info("")
        log.info("")
        log.info("")

    def _validate_parameters(self, parameters):
        """
        Do validation of the parameters that are specific to this action.

        :param parameters: The dict of parameters
        :returns: The validated and fully populated dict of parameters.
        """

        # do the base class default validation
        parameters = super(ValidateConfigAction, self)._validate_parameters(parameters)

        # get a list of valid env names
        valid_env_names = self.tk.pipeline_configuration.get_environments()

        bad_env_names = []
        env_names_to_process = []
        if parameters["envs"]:
            # some environment names supplied on the command line
            for env_param in parameters["envs"]:
                # see if this is a comma separated list
                for env_name in env_param.split(","):
                    env_name = env_name.strip()
                    if env_name in valid_env_names:
                        env_names_to_process.append(env_name)
                    else:
                        bad_env_names.append(env_name)
        else:
            # nothing specified. process all
            env_names_to_process = valid_env_names

        # bail if any bad env names
        if bad_env_names:
            if self._is_interactive:
                print("\nUsage: %s\n" % (self._usage(),))
            raise TankError(
                "Error retrieving environments mathing supplied arguments: %s"
                % (", ".join(bad_env_names),)
            )

        parameters["envs"] = sorted(env_names_to_process)

        return parameters

    def _usage(self):
        """Return a string displaying the usage of this command."""
        return "./tank validate [env_name, env_name, ...] "

    def _process_environment(self, log, tk, env):
        """Process an environment by validating each of its bundles.
        :param log: A logger instance for logging validation output.
        :param tk: A toolkit api instance.
        :param env: An environment instance.
        """

        for e in env.get_engines():
            if self._terminate_requested:
                break

            s = env.get_engine_settings(e)
            descriptor = env.get_engine_descriptor(e)
            name = "Engine %s / %s" % (env.name, e)
            self._validate_bundle(log, tk, name, s, descriptor, engine_name=e)
            for a in env.get_apps(e):
                if self._terminate_requested:
                    break

                s = env.get_app_settings(e, a)
                descriptor = env.get_app_descriptor(e, a)
                name = "%s / %s / %s" % (env.name, e, a)
                self._validate_bundle(log, tk, name, s, descriptor, engine_name=e)

    def _validate_bundle(self, log, tk, name, settings, descriptor, engine_name=None):
        """Validate the supplied bundle including the descriptor and all settings.
        :param log: A logger instance for logging validation output.
        :param tk: A toolkit api instance.
        :param name: The bundle's name.
        :param settings: The bundle's settings dict.
        :param descriptor: A descriptor object for the bundle.
        :param engine_name: The name of the containing engine or None.
            This is used when the bundle is an app and needs to validate engine-
            specific settings.
        """

        log.info("")
        log.info("Validating %s..." % name)

        if not descriptor.exists_local():
            log.info("Please wait, downloading...")
            descriptor.download_local()

        # out of date check
        latest_desc = descriptor.find_latest_version()
        if descriptor.version != latest_desc.version:
            log.info(
                "WARNING: Latest version is %s. You are running %s."
                % (latest_desc.version, descriptor.version)
            )

        manifest = descriptor.configuration_schema

        for s in settings.keys():
            if s not in manifest.keys():
                log.info("  WARNING - Parameter not needed: %s" % s)

        for s in manifest.keys():

            default = bundle.resolve_default_value(manifest[s], engine_name=engine_name)

            if s in settings:
                value = settings.get(s)
            else:
                value = default

            try:
                validation.validate_single_setting(name, tk, manifest, s, value)
            except TankError as e:
                log.info("  ERROR - Parameter %s - Invalid value: %s" % (s, e))
            else:
                # validation is ok
                if default is None:
                    # no default value
                    # don't report this
                    pass

                elif manifest[s].get("type") == "hook" and value == "default":
                    # don't display when default values are used.
                    pass

                elif default == value:
                    pass

                else:
                    log.info("  Parameter %s - OK [using non-default value]" % s)
                    log.info("    |---> Current: %s" % value)
                    log.info(r"    \---> Default: %s" % default)

                # remember templates
                if manifest[s].get("type") == "template":
                    self._templates.add(value)
                if manifest[s].get("type") == "hook":
                    self._hooks.add(value)
