# Copyright (c) 2019 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Wrapper around the re module from Python. We're essentially back porting
some functionality.
"""

# Note that contrary to the sgtk.util.json module, this one is named sgre.
# There seems to be some weird import shenanigans going on in Python 2 that
# prevents from importing the sgtk.util.re submodule using our meta-path
# importer. When we try, our meta-path importer is not called for our `re`
# module and we get an ImportError. Renaming the module to anything else
# works however, so that's what we are doing.

from tank_vendor import six

# Import constants and functions that won't be wrapped
from re import (
    DEBUG,
    I,
    IGNORECASE,
    L,
    LOCALE,  # noqa import into namespace
    M,
    MULTILINE,
    S,
    DOTALL,
    U,
    UNICODE,
    X,
    VERBOSE,
)
from re import escape  # noqa import into namespace

# In Python 3, regular expression metacharacters match unicode characters where in
# Python 2 they hadn't.  To reproduce the previous behavior, Python 3 introduces a
# new re.ASCII flag, which does not exist in Python 2.  For Python 2, we can leave
# the re behavior as-is.
if six.PY2:
    from re import compile, findall, match, search, split, sub

# For Python 3, we'll wrap the re functions to inject the ASCII flag when necessary
# to maintain the previous behavior.
else:
    import re as _re
    import typing as _typing

    def _re_wrap(fn, flags_arg_position):
        def wrapper(*args, **kwargs):
            if args and isinstance(args[0], _typing.Pattern):
                # If we've been passed a compiled pattern, we can't apply flags,
                # so we should just wrap the callable untouched.
                return fn(*args, **kwargs)
            if len(args) > flags_arg_position:
                # If flags are provided positionally, and the UNICODE flag
                # is not present, add the ASCII flag
                if not args[flags_arg_position] & _re.UNICODE:
                    args = list(args)
                    args[flags_arg_position] |= _re.ASCII
            elif "flags" in kwargs:
                if not kwargs["flags"] & _re.UNICODE:
                    # If flags are provided as a kwarg, and the UNICODE flag
                    # is not present, add the ASCII flag
                    kwargs["flags"] |= _re.ASCII
            else:
                # If no flags were specified, add a flags kwarg with the ASCII
                # flag.
                kwargs["flags"] = _re.ASCII
            return fn(*args, **kwargs)

        return wrapper

    # Since the flags arg is sometimes provided positionally, we'll specify the
    # argument's position to our wrapper so it can handle this.  These interfaces
    # all remained unchanged between Python 2 and 3, so positionally providing
    # flags does not break.
    compile = _re_wrap(_re.compile, 1)
    findall = _re_wrap(_re.findall, 2)
    match = _re_wrap(_re.match, 2)
    search = _re_wrap(_re.search, 2)
    split = _re_wrap(_re.split, 3)
    sub = _re_wrap(_re.sub, 4)
