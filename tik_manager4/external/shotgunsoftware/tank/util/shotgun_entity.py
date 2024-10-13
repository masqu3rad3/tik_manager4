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
Utilities relating to Shotgun entities
"""

from . import constants, sgre as re
from ..errors import TankError
from tank_vendor import six

# A dictionary for Shotgun entities which do not store their name
# in the standard "code" field.
SG_ENTITY_SPECIAL_NAME_FIELDS = {
    "ActionMenuItem": "title",
    "ApiUser": "firstname",
    "Attachment": None,
    "Booking": None,
    "ClientUser": "name",
    "Delivery": "title",
    "Department": "name",
    "EventLogEntry": None,
    "HumanUser": "name",
    "Icon": "name",
    "Note": "subject",
    "Page": "name",
    "PageHit": None,
    "PageSetting": None,
    "PlaylistShare": None,
    "Project": "name",
    "PublishedFileDependency": None,
    "Reply": None,
    "Tag": "name",
    "Task": "content",
    "TaskDependency": None,
    "Ticket": "title",
    "TimeLog": None,
}


def get_sg_entity_name_field(entity_type):
    """
    Return the Shotgun name field to use for the specified entity type.

    :param str entity_type: The entity type to get the name field for.
    :returns: The name field for the specified entity type.
    """
    # Deal with some known special cases and assume "code" for anything else.
    return SG_ENTITY_SPECIAL_NAME_FIELDS.get(entity_type, "code")


def sg_entity_to_string(tk, sg_entity_type, sg_id, sg_field_name, data):
    """
    Generates a string value given a Shotgun value.
    This logic is in a hook but it typically does conversions such as:

    * "foo" ==> "foo"
    * {"type":"Shot", "id":123, "name":"foo"} ==> "foo"
    * 123 ==> "123"
    * [{"type":"Shot", "id":1, "name":"foo"}, {"type":"Shot", "id":2, "name":"bar"}] ==> "foo_bar"

    This method may also raise exceptions in the case the string value is not valid.

    :param tk: Sgtk api instance
    :param sg_entity_type: the Shotgun entity type e.g. 'Shot'
    :param sg_id: The Shotgun id for the record, e.g 1234
    :param sg_field_name: The field to generate value for, e.g. 'sg_sequence'
    :param data: The Shotgun entity data chunk that should be converted to a string.
    """
    # call out to core hook
    return tk.execute_core_hook(
        constants.PROCESS_FOLDER_NAME_HOOK_NAME,
        entity_type=sg_entity_type,
        entity_id=sg_id,
        field_name=sg_field_name,
        value=data,
    )


class EntityExpression(object):
    """
    Represents a name expression for a Shotgun entity.
    A name expression converts a pattern and a set of Shotgun data into a string:

    Expression                 Shotgun Entity Data                          String Result
    ----------------------------------------------------------------------------------------
    * "code"                 + {"code": "foo_bar"}                      ==> "foo_bar"
    * "{code}_{asset_type}"  + {"code": "foo_bar", "asset_type": "car"} ==> "foo_bar_car"
    * "{code}/{asset_type}"  + {"code": "foo_bar", "asset_type": "car"} ==> "foo_bar/car"

    Optional fields are [bracketed]:

    * "{code}[_{asset_type}]" + {"code": "foo_bar", "asset_type": "car"} ==> "foo_bar_car"
    * "{code}[_{asset_type}]" + {"code": "foo_bar", "asset_type": None} ==> "foo_bar"

    Regular expressions can be used to evaluate substrings:

    * "{code:^([^_]+)}/{code:^[^_]+(.+)}" + {"code": "foo_bar"} ==> "foo/bar"

    It it is always connected to a specific Shotgun entity type and
    the fields need to be Shotgun fields that exists for that entity type.
    """

    def __init__(self, tk, entity_type, field_name_expr):
        """
        :param str entity_type: Associated Shotgun entity type.
        :param str field_name_expr: Expression, e.g. '{code}/foo'
        """
        self._tk = tk
        self._entity_type = entity_type
        self._field_name_expr = field_name_expr

        # now validate
        if "{" not in field_name_expr:
            # simple form - surround with brackets to turn into a expression
            field_name_expr = "{%s}" % field_name_expr

        # now get all permutations for expressions with optional fields
        expr_variations = self._get_expression_variations(field_name_expr)

        # We want them most inclusive(longest) version first
        self._sorted_exprs = sorted(expr_variations, key=lambda x: len(x), reverse=True)

        # Extract and store a bunch of data for each variation.
        self._variations = {}
        for expr_variation in expr_variations:

            try:
                # find all field names, for example:
                # "{xx}_{yy}_{zz.xx}" ----> ["xx", "yy", "zz.xx"]
                # "{code:([^_]+)}_{yy}" --> ["code:([^_]+)", "yy"]
                fields = set(re.findall("{([^}]*)}", expr_variation))
            except Exception as error:
                raise TankError(
                    "Could not parse the configuration field '%s' - "
                    "Error: %s" % (field_name_expr, error)
                )

            # Go over fields strings and resolve tokens

            # parsing 'sg_sequence.Sequence.code:^([^_]+)' resolves into
            # {
            #   'full_field_name': 'sg_sequence.Sequence.code',
            #   'link_field_name': 'sg_sequence',
            #   'regex_obj': <regex obj>
            # }

            # parsing 'code' resolves into
            # {
            #   'full_field_name': 'code',
            #   'link_field_name': None,
            #   'regex_obj': None
            # }

            resolved_fields = []
            for field_token_expression in fields:
                full_field_name = None
                link_field_name = None
                regex_obj = None

                if ":" in field_token_expression:
                    (full_field_name, regex) = field_token_expression.split(":", 1)

                    try:
                        regex_obj = re.compile(regex, re.UNICODE)
                    except Exception as e:
                        raise TankError(
                            "Could not parse regex in configuration "
                            "field '%s': %s" % (field_name_expr, e)
                        )
                else:
                    full_field_name = field_token_expression

                # extract the link for deep query fields
                if "." in full_field_name:
                    link_field_name = full_field_name.split(".")[0]

                resolved_fields.append(
                    {
                        "token": field_token_expression,
                        "full_field_name": full_field_name,
                        "link_field_name": link_field_name,
                        "regex_obj": regex_obj,
                    }
                )

            # add this to our variations dict
            self._variations[expr_variation] = resolved_fields

    def _get_expression_variations(self, definition):
        """
        Returns all possible optional variations for an expression.

        "{foo}"               ==> ['{foo}']
        "{foo:[xxx]}_{bar}"   ==> ['{foo:[xxx]}_{bar}']
        "{foo}[_{bar}]"       ==> ['{foo}', '{foo}_{bar}']
        "{foo}_[{bar}_{baz}]" ==> ['{foo}_', '{foo}_{bar}_{baz}']

        :param str definition: Expression to process.
        :returns: List of variations. See example above.
        """
        # Split definition by optional sections
        # Look for square brackets that contains at least one
        # {expression} and ignore any square bracket inside
        # expressions:
        tokens = re.split(r"(\[[^\]]*\{.*\}[^\]]*\])", definition)
        # seed with empty string
        definitions = [""]
        for token in tokens:
            temp_definitions = []
            if token == "":
                # regex return some blank strings, skip them
                continue
            if token.startswith("["):
                # Add definitions skipping this optional value
                temp_definitions = definitions[:]
                # strip brackets from token
                token = token[1:-1]
            # make defintions with token appended
            for definition in definitions:
                temp_definitions.append(definition + token)
            definitions = temp_definitions

        return definitions

    def get_shotgun_fields(self):
        """
        Returns the Shotgun fields that are needed in order to
        build this name expression. Returns all fields, including optional.

        :returns: Set of Shotgun field names, e.g. ('code', 'sg_sequence.Sequence.code')
        """
        # use the longest expression - this contains the most fields
        longest_expr = self._sorted_exprs[0]
        field_defs = self._variations[longest_expr]
        field_names = [field["full_field_name"] for field in field_defs]
        return set(field_names)

    def get_shotgun_link_fields(self):
        """
        Returns a list of all entity links that are used in the name expression,
        including optional ones.
        For example, if a name expression for a Shot is '{code}_{sg_sequence.Sequence.code}',
        the link fields for this expression is ['sg_sequence'].

        :returns: Set of link fields, e.g. ('sg_sequence', 'entity')
        """
        # use the longest exprssion - this contains the most fields
        longest_expr = self._sorted_exprs[0]
        field_defs = self._variations[longest_expr]
        link_names = [
            field["link_field_name"]
            for field in field_defs
            if field["link_field_name"] is not None
        ]
        return set(link_names)

    def generate_name(self, values):
        """
        Generates a name given some fields.

        Assumes the name will be used as a folder name and validates
        that the evaluated expression is suitable for disk use.

        :param dict values: Dictionary of values to use.
        :returns: Fully resolved name string.
        """
        # first make sure that each field is valid
        for field_name in self.get_shotgun_fields():
            if field_name not in values:
                # required value was not provided!
                raise TankError(
                    "Folder Configuration Error: "
                    "A PTR field '%s' is being requested as part of the expression "
                    "'%s' when creating folders connected to entities of type %s, "
                    "however no such field exists in Flow Production Tracking. Please review your "
                    "configuration!"
                    % (field_name, self._field_name_expr, self._entity_type)
                )

        # ok all fields are there. But some values may be none. Try to resolve our expression against
        # the values, starting with the longest expression first.
        for expr in self._sorted_exprs:
            val = self._generate_name(expr, values)
            if val is not None:
                # name generation worked! - do not try alternative (shorter) expressions
                break

        if val is None:
            # completely failed to generate a name because of missing fields.

            # try to make a nice descriptive name if possible
            if "code" in values:
                nice_name = "%s %s (id %s)" % (
                    self._entity_type,
                    values["code"],
                    values.get("id"),
                )
            else:
                nice_name = "%s id %s" % (self._entity_type, values.get("id"))

            raise TankError(
                "Folder Configuration Error. Could not create folders for %s! "
                "The expression %s refers to one or more values that are blank "
                "in PTR and a folder can therefore "
                "not be created." % (nice_name, self._field_name_expr)
            )

        return val

    def _generate_name(self, expression, values):
        """
        Generates a name given some fields.

        Assumes the name will be used as a folder name and validates
        that the evaluated expression is suitable for disk use.

        :param values: dictionary of values to use
        :returns: fully resolved name string or None if it cannot be resolved.
        """
        field_defs = self._variations[expression]

        # convert Shotgun values to string values
        # key these by their full expression
        str_data = {}

        # get the Shotgun id from the Shotgun entity dict
        sg_id = values.get("id")

        # first make sure that each field is valid
        for field_def in field_defs:

            full_sg_field_name = field_def["full_field_name"]
            token = field_def["token"]

            # get value from Shotgun data dict
            raw_val = values.get(full_sg_field_name)
            if raw_val is None:
                # cannot resolve this!
                return None

            # now cast the value to a string
            str_value = sg_entity_to_string(
                self._tk, self._entity_type, sg_id, full_sg_field_name, raw_val
            )

            # see if we need to transform it via regex
            if field_def["regex_obj"]:
                str_value = self._process_regex(str_value, field_def["regex_obj"])

            str_data[token] = str_value

        # Now str_data looks something like
        # {'code': 'hello', 'code:^(.)': 'h'}.
        #
        # Replace tokens in the string with actual values:
        resolved_expression = expression
        for token, value in str_data.items():
            resolved_expression = resolved_expression.replace("{%s}" % token, value)

        # now validate the entire value!
        if not self._validate_name(resolved_expression):
            raise TankError(
                "The format string '%s' used in the configuration "
                "does not generate a valid folder name ('%s')! Valid "
                "values are %s."
                % (
                    expression,
                    resolved_expression,
                    constants.VALID_SG_ENTITY_NAME_EXPLANATION,
                )
            )
        return resolved_expression

    def _validate_name(self, name):
        """
        Check that the name meets basic file system naming standards.

        :returns: True if valid, false otherwise
        """
        exp = re.compile(constants.VALID_SG_ENTITY_NAME_REGEX, re.UNICODE)

        # split into sub-segments based on slash
        # and validate each one separately
        if name is None:
            return False

        # iterate over all tokens and validate
        for folder_subgroup in name.split("/"):
            if isinstance(folder_subgroup, six.text_type):
                u_name = folder_subgroup
            else:
                # try decoding from utf-8:
                u_name = folder_subgroup.decode("utf-8")

            if exp.match(u_name) is None:
                return False

        return True

    def _process_regex(self, value, regex_obj):
        """
        Processes the given string value with the given regex.

        :param value: Value to process, either unicode or str.
        :param regex_obj: Regex object.
        :return: Processed value, same type as value input parameter.
            If input is None, an empty string is returned.
        """
        if value is None:
            return ""

        # perform the regex calculation in unicode space
        if not isinstance(value, six.text_type):
            input_is_utf8 = True
            value_to_convert = value.decode("utf-8")
        else:
            input_is_utf8 = False
            value_to_convert = value

        # now perform extraction
        match = regex_obj.match(value_to_convert)
        if match is None:
            # no match. return empty string
            resolved_value = u""
        else:
            # we have a match object. concatenate the groups
            resolved_value = "".join(match.groups())

        # resolved value is now unicode. Convert it
        # so that it is consistent with input
        if isinstance(resolved_value, six.text_type) and input_is_utf8:
            # input was utf-8, regex result is unicode, cast it back
            return resolved_value.encode("utf-8")
        else:
            return resolved_value
