# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import imp
import uuid
import os
import sys
import warnings
from .. import LogManager

log = LogManager.get_logger(__name__)


class CoreImportHandler(object):
    """
    A custom import handler to allow for core version switching.


    The core path is used to locate modules attempting to be loaded. The core
    path can be set via `set_core_path` to alter the location of existing and
    future core imports.

    For more information on custom import hooks, see PEP 302:
        https://www.python.org/dev/peps/pep-0302/

    """

    NAMESPACES_TO_TRACK = ["tank", "sgtk", "tank_vendor"]

    @classmethod
    def swap_core(cls, core_path):
        """
        Swap the current core with the core located at the supplied path.

        Actually just unloads the existing core and ensures an import handler
        exists that points to the supplied core path. When this method completes,
        all core namespaces will be removed from `sys.modules`.

        :param core_path: The path to the new core to use upon import.
        """
        # make sure handler is up
        handler = cls._initialize()

        log.debug("%s: Begin swapping core to %s" % (handler, core_path))

        # swapping core means our logging singleton will be reset.
        # make sure that there are no log handlers registered
        # and associated with the singleton as these will be lost
        # use local imports to ensure a fresh cut of the code
        from ..log import LogManager

        prev_log_file = LogManager().uninitialize_base_file_handler()
        # logging to file is now disabled and will be renamed after the
        # main tank import of the new code.

        # make sure that this entire operation runs inside the import thread lock
        # in order to not cause any type of cross-thread confusion during the swap
        imp.acquire_lock()

        try:
            handler._swap_core(core_path)

            # because we are swapping out the code that we are currently running, Python is
            # generating a runtime warning:
            #
            # RuntimeWarning: Parent module 'tank.bootstrap' not found while handling absolute import
            #
            # We are fixing this issue by re-importing tank, so it's essentially a chicken and egg
            # scenario. So it's ok to mute the warning. Interestingly, by muting the warning, the
            # execution of the reload/import becomes more complete and it seems some parts of the
            # code that weren't previously reloaded are now covered. So turning off the warnings
            # display seems to have executionary side effects.

            # Save the existing list of warning filters before we modify it using simplefilter().
            # Note: the '[:]' causes a copy of the list to be created. Without it, original_filter
            # would alias the one and only 'real' list and then we'd have nothing to restore.
            original_filters = warnings.filters[:]

            # Ignore all warnings
            warnings.simplefilter("ignore")

            log.debug("...core swap complete.")

            log.debug("running explicit 'import tank' to re-initialize new core...")

            try:
                # Kick toolkit to re-import
                import tank

            finally:
                # Restore the list of warning filters.
                warnings.filters = original_filters

            log.debug("...import complete")

        finally:
            imp.release_lock()

        # and re-init our disk logging based on the new code
        # access it from the new tank instance to ensure we get the new code
        try:
            if prev_log_file:
                tank.LogManager().initialize_base_file_handler_from_path(prev_log_file)
        except AttributeError as e:
            # older versions of the API may not have this defined.
            log.debug(
                "Switching to a version of the core API that doesn't "
                "have a LogManager.initialize_base_file_handler_from_path method defined."
            )

    @classmethod
    def _initialize(cls):
        """
        Boots up the import manager if it's not already up.

        :returns: CoreImportHandler instance
        """
        # see if there's already a core import handler in use
        for handler in sys.meta_path:
            if isinstance(handler, CoreImportHandler):
                return handler

        # no import handler found, so create one.
        current_folder = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        handler = cls(current_folder)
        # Insert our handler at the front of the list. In Python 2, the position of the
        # handler is not important because meta path is scanned first and then sys.path
        # In Python 3 however, the sys.path importer IS a meta_path importer as well.
        # If we simply append our handler, it means we'll run after the path importer,
        # which means the old copy of core will be imported instead of the
        # new one.
        sys.meta_path.insert(0, handler)
        log.debug("Added import handler to sys.meta_path to support core swapping.")
        return handler

    def __init__(self, core_path):
        """Initialize the custom importer.

        :param core_path: A str path to the core location to import from.
        """
        self._core_path = core_path

        # a dictionary to hold module information after it is found,
        # before it is loaded.
        self._module_info = {}

    def __repr__(self):
        """
        A unique representation of the handler.

        :return: str representation.
        """
        return "<CoreImportHandler for '%s'>" % self._core_path

    def _swap_core(self, core_path):
        """
        Actual payload for the core swapping.

        To swap a core, call CoreImportHandler.swap_core().

        :param core_path: core path to swap to.
        """
        if not os.path.exists(core_path):
            raise ValueError(
                "The supplied core path '%s' is not a valid directory." % core_path
            )

        # acquire a lock to prevent issues with other
        # threads importing at the same time.
        imp.acquire_lock()

        try:

            # sort by package depth, deeper modules first
            module_names = sorted(
                sys.modules.keys(),
                key=lambda module_name: module_name.count("."),
                reverse=True,
            )

            # unique prefix for stashing this session
            stash_prefix = "core_swap_%s" % uuid.uuid4().hex

            for module_name in module_names:

                # just to be safe, don't re-import this module.
                # we always use the first one added to `sys.meta_path` anyway.
                if module_name == __name__:
                    continue

                # extract just the package name
                pkg_name = module_name.split(".")[0]

                if pkg_name in self.NAMESPACES_TO_TRACK:
                    # the package name is in one of the new core namespaces. we
                    # delete it from sys.modules so that the custom import can run.
                    module = sys.modules[module_name]
                    # note: module entries that are None can safely be left in sys.modules -
                    # these are optimizations used by the importer. Read more here:
                    # http://stackoverflow.com/questions/1958417/why-are-there-dummy-modules-in-sys-modules
                    if module:
                        # make sure we don't lose any references to it - for example
                        # via instances that have been inherited from base classes
                        # to make sure a reference is kept, keep the module object
                        # but move it out of the way in sys.modules to allow for
                        # a new version of the module to be imported alongside.
                        stashed_module_name = "%s_%s" % (stash_prefix, module_name)

                        # uncomment for copious amounts of debug
                        # log.debug(
                        #     "Relocating module %s from sys.modules[%s] "
                        #     "to sys.modules[%s]" % (module, module_name, stashed_module_name)
                        # )

                        sys.modules[stashed_module_name] = module

                        # and remove the official entry
                        # log.debug("Removing sys.modules[%s]" % module_name)
                        del sys.modules[module_name]

            # reset importer to point at new core for future imports
            self._module_info = {}
            self._core_path = core_path

        finally:
            # release the lock so that other threads can continue importing from
            # the new core location.
            imp.release_lock()

    def find_module(self, module_fullname, package_path=None):
        """Locates the given module in the current core.

        This method is part of the custom import handler interface contract.

        :param module_fullname: The fullname of the module to import
        :param package_path: None for a top-level module, or
            package.__path__ for submodules or subpackages

        The package_path is currently ignored by this method as it ensures we're
        importing the module from the current core path.

        For further info, see the docs on find_module here:
            https://docs.python.org/2/library/imp.html#imp.find_module

        :returns: this object (also a loader) if module found, None otherwise.
        """
        # get the package name (first part of the module fullname)
        module_path_parts = module_fullname.split(".")
        package_name = module_path_parts[0]

        # make sure the package is in the list of namespaces before continuing.
        if package_name not in self.NAMESPACES_TO_TRACK:
            # the package is not in one of the core namespaces. returning
            # None tells python to use the next importer available (likely the
            # default import mechanism).
            return None

        if len(module_path_parts) > 1:
            # this is a dotted path. we need to recursively import the parents
            # with this logic. once we've found the immediate parent we
            # can use it's `__path__` attribute to locate this module.
            # this matches the suggested logic for finding nested modules in
            # the `imp.find_module` docs found here:
            #     https://docs.python.org/2/library/imp.html

            parent_module_parts = module_path_parts[:-1]

            # this is the parent module's full package spec.
            parent_path = ".".join(parent_module_parts)

            if parent_path in sys.modules:
                # if the parent has already been imported, then we can just grab
                # it's path to locate this module
                package_path = sys.modules[parent_path].__path__
            else:
                # parent hasn't been loaded. do a recursive find/load in order
                # to get the parent's path
                if self.find_module(parent_path):
                    parent_module = self.load_module(parent_path)
                    package_path = parent_module.__path__
                else:
                    # could not find parent module. we'll try to build a path
                    # given what we know about core and the parent package path.
                    # this turns parent package "foo.bar" into:
                    #    /path/to/current/core/foo/bar
                    package_path = [os.path.join(self._core_path, *parent_module_parts)]
        else:
            # this appears to be a top-level package. it should be in the
            # current core's root path.
            package_path = [self._core_path]

        # module path without the target module name
        module_name = module_path_parts.pop()

        try:
            # find the module and store its info in a lookup based on the
            # full module name. The module info is a tuple of the form:
            #
            #   (file_obj, filename, description)
            #
            # If this find is successful, we'll need the info in order
            # to load it later.
            module_info = imp.find_module(module_name, package_path)
            self._module_info[module_fullname] = module_info
        except ImportError:
            # no module found, fall back to regular import
            return None

        # since this object is also the "loader" return itself
        return self

    def load_module(self, module_fullname):
        """Custom loader.

        Called by python if the find_module was successful.

        This method is part of the custom import handler interface contract.

        For further info, see the docs on `load_module` here:
            https://docs.python.org/2/library/imp.html#imp.load_module

        :param module_fullname: The fullname of the module to import

        :returns: The loaded module object.

        """
        file_obj = None
        try:
            # retrieve the found module info
            (file_obj, filename, desc) = self._module_info[module_fullname]

            # uncomment for lots of import related debug :)
            # log.debug("Custom load module! %s [%s]" % (module_fullname, filename))

            # attempt to load the module. if this fails, allow it to raise
            # the usual `ImportError`
            module = imp.load_module(module_fullname, file_obj, filename, desc)
        finally:
            # as noted in the imp.load_module docs, must close the file handle.
            if file_obj:
                file_obj.close()

            # no need to carry around the module info now that we've loaded it.
            # once the module is in `sys.modules`, the custom importer will
            # no longer run.
            del self._module_info[module_fullname]

        # the module needs to know the loader so that reload() works
        module.__loader__ = self

        # the module has been loaded from the proper core location!
        return module
