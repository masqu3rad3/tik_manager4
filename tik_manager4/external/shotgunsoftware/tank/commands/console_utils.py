# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Various helper methods relating to user interaction via the shell.
"""
from __future__ import print_function

import textwrap

from .. import pipelineconfig_utils
from ..platform import validation
from ..errors import TankError, TankNoDefaultValueError
from ..descriptor import CheckVersionConstraintsError
from ..platform.bundle import resolve_default_value


##########################################################################################
# displaying of info in the terminal, ascii-graphcics style


def format_bundle_info(log, descriptor, required_updates=None):
    """
    Formats a release notes summary output for an app, engine or core.

    :param log: A logging handle.
    :param descriptor: The descriptor to summarize.
    :param required_updates: A list of bundle names that require updating.
    """
    # yay we can install! - get release notes
    (summary, url) = descriptor.changelog

    if required_updates:
        add_padding = "     "
    else:
        add_padding = ""

    if summary is None:
        summary = "No details provided."

    log.info("/%s" % ("-" * 70))
    log.info("| Item:        %s%s" % (add_padding, descriptor))
    log.info("|")

    str_to_wrap = "Description: %s%s" % (add_padding, descriptor.description)
    description = textwrap.wrap(
        str_to_wrap,
        width=68,
        initial_indent="| ",
        subsequent_indent="|              %s" % add_padding,
    )

    for x in description:
        log.info(x)

    log.info("|")
    str_to_wrap = "Change Log:  %s%s" % (add_padding, summary)
    change_log = textwrap.wrap(
        str_to_wrap,
        width=68,
        initial_indent="| ",
        subsequent_indent="|              %s" % add_padding,
    )

    for x in change_log:
        log.info(x)

    if required_updates:
        log.info("|")
        name = required_updates[0]
        fw_str = "| Required Updates: %s" % name
        log.info(fw_str)

        for name in required_updates[1:]:
            log.info("|                   %s" % name)

    log.info(r"\%s" % ("-" * 70))


def get_configuration(
    log,
    tank_api_instance,
    new_descriptor,
    old_descriptor,
    interaction_interface,
    parent_engine_name,
):
    """
    Retrieves all the parameters needed for an app, engine or framework.
    May prompt the user for information.

    For apps only, the parent_engine_name will contain the system name (e.g. tk-maya, tk-nuke) for
    the engine under which the app is parented. This is so that the configuration defaults logic
    can resolve parameter values based on engine, for example the {engine_name} token used in
    hook settings.

    Returns a hierarchical dictionary of param values to use:

    {param1:value, param2:value, param3:{child_param1:value, child_param2:value}}
    """

    # first get data for all new settings values in the config
    param_diff = _generate_settings_diff(
        parent_engine_name, new_descriptor, old_descriptor
    )

    if len(param_diff) > 0:
        log.info("Several new settings are associated with %s." % new_descriptor)
        log.info("You will now be prompted to input values for all settings")
        log.info("that do not have default values defined.")
        log.info("")

        # recurse over new parameters:
        params = _get_configuration_recursive(
            log,
            tank_api_instance,
            new_descriptor,
            param_diff,
            interaction_interface,
            parent_engine_name,
        )

    else:
        # nothing new!
        params = {}

    return params


def _get_configuration_recursive(
    log,
    tank_api_instance,
    new_ver_descriptor,
    params,
    interaction_interface,
    parent_engine_name,
    parent_path=None,
):
    """
    Retrieves all the parameters needed for an app, engine or framework.
    May prompt the user for information.

    Only values for leaf level parameters are retrieved.
    """
    parent_path = parent_path or []

    param_values = {}
    for param_name, param_data in params.items():
        if "children" in param_data:
            # recurse to children:
            param_path = list(parent_path) + [
                "%s (type: %s)" % (param_name, param_data["type"])
            ]
            child_params = _get_configuration_recursive(
                log,
                tank_api_instance,
                new_ver_descriptor,
                param_data["children"],
                interaction_interface,
                parent_engine_name,
                param_path,
            )
            param_values[param_name] = child_params

        else:

            # leaf param so need to get value:
            param_path = list(parent_path) + [param_name]

            # output info about the setting
            log.info("")
            log.info("/%s" % ("-" * 70))
            log.info("| Item:    %s" % param_path[0])
            for level, name in enumerate(param_path[1:]):
                log.info(r"|          %s  \ %s" % ("  " * level, name))
            log.info("| Type:    %s" % param_data["type"])
            str_to_wrap = "Summary: %s" % param_data["description"]
            for x in textwrap.wrap(
                str_to_wrap,
                width=68,
                initial_indent="| ",
                subsequent_indent="|          ",
            ):
                log.info(x)
            log.info(r"\%s" % ("-" * 70))

            if "value" in param_data:
                # default value in param data, just log the info for the user
                default_value = param_data["value"]
                log.info("Using default value '%s'" % (str(default_value),))
            else:
                # no default value in the param_data, prompt the user
                if not interaction_interface.supports_interaction:
                    log.warning(
                        "No default value! Please update the environment by hand later!"
                    )
                    param_values[param_name] = None
                    continue

                # get value from user
                # loop around until happy
                input_valid = False
                while not input_valid:
                    # ask user
                    answer = interaction_interface.request_input(
                        "Please enter value (enter to skip):"
                    )
                    if answer == "":
                        # user chose to skip
                        log.warning(
                            "You skipped this value! Please update the environment by hand later!"
                        )
                        param_values[param_name] = None
                        input_valid = True
                    else:
                        # validate value
                        try:
                            obj_value = _validate_parameter(
                                tank_api_instance,
                                new_ver_descriptor,
                                param_name,
                                answer,
                            )
                        except Exception as e:
                            log.error("Validation failed: %s" % e)
                        else:
                            input_valid = True
                            param_values[param_name] = obj_value

    return param_values


def ensure_frameworks_installed(
    log,
    tank_api_instance,
    file_location,
    descriptor,
    environment,
    interaction_interface,
):
    """
    Recursively check that all required frameworks are installed.
    Anything not installed will be downloaded from the app store.
    """

    missing_fws = validation.get_missing_frameworks(
        descriptor, environment, file_location
    )

    # this returns dictionaries with name and version keys, the way
    # they are defined in the manifest for that descriptor
    # [{'version': 'v0.1.x', 'name': 'tk-framework-widget'}]

    installed_fw_descriptors = []

    # first pass: install all frameworks that are required by this descriptor
    for fw_dict in missing_fws:

        name = fw_dict["name"]
        version_pattern = fw_dict["version"]

        # version pattern number can be on the following forms:
        # - exact and arbitrary, but not containing an x: v0.1.2, v0.1.2.34, v0.12.3b
        # - minor: v1.x.x
        # - increment: v1.2.x

        # get the latest version from the app store by
        # first getting a stub and then looking for latest.
        location_stub = {"type": "app_store", "name": name}

        pc = tank_api_instance.pipeline_configuration

        fw_descriptor = pc.get_latest_framework_descriptor(
            location_stub, version_pattern
        )

        installed_fw_descriptors.append(fw_descriptor)

        # and now process this framework
        log.info(
            "Installing required framework %s %s. Downloading %s..."
            % (name, version_pattern, fw_descriptor)
        )
        if not fw_descriptor.exists_local():
            fw_descriptor.download_local()

        # now assume a convention where we will name the fw_instance that we create in the environment
        # on the form name_version
        fw_instance_name = "%s_%s" % (name, version_pattern)

        # now make sure all constraints are okay
        try:
            check_constraints_for_item(fw_descriptor, environment)
        except TankError as e:
            raise TankError("Cannot install framework: %s" % e)

        # okay to install!

        # create required shotgun fields
        fw_descriptor.ensure_shotgun_fields_exist(tank_api_instance)

        # run post install hook
        fw_descriptor.run_post_install(tank_api_instance)

        # now get data for all new settings values in the config
        params = get_configuration(
            log, tank_api_instance, fw_descriptor, None, interaction_interface, None
        )

        # next step is to add the new configuration values to the environment
        environment.create_framework_settings(
            file_location, fw_instance_name, params, fw_descriptor.get_dict()
        )

    # second pass: For all the missing frameworks that were installed, ensure that these in turn also
    # have their dependency requirements satisfied...
    for fw_descriptor in installed_fw_descriptors:
        ensure_frameworks_installed(
            log,
            tank_api_instance,
            file_location,
            fw_descriptor,
            environment,
            interaction_interface,
        )


def check_constraints_for_item(descriptor, environment_obj, engine_instance_name=None):
    """
    Validates the constraints for a single item. This will check that requirements for
    minimum versions for shotgun, core API etc are fulfilled.

    Raises a TankError if one or more constraints are blocking. The exception message
    will contain details.
    """

    # get the parent engine descriptor, if we are checking an app
    if engine_instance_name:
        # we are checking an engine object (it has no parent engine)
        parent_engine_descriptor = environment_obj.get_engine_descriptor(
            engine_instance_name
        )
    else:
        parent_engine_descriptor = None

    # check constraints (minimum versions etc)
    try:
        descriptor.check_version_constraints(
            pipelineconfig_utils.get_currently_running_api_version(),
            parent_engine_descriptor,
        )
    except CheckVersionConstraintsError as e:
        reasons = e.reasons[:]
        reasons.insert(
            0,
            "%s requires an upgrade to one or more "
            "of your installed components." % descriptor,
        )
        details = " ".join(reasons)
        raise TankError(details)


##########################################################################################
# helpers


def _generate_settings_diff(parent_engine_name, new_descriptor, old_descriptor=None):
    """
    Returns a list of settings which are needed if we were to upgrade
    an environment based on old_descriptor to the one based on new_descriptor.

    Settings in the config which have default values will have their values
    populated in the return data structures.

    By omitting old_descriptor you will effectively diff against nothing, meaning
    that all the settings for the new version of the item (except default ones)
    will be part of the listing.

    For apps, the parent_engine_name parameter is passed in. This holds the value
    of the system name for the parent engine (e.g. tk-maya, tk-nuke) and is used
    to resolve engine specific default values.

    Returns a hierarchical dictionary containing details for each new parameter and
    where it exists in the tree, e.g.:

    {
        "param1": {"description" : "a required param (no default)", "type": "str", value: None }
        "param2": {"description" : "an optional param (has default)", "type": "int", value: 123 }
        "param3": {"description" : "param with new children", "type" : "dict", "children" : {
                    "child_param1" : {"description" : "a child param", "type": "str", value: "foo" }
                    "child_param2" : {"description" : "another child param", "type": "int", value: 123 }
                    }
    }
    """
    # get the new metadata (this will download the app potentially)
    schema = new_descriptor.configuration_schema
    old_schema = {}
    if old_descriptor is not None:
        try:
            old_schema = old_descriptor.configuration_schema
        except TankError:
            # download to local failed? Assume that the old version is
            # not valid. This is an edge case.
            old_schema = {}

    # find all new config parameters
    new_parameters = _generate_settings_diff_recursive(
        parent_engine_name, old_schema, schema
    )
    return new_parameters


def _generate_settings_diff_recursive(parent_engine_name, old_schema, new_schema):
    """
    Recursively find all parameters in new_schema that don't exist in old_schema.

    Returns a hierarchical dictionary containing details for each new parameter and
    where it exists in the tree, e.g.:

    {
        "param1": {"description" : "a required param (no default)", "type": "str", value: None }
        "param2": {"description" : "an optional param (has default)", "type": "int", value: 123 }
        "param3": {"description" : "param with new children", "type" : "dict", "children" : {
                    "child_param1" : {"description" : "a child param", "type": "str", value: "foo" }
                    "child_param2" : {"description" : "another child param", "type": "int", value: 123 }
                    }
    }

    Only leaf parameters should be considered 'new'.
    """

    new_params = {}

    for param_name, new_param_definition_dict in new_schema.items():

        param_type = new_param_definition_dict.get("type", "Unknown")
        param_desc = new_param_definition_dict.get("description", "No description.")

        old_param_definition_dict = old_schema.get(param_name)

        if not old_param_definition_dict:
            # found a new param:
            new_params[param_name] = {"description": param_desc, "type": param_type}

            # attempt to resolve a default value from the new parameter def.
            try:
                default_value = resolve_default_value(
                    new_param_definition_dict, parent_engine_name, raise_if_missing=True
                )
            except TankNoDefaultValueError:
                # No default value exists. We won't add it to the dict.
                # It will be prompted for later.
                pass
            else:
                new_params[param_name]["value"] = default_value

        else:
            if old_param_definition_dict.get("type", "Unknown") != param_type:
                # param type has been changed - currently we don't handle this!
                continue

            if param_type == "dict":
                # compare schema items for new and old params:
                new_items = new_param_definition_dict.get("items", {})
                old_items = old_param_definition_dict.get("items", {})

                new_child_params = _generate_settings_diff_recursive(
                    parent_engine_name, old_items, new_items
                )
                if new_child_params:
                    new_params[param_name] = {
                        "description": param_desc,
                        "type": param_type,
                        "children": new_child_params,
                    }
            elif param_type == "list":
                # check to see if this is a list of dicts:
                new_list_param_values = new_param_definition_dict.get("values", {})
                old_list_param_values = old_param_definition_dict.get("values", {})
                new_list_param_values_type = new_list_param_values.get("type")

                if new_list_param_values_type != old_list_param_values.get("type"):
                    # list param type has changed - currently we don't handle this!
                    continue

                if new_list_param_values_type == "dict":
                    new_items = new_list_param_values.get("items", {})
                    old_items = old_list_param_values.get("items", {})

                    new_child_params = _generate_settings_diff_recursive(
                        parent_engine_name, old_items, new_items
                    )
                    if new_child_params:
                        new_params[param_name] = {
                            "description": param_desc,
                            "type": param_type,
                            "children": new_child_params,
                        }
                elif new_list_param_values_type == "list":
                    # lists of lists are currently not handled!
                    continue

    return new_params


def _validate_parameter(tank_api_instance, descriptor, parameter, str_value):
    """
    Convenience wrapper. Validates a single parameter.
    Will raise exceptions if validation fails.
    Returns the object-ified value on success.
    """

    schema = descriptor.configuration_schema
    # get the type for the param we are dealing with
    schema_type = schema.get(parameter, {}).get("type", "unknown")
    # now convert string value input to objet (int, string, dict etc)
    obj_value = validation.convert_string_to_type(str_value, schema_type)
    # finally validate this object against the schema
    validation.validate_single_setting(
        descriptor.display_name, tank_api_instance, schema, parameter, obj_value
    )

    # we are here, must mean we are good to go!
    return obj_value
