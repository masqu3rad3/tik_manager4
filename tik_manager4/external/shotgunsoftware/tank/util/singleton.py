# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from __future__ import with_statement
import threading


class Singleton(object):
    """
    Thread-safe base class for singletons. Derived classes must implement _init_singleton.
    """

    __lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """
        Create the singleton instance if it hasn't been created already. Once instantiated,
        the object will be cached and never be instantiated again for performance
        reasons.
        """

        # Check if the instance has been created before taking the lock for performance
        # reason.
        if not hasattr(cls, "_instance") or cls._instance is None:
            # Take the lock.
            with cls.__lock:
                # Check the instance again, it might have been created between the
                # if and the lock.
                if hasattr(cls, "_instance") and cls._instance:
                    return cls._instance

                # Create and init the instance.
                instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
                instance._init_singleton()

                # remember the instance so that no more are created
                cls._instance = instance

        return cls._instance

    @classmethod
    def clear_singleton(cls):
        """
        Clears the internal singleton instance.
        """
        cls._instance = None
