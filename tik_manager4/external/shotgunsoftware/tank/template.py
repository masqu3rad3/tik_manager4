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
Management of file and directory templates.

"""

import os

from . import templatekey
from .errors import TankError
from . import constants
from .template_path_parser import TemplatePathParser
from tank_vendor import six
from tank_vendor.shotgun_api3.lib import sgsix
from tank_vendor.six.moves import zip
from tank.util import is_linux, is_macos, is_windows, sgre as re


class Template(object):
    """
    Represents an expression containing several dynamic tokens
    in the form of :class:`TemplateKey` objects.
    """

    @classmethod
    def _keys_from_definition(cls, definition, template_name, keys):
        """Extracts Template Keys from a definition.

        :param definition: Template definition as string
        :param template_name: Name of template.
        :param keys: Mapping of key names to keys as dict

        :returns: Mapping of key names to keys and collection of keys ordered as they appear in the definition.
        :rtype: List of Dictionaries, List of lists
        """
        names_keys = {}
        ordered_keys = []
        # regular expression to find key names
        regex = r"(?<={)%s(?=})" % constants.TEMPLATE_KEY_NAME_REGEX
        key_names = re.findall(regex, definition)
        for key_name in key_names:
            key = keys.get(key_name)
            if key is None:
                msg = "Template definition for template %s refers to key {%s}, which does not appear in supplied keys."
                raise TankError(msg % (template_name, key_name))
            else:
                if names_keys.get(key.name, key) != key:
                    # Different keys using same name
                    msg = (
                        "Template definition for template %s uses two keys"
                        + " which use the name '%s'."
                    )
                    raise TankError(msg % (template_name, key.name))
                names_keys[key.name] = key
                ordered_keys.append(key)
        return names_keys, ordered_keys

    def __init__(self, definition, keys, name=None):
        """
        This class is not designed to be used directly but
        should be subclassed by any Template implementations.

        Current implementations can be found in
        the :class:`TemplatePath` and :class:`TemplateString` classes.

        :param definition: Template definition.
        :type definition: String
        :param keys: Mapping of key names to keys
        :type keys: Dictionary
        :param name: (Optional) name for this template.
        :type name: String
        """
        self.name = name
        # version for __repr__
        self._repr_def = self._fix_key_names(definition, keys)

        variations = self._definition_variations(definition)
        # We want them most inclusive(longest) version first
        variations.sort(key=lambda x: len(x), reverse=True)

        # get format keys and types
        self._keys = []
        self._ordered_keys = []
        for variation in variations:
            var_keys, ordered_keys = self._keys_from_definition(variation, name, keys)
            self._keys.append(var_keys)
            self._ordered_keys.append(ordered_keys)

        # substitute aliased key names
        self._definitions = []
        for variation in variations:
            self._definitions.append(self._fix_key_names(variation, keys))

        # get defintion ready for string substitution
        self._cleaned_definitions = []
        for definition in self._definitions:
            self._cleaned_definitions.append(self._clean_definition(definition))

        # string which will be prefixed to definition
        self._prefix = ""
        self._static_tokens = []

    def __repr__(self):
        class_name = self.__class__.__name__
        if self.name:
            return "<Sgtk %s %s: %s>" % (class_name, self.name, self._repr_def)
        else:
            return "<Sgtk %s %s>" % (class_name, self._repr_def)

    @property
    def definition(self):
        """
        The template as a string, e.g ``shots/{Shot}/{Step}/pub/{name}.v{version}.ma``
        """
        # Use first definition as it should be most inclusive in case of variations
        return self._definitions[0]

    @property
    def keys(self):
        """
        The keys that this template is using. For a template
        ``shots/{Shot}/{Step}/pub/{name}.v{version}.ma``, the keys are ``{Shot}``,
        ``{Step}`` and ``{name}``.

        :returns: a dictionary of class:`TemplateKey` objects, keyed by token name.
        """
        # First keys should be most inclusive
        return self._keys[0].copy()

    @property
    def ordered_keys(self):
        """
        The keys that this template is using in the order they appear. For a
        template ``shots/{Shot}/{Step}/pub/{name}.v{version}.ma``, the keys are
        ``{Shot}``, ``{Step}`` and ``{name}``.

        :returns: a list of class:`TemplateKey` objects.
        """
        # First keys should be most inclusive.  Return a copy of the list by
        # instantiating a new list from it.
        return list(self._ordered_keys[0])

    def is_optional(self, key_name):
        """
        Returns true if the given key name is optional for this template.

        For the template ``{Shot}[_{name}]``,
        ``is_optional("Shot")`` would return ``False`` and ``is_optional("name")``
        would return ``True``

        :param key_name: Name of template key for which the check should be carried out
        :returns: True if key is optional, False if not.
        """
        # the key is required if it's in the
        # minimum set of keys for this template
        if key_name in min(self._keys, key=lambda i: len(i.keys())):
            # this key is required
            return False
        else:
            return True

    def missing_keys(self, fields, skip_defaults=False):
        """
        Determines keys required for use of template which do not exist
        in a given fields.

        Example::

            >>> tk.templates["max_asset_work"].missing_keys({})
            ['Step', 'sg_asset_type', 'Asset', 'version', 'name']

            >>> tk.templates["max_asset_work"].missing_keys({"name": "foo"})
            ['Step', 'sg_asset_type', 'Asset', 'version']


        :param fields: fields to test
        :type fields: mapping (dictionary or other)
        :param skip_defaults: If true, do not treat keys with default values as missing.
        :type skip_defaults: Bool

        :returns: Fields needed by template which are not in inputs keys or which have
                  values of None.
        :rtype: list
        """
        # find shortest keys dictionary
        keys = min(self._keys, key=lambda i: len(i.keys()))
        return self._missing_keys(fields, keys, skip_defaults)

    def _missing_keys(self, fields, keys, skip_defaults):
        """
        Compares two dictionaries to determine keys in second missing in first.

        :param fields: fields to test
        :param keys: Dictionary of template keys to test
        :param skip_defaults: If true, do not treat keys with default values as missing.
        :returns: Fields needed by template which are not in inputs keys or which have
                  values of None.
        """
        if skip_defaults:
            required_keys = [key.name for key in keys.values() if key.default is None]
        else:
            required_keys = keys

        return [x for x in required_keys if (x not in fields) or (fields[x] is None)]

    def apply_fields(self, fields, platform=None):
        r"""
        Creates path using fields. Certain fields may be processed in special ways, for
        example :class:`SequenceKey` fields, which can take a `FORMAT` string which will intelligently
        format a image sequence specifier based on the type of data is being handled. Example::

            # get a template object from the API
            >>> template_obj = sgtk.templates["maya_shot_publish"]
            <Sgtk Template maya_asset_project: shots/{Shot}/{Step}/pub/{name}.v{version}.ma>

            >>> fields = {'Shot': '001_002',
                          'Step': 'comp',
                          'name': 'main_scene',
                          'version': 3
                          }

            >>> template_obj.apply_fields(fields)
            '/projects/bbb/shots/001_002/comp/pub/main_scene.v003.ma'

        .. note:: For formatting of special values, see :class:`SequenceKey` and :class:`TimestampKey`.

        Example::

            >>> fields = {"Sequence":"seq_1", "Shot":"shot_2", "Step":"comp", "name":"henry", "version":3}

            >>> template_path.apply_fields(fields)
            '/studio_root/sgtk/demo_project_1/sequences/seq_1/shot_2/comp/publish/henry.v003.ma'

            >>> template_path.apply_fields(fields, platform='win32')
            'z:\studio_root\sgtk\demo_project_1\sequences\seq_1\shot_2\comp\publish\henry.v003.ma'

            >>> template_str.apply_fields(fields)
            'Maya Scene henry, v003'


        :param fields: Mapping of keys to fields. Keys must match those in template
                       definition.
        :param platform: Optional operating system platform. If you leave it at the
                         default value of None, paths will be created to match the
                         current operating system. If you pass in a sys.platform-style string
                         (e.g. ``win32``, ``linux2`` or ``darwin``), paths will be generated to
                         match that platform.

        :returns: Full path, matching the template with the given fields inserted.
        """
        return self._apply_fields(fields, platform=platform)

    def _apply_fields(
        self, fields, ignore_types=None, platform=None, skip_defaults=False
    ):
        """
        Creates path using fields.

        :param fields: Mapping of keys to fields. Keys must match those in template
                       definition.
        :param ignore_types: Keys for whom the defined type is ignored as list of strings.
                            This allows setting a Key whose type is int with a string value.
        :param platform: Optional operating system platform. If you leave it at the
                         default value of None, paths will be created to match the
                         current operating system. If you pass in a sys.platform-style string
                         (e.g. 'win32', 'linux2' or 'darwin'), paths will be generated to
                         match that platform.
        :param skip_defaults: Optional. If set to True, if a key has a default value and no
                              corresponding value in the fields argument, its default value
                              will be used. If set to False, keys that are not specified in
                              the fields argument are skipped whether they have a default
                              value or not. Defaults to False

        :returns: Full path, matching the template with the given fields inserted.
        """
        ignore_types = ignore_types or []

        # find largest key mapping without missing values
        keys = None
        # index of matching keys will be used to find cleaned_definition
        index = -1
        for index, cur_keys in enumerate(self._keys):
            # We are iterating through all possible key combinations from the longest to shortest
            # and using the first one that doesn't have any missing keys. skip_defaults=False on
            # _apply_fields means we don't want to use a key that is not specified in the fields
            # parameter. So we want the missing_keys function to flag even the default keys that are
            # missing. Therefore we need to negate the skip_defaults parameter for the _missing_keys argument
            missing_keys = self._missing_keys(
                fields, cur_keys, skip_defaults=not skip_defaults
            )
            if not missing_keys:
                keys = cur_keys
                break

        if keys is None:
            raise TankError(
                "Tried to resolve a path from the template %s and a set "
                "of input fields '%s' but the following required fields were missing "
                "from the input: %s" % (self, fields, missing_keys)
            )

        # Process all field values through template keys
        processed_fields = {}
        for key_name, key in keys.items():
            value = fields.get(key_name)
            ignore_type = key_name in ignore_types
            processed_fields[key_name] = key.str_from_value(
                value, ignore_type=ignore_type
            )

        return self._cleaned_definitions[index] % processed_fields

    def _definition_variations(self, definition):
        """
        Determines all possible definition based on combinations of optional sectionals.

        "{foo}"               ==> ['{foo}']
        "{foo}_{bar}"         ==> ['{foo}_{bar}']
        "{foo}[_{bar}]"       ==> ['{foo}', '{foo}_{bar}']
        "{foo}_[{bar}_{baz}]" ==> ['{foo}_', '{foo}_{bar}_{baz}']

        """
        # split definition by optional sections
        tokens = re.split(r"(\[[^]]*\])", definition)

        # seed with empty string
        definitions = [""]
        for token in tokens:
            temp_definitions = []
            # regex return some blank strings, skip them
            if token == "":
                continue
            if token.startswith("["):
                # check that optional contains a key
                if not re.search("{*%s}" % constants.TEMPLATE_KEY_NAME_REGEX, token):
                    raise TankError(
                        'Optional sections must include a key definition. Token: "%s" Template: %s'
                        % (token, self)
                    )

                # Add definitions skipping this optional value
                temp_definitions = definitions[:]
                # strip brackets from token
                token = re.sub(r"[\[\]]", "", token)

            # check non-optional contains no dangleing brackets
            if re.search(r"[\[\]]", token):
                raise TankError(
                    "Square brackets are not allowed outside of optional section definitions."
                )

            # make defintions with token appended
            for definition in definitions:
                temp_definitions.append(definition + token)

            definitions = temp_definitions

        return definitions

    def _fix_key_names(self, definition, keys):
        """
        Substitutes key name for name used in definition
        """
        # Substitute key names for original key input names(key aliasing)
        substitutions = [
            (key_name, key.name)
            for key_name, key in keys.items()
            if key_name != key.name
        ]
        for old_name, new_name in substitutions:
            old_def = r"{%s}" % old_name
            new_def = r"{%s}" % new_name
            definition = re.sub(old_def, new_def, definition)
        return definition

    def _clean_definition(self, definition):
        # Create definition with key names as strings with no format, enum or default values
        regex = r"{(%s)}" % constants.TEMPLATE_KEY_NAME_REGEX
        cleaned_definition = re.sub(regex, r"%(\g<1>)s", definition)
        return cleaned_definition

    def _calc_static_tokens(self, definition):
        """
        Finds the tokens from a definition which are not involved in defining keys.
        """
        # expand the definition to include the prefix unless the definition is empty in which
        # case we just want to parse the prefix.  For example, in the case of a path template,
        # having an empty definition would result in expanding to the project/storage root
        expanded_definition = (
            os.path.join(self._prefix, definition) if definition else self._prefix
        )
        regex = r"{%s}" % constants.TEMPLATE_KEY_NAME_REGEX
        tokens = re.split(regex, expanded_definition.lower())
        # Remove empty strings
        return [x for x in tokens if x]

    @property
    def parent(self):
        """
        Returns Template representing the parent of this object.

        :returns: :class:`Template`
        """
        raise NotImplementedError

    def validate_and_get_fields(self, path, required_fields=None, skip_keys=None):
        """
        Takes an input string and determines whether it can be mapped to the template pattern.
        If it can then the list of matching fields is returned. Example::

            >>> good_path = '/studio_root/sgtk/demo_project_1/sequences/seq_1/shot_2/comp/publish/henry.v003.ma'
            >>> template_path.validate_and_get_fields(good_path)
            {'Sequence': 'seq_1',
             'Shot': 'shot_2',
             'Step': 'comp',
             'name': 'henry',
             'version': 3}

            >>> bad_path = '/studio_root/sgtk/demo_project_1/shot_2/comp/publish/henry.v003.ma'
            >>> template_path.validate_and_get_fields(bad_path)
            None


        :param path:            Path to validate
        :param required_fields: An optional dictionary of key names to key values. If supplied these values must
                                be present in the input path and found by the template.
        :param skip_keys:       List of field names whose values should be ignored

        :returns:               Dictionary of fields found from the path or None if path fails to validate
        """
        required_fields = required_fields or {}
        skip_keys = skip_keys or []

        # Path should split into keys as per template
        path_fields = {}
        try:
            path_fields = self.get_fields(path, skip_keys=skip_keys)
        except TankError:
            return None

        # Check that all required fields were found in the path:
        for key, value in required_fields.items():
            if (key not in skip_keys) and (path_fields.get(key) != value):
                return None

        return path_fields

    def validate(self, path, fields=None, skip_keys=None):
        """
        Validates that a path can be mapped to the pattern given by the template. Example::

            >>> good_path = '/studio_root/sgtk/demo_project_1/sequences/seq_1/shot_2/comp/publish/henry.v003.ma'
            >>> template_path.validate(good_path)
            True

            >>> bad_path = '/studio_root/sgtk/demo_project_1/shot_2/comp/publish/henry.v003.ma'
            >>> template_path.validate(bad_path)
            False

        :param path:        Path to validate
        :type path:         String
        :param fields:      An optional dictionary of key names to key values. If supplied these values must
                            be present in the input path and found by the template.
        :type fields:       Dictionary
        :param skip_keys:   Field names whose values should be ignored
        :type skip_keys:    List
        :returns:           True if the path is valid for this template
        :rtype:             Bool
        """
        return self.validate_and_get_fields(path, fields, skip_keys) != None

    def get_fields(self, input_path, skip_keys=None):
        """
        Extracts key name, value pairs from a string. Example::

            >>> input_path = '/studio_root/sgtk/demo_project_1/sequences/seq_1/shot_2/comp/publish/henry.v003.ma'
            >>> template_path.get_fields(input_path)

            {'Sequence': 'seq_1',
             'Shot': 'shot_2',
             'Step': 'comp',
             'name': 'henry',
             'version': 3}

        :param input_path: Source path for values
        :type input_path: String
        :param skip_keys: Optional keys to skip
        :type skip_keys: List

        :returns: Values found in the path based on keys in template
        :rtype: Dictionary
        """
        path_parser = None
        fields = None

        for ordered_keys, static_tokens in zip(self._ordered_keys, self._static_tokens):
            path_parser = TemplatePathParser(ordered_keys, static_tokens)
            fields = path_parser.parse_path(input_path, skip_keys)
            if fields != None:
                break

        if fields is None:
            raise TankError("Template %s: %s" % (str(self), path_parser.last_error))

        return fields


class TemplatePath(Template):
    """
    :class:`Template` representing a complete path on disk. The template definition is multi-platform
    and you can pass it per-os roots given by a separate :meth:`root_path`.
    """

    def __init__(self, definition, keys, root_path, name=None, per_platform_roots=None):
        """
        TemplatePath objects are typically created automatically by toolkit reading
        the template configuration.

        :param definition: Template definition string.
        :param keys: Mapping of key names to keys (dict)
        :param root_path: Path to project root for this template.
        :param name: Optional name for this template.
        :param per_platform_roots: Root paths for all supported operating systems.
                                   This is a dictionary with sys.platform-style keys
        """
        super(TemplatePath, self).__init__(definition, keys, name=name)
        self._prefix = root_path
        self._per_platform_roots = per_platform_roots

        # Make definition use platform separator
        for index, rel_definition in enumerate(self._definitions):
            self._definitions[index] = os.path.join(*split_path(rel_definition))

        # get definition ready for string substitution
        self._cleaned_definitions = []
        for definition in self._definitions:
            self._cleaned_definitions.append(self._clean_definition(definition))

        # split by format strings the definition string into tokens
        self._static_tokens = []
        for definition in self._definitions:
            self._static_tokens.append(self._calc_static_tokens(definition))

    @property
    def root_path(self):
        """
        Returns the root path associated with this template.
        """
        return self._prefix

    @property
    def parent(self):
        """
        Returns Template representing the parent of this object.

        For paths, this means the parent folder.

        :returns: :class:`Template`
        """
        parent_definition = os.path.dirname(self.definition)
        if parent_definition:
            return TemplatePath(
                parent_definition,
                self.keys,
                self.root_path,
                None,
                self._per_platform_roots,
            )
        return None

    def _apply_fields(
        self, fields, ignore_types=None, platform=None, skip_defaults=False
    ):
        """
        Creates path using fields.

        :param fields: Mapping of keys to fields. Keys must match those in template
                       definition.
        :param ignore_types: Keys for whom the defined type is ignored as list of strings.
                            This allows setting a Key whose type is int with a string value.
        :param platform: Optional operating system platform. If you leave it at the
                         default value of None, paths will be created to match the
                         current operating system. If you pass in a sys.platform-style string
                         (e.g. 'win32', 'linux2' or 'darwin'), paths will be generated to
                         match that platform.
        :param skip_defaults: Optional. If set to True, if a key has a default value and no
                              corresponding value in the fields argument, its default value
                              will be used. If set to False, keys that are not specified in
                              the fields argument are skipped whether they have a default
                              value or not. Defaults to False

        :returns: Full path, matching the template with the given fields inserted.
        """
        relative_path = super(TemplatePath, self)._apply_fields(
            fields, ignore_types, platform, skip_defaults=skip_defaults
        )

        if platform is None:
            # return the current OS platform's path
            return (
                os.path.join(self.root_path, relative_path)
                if relative_path
                else self.root_path
            )

        else:
            platform = sgsix.normalize_platform(platform)
            # caller has requested a path for another OS
            if self._per_platform_roots is None:
                # it's possible that the additional os paths are not set for a template
                # object (mainly because of backwards compatibility reasons) and in this case
                # we cannot compute the path.
                raise TankError(
                    "Template %s cannot resolve path for operating system '%s' - "
                    "it was instantiated in a mode which only supports the resolving "
                    "of current operating system paths." % (self, platform)
                )

            platform_root_path = self._per_platform_roots.get(platform)

            if platform_root_path is None:
                # either the platform is undefined or unknown
                raise TankError(
                    "Cannot resolve path for operating system '%s'! Please ensure "
                    "that you have a valid storage set up for this platform." % platform
                )

            elif is_windows(platform):
                # use backslashes for windows
                if relative_path:
                    return "%s\\%s" % (
                        platform_root_path,
                        relative_path.replace(os.sep, "\\"),
                    )
                else:
                    # not path generated - just return the root path
                    return platform_root_path

            elif is_macos(platform) or is_linux(platform):
                # unix-like plaforms - use slashes
                if relative_path:
                    return "%s/%s" % (
                        platform_root_path,
                        relative_path.replace(os.sep, "/"),
                    )
                else:
                    # not path generated - just return the root path
                    return platform_root_path

            else:
                raise TankError(
                    "Cannot evaluate path. Unsupported platform '%s'." % platform
                )


class TemplateString(Template):
    """
    :class:`Template` class for templates representing strings.

    Templated strings are useful if you want to write code where you can configure
    the formatting of strings, for example how a name or other string field should
    be configured in Shotgun, given a series of key values.
    """

    def __init__(self, definition, keys, name=None, validate_with=None):
        """
        TemplatePath objects are typically created automatically by toolkit reading
        the template configuration.

        :param definition: Template definition string.
        :param keys: Mapping of key names to keys (dict)
        :param name: Optional name for this template.
        :param validate_with: Optional :class:`Template` to use for validation
        """
        super(TemplateString, self).__init__(definition, keys, name=name)
        self.validate_with = validate_with
        self._prefix = "@"

        # split by format strings the definition string into tokens
        self._static_tokens = []
        for definition in self._definitions:
            self._static_tokens.append(self._calc_static_tokens(definition))

    @property
    def parent(self):
        """
        Strings don't have a concept of parent so this always returns ``None``.
        """
        return None

    def get_fields(self, input_path, skip_keys=None):
        """
        Extracts key name, value pairs from a string. Example::

            >>> input = 'filename.v003.ma'
            >>> template_string.get_fields(input)

            {'name': 'henry',
             'version': 3}

        :param input_path: Source path for values
        :type input_path: String
        :param skip_keys: Optional keys to skip
        :type skip_keys: List

        :returns: Values found in the path based on keys in template
        :rtype: Dictionary
        """
        # add path prefix as original design was to require project root
        adj_path = os.path.join(self._prefix, input_path)
        return super(TemplateString, self).get_fields(adj_path, skip_keys=skip_keys)


def split_path(input_path):
    """
    Split a path into tokens.

    :param input_path: path to split
    :type input_path: string

    :returns: tokenized path
    :rtype: list of tokens
    """
    cur_path = os.path.normpath(input_path)
    cur_path = cur_path.replace("\\", "/")
    return cur_path.split("/")


def read_templates(pipeline_configuration):
    """
    Creates templates and keys based on contents of templates file.

    :param pipeline_configuration: pipeline config object

    :returns: Dictionary of form {template name: template object}
    """
    per_platform_roots = pipeline_configuration.get_all_platform_data_roots()
    data = pipeline_configuration.get_templates_config()

    # get dictionaries from the templates config file:
    def get_data_section(section_name):
        # support both the case where the section
        # name exists and is set to None and the case where it doesn't exist
        d = data.get(section_name)
        if d is None:
            d = {}
        return d

    keys = templatekey.make_keys(get_data_section("keys"))

    template_paths = make_template_paths(
        get_data_section("paths"),
        keys,
        per_platform_roots,
        default_root=pipeline_configuration.get_primary_data_root_name(),
    )

    template_strings = make_template_strings(
        get_data_section("strings"), keys, template_paths
    )

    # Detect duplicate names across paths and strings
    dup_names = set(template_paths).intersection(set(template_strings))
    if dup_names:
        raise TankError(
            "Detected paths and strings with the same name: %s" % str(list(dup_names))
        )

    # Put path and strings together
    templates = template_paths
    templates.update(template_strings)
    return templates


def make_template_paths(data, keys, all_per_platform_roots, default_root=None):
    """
    Factory function which creates TemplatePaths.

    :param data: Data from which to construct the template paths.
                 Dictionary of form: {<template name>: {<option>: <option value>}}
    :param keys: Available keys. Dictionary of form: {<key name> : <TemplateKey object>}
    :param all_per_platform_roots: Root paths for all platforms. nested dictionary first keyed by
                                   storage root name and then by sys.platform-style os name.

    :returns: Dictionary of form {<template name> : <TemplatePath object>}
    """

    if data and not all_per_platform_roots:
        raise TankError(
            "At least one root must be defined when using 'path' templates."
        )

    template_paths = {}
    templates_data = _process_templates_data(data, "path")

    for template_name, template_data in templates_data.items():
        definition = template_data["definition"]
        root_name = template_data.get("root_name")
        if not root_name:
            # If the root name is not explicitly set we use the default arg
            # provided
            if default_root:
                root_name = default_root
            else:
                raise TankError(
                    "The template %s (%s) can not be evaluated. No root_name "
                    "is specified, and no root name can be determined from "
                    "the configuration. Update the template definition to "
                    "include a root_name or update your configuration's "
                    "roots.yml file to mark one of the storage roots as the "
                    "default: `default: true`." % (template_name, definition)
                )
        # to avoid confusion between strings and paths, validate to check
        # that each item contains at least a "/" (#19098)
        if "/" not in definition:
            raise TankError(
                "The template %s (%s) does not seem to be a valid path. A valid "
                "path needs to contain at least one '/' character. Perhaps this "
                "template should be in the strings section "
                "instead?" % (template_name, definition)
            )

        root_path = all_per_platform_roots.get(root_name, {}).get(sgsix.platform)
        if root_path is None:
            raise TankError(
                "Undefined PTR storage! The local file storage '%s' is not defined for this "
                "operating system." % root_name
            )

        template_path = TemplatePath(
            definition,
            keys,
            root_path,
            template_name,
            all_per_platform_roots[root_name],
        )
        template_paths[template_name] = template_path

    return template_paths


def make_template_strings(data, keys, template_paths):
    """
    Factory function which creates TemplateStrings.

    :param data: Data from which to construct the template strings.
    :type data:  Dictionary of form: {<template name>: {<option>: <option value>}}
    :param keys: Available keys.
    :type keys:  Dictionary of form: {<key name> : <TemplateKey object>}
    :param template_paths: TemplatePaths available for optional validation.
    :type template_paths: Dictionary of form: {<template name>: <TemplatePath object>}

    :returns: Dictionary of form {<template name> : <TemplateString object>}
    """
    template_strings = {}
    templates_data = _process_templates_data(data, "path")

    for template_name, template_data in templates_data.items():
        definition = template_data["definition"]

        validator_name = template_data.get("validate_with")
        validator = template_paths.get(validator_name)
        if validator_name and not validator:
            msg = "Template %s validate_with is set to undefined template %s."
            raise TankError(msg % (template_name, validator_name))

        template_string = TemplateString(
            definition, keys, template_name, validate_with=validator
        )

        template_strings[template_name] = template_string

    return template_strings


def _conform_template_data(template_data, template_name):
    """
    Takes data for single template and conforms it expected data structure.
    """
    if isinstance(template_data, six.string_types):
        template_data = {"definition": template_data}
    elif not isinstance(template_data, dict):
        raise TankError(
            "template %s has data which is not a string or dictionary." % template_name
        )

    if "definition" not in template_data:
        raise TankError("Template %s missing definition." % template_name)

    return template_data


def _process_templates_data(data, template_type):
    """
    Conforms templates data and checks for duplicate definitions.

    :param data: Dictionary in form { <template name> : <data> }
    :param template_type: path or string

    :returns: Processed data.
    """
    templates_data = {}
    # Track definition to detect duplicates
    definitions = {}

    for template_name, template_data in data.items():
        cur_data = _conform_template_data(template_data, template_name)
        definition = cur_data["definition"]
        if template_type == "path":
            root_name = cur_data.get("root_name")
        else:
            root_name = None

        # Record this templates definition
        cur_key = (root_name, definition)
        definitions[cur_key] = definitions.get(cur_key, []) + [template_name]

        templates_data[template_name] = cur_data

    dups_msg = ""
    for (root_name, definition), template_names in definitions.items():
        if len(template_names) > 1:
            # We have a duplicate
            dups_msg += "%s: %s\n" % (", ".join(template_names), definition)

    if dups_msg:
        raise TankError(
            "It looks like you have one or more "
            "duplicate entries in your templates.yml file. Each template path that you "
            "define in the templates.yml file needs to be unique, otherwise toolkit "
            "will not be able to resolve which template a particular path on disk "
            "corresponds to. The following duplicate "
            "templates were detected:\n %s" % dups_msg
        )

    return templates_data
