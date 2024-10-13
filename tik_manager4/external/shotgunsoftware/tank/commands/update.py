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

from .action_base import Action
from . import console_utils
from . import util
from ..platform.environment import WritableEnvironment
from ..descriptor import CheckVersionConstraintsError
from . import constants
from ..util.version import is_version_number, is_version_newer
from .. import pipelineconfig_utils


class AppUpdatesAction(Action):
    """
    Action that updates apps and engines.
    """

    def __init__(self):

        Action.__init__(
            self,
            "updates",
            Action.TK_INSTANCE,
            "Checks if there are any app or engine updates for the current configuration.",
            "Configuration",
        )

        # this method can be executed via the API
        self.supports_api = True

        self.parameters = {}

        self.parameters["environment_filter"] = {
            "description": "Name of environment to check.",
            "default": "ALL",
            "type": "str",
        }

        self.parameters["engine_filter"] = {
            "description": "Name of engine to check.",
            "default": "ALL",
            "type": "str",
        }

        self.parameters["app_filter"] = {
            "description": "Name of app to check.",
            "default": "ALL",
            "type": "str",
        }

        self.parameters["external"] = {
            "description": "Specify an external config to update.",
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

        self._descriptor_look_up = {}

    def run_noninteractive(self, log, parameters):
        """
        Tank command API accessor.
        Called when someone runs a tank command through the core API.

        :param log: std python logger
        :param parameters: dictionary with tank command parameters
        """
        # validate params and seed default values
        computed_params = self._validate_parameters(parameters)

        if computed_params["environment_filter"] == "ALL":
            computed_params["environment_filter"] = None
        if computed_params["engine_filter"] == "ALL":
            computed_params["engine_filter"] = None
        if computed_params["app_filter"] == "ALL":
            computed_params["app_filter"] = None

        return self._check_for_updates(
            log,
            self.tk,
            computed_params["environment_filter"],
            computed_params["engine_filter"],
            computed_params["app_filter"],
            computed_params["external"],
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

        if len(args) == 0:
            # update EVERYTHING!

            log.info(
                "This command will go through your current configuration and check if there "
                "are any updates available. If there are updates, you will be asked if you "
                "want to perform an upgrade. If settings has been added to the new version "
                "that you are installing, you may be prompted to specified values for these."
            )
            log.info("")
            log.info(
                "Running this command with no parameters will check all environments, engines "
                "and app. This may take a long time. You can also run the updater on a subset "
                "of your installed apps and engines."
            )
            log.info("")
            log.info("")
            log.info("")
            log.info("General syntax:")
            log.info("---------------")
            log.info("")
            log.info(
                "> tank updates [environment_name] "
                "[engine_name] [app_name] [%s] "
                "[--external='/path/to/config']" % constants.LEGACY_YAML_PARSER_FLAG
            )
            log.info("")
            log.info(
                "- The special keyword ALL can be used to denote all items in a category."
            )
            log.info("")
            log.info(
                "- If you want to update an external configuration instead of the current project, "
                "pass in a path via the --external flag."
            )
            log.info("")
            log.info(
                "If you add a %s flag, the original, non-structure-preserving "
                "yaml parser will be used. This parser was used by default in core v0.17.x "
                "and below." % constants.LEGACY_YAML_PARSER_FLAG
            )
            log.info("")
            log.info("")
            log.info("")
            log.info("Examples:")
            log.info("---------")
            log.info("")
            log.info("Check everything:")
            log.info("> tank updates")
            log.info("")
            log.info("Check the Shot environment:")
            log.info("> tank updates Shot")
            log.info("")
            log.info("Check all maya apps in all environments:")
            log.info("> tank updates ALL tk-maya")
            log.info("")
            log.info("Check all maya apps in the Shot environment:")
            log.info("> tank updates Shot tk-maya")
            log.info("")
            log.info("Make sure the loader app is up to date everywhere:")
            log.info("> tank updates ALL ALL tk-multi-loader")
            log.info("")
            log.info("Make sure the loader app is up to date in maya:")
            log.info("> tank updates ALL tk-maya tk-multi-loader")
            log.info("")
            log.info("")

            if self._interaction_interface.ask_yn_question(
                "Continue with full update?"
            ):
                self._check_for_updates(
                    log,
                    self.tk,
                    env_name=None,
                    engine_instance_name=None,
                    app_instance_name=None,
                    preserve_yaml=preserve_yaml,
                )

            return

        env_filter = None
        engine_filter = None
        app_filter = None
        external_path = None

        # look for an --external argument
        for arg in args:
            if arg.startswith("--external="):
                # remove it from args list
                args.remove(arg)
                # from '--external=/path/to/my config' get '/path/to/my config'
                external_path = arg[len("--external=") :]
                if external_path == "":
                    log.error("You need to specify a path to a toolkit configuration!")
                    return

        if len(args) > 0:
            env_filter = args[0]
            if env_filter == "ALL":
                log.info("- Update will check all environments.")
                env_filter = None
            else:
                log.info("- Update will only check the %s environment." % env_filter)

        if len(args) > 1:
            engine_filter = args[1]
            if engine_filter == "ALL":
                log.info("- Update will check all engines.")
                engine_filter = None
            else:
                log.info("- Update will only check the %s engine." % engine_filter)

        if len(args) > 2:
            app_filter = args[2]
            if app_filter == "ALL":
                log.info("- Update will check all apps.")
                app_filter = None
            else:
                log.info("- Update will only check the %s app." % app_filter)

        self._check_for_updates(
            log,
            self.tk,
            env_name=env_filter,
            engine_instance_name=engine_filter,
            app_instance_name=app_filter,
            external=external_path,
            preserve_yaml=preserve_yaml,
        )

    ################################################################################################
    # helper methods for update

    def _check_for_updates(
        self,
        log,
        tk,
        env_name,
        engine_instance_name,
        app_instance_name,
        external=None,
        preserve_yaml=True,
    ):
        """
        Runs the update checker.

        :param log: Python logger
        :param tk: Toolkit instance
        :param env_name: Environment name to update
        :param engine_instance_name: Engine instance name to update
        :param app_instance_name: App instance name to update
        :param preserve_yaml: If True, a comment preserving yaml parser is used.
        :param external: Path to external config to operate on
        """
        pc = tk.pipeline_configuration

        self._descriptor_look_up = {}

        processed_items = []

        if external:

            # try to load external file
            external = os.path.expanduser(external)
            if not os.path.exists(external):
                log.error("Cannot find external config %s" % external)
                return

            env_path = os.path.join(external, "env")

            if not os.path.exists(env_path):
                log.error("Cannot find environment folder '%s'" % env_path)
                return

            # find all environment files
            log.info("Looking for matching environments in %s:" % env_path)
            log.info("")
            env_filenames = []
            for filename in os.listdir(env_path):
                if filename.endswith(".yml"):
                    if env_name is None or ("%s.yml" % env_name) == filename:
                        # matching the env filter (or no filter set)
                        log.info("> found %s" % filename)
                        env_filenames.append(os.path.join(env_path, filename))

            # now process them one after the other
            for env_filename in env_filenames:
                log.info("")
                log.info("")
                log.info(
                    "======================================================================"
                )
                log.info("Environment %s..." % env_name)
                log.info(
                    "======================================================================"
                )
                log.info("")

                env_obj = WritableEnvironment(env_filename, pc)
                env_obj.set_yaml_preserve_mode(preserve_yaml)

                log.info("Environment path: %s" % (env_obj.disk_location))
                log.info("")

                processed_items += self._process_environment(
                    tk, log, env_obj, engine_instance_name, app_instance_name
                )

        else:

            # process non-external config
            if env_name is None:
                env_names_to_process = pc.get_environments()
            else:
                env_names_to_process = [env_name]

            for env_name in env_names_to_process:
                log.info("")
                log.info("")
                log.info(
                    "======================================================================"
                )
                log.info("Environment %s..." % env_name)
                log.info(
                    "======================================================================"
                )

                env_obj = pc.get_environment(env_name, writable=True)
                env_obj.set_yaml_preserve_mode(preserve_yaml)

                log.info("Environment path: %s" % (env_obj.disk_location))
                log.info("")

                processed_items += self._process_environment(
                    tk, log, env_obj, engine_instance_name, app_instance_name
                )

                if self._terminate_requested:
                    break

        # display summary
        log.info("")
        summary = []
        for x in processed_items:
            if x["was_updated"]:

                summary.append(
                    "%s was updated from %s to %s"
                    % (
                        x["new_descriptor"],
                        x["old_descriptor"].version,
                        x["new_descriptor"].version,
                    )
                )
                (_, url) = x["new_descriptor"].changelog
                if url:
                    summary.append("Change Log: %s" % url)
                summary.append("")

        if len(summary) > 0:
            log.info("Items were updated. Details follow below:")
            log.info("-" * 70)
            for x in summary:
                log.info(x)
            log.info("-" * 70)

        log.info("")

        # generate return data for api access
        ret_val = []
        for x in processed_items:
            d = {}
            d["engine_instance"] = x["engine_name"]
            d["app_instance"] = x["app_name"]
            d["framework_name"] = x["framework_name"]
            d["environment"] = x["env_name"].name
            d["updated"] = x["was_updated"]
            if x["was_updated"]:
                d["new_version"] = x["new_descriptor"].version
            ret_val.append(d)

        return ret_val

    def _process_environment(
        self,
        tk,
        log,
        environment_obj,
        engine_instance_name=None,
        app_instance_name=None,
    ):
        """
        Updates a given environment object

        :param log: Python logger
        :param tk: Toolkit instance
        :param environment_obj: Environment object to update
        :param engine_instance_name: Engine instance name to update
        :param app_instance_name: App instance name to update

        :returns: list of updated items
        """
        items = []

        if engine_instance_name is None:
            # process all engines
            engines_to_process = environment_obj.get_engines()

        else:
            # there is a filter! Ensure the filter matches something
            # in this environment
            if engine_instance_name in environment_obj.get_engines():
                # the filter matches something in this environment
                engines_to_process = [engine_instance_name]
            else:
                # the item we are filtering on does not exist in this env
                engines_to_process = []

        for engine in engines_to_process:

            if self._terminate_requested:
                break

            items.extend(
                self._process_item(log, tk, environment_obj, engine_name=engine)
            )
            log.info("")

            if app_instance_name is None:
                # no filter - process all apps
                apps_to_process = environment_obj.get_apps(engine)
            else:
                # there is a filter! Ensure the filter matches
                # something in the current engine apps listing
                if app_instance_name in environment_obj.get_apps(engine):
                    # the filter matches something!
                    apps_to_process = [app_instance_name]
                else:
                    # the app filter does not match anything in this engine
                    apps_to_process = []

            for app in apps_to_process:
                if self._terminate_requested:
                    break

                items.extend(
                    self._process_item(
                        log, tk, environment_obj, engine_name=engine, app_name=app
                    )
                )
                log.info("")

        if len(environment_obj.get_frameworks()) > 0:
            log.info("")
            log.info("Frameworks:")
            log.info("-" * 70)

            for framework in environment_obj.get_frameworks():
                if self._terminate_requested:
                    break
                items.extend(
                    self._process_item(
                        log, tk, environment_obj, framework_name=framework
                    )
                )

        return items

    def _update_item(
        self,
        log,
        tk,
        env,
        old_descriptor,
        new_descriptor,
        engine_name=None,
        app_name=None,
        framework_name=None,
    ):
        """
        Performs an upgrade of an engine/app/framework.
        """
        # note! Some of these methods further down are likely to pull the apps local
        # in order to do deep introspection. In order to provide better error reporting,
        # pull the apps local before we start
        if not new_descriptor.exists_local():
            log.info("Downloading %s..." % new_descriptor)
            new_descriptor.download_local()

        # create required shotgun fields
        new_descriptor.ensure_shotgun_fields_exist(tk)

        # run post install hook
        new_descriptor.run_post_install(tk)

        # ensure that all required frameworks have been installed
        # find the file where our item is being installed
        if framework_name:
            (_, yml_file) = env.find_location_for_framework(framework_name)
        elif app_name:
            (_, yml_file) = env.find_location_for_app(engine_name, app_name)
        else:
            (_, yml_file) = env.find_location_for_engine(engine_name)

        console_utils.ensure_frameworks_installed(
            log, tk, yml_file, new_descriptor, env, self._interaction_interface
        )

        # if we are updating an app, we pass the engine system name to the configuration method
        # so that it can resolve engine based defaults
        parent_engine_system_name = None
        if app_name:
            parent_engine_system_name = env.get_engine_descriptor(
                engine_name
            ).system_name

        # now get data for all new settings values in the config
        params = console_utils.get_configuration(
            log,
            tk,
            new_descriptor,
            old_descriptor,
            self._interaction_interface,
            parent_engine_system_name,
        )

        # awesome. got all the values we need.
        log.info("")
        log.info("")

        # next step is to add the new configuration values to the environment
        if framework_name:
            env.update_framework_settings(
                framework_name, params, new_descriptor.get_dict()
            )
        elif app_name:
            env.update_app_settings(
                engine_name, app_name, params, new_descriptor.get_dict()
            )
        else:
            env.update_engine_settings(engine_name, params, new_descriptor.get_dict())

    def _process_item(
        self,
        log,
        tk,
        env,
        force_upgrade=False,
        engine_name=None,
        app_name=None,
        framework_name=None,
    ):
        """
        Checks if an app/engine/framework is up to date and potentially upgrades it.

        Returns a dictionary with keys:
        - was_updated (bool)
        - old_descriptor
        - new_descriptor (may be None if was_updated is False)
        - app_name
        - engine_name
        - env_name
        """

        if framework_name:
            log.info("Framework %s (Environment %s)" % (framework_name, env.name))

        elif app_name:
            log.info(
                "App %s (Engine %s, Environment %s)" % (app_name, engine_name, env.name)
            )

        else:
            log.info("")
            log.info("-" * 70)
            log.info("Engine %s (Environment %s)" % (engine_name, env.name))

        status = self._check_item_update_status(
            env, engine_name, app_name, framework_name
        )
        item_was_updated = False
        updated_items = []

        if status["skip"]:
            log.info("Skipping %s as it has already been checked." % status["current"])
        elif status["can_update"]:
            new_descriptor = status["latest"]

            required_framework_updates = self._get_framework_requirements(
                log=log, environment=env, descriptor=new_descriptor
            )

            # print summary of changes
            console_utils.format_bundle_info(
                log, new_descriptor, required_framework_updates
            )

            # ask user
            if force_upgrade or self._interaction_interface.ask_yna_question(
                "Update to %s?" % new_descriptor
            ):
                curr_descriptor = status["current"]
                self._update_item(
                    log,
                    tk,
                    env,
                    curr_descriptor,
                    new_descriptor,
                    engine_name,
                    app_name,
                    framework_name,
                )

                # If we have frameworks that need to be updated along with
                # this item, then we do so here. We're suppressing prompts
                # for this because these framework updates are required for
                # the proper functioning of the bundle that was just updated.
                # This will be due to a minimum-required version setting for
                # the bundle in its info.yml that isn't currently satisfied.
                for fw_name in required_framework_updates:
                    updated_items.extend(
                        self._process_item(
                            log, tk, env, force_upgrade=True, framework_name=fw_name
                        )
                    )

                item_was_updated = True

        elif status["out_of_date"] is False and not status["current"].exists_local():
            # app does not exist in the local app download cache area
            if self._interaction_interface.ask_yna_question(
                "Current version does not exist locally - download it now?"
            ):
                log.info("Downloading %s..." % status["current"])
                status["current"].download_local()

        elif status["out_of_date"] is False:
            log.info(
                r" \-- You are running version %s which is the most recent release."
                % status["latest"].version
            )

        else:
            # cannot update for some reason
            log.warning(status["update_status"])

        # return data
        d = {}
        d["was_updated"] = item_was_updated
        d["old_descriptor"] = status["current"]
        d["new_descriptor"] = status["latest"]
        d["app_name"] = app_name
        d["engine_name"] = engine_name
        d["framework_name"] = framework_name
        d["env_name"] = env

        updated_items.append(d)

        # Add the new and current descriptors to the descriptor lookup so that if
        # we come across another instance of the new descriptor we can either skip updating it
        # or at least skip looking up the latest version.
        # We store the status data as well as whether we updated this descriptor or not.

        current_desc_key = self._get_descriptor_dict_lookup(
            status["current"], framework_name
        )
        if current_desc_key not in self._descriptor_look_up:
            self._descriptor_look_up[current_desc_key] = (status, item_was_updated)

        # When we store the latest descriptor to the look up we always say it was not updated
        # so that if we come across it again in a different environment we know to skip it and not update it.
        new_desc_key = self._get_descriptor_dict_lookup(
            status["latest"], framework_name
        )
        if new_desc_key not in self._descriptor_look_up:
            self._descriptor_look_up[new_desc_key] = (status, False)

        return updated_items

    def _get_descriptor_dict_lookup(self, descriptor, framework_name=None):
        """
        Converts the descriptors dictionary into an immutable value that
        can be used as a key in a dictionary.
        If the framework name is provided it will be added to the returned key. This is important for frameworks
        since it is possible to have two descriptors that are the same but have different behaviour.
        For example given the following:

        tk-framework-qtwidgets_v2.9.1:
            location:
                type: app_store
                name: tk-framework-qtwidgets
                version: v2.9.1
        tk-framework-qtwidgets_v2.x.x:
            location:
                type: app_store
                name: tk-framework-qtwidgets
                version: v2.9.1

        One descriptor is already up to date and the other is not so should be updated.
        However the location descriptor itself is the same in both cases, so we need
        to include the framework name so that we can distinguish between them.

        :param descriptor: Descriptor
        :param framework_name: str optional framework name.
        :return: frozenset
        """

        desc_dict = descriptor.get_dict()
        if framework_name:
            desc_dict["framework_name"] = framework_name
        return frozenset(desc_dict.items())

    def _check_item_update_status(
        self, environment_obj, engine_name=None, app_name=None, framework_name=None
    ):
        """
        Checks if an engine or app or framework is up to date.
        Will locate the latest version of the item and run a comparison.
        Will check for constraints and report about these
        (if the new version requires minimum version of shotgun, the core API, etc.)

        Returns a dictionary with the following keys:
        - current:       Current engine descriptor
        - latest:        Latest engine descriptor
        - out_of_date:   Is the current version out of date?
        - deprecated:    Is this item deprecated?
        - can_update:    Can we update?
        - update_status: String with details describing the status.
        """

        parent_engine_desc = None
        version_pattern = None

        if framework_name:
            curr_desc = environment_obj.get_framework_descriptor(framework_name)
            # framework_name follows a convention and is on the form 'frameworkname_version',
            # where version is on the form v1.2.3, v1.2.x, v1.x.x
            version_pattern = framework_name.split("_")[-1]

        elif app_name:
            curr_desc = environment_obj.get_app_descriptor(engine_name, app_name)
            # for apps, also get the descriptor for their parent engine
            parent_engine_desc = environment_obj.get_engine_descriptor(engine_name)

        else:
            curr_desc = environment_obj.get_engine_descriptor(engine_name)

        desc_key = self._get_descriptor_dict_lookup(curr_desc)
        pre_checked_descriptor, was_updated = self._descriptor_look_up.get(
            desc_key, (None, False)
        )
        if not was_updated and pre_checked_descriptor:
            # The cached descriptor was not updated when it was found last time so we should skip it this time as well.
            # Or this descriptor has been updated previously in this same process and we have come across the updated
            # descriptor, in which case it has already been updated and we can skip it.
            # prepare return data
            data = {}
            data["current"] = pre_checked_descriptor["current"]
            data["latest"] = pre_checked_descriptor["latest"]
            data["out_of_date"] = pre_checked_descriptor["out_of_date"]
            data["can_update"] = pre_checked_descriptor["can_update"]
            data["update_status"] = pre_checked_descriptor["update_status"]
            data["skip"] = True

            return data
        elif was_updated and pre_checked_descriptor:
            # Rather than searching for what the latest descriptor should be, use the cached instance of this descriptor
            # we found to grab the latest update descriptor.
            latest_desc = pre_checked_descriptor["latest"]
        else:
            # Descriptor has not previously been cached so we should find the latest version.
            latest_desc = curr_desc.find_latest_version(version_pattern)

        # out of date check
        out_of_date = latest_desc.version != curr_desc.version

        # check deprecation
        (is_dep, dep_msg) = latest_desc.deprecation_status

        if is_dep:
            # we treat deprecation as an out of date that cannot be upgraded!
            out_of_date = True
            can_update = False
            status = (
                "This item has been flagged as deprecated with the following status: %s"
                % dep_msg
            )

        elif not out_of_date:
            can_update = False
            status = "Item is up to date!"

        else:
            # maybe we can update!
            # look at constraints
            try:
                latest_desc.check_version_constraints(
                    pipelineconfig_utils.get_currently_running_api_version(),
                    parent_engine_desc,
                )
            except CheckVersionConstraintsError as e:
                reasons = e.reasons
                reasons.insert(
                    0,
                    "The latest version (%s) of the item requires an upgrade to one "
                    "or more of your installed components." % latest_desc.version,
                )
                status = " ".join(reasons)
                can_update = False
            else:
                status = (
                    "A new version (%s) of the item is available for installation."
                    % latest_desc.version
                )
                can_update = True

        # prepare return data
        data = {}
        data["current"] = curr_desc
        data["latest"] = latest_desc
        data["out_of_date"] = out_of_date
        data["can_update"] = can_update
        data["update_status"] = status
        data["skip"] = False

        return data

    def _get_framework_requirements(self, log, environment, descriptor):
        """
        Returns a list of framework names that will be require updating. This
        is checking the given descriptor's required frameworks for any
        minimum-required versions it might be expecting. Any version
        requirements not already met by the frameworks configured for the
        given environment will be returned by name.

        :param log: The logging handle.
        :param environment: The environment object.
        :param descriptor: The descriptor object to check.

        :returns: A list of framework names requiring update.
                  Example: ["tk-framework-widget_v0.2.x", ...]
        """
        required_frameworks = descriptor.required_frameworks

        if not required_frameworks:
            return []

        env_fw_descriptors = dict()
        env_fw_instances = environment.get_frameworks()

        for fw in env_fw_instances:
            env_fw_descriptors[fw] = environment.get_framework_descriptor(fw)

        frameworks_to_update = []

        for fw in required_frameworks:
            # Example: tk-framework-widget_v0.2.x
            name = "%s_%s" % (fw.get("name"), fw.get("version"))

            min_version = fw.get("minimum_version")

            if not min_version:
                log.debug("No minimum_version setting found for %s" % name)
                continue

            # If we don't have the framework configured then there's
            # not going to be anything for us to check against. It's
            # best to simply continue on.
            if name not in env_fw_descriptors:
                log.warning(
                    "Framework %s isn't configured; unable to check "
                    "its minimum-required version as a result." % name
                )
                continue

            env_fw_version = env_fw_descriptors[name].version

            if env_fw_version == "Undefined":
                log.debug(
                    "Installed framework has no version specified. Not checking "
                    "the bundle's required framework version as a result."
                )
                continue

            if not is_version_number(min_version) or not is_version_number(
                env_fw_version
            ):
                log.warning(
                    "Unable to check minimum-version requirements for %s "
                    "due to one or both version numbers being malformed: "
                    "%s and %s" % (name, min_version, env_fw_version)
                )

            if is_version_newer(min_version, env_fw_version):
                frameworks_to_update.append(name)

        return frameworks_to_update
