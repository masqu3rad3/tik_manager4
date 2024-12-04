# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

r"""
include files management for template.yml

includes
----------------------------------------------------------------------
includes are defined in the following sections in the data structure:

include: path
includes: [path, path]


paths are on the following form:
----------------------------------------------------------------------
foo/bar.yml - local path, relative to current file

/foo/bar/hello.yml - absolute path, *nix
c:\foo\bar\hello.yml - absolute path, windows

"""

import os

from .errors import TankError
from . import constants
from .util import yaml_cache
from .util.includes import resolve_include
from tank_vendor import six


def _get_includes(file_name, data):
    """
    Parse the includes section and return a list of valid paths

    :param str file_name: Name of the file to parse.
    :param aray or str data: Include path or array of include paths to evaluate.
    """
    includes = []

    resolved_includes = list()

    if constants.SINGLE_INCLUDE_SECTION in data:
        # single include section
        includes.append(data[constants.SINGLE_INCLUDE_SECTION])

    if constants.MULTI_INCLUDE_SECTION in data:
        # multi include section
        includes.extend(data[constants.MULTI_INCLUDE_SECTION])

    for include in includes:
        resolved = resolve_include(file_name, include)
        if resolved and resolved not in resolved_includes:
            resolved_includes.append(resolved)

    return resolved_includes


def _process_template_includes_r(file_name, data):
    """
    Recursively add template include files.

    For each of the sections keys, strings, path, populate entries based on
    include files.
    """

    # return data
    output_data = {}
    # add items for keys, paths, strings etc
    for ts in constants.TEMPLATE_SECTIONS:
        output_data[ts] = {}

    if data is None:
        return output_data

    # process includes
    included_paths = _get_includes(file_name, data)

    for included_path in included_paths:
        included_data = (
            yaml_cache.g_yaml_cache.get(included_path, deepcopy_data=False) or dict()
        )

        # before doing any type of processing, allow the included data to be resolved.
        included_data = _process_template_includes_r(included_path, included_data)

        # add the included data's different sections
        for ts in constants.TEMPLATE_SECTIONS:
            if ts in included_data:
                output_data[ts].update(included_data[ts])

    # now all include data has been added into the data structure.
    # now add the template data itself
    for ts in constants.TEMPLATE_SECTIONS:
        if ts in data:
            output_data[ts].update(data[ts])

    return output_data


def process_includes(file_name, data):
    """
    Processes includes for the main templates file. Will look for
    any include data structures and transform them into real data.

    Algorithm (recursive):

    1. first load in include data into keys, strings, path sections.
       if there are multiple files, they are loaded in order.
    2. now, on top of this, load in this file's keys, strings and path defs
    3. lastly, process all @refs in the paths section

    """
    # first recursively load all template data from includes
    resolved_includes_data = _process_template_includes_r(file_name, data)

    # Now recursively process any @resolves.
    # these are of the following form:
    #   foo: bar
    #   ttt: @foo/something
    # You can only use these in the paths and strings sections.
    #
    # @ can be used anywhere in the template definition.  @ should
    # be used to escape itself if required.  e.g.:
    #   foo: bar
    #   ttt: @foo/something/@@/_@foo_
    # Would result in:
    #   bar/something/@/_bar_
    template_paths = resolved_includes_data[constants.TEMPLATE_PATH_SECTION]
    template_strings = resolved_includes_data[constants.TEMPLATE_STRING_SECTION]

    # process the template paths section:
    for template_name, template_definition in template_paths.items():
        _resolve_template_r(
            template_paths, template_strings, template_name, template_definition, "path"
        )

    # and process the strings section:
    for template_name, template_definition in template_strings.items():
        _resolve_template_r(
            template_paths,
            template_strings,
            template_name,
            template_definition,
            "string",
        )

    # finally, resolve escaped @'s in template definitions:
    for templates in [template_paths, template_strings]:
        for template_name, template_definition in templates.items():
            # find the template string from the definition:
            template_str = None
            complex_syntax = False
            if isinstance(template_definition, dict):
                template_str = template_definition.get("definition")
                complex_syntax = True
            elif isinstance(template_definition, six.string_types):
                template_str = template_definition
            if not template_str:
                raise TankError(
                    "Invalid template configuration for '%s' - "
                    "it looks like the definition is missing!" % (template_name)
                )

            # resolve escaped @'s
            resolved_template_str = template_str.replace("@@", "@")
            if resolved_template_str == template_str:
                continue

            # set the value back again:
            if complex_syntax:
                templates[template_name]["definition"] = resolved_template_str
            else:
                templates[template_name] = resolved_template_str

    return resolved_includes_data


def _find_matching_ref_template(template_paths, template_strings, ref_string):
    """
    Find a template whose name matches a portion of ref_string.  This
    will find the longest/best match and will look at both path and string
    templates
    """
    matching_templates = []

    # find all templates that match the start of the ref string:
    for templates, template_type in [
        (template_paths, "path"),
        (template_strings, "string"),
    ]:
        for name, definition in templates.items():
            if ref_string.startswith(name):
                matching_templates.append((name, definition, template_type))

    # if there are more than one then choose the one with the longest
    # name/longest match:
    best_match = None
    best_match_len = 0
    for name, definition, template_type in matching_templates:
        name_len = len(name)
        if name_len > best_match_len:
            best_match_len = name_len
            best_match = (name, definition, template_type)

    return best_match


def _resolve_template_r(
    template_paths,
    template_strings,
    template_name,
    template_definition,
    template_type,
    template_chain=None,
):
    """
    Recursively resolve path templates so that they are fully expanded.
    """

    # check we haven't searched this template before and keep
    # track of the ones we have visited
    template_key = (template_name, template_type)
    visited_templates = list(template_chain or [])
    if template_key in visited_templates:
        raise TankError(
            "A cyclic %s template was found - '%s' references itself (%s)"
            % (
                template_type,
                template_name,
                " -> ".join(
                    [
                        name
                        for name, _ in visited_templates[
                            visited_templates.index(template_key) :
                        ]
                    ]
                    + [template_name]
                ),
            )
        )
    visited_templates.append(template_key)

    # find the template string from the definition:
    template_str = None
    complex_syntax = False
    if isinstance(template_definition, dict):
        template_str = template_definition.get("definition")
        complex_syntax = True
    elif isinstance(template_definition, six.string_types):
        template_str = template_definition
    if not template_str:
        raise TankError(
            "Invalid template configuration for '%s' - it looks like the "
            "definition is missing!" % (template_name)
        )

    # look for @ specified in template definition.  This can be escaped by
    # using @@ so split out escaped @'s first:
    template_str_parts = template_str.split("@@")
    resolved_template_str_parts = []
    for part in template_str_parts:

        # split to find seperate @ include parts:
        ref_parts = part.split("@")
        resolved_ref_parts = ref_parts[:1]
        for ref_part in ref_parts[1:]:

            if not ref_part:
                # this would have been an @ so ignore!
                continue

            # find a template that matches the start of the template string:
            ref_template = _find_matching_ref_template(
                template_paths, template_strings, ref_part
            )
            if not ref_template:
                raise TankError(
                    "Failed to resolve template reference from '@%s' defined by "
                    "the %s template '%s'" % (ref_part, template_type, template_name)
                )

            # resolve the referenced template:
            ref_template_name, ref_template_definition, ref_template_type = ref_template
            resolved_ref_str = _resolve_template_r(
                template_paths,
                template_strings,
                ref_template_name,
                ref_template_definition,
                ref_template_type,
                visited_templates,
            )
            resolved_ref_str = "%s%s" % (
                resolved_ref_str,
                ref_part[len(ref_template_name) :],
            )

            resolved_ref_parts.append(resolved_ref_str)

        # rejoin resolved parts:
        resolved_template_str_parts.append("".join(resolved_ref_parts))

    # re-join resolved parts with escaped @:
    resolved_template_str = "@@".join(resolved_template_str_parts)

    # put the value back:
    templates = {"path": template_paths, "string": template_strings}[template_type]
    if complex_syntax:
        templates[template_name]["definition"] = resolved_template_str
    else:
        templates[template_name] = resolved_template_str

    return resolved_template_str
