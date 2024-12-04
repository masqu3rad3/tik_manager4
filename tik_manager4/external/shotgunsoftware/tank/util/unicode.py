# Copyright (c) 2019 Shotgun Software Inc.
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Utility methods for filtering dictionaries
"""

try:
    from tank_vendor import sgutils
except ImportError:
    from tank_vendor import six as sgutils


def _ensure_contains_str(input_value, visited):
    """
    Convert the keys and values of arrays and dicts to ensure no ``unicode``
    objects are present.

    :param object input_value: Value to validate.
    :param set visited: List of objects already visited.

    :returns: The converted value, if required.
    :rtype: object
    """
    # It's important to keep track of visited lists and dictionary, as
    # there can be circular dependencies between those. Failing to
    # keep track of them will introduce cycles which will make this method
    # do a stack overflow.
    #
    # Certain parts of Toolkit, like the ShotgunModel's cache from shotgunutils
    # actually pickle structures with circular dependencies, so we have to
    # handle that case.
    #
    # Also, we need to keep the instances of the dict and array's the same so
    # those back references are kept, so we'll always in-place edit arrays
    # and dicts instead of instantiating a new array or dict with the
    # updated values.

    # If we've found a unicode object of a bytes string, convert them back to
    # string.
    if isinstance(input_value, (str, bytes)):
        return sgutils.ensure_str(input_value)
    # If we've found a new array, we must ensure each element is
    # not a unicode object.
    elif isinstance(input_value, list) and id(input_value) not in visited:
        visited.add(id(input_value))
        for i in range(len(input_value)):
            item = input_value[i]
            input_value[i] = _ensure_contains_str(item, visited)
        return input_value
    elif isinstance(input_value, tuple):
        # Tuples are immutable, so we don't need to track which one have been
        # converted so far.
        #
        # We could start to track tuples instances that have been converted and reinsert
        # those, but it would make the code a lot more complex for very little benefit.
        # We need to modify other types in place as we can create circular dependencies,
        # but you cannot create a circular dependency of tuples, so this is not an issue.
        return tuple(
            _ensure_contains_str(tuple_item, visited) for tuple_item in input_value
        )
    # If we've found a new dict, we must ensure each key and value
    # is not a unicode object.
    elif isinstance(input_value, dict) and id(input_value) not in visited:
        visited.add(id(input_value))
        for key in list(input_value.keys()):
            item = input_value.pop(key)
            converted_item = _ensure_contains_str(item, visited)
            converted_key = _ensure_contains_str(key, visited)
            input_value[converted_key] = converted_item
        return input_value
    # Not a unicode, bytes, list or array, so return as is.
    else:
        return input_value


def ensure_contains_str(input_value):
    """
    Converts any :class:`unicode` instances in the input value into a utf-8
    encoded :class`str` instance.

    This method will detect cycles and preserve them.

    :param input_value: Value to convert. Can be a scalar, list or dictionary.

    :returns: A value with utf-8 encoded :class:`str` instances.
    """
    return _ensure_contains_str(input_value, set())
