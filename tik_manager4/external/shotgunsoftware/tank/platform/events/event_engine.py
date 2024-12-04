# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.


class EngineEvent(object):
    """
    The base class of all concrete engine event objects. It provides a very
    basic interface that is expanded on in deriving classes.
    """

    def __repr__(self):
        class_name = self.__class__.__name__
        return "<%s 0x%08x>" % (class_name, id(self))
