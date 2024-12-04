# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Methods for loading and managing plugins, e.g. Apps, Engines, Hooks etc.

"""

import sys
import imp
import traceback
import inspect

from ..errors import TankError
from .. import LogManager

log = LogManager.get_logger(__name__)


class TankLoadPluginError(TankError):
    """
    Errors related to git communication
    """

    pass


def load_plugin(plugin_file, valid_base_class, alternate_base_classes=None):
    """
    Load a plugin into memory and extract its single interface class.

    :param plugin_file:             The file to use when looking for the plug-in class to load
    :param valid_base_class:        A type to use when searching for a derived class.
    :param alternate_base_classes:  A list of alternate base classes to be searched for if a class deriving
                                    from valid_base_class can't be found
    :returns:                       A class derived from the base class if found
    :raises:                        Raises a TankError if it fails to load the file or doesn't find exactly
                                    one matching class.
    """
    # build a single list of valid base classes including any alternate base classes
    alternate_base_classes = alternate_base_classes or []
    valid_base_classes = [valid_base_class] + alternate_base_classes

    # construct a uuid and use this as the module name to ensure
    # that each import is unique
    import uuid

    module_uid = uuid.uuid4().hex
    module = None
    try:
        imp.acquire_lock()
        module = imp.load_source(module_uid, plugin_file)
    except Exception:
        # log the full callstack to make sure that whatever the
        # calling code is doing, this error is logged to help
        # with troubleshooting and support
        log.exception("Cannot load plugin file '%s'" % plugin_file)

        # dump out the callstack for this one -- to help people get good messages when there is a plugin error
        (exc_type, exc_value, exc_traceback) = sys.exc_info()
        message = ""
        message += (
            "Failed to load plugin %s. The following error was reported:\n"
            % plugin_file
        )
        message += "Exception: %s - %s\n" % (exc_type, exc_value)
        message += "Traceback (most recent call last):\n"
        message += "\n".join(traceback.format_tb(exc_traceback))
        raise TankLoadPluginError(message)
    finally:
        imp.release_lock()

    # cool, now validate the module
    found_classes = list()
    try:
        # first, find all classes in the module, being careful to only find classes that
        # are actually from this module and not from any other imports!
        search_predicate = (
            lambda member: inspect.isclass(member)
            and member.__module__ == module.__name__
        )
        all_classes = [cls for _, cls in inspect.getmembers(module, search_predicate)]

        # Now look for classes in the module that are derived from the specified base
        # class.  Note that 'inspect.getmembers' returns the contents of the module
        # in alphabetical order so no assumptions should be made based on the order!
        #
        # Enumerate the valid_base_classes in order so that we find the highest derived
        # class we can.
        for base_cls in valid_base_classes:
            found_classes = [cls for cls in all_classes if issubclass(cls, base_cls)]
            if len(found_classes) > 1:
                # it's possible that this file contains multiple levels of derivation - if this
                # is the case then we should try to remove any intermediate classes from the list
                # of found classes so that we are left with only leaf classes:
                filtered_classes = list(found_classes)
                for cls in found_classes:
                    for base in cls.__bases__:
                        if base in filtered_classes:
                            # this is an intermediate class so remove it from the list:
                            filtered_classes.remove(base)
                found_classes = filtered_classes
            if found_classes:
                # we found at least one class so assume this is a match!
                break
    except Exception as e:

        # log the full callstack to make sure that whatever the
        # calling code is doing, this error is logged to help
        # with troubleshooting and support
        log.exception("Failed to introspect hook structure for '%s'" % plugin_file)

        # re-raise as a TankError
        raise TankError(
            "Introspection error while trying to load and introspect file %s. "
            "Error Reported: %s" % (plugin_file, e)
        )

    if len(found_classes) != 1:
        # didn't find exactly one matching class!
        msg = (
            "Error loading the file '%s'. Couldn't find a single class deriving from '%s'. "
            "You need to have exactly one class defined in the file deriving from that base class. "
            "If your file looks fine, it is possible that the cached .pyc file that python "
            "generates is invalid and this is causing the error. In that case, please delete "
            "the .pyc file and try again." % (plugin_file, valid_base_class.__name__)
        )

        raise TankLoadPluginError(msg)

    # return the class that was found.
    return found_classes[0]
