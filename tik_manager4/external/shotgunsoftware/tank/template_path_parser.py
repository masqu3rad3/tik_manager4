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
Parsing of template paths into values for specified keys using a list of static tokens
"""

import os
from .errors import TankError


class TemplatePathParser(object):
    """
    Class for parsing a path for a known set of keys, and known set of static
    tokens which should appear between the key values.
    """

    class ResolvedValue(object):
        """
        Container class used to store possible resolved values during template
        parsing.  Stores the possible value as well as the downstream hierarchy
        of possible values, the last error found whilst parsing and a flag
        to specify if any of the branches in the downstream hierarchy are fully
        resolved (a value was found for every remaining key)
        """

        def __init__(self, value, downstream_values, fully_resolved, last_error):
            """
            Construction

            :param value:               The resolved value to keep track of
            :param downstream_values:   ResolvedValue instances for all possible downstream branches of
                                        possible resolved values
            :param fully_resolved:      Flag to track if any of the downstream branches are fully resolved
                                        or not
            :param last_error:          The last error reported from the template parsing for the current
                                        branch of possible values.
            """
            self.value = value
            self.downstream_values = downstream_values
            self.fully_resolved = fully_resolved
            self.last_error = last_error

    def __init__(self, ordered_keys, static_tokens):
        """
        Construction

        :param ordered_keys:    Template key objects in order that they appear in the
                                template definition.
        :param static_tokens:   Pieces of the definition that don't represent Template Keys.
        """
        self.ordered_keys = ordered_keys
        self.static_tokens = static_tokens
        self.fields = {}
        self.input_path = None
        self.last_error = "Unable to parse path"

    def parse_path(self, input_path, skip_keys):
        """
        Parses a path against the set of keys and static tokens to extract valid values
        for the keys.  This will make use of as much information as it can within all
        keys to correctly determine the value for a field and will detect if a key
        resolves to ambiguous values where there is not enough information to resolve
        correctly!

        e.g. with the template:

            {shot}_{name}_v{version}.ma

        and a path:

            shot_010_name_v001.ma

        The algorithm would correctly determine that the value for the shot key is
        'shot_010' assuming that the name key is restricted to be alphanumeric.  If
        name allowed underscores then the shot key would be ambiguous and would resolve
        to either 'shot' or 'shot_010' which would error.

        :param input_path:  The path to parse.
        :param skip_keys:   List of keys for whom we do not need to find values.

        :returns:           If succesful, a dictionary of fields mapping key names to
                            their values. None if the fields can't be resolved.
        """
        skip_keys = skip_keys or []
        input_path = os.path.normpath(input_path)

        # all token comparisons are done case insensitively.
        lower_path = input_path.lower()

        # if no keys, nothing to discover
        if not self.ordered_keys:
            if lower_path == self.static_tokens[0]:
                # this is a template where there are no keys
                # but where the static part of the template is matching
                # the input path
                # (e.g. template: foo/bar - input path foo/bar)
                return {}
            else:
                # template with no keys - in this case not matching
                # the input path. Return for no match.
                return None

        # find all occurances of all tokens in the path.  This will
        # produce a list of lists, one list of positions for each token.
        #
        # Possible token positions are split into domains where the first
        # occurance of a token must be after the first occurance of the
        # preceding token and the last occurance must be before the last
        # occurance of the following token.  e.g. The valid tokens for
        # the example path are shown below:
        #
        # Template : {shot}_{name}_v{version}.ma
        # Path     : shot_010_name_v010.ma
        # Token _  :    [_   _]
        # Token _v :             [_v]
        # Token .ma:                  [.ma]
        token_positions = []
        start_pos = 0
        for token in self.static_tokens:
            positions = []
            token_pos = start_pos

            while token_pos >= 0:
                token_pos = lower_path.find(token, token_pos)
                if token_pos >= 0:
                    if not positions:
                        # this is the first instance of this token we found so it
                        # will be the start position to look for the next token
                        # as it will be the first possible location available!
                        start_pos = token_pos + len(token)
                    positions.append(token_pos)
                    token_pos += len(token)
            if not positions:
                # didn't find token!
                self.last_error = (
                    "Tried to extract fields from path '%s', "
                    "but the path does not fit the template." % input_path
                )
                return None
            token_positions.append(positions)

        # disgard positions that can't be valid - e.g. where the position is greater than the
        # last possible position of any subsequent tokens:
        max_position = len(lower_path) + 1
        for ti in reversed(range(len(token_positions))):
            token_positions[ti] = [p for p in token_positions[ti] if p < max_position]
            max_position = max(token_positions[ti]) if token_positions[ti] else 0

        # find all possible values for keys based on token positions - this will
        # return a list of lists including all potential variations:
        num_keys = len(self.ordered_keys)
        num_tokens = len(self.static_tokens)
        possible_values = []
        if token_positions[0][0] == 0:
            # path may start with the first static token - possible scenarios:
            #    t-k-t
            #    t-k-t-k
            #    t-k-t-k-k
            if num_keys >= num_tokens - 1:
                possible_values.extend(
                    self.__find_possible_key_values_recursive(
                        input_path,
                        len(self.static_tokens[0]),
                        self.static_tokens[1:],
                        token_positions[1:],
                        self.ordered_keys,
                        skip_keys,
                    )
                )

            # we've handled this case so remove the first position:
            token_positions[0] = token_positions[0][1:]

        if len(token_positions[0]) > 0:
            # we still have non-zero positions for the first token so the
            # path may actually start with a key - possible scenarios:
            #    k-t-k
            #    k-t-k-t
            #    k-t-k-k
            if num_keys >= num_tokens:
                possible_values.extend(
                    self.__find_possible_key_values_recursive(
                        input_path,
                        0,
                        self.static_tokens,
                        token_positions,
                        self.ordered_keys,
                        skip_keys,
                    )
                )

        if not possible_values:
            # failed to find anything!
            if not self.last_error:
                self.last_error = (
                    "Tried to extract fields from path '%s', "
                    "but the path does not fit the template." % input_path
                )
            return None

        # ensure that we only have a single set of valid values for all keys.  If we don't
        # then attempt to report the best error we can
        fields = {}
        for key in self.ordered_keys:
            key_value = None
            if not possible_values:
                # we didn't find any possible values for this key!
                break
            elif len(possible_values) == 1:
                if not possible_values[0].fully_resolved:
                    # failed to fully resolve the path!
                    self.last_error = possible_values[0].last_error
                    return None

                # only found one possible value!
                key_value = possible_values[0].value
                possible_values = possible_values[0].downstream_values
            else:
                # found more than one possible value so check to see how many are fully resolved:
                resolved_possible_values = [
                    v for v in possible_values if v.fully_resolved
                ]
                num_resolved = len(resolved_possible_values)

                if num_resolved == 1:
                    # only found one resolved value - awesome!
                    key_value = resolved_possible_values[0].value
                    possible_values = resolved_possible_values[0].downstream_values
                elif num_resolved > 1:
                    # found more than one valid value so value is ambiguous!
                    self.last_error = (
                        "Ambiguous values found for key '%s' could be any of: '%s'"
                        % (
                            key.name,
                            "', '".join([v.value for v in resolved_possible_values]),
                        )
                    )
                    return None
                else:
                    # didn't find any fully resolved values so we have multiple
                    # non-fully resolved values which also means the value is ambiguous!
                    self.last_error = (
                        "Ambiguous values found for key '%s' could be any of: '%s'"
                        % (key.name, "', '".join([v.value for v in possible_values]))
                    )
                    return None

            # if key isn't a skip key then add it to the fields dictionary:
            if key_value is not None and key.name not in skip_keys:
                fields[key.name] = key_value

        # return the single unique set of fields:
        return fields

    def __find_possible_key_values_recursive(
        self,
        path,
        key_position,
        tokens,
        token_positions,
        keys,
        skip_keys,
        key_values=None,
    ):
        """
        Recursively traverse through the tokens & keys to find all possible values for the keys
        given the available token positions im the path.

        :param path:            The path to find possible key values from
        :param key_position:    The starting point in the path where we should look for a value
                                for the next key
        :param tokens:          A list of the remaining static tokens to look for
        :param token_positions: A list of lists containing all the valid positions where each static token
                                can be found in the path
        :param keys:            A list of the remaining keys to find values for
        :param skip_keys:       A list of keys that can be skipped from the result
        :param key_values:      A dictionary of all values that were previously found for any keys

        :returns:               A list of ResolvedValue instances representing the hierarchy of possible
                                values for all keys being parsed.
        """
        key_values = key_values or {}
        key = keys[0]
        keys = keys[1:]
        token = tokens[0] if tokens else ""
        tokens = tokens[1:]
        positions = token_positions[0] if token_positions else [len(path)]
        token_positions = token_positions[1:]

        key_value = key_values.get(key.name)

        # using the token positions, find all possible values for the key
        possible_values = []
        for token_position in positions:

            # make sure that the length of the possible value substring will be valid:
            if token_position <= key_position:
                continue
            if key.length is not None and token_position - key_position < key.length:
                continue

            # get the possible value substring:
            possible_value_str = path[key_position:token_position]

            # from this, find the possible value:
            possible_value = None
            last_error = None
            if key.name not in skip_keys:
                # validate the value for this key:

                # slashes are not allowed in key values!  Note, the possible value is a section
                # of the input path so the OS specific path separator needs to be checked for:
                if os.path.sep in possible_value_str:
                    last_error = "%s: Invalid value found for key %s: %s" % (
                        self,
                        key.name,
                        possible_value_str,
                    )
                    continue

                # can't have two different values for the same key:
                if key_value and possible_value_str != key_value:
                    last_error = (
                        "%s: Conflicting values found for key %s: %s and %s"
                        % (self, key.name, key_value, possible_value_str)
                    )
                    continue

                # get the actual value for this key - this will also validate the value:
                try:
                    possible_value = key.value_from_str(possible_value_str)
                except TankError as e:
                    # it appears some locales are not able to correctly encode
                    # the error message to str here, so use the %r form for the error
                    # (ticket 24810)
                    last_error = "%s: Failed to get value for key '%s' - %r" % (
                        self,
                        key.name,
                        e,
                    )
                    continue

            else:
                # don't bother doing validation/conversion for this value as it's being skipped!
                possible_value = possible_value_str

            downstream_values = []
            fully_resolved = False
            if keys:
                # still have keys to process:
                if token_position + len(token) >= len(path):
                    # but we've run out of path!  This is ok
                    # though - we just stop processing keys...
                    fully_resolved = True
                else:
                    # have keys remaining and some path left to process so recurse to next position for next key:
                    downstream_values = self.__find_possible_key_values_recursive(
                        path,
                        token_position + len(token),
                        tokens,
                        token_positions,
                        keys,
                        skip_keys,
                        dict(
                            list(key_values.items()) + [(key.name, possible_value_str)]
                        ),
                    )

                    # check that at least one of the returned values is fully
                    # resolved and find the last error found if any
                    fully_resolved = False
                    for v in downstream_values:
                        if v.fully_resolved:
                            fully_resolved = True
                        if v.last_error:
                            last_error = v.last_error

            elif tokens:
                # we don't have keys but we still have remaining tokens - this is bad!
                fully_resolved = False
            elif token_position + len(token) != len(path):
                # no keys or tokens left but we haven't fully consumed the path either!
                fully_resolved = False
            else:
                # processed all keys and tokens and fully consumed the path
                fully_resolved = True

            # keep track of the possible values:
            possible_values.append(
                TemplatePathParser.ResolvedValue(
                    possible_value, downstream_values, fully_resolved, last_error
                )
            )

        return possible_values
