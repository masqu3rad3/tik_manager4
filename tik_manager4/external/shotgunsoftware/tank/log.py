# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Toolkit uses the standard python logging for its
log management. The :class:`LogManager` class below
acts as an interface that helps make it easy to access
and manage Toolkit logging.


Logging hierarchy
-----------------------------------

All Toolkit logging is written into a ``sgtk.*`` logging
namespace. This has been "sealed" so that log messages
from Toolkit do not propagate up to the root logger. This
is to ensure that Toolkit doesn't interfere with other logging
that has been already configured.

The following sub-hierarchies exist:

- Each app, engine and bundle provides access to logging and
  these log streams are collected and organized under the
  ``sgtk.env`` logging namespace. Below this level, messages
  are broken down further by environment, engine, etc.

- Logging from external tools and scripts is written to ``sgtk.ext``.

- All core logging is written to the ``sgtk.core`` logger.

Below is a simple log hierarchy to illustrate what this might look like in practice.

.. code-block:: text

    sgtk                                              Root point for all Toolkit logging
     |
     |- core                                          Root point for the Core API
     |   |
     |   |- descriptor                                Logging from core Modules
     |   |- path_cache
     |   |- hook
     |       |- create_folders                        Logging from a core hook
     |
     |- env                                           Logging from apps and engines
     |   |
     |   |- project                                   Toolkit Environment
     |       |
     |       |- tk-maya                               Toolkit Engine
     |             |
     |             |- startup                         Toolkit Engine Software Launcher
     |             |
     |             |- tk-multi-workfiles2             Toolkit App (or framework)
     |                  |
     |                  |- tkimp63c3b2d57f85          Toolkit Command Session
     |                  |   |
     |                  |   |- tk_multi_workfiles     Python hierarchy inside app's python folder
     |                  |       |
     |                  |       |- entity_tree
     |                  |
     |                  |
     |                  |
     |                  |- hook
     |                      |- scene_operations       Logging from a hook
     |
     |
     |- ext                                           Logging from associated external scripts
         |
         |- tank_cmd


Generating log messages in Toolkit
-----------------------------------

Generating log messages are done differently depending on your context.
Below are a series of examples and best practice recipes explaining how to best
apply logging to different scenarios.


Logging from within your App, Engine or Framework
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Inside your app, a logger is available via :meth:`~sgtk.platform.Application.logger`.
Alternatively, you can also
use the legacy methods ``log_debug|error|info|...()``. This provides
a basic level of general logging.

For code inside the ``python`` folder, which has been imported via
Toolkit's :meth:`~sgtk.platform.Application.import_module()` method,
we recommend that you access a logger using the following method::

    # at the top of the file, include the following
    import sgtk
    logger = sgtk.platform.get_logger(__name__)

    def my_method():
        logger.debug("inside my code, i can log like this")

This logger will be grouped per invocation instance,
meaning that you can see for example which dialog UI
a particular collection of log messages comes from.
An invocation is typically associated with someone launching
the app from the Shotgun menu.

    .. note:: Because log messages are grouped per invocation,
              this makes it easy to for example generate log files
              for export or import sessions running as part of an
              app. It also makes it possible to create a log window
              which displays the logging associated with a particular
              app UI dialog.

Logging from scripts and other external locations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to add standard Toolkit logging to a script, simply
use the following recipe::

    # at the top of the file, include the following
    import sgtk
    logger = sgtk.LogManager.get_logger(__name__)

    def my_method():
        logger.debug("inside my code, i can log like this")

All this logging will appear below the ``sgtk.ext`` logger.

Logging from inside the Core API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To emit log messages from inside the Toolkit Core API, use the following pattern::

    # at the top of the file, include the following
    import sgtk
    logger = sgtk.LogManager.get_logger(__name__)

    def my_method():
        logger.debug("inside my code, i can log like this")



Consuming log messages in Toolkit
-----------------------------------

Toolkit provides several ways to access the log information generated by
the various methods and recipes shown above.

The general approach is to attach one or several log handlers to the root
logging point of the hierarchy (``sgtk``). Each handler controls its own
logging resolution, e.g. how much log information to display. The toolkit
logging hierarchy itself is set to DEBUG resolution.

The Toolkit :class:`LogManager` provides a default set of logging methods
to help access log information.


Global debug
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Toolkit has a concept of a global debug flag. This flag can be
enabled by setting the ``TK_DEBUG`` environment variable or
alternatively setting the :meth:`LogManager.global_debug` property.

All log handlers that have been created using the :class:`LogManager`
will be affected by the flag.


Backend file logging
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Log information is automatically written to disk by the :class:`LogManager`.
The location to which log files are written can be accessed via the
:meth:`LogManager.log_folder` property. Backend file logging is normally
automatically enabled and end users do not need to worry about this.
If you want debug logging to be written to these files, enable the
global debug flag.

    .. note:: If you are writing a toolkit plugin, we recommend
              that you initialize logging early on in your code by
              calling :meth:`LogManager.initialize_base_file_handler`.
              This will ensure that all your logs are written to disk.
              If you omit this call, logging will automatically be
              started up as the engine is launched.

DCC Logging
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each toolkit engine integrates logging into the DCC. DCCs such as
Maya, Nuke or houdini traditionally have a console of some sort where
logging information typically should be dispatched.

Engine log output has traditionally been implemented by subclassing
the ``log_info``, ``log_error`` methods. In Core v0.18, a new and
improved logging platform is introduced and we recommend that engines
*do not* implement the ``log_xxx`` methods at all but instead implement
a single :meth:`~sgtk.platform.Engine._emit_log_message` method.


Standard Logging
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want some sort of log output in addition to the logging an
engine provides, you can add standard toolkit handlers. These handlers
are created via the :meth:`LogManager.initialize_custom_handler` method.

All log handlers created or registered via this method will respond
to the global debug flag.

    .. note:: If you want a raw log output that is not affected
              by any changes to the global debug flag, we recommend that
              you manually create your log handler and attach it to
              the ``sgtk`` root logger.

Python provides a large number of log handlers as part of its standard library.
For more information, see https://docs.python.org/2/library/logging.handlers.html#module-logging.handlers
"""


import logging
from logging.handlers import RotatingFileHandler
import os
import sys
import time
import weakref
import uuid
from functools import wraps
from . import constants
from tank_vendor import six


class LogManager(object):
    """
    Main interface for logging in Toolkit.

    This class contains a series of methods to help standardize log output
    and access. Since Toolkit uses the standard python logging interface,
    you can manually configure and associate your logging if you like.

    .. note:: This is a singleton class, so every time you instantiate it,
              the same object is returned.
    """

    # keeps track of the single instance of the class
    __instance = None

    class _SafeRotatingFileHandler(RotatingFileHandler):
        """
        Provides all the functionality provided by Python's built-in RotatingFileHandler, but with a
        failsafe when an I/O error happens when doing the rollover. In that case, the failure to
        rename files will be ignored and the handler will keep writing to the current file. A message
        will also be logged at the debug level so the user is aware that something really bad just
        happened. Finally, the handler will not try to rollover in the future and the handler will keep
        appending to the current log file.
        """

        def __init__(
            self, filename, mode="a", maxBytes=0, backupCount=0, encoding=None
        ):
            """
            :param str filename: Name of of the log file.
            :param str mode: Mode to open the file, should be  "w" or "a". Defaults to "a"
            :param int maxBytes: Maximum file size before rollover. By default, rollover never happens.
            :param int backupCount: Number of backups to make. Defaults to 0.
            :param encoding: Encoding to use when writing to the file. Defaults to None.
                File will be opened by default.
            """
            RotatingFileHandler.__init__(
                self, filename, mode, maxBytes, backupCount, encoding
            )
            self._disable_rollover = False

        def doRollover(self):
            """
            Rename every backups so the current log can be promoted to backup number one.

            The new log file is empty. If this process fails due to any I/O error, rollover is
            deactivated for this handler and logs will be appended to the current log file indefinitely.
            """

            temp_backup_name = "%s.%s" % (self.baseFilename, uuid.uuid4())

            # We need to close the file before renaming it (windows!)
            if self.stream:
                self.stream.close()
                self.stream = None

            # Before doing the rollover, check if the first file will fail at all.
            # If it does, then it is a good thing that we checked otherwise the last
            # backup would have been blown away before encountering the error.

            # Take the scenario where there's only one backup. This means that
            # doRollover would first delete the backup (.1) file so it can make
            # room for the main file to be renamed to .1. However, if the main file
            # can't be renamed, we've effectively lost 50% of the logs we had, which
            # is not cool. Since most of the time only the first file will be locked,
            # we will try to rename it first. If that fails right away as expected,
            # we don't try any rollover and append to the current log file.
            # and raise the _disable_rollover flag.

            try:
                os.rename(self.baseFilename, temp_backup_name)
            except:
                # It failed, so we'll simply append from now on.
                log.debug(
                    "Cannot rotate log file '%s'. Logging will continue to this file, "
                    "exceeding the specified maximum size",
                    self.baseFilename,
                    exc_info=True,
                )
                self._handle_rename_failure("a", disable_rollover=True)
                return

            # Everything went well, so now simply move the log file back into place
            # so doRollover can do its work.
            try:
                os.rename(temp_backup_name, self.baseFilename)
            except:
                # For some reason we couldn't move the backup in its place.
                log.debug(
                    "Unexpected issue while rotating log file '%s'. Logging will continue to this file, "
                    "exceeding the specified maximum size",
                    self.baseFilename,
                    exc_info=True,
                )
                # The main log file doesn't exist anymore, so create a new file.
                # Don't disable the rollover, this has nothing to do with rollover
                # failing.
                self._handle_rename_failure("w")
                return

            # Python 2.6 expects the file to be opened during rollover.
            if not self.stream and sys.version_info[:2] < (2, 7):
                self.mode = "a"
                self.stream = self._open()

            # Now, that we are back in the original state we were in,
            # were pretty confident that the rollover will work. However, due to
            # any number of reasons it could still fail. If it does, simply
            # disable rollover and append to the current log.
            try:
                RotatingFileHandler.doRollover(self)
            except:
                # Something probably failed trying to rollover the backups,
                # since the code above proved that in theory the main log file
                # should be renamable. In any case, we didn't succeed in renaming,
                # so disable rollover and reopen the main log file in append mode.
                log.debug(
                    "Cannot rotate log file '%s'. Logging will continue to this file, "
                    "exceeding the specified maximum size",
                    self.baseFilename,
                    exc_info=True,
                )
                self._handle_rename_failure("a", disable_rollover=True)

        def _handle_rename_failure(self, mode, disable_rollover=False):
            """
            Reopen the log file in the specific mode and optionally disable
            future rollover operations.

            :param str mode: Mode in which to reopen the main log file.
            :param bool disable_rollover: If True, rollover won't be possible in the
                future. Defaults to False.
            """
            # Keep track that the rollover failed.
            self._disable_rollover = disable_rollover
            # If the file has been closed, reopen it in append mode.
            if not self.stream:
                self.mode = mode
                self.stream = self._open()

        def shouldRollover(self, record):
            """
            Return if the log files should rollover.

            If a rollover operation failed in the past this method will always return False.

            :param logging.Record record: record that is about to be written to the logs.

            :returns: True if rollover should happen, False otherwise.
            :rtype: bool
            """
            return not self._disable_rollover and RotatingFileHandler.shouldRollover(
                self, record
            )

    def __new__(cls, *args, **kwargs):
        #
        # note - this init isn't currently threadsafe.
        #
        # create the instance if it hasn't been created already
        if not cls.__instance:
            # remember the instance so that no more are created
            instance = super(LogManager, cls).__new__(cls, *args, **kwargs)

            # a global and standard rotating log file handler
            # for writing generic toolkit logs to disk
            instance._std_file_handler = None
            instance._std_file_handler_log_file = None

            # collection of weak references to handlers
            # that were created via the log manager.
            instance._handlers = []

            # the root logger, created at code init
            instance._root_logger = logging.getLogger(constants.ROOT_LOGGER_NAME)

            # check the TK_DEBUG flag at startup
            # this controls the "global debug" state
            # in the log manager
            if constants.DEBUG_LOGGING_ENV_VAR in os.environ:
                log.debug(
                    "%s environment variable detected. Enabling debug logging."
                    % constants.DEBUG_LOGGING_ENV_VAR
                )
                instance._global_debug = True
            else:
                instance._global_debug = False

            cls.__instance = instance

        return cls.__instance

    @staticmethod
    def get_logger(log_name):
        """
        Generates standard logger objects for Toolkit.

        If you want to add standard toolkit logging to your code,
        the easiest way is to include the following at the top of
        your python file::

            import sgtk
            logger = sgtk.LogManager.get_logger(__name__)

        This will pick up the module hierarchy of your code and
        parent it under the standard Toolkit logger.

        .. note:: This method is useful if you are writing scripts, tools or wrappers.
                  If you are developing a Toolkit app, framework or engine,
                  you typically want to use :meth:`sgtk.platform.get_logger`
                  for your logging.

        .. note:: To output logging to screen or to a console,
                  we recommend using the :meth:`initialize_custom_handler`
                  convenience method.

        :param log_name: Name of logger to create. This name will be parented under
                         the sgtk namespace. If the name begins with ``tank.``, it will
                         be automatically replaced with ``sgtk.``.
        :returns: Standard python logger.
        """
        if log_name.startswith("tank."):
            # old style import of core
            #
            # this will be parented under sgtk.core.xxx
            #
            log_name = "%s.core.%s" % (constants.ROOT_LOGGER_NAME, log_name[5:])
        elif log_name.startswith("sgtk."):
            # new style import of core
            #
            # this will be parented under sgtk.core.xxx
            #
            log_name = "%s.core.%s" % (constants.ROOT_LOGGER_NAME, log_name[5:])
        elif log_name.startswith("env."):
            # engine logging
            #
            # this will be parented under sgtk.env.xxx
            # for example sgtk.env.asset.tk-maya
            #

            log_name = "%s.%s" % (constants.ROOT_LOGGER_NAME, log_name)
        else:
            # some external script or tool
            log_name = "%s.ext.%s" % (constants.ROOT_LOGGER_NAME, log_name)

        return logging.getLogger(log_name)

    @staticmethod
    def log_timing(func):
        """
        Decorator that times and logs the execution of a method.

        Sometimes it is useful to log runtime statistics about
        how long time a certain method takes to execute. In the
        case of Toolkit, it is particularly helpful when debugging
        issues to do with I/O or cloud connectivity.

        If you have a method that for example connects to Shotgun to
        retrieve data, you can decorate it::

            @sgtk.LogManager.log_timing
            def my_shotgun_publish_method():
                '''
                Publishes lots of files to Shotgun
                '''
                # shotgun code here

        In the debug logs, timings will be written to the
        ``sgtk.stopwatch`` logger::

            [DEBUG sgtk.stopwatch.module] my_shotgun_publish_method: 0.633s

        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            time_before = time.time()
            try:
                response = func(*args, **kwargs)
            finally:
                time_spent = time.time() - time_before
                # log to special timing logger
                timing_logger = logging.getLogger(
                    "%s.%s" % (constants.PROFILING_LOG_CHANNEL, func.__module__)
                )
                timing_logger.debug("%s: %fs" % (func.__name__, time_spent))
            return response

        return wrapper

    def _set_global_debug(self, state):
        """
        Sets the state of the global debug in toolkit.
        """
        if not state:
            # This needs to be logged before we turn off the global
            # debug logging.
            #
            # We don't want subprocesses of this process to spawn with
            # logging on. An example of where this is useful is in the
            # comment below, where the case of tk-desktop is outlined.
            if constants.DEBUG_LOGGING_ENV_VAR in os.environ:
                log.debug(
                    "Removing %s from the environment for this session. This "
                    "ensures that subprocesses spawned from this process will "
                    "inherit the global debug logging setting from this process.",
                    constants.DEBUG_LOGGING_ENV_VAR,
                )
                del os.environ[constants.DEBUG_LOGGING_ENV_VAR]

        self._global_debug = state
        if self._global_debug:
            new_log_level = logging.DEBUG
        else:
            log.debug("Disabling debug logging.")
            new_log_level = logging.INFO

        # process handlers
        for handler_weak_ref in self._handlers:
            handler = handler_weak_ref()
            if handler:
                handler.setLevel(new_log_level)

        # process backdoor logger
        if self.base_file_handler:
            self.base_file_handler.setLevel(new_log_level)

        # log notifications
        if self._global_debug:
            log.debug(
                "Debug logging enabled. To permanently enable it, "
                "set the %s environment variable." % constants.DEBUG_LOGGING_ENV_VAR
            )
            # This needs to be logged after the global debug has been
            # turned on, which is why it is happening last.
            #
            # Setting the environment variable for this session will
            # mean that any subprocesses spawned will inherit debug
            # logging from this process. A good example of where this
            # is advantageous is in tk-desktop, where we provide a
            # menu action to toggle debug logging. When it is toggled
            # on, we set the env var here, which then means that when
            # a user navigates to a project in the PTR desktop app, the
            # Python subprocess spawned will also have debug logging active.
            log.debug(
                "Setting %s in the environment for this session. This "
                "ensures that subprocesses spawned from this process will "
                "inherit the global debug logging setting from this process.",
                constants.DEBUG_LOGGING_ENV_VAR,
            )
            os.environ[constants.DEBUG_LOGGING_ENV_VAR] = "1"

    def _get_global_debug(self):
        """
        Controls the global debug flag in toolkit. Toggling this
        flag will affect all log handlers that have been created
        via :meth:`initialize_custom_handler`.

        .. note:: Debug logging is off by default.
                  If you want to permanently enable debug logging,
                  set the environment variable ``TK_DEBUG``.
        """
        return self._global_debug

    global_debug = property(_get_global_debug, _set_global_debug)

    @property
    def log_file(self):
        """ Full path to the current log file or None if logging is not active. """
        return self._std_file_handler_log_file

    @property
    def log_folder(self):
        """
        The folder where log files generated by :meth:`initialize_base_file_handler` are stored.
        """
        # avoid cyclic references
        from .util import LocalFileStorageManager

        return LocalFileStorageManager.get_global_root(LocalFileStorageManager.LOGGING)

    @property
    def root_logger(self):
        """
        Returns the root logger for Toolkit.

        .. note:: If you want to add a custom logging handler to the root logger,
                  we recommend using the :meth:`initialize_custom_handler` method.

        .. warning:: The root logger logs down to a debug resolution by default.
                     Do not change the output level of logger as this will have
                     a global effect. If you are connecting a logging handler
                     and want to limit the stream of messages that are being
                     emitted, instead adjust the logging level of the handler.

        :return: log object
        """
        return self._root_logger

    @property
    def base_file_handler(self):
        """
        The base file handler that is used to write log files to disk
        in a default location, or None if not defined.
        """
        return self._std_file_handler

    def initialize_custom_handler(self, handler=None):
        """
        Convenience method that initializes a log handler
        and attaches it to the toolkit logging root.

        .. note:: If you want to display log messages inside a DCC,
                  implement :meth:`~sgtk.platform.Engine._emit_log_message`.

        .. note:: If :meth:`global_debug` is set to True, the handler created
                  will be set to debug level, otherwise it will be set to info level.
                  Furthermore, the log handler will automatically adjust its log
                  level whenever the global debug flag changes its state.

        Calling this without parameters will generate a standard
        stream based logging handler that logs to stderr::

            # start logging to stderr
            import sgtk.LogManager
            LogManager().initialize_custom_handler()

        If you want to log to a file instead, create a log handler
        and pass that to the method::

            handler = logging.FileHandler("/tmp/toolkit.log)
            LogManager().initialize_custom_handler(handler)

        The log handler will be configured to output its messages
        in a standard fashion.

        :param handler: Logging handler to connect with the toolkit logger.
                        If not passed, a standard stream handler will be created.
        :return: The configured log handler.
        """
        if handler is None:
            handler = logging.StreamHandler()

            # example: [DEBUG tank.log] message message
            formatter = logging.Formatter("[%(levelname)s %(name)s] %(message)s")

            handler.setFormatter(formatter)

        self._root_logger.addHandler(handler)

        if self.global_debug:
            handler.setLevel(logging.DEBUG)
        else:
            handler.setLevel(logging.INFO)

        # add it to our list of handlers, but as a
        # weak reference so that it can be destroyed
        # elsewhere (e.g. at engine shutdown)
        self._handlers.append(weakref.ref(handler))

        return handler

    def uninitialize_base_file_handler(self):
        """
        Uninitialize base file handler created with :meth:`initialize_base_file_handler`.

        :returns: The path to the previous log file that is being switched away from,
                  None if no base logger was previously active.
        """
        if self._std_file_handler is None:
            return None

        base_log_file = self._std_file_handler_log_file

        # there is a log handler, so terminate it
        log.debug(
            "Tearing down existing log handler '%s' (%s)"
            % (base_log_file, self._std_file_handler)
        )
        self._root_logger.removeHandler(self._std_file_handler)
        self._std_file_handler = None
        self._std_file_handler_log_file = None

        # return the previous base log file path.
        return base_log_file

    def initialize_base_file_handler(self, log_name):
        """
        Create a file handler and attach it to the stgk base logger.
        This will write a rotating log file to disk in a standard
        location and will capture all log messages passed through
        the log hierarchy.

        .. note:: Files will be written into the location on disk
                  defined by :meth:`log_folder`.

        When you start an engine via the :meth:`sgtk.platform.start_engine` method,
        a file handler will automatically be created if one doesn't already exist.

        If you are manually launching toolkit, we recommend that you call
        this method to initialize logging to file early on in your setup.
        Calling it multiple times will not result in the information being
        written to multiple different files - only one file logger can
        exist per session.

        :param log_name: Name of logger to create. This will form the
                         filename of the log file. The ``.log`` will be suffixed.

        :returns: The path to the previous log file that is being switched away from,
                  None if no base logger was previously active.
        """
        # avoid cyclic references
        from .util import filesystem

        return self.initialize_base_file_handler_from_path(
            os.path.join(
                self.log_folder, "%s.log" % filesystem.create_valid_filename(log_name)
            )
        )

    def initialize_base_file_handler_from_path(self, log_file):
        """
        Create a file handler and attach it to the sgtk base logger.

        This method is there for legacy Toolkit applications and shouldn't be used. Use
        ``initialize_base_file_handler`` instead.

        :param log_file: Path of the file to write the logs to.

        :returns: The path to the previous log file that is being switched away from,
                  None if no base logger was previously active.
        """
        # shut down any previous logger
        previous_log_file = self.uninitialize_base_file_handler()

        log_folder, log_file_name = os.path.split(log_file)
        log_name, _ = os.path.splitext(log_file_name)

        log.debug(
            "Switching file based std logger from '%s' to '%s'.",
            previous_log_file,
            log_file,
        )

        # store new log name
        self._std_file_handler_log_file = log_file

        # avoid cyclic references
        from .util import filesystem

        # set up logging root folder
        filesystem.ensure_folder_exists(log_folder)

        # create a rotating log file with a max size of 5 megs -
        # this should make all log files easily attachable to support tickets.
        self._std_file_handler = self._SafeRotatingFileHandler(
            log_file,
            # 5 MiB
            maxBytes=1024 * 1024 * 5,
            # Need at least one backup in order to rotate
            backupCount=1,
            # Python 3 is pickier about the encoding type of a file.
            # Python 2 treats str as bytes, so it writes them
            # directly to disk. Putting utf8 encoding actually
            # causes problems.
            encoding="utf8" if six.PY3 else None,
        )

        # set the level based on global debug flag
        if self.global_debug:
            self._std_file_handler.setLevel(logging.DEBUG)
        else:
            self._std_file_handler.setLevel(logging.INFO)

        # Set up formatter. Example:
        # 2016-04-25 08:56:12,413 [44862 DEBUG tank.log] message message
        formatter = logging.Formatter(
            "%(asctime)s [%(process)d %(levelname)s %(name)s] %(message)s"
        )

        self._std_file_handler.setFormatter(formatter)
        self._root_logger.addHandler(self._std_file_handler)

        # log the fact that we set up the log file :)
        log.debug("Writing to standard log file %s" % log_file)

        # return previous log name
        return previous_log_file


# the logger for logging messages from this file :)
log = LogManager.get_logger(__name__)

# initialize toolkit logging
#
# retrieve top most logger in the sgtk hierarchy
sgtk_root_logger = logging.getLogger(constants.ROOT_LOGGER_NAME)
# 'cap it' so that log messages don't propagate
# further upwards in the hierarchy. This is to avoid
# log message spilling over into other loggers; if you
# want to receive toolkit log messages, you have to
# explicitly attach a log handler to the sgtk top level
# logger (or any of its child loggers).
sgtk_root_logger.propagate = False
# The top level logger object has its message throughput
# level set to DEBUG by default.
# this should not be changed, but any filtering
# should happen via log handlers
sgtk_root_logger.setLevel(logging.DEBUG)
#
# create a 'nop' log handler to be attached.
# this is to avoid warnings being reported that
# logging is missing.
#
class NullHandler(logging.Handler):
    def emit(self, record):
        pass


# and add it to the logger
sgtk_root_logger.addHandler(NullHandler())
