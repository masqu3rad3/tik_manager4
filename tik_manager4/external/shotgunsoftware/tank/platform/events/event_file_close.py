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


class FileCloseEvent(EngineEvent):
    """
    An object representation of a file-close event.

    The event holds a :meth:file_path property, indicating which open file or
    document the event is referring to. In engine implementations which
    integrate with MDI applications, the path is required in order to
    distinguish which document is being closed.

    In engine implementations where the current file isn't known, well defined
    or accessible, a None value should be returned to indicate this.

    Note that the file_path may represent a document that has not yet been
    saved. In this case, it may not be a full path but instead the name of the
    document, for example "untitled" or an empty string "". The event
    information should transparently reflect whatever is returned from the
    underlying application.
    """

    def __init__(self, file_path):
        """
        Constructor.

        :param str file_path: The path to the file closed.
        """
        super(FileCloseEvent, self).__init__()
        self._file_path = file_path

    @property
    def file_path(self):
        """
        The string path of the file that was closed.
        """
        return self._file_path

    def __str__(self):
        return "%s: %s" % ("FileCloseEvent", self.file_path)
