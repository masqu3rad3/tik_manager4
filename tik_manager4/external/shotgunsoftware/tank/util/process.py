# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import subprocess
import pprint

from .platforms import is_windows
from ..log import LogManager

try:
    from tank_vendor import sgutils
except ImportError:
    from tank_vendor import six as sgutils

logger = LogManager.get_logger(__name__)


class SubprocessCalledProcessError(Exception):
    """
    Subprocess exception
    """

    def __init__(self, returncode, cmd, output=None):
        self.returncode = returncode
        self.cmd = cmd
        self.output = output

    def __str__(self):
        return "Command '%s' returned non-zero exit status %d" % (
            self.cmd,
            self.returncode,
        )


def subprocess_check_output(*popenargs, **kwargs):
    """
    Run command with arguments and return its output as a byte string.

    A somewhat-python 2.6 compatible subprocess.check_output call.
    Subprocess.check_output was added to Python 2.7. For docs, see
    https://docs.python.org/2/library/subprocess.html#subprocess.check_output

    Adopted from from http://stackoverflow.com/questions/2924310

    This version however doesn't allow to override stderr, stdout and stdin. stdin
    is always closed right after launch and stderr is always redirected to stdout. This
    is done in order to avoid DUPLICATE_SAME_ACCESS errors on Windows. Learn more about
    it here: https://bugs.python.org/issue3905.

    :returns: The output from the command
    :raises: If the return code was non-zero it raises a SubprocessCalledProcessError.
             The SubprocessCalledProcessError object will have the return code in the returncode
             attribute and any output in the output attribute.
    """
    if "stdout" in kwargs or "stderr" in kwargs or "stdin" in kwargs:
        raise ValueError(
            "stdout, stderr and stdin arguments not allowed, they will be overridden."
        )

    process = subprocess.Popen(
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.PIPE,
        *popenargs,
        **kwargs
    )
    # Very important to close stdin on Windows. See issue mentioned above.
    if is_windows():
        process.stdin.close()
    output, unused_err = process.communicate()
    # It's okay to expect a string out of subprocess. We're only calling this tool
    # to retrieve text from the console to parse it and not binary, so for our
    # use case converting to a str will always make case and simplifies
    # the caller's logic.
    output = sgutils.ensure_str(output)
    retcode = process.poll()

    if retcode:

        logger.debug("Subprocess invocation failed:")
        if popenargs:
            logger.debug("Args  : %s", pprint.pformat(popenargs))
        if kwargs:
            logger.debug("Kwargs: %s", pprint.pformat(kwargs))
        logger.debug("Return code: %d", retcode)
        logger.debug("Process stdout/stderr:")
        logger.debug(output)

        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]

        raise SubprocessCalledProcessError(retcode, cmd, output=output)
    return output
