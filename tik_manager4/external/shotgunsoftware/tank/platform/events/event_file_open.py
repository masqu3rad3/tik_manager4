# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from .event_engine import EngineEvent


class FileOpenEvent(EngineEvent):
    """
    An object representation of a file-open event.
    """

    def __init__(self, file_path):
        """
        Constructor.

        :param str file_path: The path to the file opened.
        """
        super(FileOpenEvent, self).__init__()
        self._file_path = file_path

    @property
    def file_path(self):
        """
        The string path of the file that was opened.
        """
        return self._file_path

    def __str__(self):
        return "%s: %s" % ("FileOpenEvent", self.file_path)
