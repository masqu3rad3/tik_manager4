# Copyright (c) 2018 Shotgun Software Inc.
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Utility methods for unserializing JSON documents.
"""

# We need to add this to the file or the import json will reimport this
# module instead of importing the global json module.
from __future__ import absolute_import
import sys
import json

from .unicode import ensure_contains_str


# This is the Python 2.6 signature. 2.7 has an extra object_hook_pairs argument.
def load(
    fp,
    encoding=None,
    cls=None,
    object_hook=None,
    parse_float=None,
    parse_int=None,
    parse_constant=None,
    **kw
):
    """
    Deserialize ``fp`` (a ``.read()``-supporting file-like object containing
    a JSON document) to a Python object.

    This method is a simple thin wrapper around :func:`json.load` that
    ensures unserialized strings are utf-8 encoded :class:`str` objects.

    See the documentation for :func:`json.load` to learn more about this method.
    """
    # Specify kwargs explicitly to avoid problems caused by the signature change
    # between Python 2 and 3.
    # See https://docs.python.org/3/library/json.html#json.load and
    # https://docs.python.org/2/library/json.html#json.load for both signatures.
    # Python 3.9 does not have an encodings parameter, so don't add the value to the arguments list.
    if sys.version_info[0:2] < (3, 9):
        kw["encoding"] = encoding
    loaded_value = json.load(
        fp,
        cls=cls,
        object_hook=object_hook,
        parse_float=parse_float,
        parse_int=parse_int,
        parse_constant=parse_constant,
        **kw
    )

    return ensure_contains_str(loaded_value)


# This is the Python 2.6 signature. 2.7 has an extra object_hook_pairs argument.
def loads(
    s,
    encoding=None,
    cls=None,
    object_hook=None,
    parse_float=None,
    parse_int=None,
    parse_constant=None,
    **kw
):
    """
    Deserialize ``s`` (a ``str`` or ``unicode`` instance containing a JSON
    document) to a Python object.

    This method is a simple thin wrapper around :func:`json.loads` that
    ensures unserialized strings are utf-8 encoded :class:`str` objects.

    See the documentation for :func:`json.loads` to learn more about this method.
    """
    # Specify kwargs explicitly to avoid problems caused by the signature change
    # between Python 2 and 3.
    # See https://docs.python.org/3/library/json.html#json.loads and
    # https://docs.python.org/2/library/json.html#json.loads for both signatures.
    # Python 3.9 does not have an encodings parameter, so don't add the value to the arguments list.
    if sys.version_info[0:2] < (3, 9):
        kw["encoding"] = encoding
    loaded_value = json.loads(
        s,
        cls=cls,
        object_hook=object_hook,
        parse_float=parse_float,
        parse_int=parse_int,
        parse_constant=parse_constant,
        **kw
    )

    return ensure_contains_str(loaded_value)
