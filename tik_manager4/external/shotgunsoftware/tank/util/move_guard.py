# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os

from ..log import LogManager

log = LogManager.get_logger(__name__)


class MoveGuard(object):
    """
    Ensures that files that were moved during a scope are moved to their
    original location if an exception was raised during that scope.
    """

    def __init__(self, undo_on_error):
        """
        :param bool undo_on_error: If true, the moves will be undone when an exception
            is raised. If false, the files won't be moved back when an exception is raised.
        """
        self._undo_on_error = undo_on_error
        self._moves = []

    def __enter__(self):
        """
        Returns itself so files can be moved and tracked.
        """
        return self

    def move(self, source, dest):
        """
        Moves a file and keeps track of the move operation if it succeeded.

        :param str source: File to move.
        :param str dest: New location for that file.
        """
        os.rename(source, dest)
        self._moves.append((source, dest))

    def done(self):
        """
        Indicates the guard that we are done with our operations and that further exceptions
        shouldn't undo file operations.
        """
        self._undo_on_error = False

    def __exit__(self, ex_type, value, traceback):
        """
        Invoked when leaving the scope of the guard.

        If some files have been moved, move them back to their original location.
        """
        if (ex_type or value or traceback) and self._undo_on_error and self._moves:
            log.debug("Reverting changes!")
            # Move files back to their original location.
            for source, dest in self._moves:
                log.debug("Moving %s -> %s" % (dest, source))
                os.rename(dest, source)
