# Copyright (c) 2019 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os

from .. import LogManager
from .unicode import ensure_contains_str

from tank_vendor.six.moves import cPickle
from tank_vendor import six

try:
    from tank_vendor import sgutils
except ImportError:
    from tank_vendor import six as sgutils


log = LogManager.get_logger(__name__)


# kwargs for pickle.load* and pickle.dump* calls.
LOAD_KWARGS = {"encoding": "bytes"} if six.PY3 else {}
# Protocol 0 ensures ASCII encoding, which is required when writing
# a pickle to an environment variable.
DUMP_KWARGS = {"protocol": 0}

# Fix unicode issue when ensuring string values
# https://jira.autodesk.com/browse/SG-6588
FALLBACK_ENCODING = "ISO-8859-1"
FALLBACK_ENCODING_KEY = "_payload_encoding"


def dumps(data):
    """
    Return the pickled representation of ``data`` as a ``str``.

    This methods wraps the functionality from the :func:`pickle.dumps` method so
    pickles can be shared between Python 2 and Python 3.

    As opposed to the Python 3 implementation, it will return a ``str`` object
    and not ``bytes`` object.

    :param data: The object to pickle and store.
    :returns: A pickled str of the input object.
    :rtype: str
    """
    # Force pickle protocol 0, since this is a non-binary pickle protocol.
    # See https://docs.python.org/2/library/pickle.html#pickle.HIGHEST_PROTOCOL
    # Decode the result to a str before returning.
    serialized = cPickle.dumps(data, **DUMP_KWARGS)
    try:
        return sgutils.ensure_str(serialized)
    except UnicodeError as e:
        # Fix unicode issue when ensuring string values
        # https://jira.autodesk.com/browse/SG-6588
        if e.encoding == "utf-8" and e.reason in ("invalid continuation byte", "invalid start byte"):
            encoding = FALLBACK_ENCODING
            if isinstance(data, dict):
                data[FALLBACK_ENCODING_KEY] = encoding
                serialized = cPickle.dumps(data, **DUMP_KWARGS)
            return sgutils.ensure_str(serialized, encoding=encoding)

        raise


def dump(data, fh):
    """
    Write the pickled representation of ``data`` to a file object.

    This methods wraps the functionality from the :func:`pickle.dump` method so
    pickles can be shared between Python 2 and Python 3.

    :param data: The object to pickle and store.
    :param fh: A file object
    """
    cPickle.dump(data, fh, **DUMP_KWARGS)


def loads(data):
    """
    Read the pickled representation of an object from a string
    and return the reconstituted object hierarchy specified therein.

    This method wraps the functionality from the :func:`pickle.loads` method so
    unicode strings are always returned as utf8-encoded ``str`` instead of ``unicode``
    objects in Python 2.

    :param object data: A pickled representation of an object.
    :returns: The unpickled object.
    :rtype: object
    """
    binary = sgutils.ensure_binary(data)
    loads_data = ensure_contains_str(cPickle.loads(binary, **LOAD_KWARGS))

    if isinstance(loads_data, dict) and FALLBACK_ENCODING_KEY in loads_data:
        encoding = loads_data[FALLBACK_ENCODING_KEY]
        binary = sgutils.ensure_binary(data, encoding=encoding)
        loads_data = ensure_contains_str(cPickle.loads(binary, **LOAD_KWARGS))

    return loads_data


def load(fh):
    """
    Read the pickled representation of an object from the open file object
    and return the reconstituted object hierarchy specified therein.

    This method wraps the functionality from the :func:`pickle.load` method so
    unicode strings are always returned as utf8-encoded ``str`` instead of ``unicode``
    objects in Python 2.

    :param fh: A file object
    :returns: The unpickled object.
    :rtype: object
    """
    return ensure_contains_str(cPickle.load(fh, **LOAD_KWARGS))


def store_env_var_pickled(key, data):
    """
    Stores the provided data under the environment variable specified.

    .. note::
        This method is part of Toolkit's internal API.

    In Python 3 pickle.dumps() returns a binary object that can't be decoded to
    a string for storage in an environment variable.  To work around this, we
    encode the pickled data to base64, compress the result, and store that.

    :param key: The name of the environment variable to store the data in.
    :param data: The object to pickle and store.
    """
    # Force pickle protocol 0, since this is a non-binary pickle protocol.
    # See https://docs.python.org/2/library/pickle.html#pickle.HIGHEST_PROTOCOL
    pickled_data = dumps(data)
    encoded_data = sgutils.ensure_str(pickled_data)
    os.environ[key] = encoded_data


def retrieve_env_var_pickled(key):
    """
    Retrieves and unpacks the pickled data stored in the environment variable
    specified.

    .. note::
        This method is part of Toolkit's internal API.

    In Python 3 pickle.dumps() returns a binary object that can't be decoded to
    a string for storage in an environment variable.  To work around this, we
    encode the pickled data to base64, compress the result, and store that.

    :param key: The name of the environment variable to retrieve data from.
    :returns: The original object that was stored.
    """
    envvar_contents = sgutils.ensure_binary(os.environ[key])
    return loads(envvar_contents)
