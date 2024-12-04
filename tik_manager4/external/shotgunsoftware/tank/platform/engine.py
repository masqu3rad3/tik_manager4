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
Defines the base class for all Tank Engines.
"""

from __future__ import with_statement

import os
import sys
import logging
import pprint
import traceback
import inspect
import weakref
import threading

from tank_vendor import six

from ..util.qt_importer import QtImporter
from ..util.loader import load_plugin
from .. import hook

from ..errors import TankError
from .errors import (
    TankEngineInitError,
    TankUnresolvedEnvironmentError,
    TankContextChangeNotSupportedError,
    TankEngineEventError,
    TankMissingEngineError,
)

from ..util import sgre as re
from ..util.metrics import EventMetric
from ..util.metrics import MetricsDispatcher
from ..util import metrics_cache
from ..log import LogManager

from . import application
from . import constants
from . import validation
from . import events
from . import qt
from . import qt5
from . import qt6
from .bundle import TankBundle
from .framework import setup_frameworks
from .engine_logging import ToolkitEngineHandler, ToolkitEngineLegacyHandler

# std core level logger
core_logger = LogManager.get_logger(__name__)


class Engine(TankBundle):
    """
    Base class for an engine. When a new DCC integration is created, it should
    derive from this class.
    """

    _ASYNC_INVOKER, _SYNC_INVOKER = range(2)

    def __init__(self, tk, context, engine_instance_name, env):
        """
        Engine instances are constructed by the toolkit launch process
        and various factory methods such as :meth:`start_engine`.

        :param tk: :class:`~sgtk.Sgtk` instance
        :param context: A context object to define the context on disk where the engine is operating
        :type context: :class:`~sgtk.Context`
        :param engine_instance_name: The name of the engine as it has been defined in the environment.
        :param env: An Environment object to associate with this engine.

        """

        self.__env = env
        self.__engine_instance_name = engine_instance_name
        self.__applications = {}
        self.__application_pool = {}
        self.__shared_frameworks = {}
        self.__commands = {}
        self.__command_pool = {}
        self.__panels = {}
        self.__currently_initializing_app = None

        self.__qt_widget_trash = []
        self.__created_qt_dialogs = []
        self.__qt_debug_info = {}
        self.__has_qt5 = False
        self.__has_qt6 = False

        self.__commands_that_need_prefixing = []

        self.__global_progress_widget = None

        self.__fonts_loaded = False

        self._metrics_dispatcher = None

        # Initialize these early on so that methods implemented in the derived class and trying
        # to access the invoker don't trip on undefined variables.
        self._invoker = None
        self._async_invoker = None

        # get the engine settings
        settings = self.__env.get_engine_settings(self.__engine_instance_name)

        # get the descriptor representing the engine
        descriptor = self.__env.get_engine_descriptor(self.__engine_instance_name)

        # create logger for this engine.
        # log will be parented in a sgtk.env.environment_name.engine_instance_name hierarchy
        logger = LogManager.get_logger("env.%s.%s" % (env.name, engine_instance_name))

        # init base class
        TankBundle.__init__(self, tk, context, settings, descriptor, env, logger)

        # create a log handler to handle log dispatch from self.log
        # (and the rest of the sgtk logging ) to the user
        self.__log_handler = self.__initialize_logging()

        # check general debug log setting and if this flag is turned on,
        # adjust the global setting
        if self.get_setting("debug_logging", False):
            LogManager().global_debug = True
            self.log_debug(
                "Detected setting 'config/env/%s.yml:%s.debug_logging: true' "
                "in your environment configuration. Turning on debug output."
                % (env.name, engine_instance_name)
            )

        # check that the context contains all the info that the app needs
        validation.validate_context(descriptor, context)

        # make sure the current operating system platform is supported
        validation.validate_platform(descriptor)

        # Get the settings for the engine and then validate them
        engine_schema = descriptor.configuration_schema
        validation.validate_settings(
            self.__engine_instance_name, tk, context, engine_schema, settings
        )

        # set up any frameworks defined
        setup_frameworks(self, self, self.__env, descriptor)

        # run the engine init
        self.log_debug("Engine init: Instantiating %s" % self)
        self.log_debug("Engine init: Current Context: %s" % context)

        # now if a folder named python is defined in the engine, add it to the pythonpath
        my_path = os.path.dirname(sys.modules[self.__module__].__file__)
        python_path = os.path.join(my_path, constants.BUNDLE_PYTHON_FOLDER)
        if os.path.exists(python_path):
            # Only append if __init__.py doesn't exist. If it does then we
            # should use the special tank import instead.
            init_path = os.path.join(python_path, "__init__.py")
            if not os.path.exists(init_path):
                self.log_debug("Appending to PYTHONPATH: %s" % python_path)
                sys.path.append(python_path)

        # Note, 'init_engine()' is now deprecated and all derived initialisation should be
        # done in either 'pre_app_init()' or 'post_app_init()'.  'init_engine()' is left
        # in here to provide backwards compatibility with any legacy code.
        self.init_engine()

        # try to pull in QT classes and assign to tank.platform.qt.XYZ
        base_def = self._define_qt_base()
        qt.QtCore = base_def.get("qt_core")
        qt.QtGui = base_def.get("qt_gui")
        qt.TankDialogBase = base_def.get("dialog_base")
        qt.shiboken = base_def.get("shiboken")

        qt5_base = self.__define_qt5_base()
        self.__has_qt5 = len(qt5_base) > 0
        for name, value in qt5_base.items():
            setattr(qt5, name, value)

        qt6_base = self.__define_qt6_base()
        self.__has_qt6 = len(qt6_base) > 0
        for name, value in qt6_base.items():
            setattr(qt6, name, value)

        # Update the authentication module to use the engine's Qt.
        # @todo: can this import be untangled? Code references internal part of the auth module
        from ..authentication.ui import qt_abstraction

        qt_abstraction.QtCore = qt.QtCore
        qt_abstraction.QtGui = qt.QtGui

        # load the fonts. this will work if there is a QApplication instance
        # available.
        self._ensure_core_fonts_loaded()

        # create invoker to allow execution of functions on the
        # main thread:
        self._invoker, self._async_invoker = self.__create_invokers()

        # run any init that needs to be done before the apps are loaded:
        self.pre_app_init()

        # now load all apps and their settings
        self.__load_apps()

        # execute the post engine init for all apps
        # note that this is executed before the post_app_init
        # in the engine - this is because typically the post app
        # init in the engine will contain code which captures the
        # state of the apps - for example creates a menu, so at that
        # point we want to try and have all app initialization complete.
        self.__run_post_engine_inits()

        # The new way to handle this situation is via the register_toggle_debug_command
        # property on the engine. We also explicitly skip the shell and shotgun engines
        # here for the sake of backwards compatibility, as these engines have always
        # skipped registering the command by name.
        is_skipped_engine = self.name in [
            constants.SHELL_ENGINE_NAME,
            constants.SHOTGUN_ENGINE_NAME,
        ]
        supports_018_logging = self.__has_018_logging_support()
        wants_toggle_debug = self.register_toggle_debug_command

        if not is_skipped_engine and supports_018_logging and wants_toggle_debug:
            # if engine supports new logging implementation,
            #
            # we cannot add the 'toggle debug logging' for
            # an engine that has the old logging implementation
            # because that typically contains overrides in log_debug
            # which effectively renders the command below useless

            # note that we omit this action in the special built-in
            # engines tk-shell and tk-shotgun

            self.register_command(
                "Toggle Debug Logging",
                self.__toggle_debug_logging,
                {
                    "short_name": "toggle_debug",
                    "icon": self.__get_platform_resource_path("book_256.png"),
                    "description": (
                        "Toggles toolkit debug logging on and off. "
                        "This affects all debug logging, including log "
                        "files that are being written to disk."
                    ),
                    "type": "context_menu",
                },
            )

        # add a 'open log folder' command to the engine's context menu
        # note: we make an exception for the shotgun engine which is a
        # special case.
        if self.name != constants.SHOTGUN_ENGINE_NAME:

            self.register_command(
                "Open Log Folder",
                self.__open_log_folder,
                {
                    "short_name": "open_log_folder",
                    "icon": self.__get_platform_resource_path("folder_256.png"),
                    "description": "Opens the folder where log files are being stored.",
                    "type": "context_menu",
                },
            )

        # Useful dev helpers: If there is one or more dev descriptors in the
        # loaded environment, add a reload button to the menu!
        self.__register_reload_command()

        # now run the post app init
        self.post_app_init()

        # emit an engine started event
        tk.execute_core_hook(constants.TANK_ENGINE_INIT_HOOK_NAME, engine=self)

        # if the engine supports logging metrics, begin dispatching logged metrics
        if self.metrics_dispatch_allowed:
            self._metrics_dispatcher = MetricsDispatcher(self)
            self.log_debug("Starting metrics dispatcher...")
            self._metrics_dispatcher.start()
            self.log_debug("Metrics dispatcher started.")

        self.log_debug("Init complete: %s" % self)

    def __repr__(self):
        return "<Sgtk Engine 0x%08x: %s, env: %s>" % (
            id(self),
            self.name,
            self.__env.name,
        )

    ##########################################################################################
    # properties used by internal classes, not part of the public interface

    def get_env(self):
        """
        Returns the environment object associated with this engine.
        This is a private method which is internal to tank and should
        not be used by external code. This method signature may change at any point
        and the object returned may also change. Do not use outside of the core api.
        """
        return self.__env

    def __toggle_debug_logging(self):
        """
        Toggles global debug logging on and off in the log manager.
        This will affect all logging across all of toolkit.
        """
        # flip debug logging
        LogManager().global_debug = not LogManager().global_debug

    def __open_log_folder(self):
        """
        Opens the file system folder where log files are being stored.
        """
        self.log_info("Log folder is located in '%s'" % LogManager().log_folder)

        if self.has_ui:
            # only import QT if we have a UI
            from .qt import QtGui, QtCore

            url = QtCore.QUrl.fromLocalFile(LogManager().log_folder)
            status = QtGui.QDesktopServices.openUrl(url)
            if not status:
                self._engine.log_error("Failed to open folder!")

    def __is_method_subclassed(self, method_name):
        """
        Helper that determines if the given method name
        has been subclassed in the currently running
        instance of the class or not.

        :param method_name: Name of engine method to check, e.g. 'log_debug'.
        :return: True if subclassed, false if not
        """
        # grab active method and baseclass method
        running_method = getattr(self, method_name)
        base_method = getattr(Engine, method_name)

        # This should be a safe way to test, and is both Python 2 and 3 compatible.
        # the __func__ attribute of callables that was previously used was removed
        # in Python 3.4, and rather than continue to use that only in python 2, we
        # will use the universally available __module__ attribute.
        return running_method.__module__ != base_method.__module__

    def __has_018_logging_support(self):
        """
        Determine if the engine supports the new logging implementation.

        This is done by introspecting the _emit_log_message method.
        If this method is implemented for this engine, it is assumed
        that we are using the new logging system.

        :return: True if new logging is used, False otherwise
        """
        return self.__is_method_subclassed("_emit_log_message")

    def __initialize_logging(self):
        """
        Creates a std python logging LogHandler
        that dispatches all log messages to the
        :meth:`Engine._emit_log_message()` method
        in a thread safe manner.

        For engines that do not yet implement :meth:`_emit_log_message`,
        a legacy log handler is used that dispatches messages
        to the legacy output methods log_xxx.

        :return: :class:`python.logging.LogHandler`
        """
        if self.__has_018_logging_support():
            handler = LogManager().initialize_custom_handler(ToolkitEngineHandler(self))
            # make it easy for engines to implement a consistent log format
            # by equipping the handler with a standard formatter:
            # [DEBUG tk-maya] message message
            #
            # engines subclassing log output can call
            # handler.format to access this formatter for
            # a consistent output implementation
            # (see _emit_log_message for details)
            #
            formatter = logging.Formatter("[%(levelname)s %(basename)s] %(message)s")
            handler.setFormatter(formatter)

        else:
            # legacy engine that doesn't have _emit_log_message implemented
            handler = LogManager().initialize_custom_handler(
                ToolkitEngineLegacyHandler(self)
            )

            # create a minimalistic format suitable for
            # existing output implementations of log_xxx
            #
            formatter = logging.Formatter("%(basename)s: %(message)s")
            handler.setFormatter(formatter)

        return handler

    def __show_busy(self, title, details):
        """
        Payload for the show_busy method.

        For details, see the main show_busy documentation.

        :param title: Short descriptive title of what is happening
        :param details: Detailed message describing what is going on.
        """
        if self.has_ui:
            # we cannot import QT until here as non-ui engines don't have QT defined.
            try:
                from .qt.busy_dialog import BusyDialog
                from .qt import QtGui, QtCore

            except:
                # QT import failed. This may be because someone has upgraded the core
                # to the latest but are still running a earlier version of the
                # Shotgun or Shell engine where the self.has_ui method is not
                # correctly implemented. In that case, absorb the error and
                # emit a log message
                self.log_info("[%s] %s" % (title, details))

            else:
                # our qt import worked!
                if not self.__global_progress_widget:

                    # no window exists - create one!
                    (
                        window,
                        self.__global_progress_widget,
                    ) = self._create_dialog_with_widget(
                        title="Toolkit is busy", bundle=self, widget_class=BusyDialog
                    )

                    # make it a splashscreen that sits on top
                    window.setWindowFlags(
                        QtCore.Qt.SplashScreen | QtCore.Qt.WindowStaysOnTopHint
                    )

                    # set the message before the window is raised to avoid briefly
                    # showing default values
                    self.__global_progress_widget.set_contents(title, details)

                    # if the user closes manually by clicking on the dialog,
                    # make sure we remove the reference to it via the
                    # clear_busy method.
                    window.dialog_closed.connect(self.clear_busy)

                    # kick it off
                    window.show()

                else:

                    # just update the message for the existing window
                    self.__global_progress_widget.set_contents(title, details)

                # make sure events are properly processed and the window is updated
                QtCore.QCoreApplication.processEvents()

        else:
            # no UI support! Instead, just emit a log message
            self.log_info("[%s] %s" % (title, details))

    def __clear_busy(self):
        """
        Payload for clear_busy method.
        For details, see the main clear_busy documentation.
        """
        if self.__global_progress_widget:
            self.__global_progress_widget.close()
            self.__global_progress_widget = None

    def log_user_attribute_metric(self, attr_name, attr_value, log_once=False):
        """
        This method is deprecated and shouldn't be used anymore.
        """
        pass

    def get_metrics_properties(self):
        """
        Returns a dictionary with properties to use when emitting a metric event for
        this engine.

        The dictionary contains information about this engine: its name and version,
        and informations about the application hosting the engine: its name and
        version::

            {
                'Host App': 'Maya',
                'Host App Version': '2017',
                'Engine': 'tk-maya',
                'Engine Version': 'v0.4.1',
            }

        :returns: A dictionary with metrics properties as per above.
        """
        # Always create a new dictionary so the caller can safely modify it.
        return {
            EventMetric.KEY_ENGINE: self.name,
            EventMetric.KEY_ENGINE_VERSION: self.version,
            EventMetric.KEY_HOST_APP: self.host_info.get("name", "unknown"),
            EventMetric.KEY_HOST_APP_VERSION: self.host_info.get("version", "unknown"),
        }

    def get_child_logger(self, name):
        """
        Create a child logger for this engine.

        :param name: Name of child logger, can contain periods for nesting
        :return: :class:`logging.Logger` instance
        """
        full_log_path = "%s.%s" % (self.logger.name, name)
        return logging.getLogger(full_log_path)

    ##########################################################################################
    # properties

    @property
    def shotgun(self):
        """
        Returns a Shotgun API handle associated with the currently running
        environment. This method is a convenience method that calls out
        to :meth:`~sgtk.Tank.shotgun`.

        :returns: Shotgun API handle
        """
        # pass on information to the user agent manager which bundle is returning
        # this sg handle. This information will be passed to the web server logs
        # in the shotgun data centre and makes it easy to track which app and engine versions
        # are being used by clients
        try:
            self.tank.shotgun.tk_user_agent_handler.set_current_engine(
                self.name, self.version
            )
        except AttributeError:
            # looks like this sg instance for some reason does not have a
            # tk user agent handler associated.
            pass

        return self.tank.shotgun

    @property
    def environment(self):
        """
        A dictionary with information about the environment.

        :returns: dictionary with keys ``name``,
                  ``description`` and ``disk_location``.
        """
        data = {}
        data["name"] = self.__env.name
        data["description"] = self.__env.description
        data["disk_location"] = self.__env.disk_location

        return data

    @property
    def instance_name(self):
        """
        The instance name for this engine. The instance name
        is the entry that is defined in the environment file.

        :returns: instance name as string, e.g. ``tk-maya``
        """
        return self.__engine_instance_name

    @property
    def apps(self):
        """
        Dictionary of apps associated with this engine

        :returns: dictionary with keys being app name and values being app objects
        """
        return self.__applications

    @property
    def commands(self):
        """
        A dictionary representing all the commands that have been registered
        by apps in this engine via :meth:`register_command`.
        Each dictionary item contains the following keys:

        - ``callback`` - function pointer to function to execute for this command
        - ``properties`` - dictionary with free form options - these are typically
          engine specific and driven by convention.

        :returns: commands dictionary, keyed by command name
        """
        return self.__commands

    @property
    def panels(self):
        """
        Panels which have been registered with the engine via the :meth:`register_panel()`
        method. Returns a dictionary keyed by panel unique ids. Each value is a dictionary with keys
        ``callback`` and ``properties``.

        Returns all the panels which have been registered with the engine.

        :returns: A dictionary keyed by panel unique ids. Each value is a dictionary
                  with keys 'callback' and 'properties'
        """
        return self.__panels

    @property
    def has_ui(self):
        """
        Indicates that the host application that the engine is connected to has a UI enabled.
        This always returns False for some engines (such as the shell engine) and may vary
        for some engines, depending if the host application for example is in batch mode or
        UI mode.

        :returns: boolean value indicating if a UI currently exists
        """
        # default implementation is to assume a UI exists
        # this is since most engines are supporting a graphical application
        return True

    @property
    def has_qt5(self):
        """
        Indicates that the host application has access to Qt 5 and that the ``sgtk.platform.qt5``  module
        has been populated with the Qt 5 modules and information.

        :returns bool: boolean value indicating if Qt 5 is available.
        """
        return self.__has_qt5

    @property
    def has_qt6(self):
        """
        Indicates that the host application has access to Qt 6 and that the ``sgtk.platform.qt6`` module
        has been populated with the Qt 6 modules and information.

        :returns bool: boolean value indicating if Qt 6 is available.
        """
        return self.__has_qt6

    @property
    def metrics_dispatch_allowed(self):
        """
        Indicates this engine will allow the metrics worker threads to forward
        the user metrics logged via core, this engine, or registered apps to
        PTR.

        :returns: boolean value indicating that the engine allows user metrics
            to be forwarded to PTR.
        """
        return True

    @property
    def created_qt_dialogs(self):
        """
        A list of dialog objects that have been created by the engine.

        :returns:   A list of TankQDialog objects.
        """
        return self.__created_qt_dialogs

    @property
    def host_info(self):
        """
        Returns information about the application hosting this engine.

        This should be re-implemented in deriving classes to handle the logic
        specific to the application the engine is designed for.

        A dictionary with at least a "name" and a "version" key should be returned
        by derived implementations, with respectively the host application name
        and its release string as values, e.g. ``{ "name": "Maya", "version": "2017.3"}``.

        :returns: A ``{"name": "unknown", "version" : "unknown"}`` dictionary.
        """
        return {"name": "unknown", "version": "unknown"}

    @property
    def register_toggle_debug_command(self):
        """
        Indicates whether the engine should have a toggle debug logging
        command registered during engine initialization.

        :rtype: bool
        """
        return True

    ##########################################################################################
    # init and destroy

    def init_engine(self):
        """
        Note: Now deprecated - Please use pre_app_init instead.
        """
        pass

    def pre_app_init(self):
        """
        Sets up the engine into an operational state. Executed by the system and typically
        implemented by deriving classes. This method called before any apps are loaded.
        """
        pass

    def post_app_init(self):
        """
        Executed by the system and typically implemented by deriving classes.
        This method called after all apps have been loaded.
        """
        pass

    def destroy(self):
        """
        Destroy all apps, then call destroy_engine so subclasses can add their own tear down code.

        .. note:: This method should not be subclassed. Instead, implement :meth:`destroy_engine()`.

        """
        with _CoreContextChangeHookGuard(self.sgtk, self.context, None):
            self.__destroy_frameworks()
            self.__destroy_apps()

            self.log_debug("Destroying %s" % self)
            self.destroy_engine()

            # finally remove the current engine reference
            set_current_engine(None)

            # now clear the hooks cache to make sure fresh hooks are loaded the
            # next time an engine is initialized
            hook.clear_hooks_cache()

            # clean up the main thread invoker - it's a QObject so it's important we
            # explicitly set the value to None!
            self._invoker = None
            self._async_invoker = None

            # halt metrics dispatching
            if self._metrics_dispatcher and self._metrics_dispatcher.dispatching:
                self.log_debug("Stopping metrics dispatcher.")
                self._metrics_dispatcher.stop()
                self.log_debug("Metrics dispatcher stopped.")

        # kill log handler
        LogManager().root_logger.removeHandler(self.__log_handler)
        self.__log_handler = None

    def destroy_engine(self):
        """
        Called when the engine should tear down itself and all its apps.
        Implemented by deriving classes.
        """
        pass

    def change_context(self, new_context):
        """
        Called when the engine is being asked to change contexts. This
        will only be allowed if the engine explicitly suppose on-the-fly
        context changes by way of its context_change_allowed property. Any
        apps that do not support context changing will be restarted instead.
        Custom behavior at the engine level should be handled by overriding
        one or both of pre_context_change and post_context_change methods.

        :param new_context:     The context to change to.
        :type new_context: :class:`~sgtk.Context`
        """
        # Make sure we're allowed to change context at the engine level.
        if not self.context_change_allowed:
            self.log_debug("Engine %r does not allow context changes." % self)
            raise TankContextChangeNotSupportedError()

        # Make sure that this engine is configured to run in the new context,
        # and that it's the EXACT same engine. This can be handled by comparing
        # the current engine's descriptor to the one coming from the new environment.
        # If this fails then it's more than just the engine not supporting the
        # context change, it's that the target context isn't configured properly.
        # As such, we'll let any exceptions (mostly TankEngineInitError) bubble
        # up since it's a critical error case.
        (new_env, engine_descriptor) = get_env_and_descriptor_for_engine(
            engine_name=self.instance_name, tk=self.tank, context=new_context
        )

        # Make sure that the engine in the target context is the same as the current
        # engine. In the case of git or app_store descriptors, the equality check
        # is an "is" check to see if they're references to the same object due to the
        # fact that those descriptor types are singletons. For dev descriptors, the
        # check is going to compare the paths of the descriptors to see if they're
        # referencing the same data on disk, in which case they are equivalent.
        if engine_descriptor != self.descriptor:
            self.log_debug(
                "Engine %r does not match descriptors between %r and %r."
                % (self, self.context, new_context)
            )
            raise TankContextChangeNotSupportedError()

        # Run the pre_context_change method to allow for any engine-specific
        # prep work to happen.
        self.log_debug(
            "Executing pre_context_change for %r, changing from %r to %r."
            % (self, self.context, new_context)
        )

        with _CoreContextChangeHookGuard(self.sgtk, self.context, new_context):
            self.pre_context_change(self.context, new_context)
            self.log_debug(
                "Execution of pre_context_change for engine %r is complete." % self
            )

            # Check to see if all of our apps are capable of accepting
            # a context change. If one of them is not, then we remove it
            # from the persistent app pool, which will force it to be
            # rebuilt when apps are loaded later on.
            non_compliant_app_paths = []
            for install_path, app_instances in self.__application_pool.items():
                for instance_name, app in app_instances.items():
                    self.log_debug(
                        "Executing pre_context_change for %r, changing from %r to %r."
                        % (app, self.context, new_context)
                    )
                    app.pre_context_change(self.context, new_context)
                    self.log_debug(
                        "Execution of pre_context_change for app %r is complete." % app
                    )

            # Now that we're certain we can perform a context change,
            # we can tell the environment what the new context is, update
            # our own context property, and load the apps. The app load
            # will repopulate the __applications dict to contain the appropriate
            # apps for the new context, and will pull apps that have already
            # been loaded from the __application_pool, which is persistent.
            old_context = self.context
            new_engine_settings = new_env.get_engine_settings(
                self.__engine_instance_name
            )
            self.__env = new_env
            self._set_context(new_context)
            self._set_settings(new_engine_settings)
            self.__load_apps(reuse_existing_apps=True, old_context=old_context)

            # Call the post_context_change method to allow for any engine
            # specific post-change logic to be run.
            self.log_debug(
                "Executing post_context_change for %r, changing from %r to %r."
                % (self, self.context, new_context)
            )

            # Emit the core level event.
            self.post_context_change(old_context, new_context)

        self.log_debug(
            "Execution of post_context_change for engine %r is complete." % self
        )

        # Last, now that we're otherwise done, we can run the
        # apps' post_engine_init methods.
        self.__run_post_engine_inits()

    ##########################################################################################
    # public methods

    def show_busy(self, title, details):
        """
        Displays or updates a global "busy window" tied to this engine. The window
        is a splash screen type window, floats on top and contains details of what
        is currently being processed.

        This method pops up a splash screen with a message and the idea is that
        long running core processes can use this as a way to communicate their intent
        to the user and keep the user informed as slow processes are executed. If the engine
        has a UI present, this will be used to display the progress message. If the engine
        does not have UI support, a message will be logged. The UI always appears in the
        main thread for safety.

        Only one global progress window can exist per engine at a time, so if you want to
        push several updates one after the other, just keep calling this method.

        When you want to remove the window, call :meth:`clear_busy()`.

        Note! If you are calling this from the Core API you typically don't have
        access to the current engine object. In this case you can use the
        convenience method ``tank.platform.engine.show_global_busy()`` which will
        attempt to broadcast the request to the currently active engine.

        :params title: Short descriptive title of what is happening
        :params details: Detailed message describing what is going on.
        """
        # make sure that the UI is always shown in the main thread
        self.execute_in_main_thread(self.__show_busy, title, details)

    def clear_busy(self):
        """
        Closes any active busy window.

        For more details, see the :meth:`show_busy()` documentation.
        """
        if self.__global_progress_widget:
            self.execute_in_main_thread(self.__clear_busy)

    def register_command(self, name, callback, properties=None):
        """
        Register a ``command`` with a name and a callback function.

        A *command* refers to an access point for some functionality.
        In most cases, commands will appear as items on a Shotgun dropdown
        menu, but it ultimately depends on the engine - in the Shell engine,
        commands are instead represented as a text base listing and in the
        PTR desktop app it is a scrollable list of larger icons.

        .. note:: This method is used to add menu entries for launching
           toolkit UIs. If you wish to register a panel UI with toolkit,
           you need call this method in order to register a menu command
           with which a user can launch the panel. In addition to this,
           you also need to call :meth:`register_panel` in order to
           register the panel so that the engine can handle its
           management and persistence.

        An arbitrary list of properties can be passed into the engine
        in the form of a properties dictionary. The interpretation of
        the properties dictionary is engine specific, but in general
        the following properties are supported:

        - ``short_name`` - A shorter name, typically intended for console use (e.g. 'import_cut')

        - ``icon`` - A path to a 256x256 png app icon. If not specified, the icon for the app will be used.

        - ``description`` - a one line description of the command, suitable for a tooltip.
          If no description is passed, the one provided in the app manifest will be used.

        - ``title`` - Title to appear on shotgun action menu (e.g. "Create Folders")

        - ``type`` - The type of command - hinting at which menu the command should appear.
          Options vary between engines and the following are supported:

            - ``context_menu`` - Supported on all engines. Places an item on
              the context menu (first item on the shotgun menu). The context menu is a
              suitable location for utility items, helpers and tools.

            - ``panel`` - Some DCCs have a special menu which is accessible only when
              right clicking on a panel. Passing ``panel`` as the command type hints
              to the system that the command should be added to this menu. If no panel
              menu is available, it will be added to the main menu. Nuke is an example
              of a DCC which supports this behavior.

            - ``node`` - Node based applications such as Nuke typically have a separate
              menu system for accessing nodes. If you want your registered command to appear
              on this menu, use this type.


        **Grouping commands into collections**

        It is possible to group several commands into a collection. Such a collection is called
        a *group*.  For example, you may have three separate commands to launch Maya 2017,
        Maya 2016 and Maya 2015, all under a 'Launch Maya' group. It is up to each engine to
        implement this specification in a suitable way but typically, it would be displayed as a
        "Launch Maya" menu with three sub menu items to represent each version of Maya.

        Each group has a concept of a group default - this is what would get executed if you click
        on the 'Launch Maya' group.

        To register commands with groups, pass the following two parameters in the properties
        dictionary:

        - ``group`` - The name for a group this command should be considered a member of.

        - ``group_default`` - Boolean value indicating whether this command should represent the
          group as a whole.

        .. note:: It is up to each engine to implement grouping and group defaults in an
                  appropriate way. Some engines may not support grouping.


        The following properties are supported for the Shotgun engine specifically:

        - ``deny_permissions`` - List of permission groups to exclude this
          menu item for (e.g. ``["Artist"]``)

        - ``deny_platforms`` - List of platforms for which not to show the menu
          (e.g. ``["windows", "mac", "linux"]``). Please note that there are
          other ways to achieve this same result.

        - ``supports_multiple_selection`` - a special flag that allows multiple objects
          in Shotgun to be selected and operated on. An example showing how to write a
          multi select shotgun app is provided in a special branch in the sample starter
          app: https://github.com/shotgunsoftware/tk-multi-starterapp/tree/shotgun_multi_select

        - Please note that custom icons are not supported by the Shotgun engine.

        Typical usage normally looks something like this -
        register_command is called from the :meth:`Application.init_app()` method of an app::

            self.engine.register_command(
                "Work Area Info...",
                callback,
                {"type": "context_menu", "short_name": "work_area_info"}
            )

        :param name: Name of the command. This will be the key when accessed via the
                     :meth:`commands` dictionary.
        :param callback: Callback to call upon command execution
        :param properties: Dictionary with command properties.
        """
        if properties is None:
            properties = {}

        # uniqueness prefix, populated when there are several instances of the same app
        properties["prefix"] = None

        # try to add an app key to the dict with the app requesting the command
        if self.__currently_initializing_app is not None:
            # track which apps this request came from
            properties["app"] = self.__currently_initializing_app

        # add some defaults. If there isn't a description key, add it from the app's manifest
        if "description" not in properties and self.__currently_initializing_app:
            properties["description"] = self.__currently_initializing_app.description

        if "icon" not in properties and self.__currently_initializing_app:
            properties["icon"] = self.__currently_initializing_app.descriptor.icon_256

        if name in self.__commands:
            # Duplicate command name detected! Attempt to make commands unique by prepending the
            # a prefix derived from information in the properties.
            existing_item = self.__commands[name]
            command_prefix = _get_command_prefix(existing_item["properties"])
            if command_prefix:
                new_name_for_existing = "%s:%s" % (command_prefix, name)
                self.__commands[new_name_for_existing] = existing_item
                # Record the command prefix in the properties dictionary for future reference.
                self.__commands[new_name_for_existing]["properties"][
                    "prefix"
                ] = command_prefix
                del self.__commands[name]
                # Record the original command name to make sure any additional commands
                # registered with this name are treated as duplicates and fully prefixed.
                self.__commands_that_need_prefixing.append(name)

        if name in self.__commands_that_need_prefixing:
            # At least one instance of this command name has already been detected.
            # Resolve the duplicate command by application name and/or group name.
            command_prefix = _get_command_prefix(properties)
            if command_prefix:
                name = "%s:%s" % (command_prefix, name)
                # Record the command prefix in the properties dictionary for future reference.
                properties["prefix"] = command_prefix

        # now define command wrappers to capture metrics logging
        # on command execution. The toolkit callback system supports
        # two different callback styles:
        #
        # - A legacy type which is only used by Shotgun Apps which
        #   utilize multi select. These callbacks are always on the
        #   form callback(entity_type, entity_ids)
        #
        # - The standard type, which does not pass any arguments:
        #   callback()
        #

        # introspect the arg list to determine this and set a flag
        # to highlight this state. This is used by the tank_command
        # execution logic to correctly dispatch the callback during
        # runtime.
        # getargspec has been deprecated in Python 3 and generates a copious
        # amount of warnings, so use getfullargspec which is backwards
        # compatible in Python 3. Unfortunately, it doesn't exist in Python
        # 2 and six doesn't offer a wrapper for it.
        if six.PY2:
            arg_spec = inspect.getargspec(callback)
        else:
            arg_spec = inspect.getfullargspec(callback)
        # note - cannot use named tuple form because it is py2.6+
        arg_list = arg_spec[0]

        if "entity_type" in arg_list and "entity_ids" in arg_list:
            # add property flag
            properties[constants.LEGACY_MULTI_SELECT_ACTION_FLAG] = True

        # define a generic callback wrapper for metrics logging
        def callback_wrapper(*args, **kwargs):

            if properties.get("app"):
                # Track which app command is being launched
                command_name = properties.get("short_name") or name
                properties["app"].log_metric(
                    "Launched Command", command_name=command_name
                )

            # run the actual payload callback
            return callback(*args, **kwargs)

        self.log_debug(
            "Registering command '%s' with options:\n%s"
            % (name, pprint.pformat(properties))
        )

        self.__commands[name] = {"callback": callback_wrapper, "properties": properties}

    def register_panel(self, callback, panel_name="main", properties=None):
        """
        Similar to :meth:`register_command()`, but instead of registering a menu item in the form of a
        command, this method registers a UI panel. A register_panel call should
        be used in conjunction with a register_command call.

        Panels need to be registered if they should persist between DCC sessions (e.g.
        for example 'saved layouts').

        Just like with the :meth:`register_command` method, panel registration should be executed
        from within the init phase of the app. Once a panel has been registered, it is possible
        for the engine to correctly restore panel UIs at startup and profile switches.

        Not all engines support this feature, but in for example Nuke, a panel can be added to
        a saved layout. Apps wanting to be able to take advantage of the persistence given by
        these saved layouts will need to call register_panel as part of their init_app phase.

        In order to show or focus on a panel, use the :meth:`show_panel` method instead.

        :param callback: Callback to a factory method that creates the panel and returns a panel widget.
        :param panel_name: A string to distinguish this panel from other panels created by
                           the app. This will be used as part of the unique id for the panel.
        :param properties: Properties dictionary. Reserved for future use.
        :returns: A unique identifier that can be used to consistently identify the
                  panel across sessions. This identifier should be used to identify the panel
                  in all subsequent calls, e.g. for example :meth:`show_panel()`.
        """
        properties = properties or {}

        if self.__currently_initializing_app is None:
            # register_panel is called from outside of init_app
            raise TankError(
                "register_panel must be called from inside of the init_app() method!"
            )

        current_app = self.__currently_initializing_app

        # similar to register_command, track which app this request came from
        properties["app"] = current_app

        # now compose a unique id for this panel.
        # This is done based on the app instance name plus the given panel name.
        # By using the instance name rather than the app name, we support the
        # use case where more than one instance of an app exists within a
        # config.
        panel_id = "%s_%s" % (current_app.instance_name, panel_name)
        # to ensure the string is safe to use in most engines,
        # sanitize to simple alpha-numeric form
        panel_id = re.sub(r"\W", "_", panel_id)
        panel_id = panel_id.lower()

        # add it to the list of registered panels
        self.__panels[panel_id] = {"callback": callback, "properties": properties}

        self.log_debug("Registered panel %s" % panel_id)

        return panel_id

    def execute_in_main_thread(self, func, *args, **kwargs):
        """
        Execute the specified function in the main thread when called from a non-main
        thread.  This will block the calling thread until the function returns. Note that this
        method can introduce a deadlock if the main thread is waiting for a background thread
        and the background thread is invoking this method. Since the main thread is waiting
        for the background thread to finish, Qt's event loop won't be able to process the request
        to execute in the main thread::

            >>> from sgtk.platform.qt import QtGui
            >>> engine.execute_in_main_thread(QtGui.QMessageBox.information, None, "Hello", "Hello from the main thread!")

        .. note:: This currently only works if Qt is available, otherwise it just
                  executes immediately on the current thread.

        :param func: function to call
        :param args: arguments to pass to the function
        :param kwargs: named arguments to pass to the function

        :returns: the result of the function call
        """
        return self._execute_in_main_thread(self._SYNC_INVOKER, func, *args, **kwargs)

    def async_execute_in_main_thread(self, func, *args, **kwargs):
        """
        Execute the specified function in the main thread when called from a non-main
        thread.  This call will return immediately and will not wait for the code to be
        executed in the main thread.

        .. note:: This currently only works if Qt is available, otherwise it just
                  executes immediately on the current thread.

        :param func: function to call
        :param args: arguments to pass to the function
        :param kwargs: named arguments to pass to the function
        """
        self._execute_in_main_thread(self._ASYNC_INVOKER, func, *args, **kwargs)

    def _execute_in_main_thread(self, invoker_id, func, *args, **kwargs):
        """
        Executes the given method and arguments with the specified invoker.
        If the invoker is not ready or if the calling thread is the main thread,
        the method is called immediately with it's arguments.

        :param invoker_id: Either _ASYNC_INVOKER or _SYNC_INVOKER.
        :param func: function to call
        :param args: arguments to pass to the function
        :param kwargs: named arguments to pass to the function

        :returns: The return value from the invoker.
        """
        # Execute in main thread might be called before the invoker is ready.
        # For example, an engine might use the invoker for logging to the main
        # thread.
        invoker = (
            self._invoker if invoker_id == self._SYNC_INVOKER else self._async_invoker
        )
        if invoker:
            from .qt import QtGui, QtCore

            if (
                QtGui.QApplication.instance()
                and QtCore.QThread.currentThread()
                != QtGui.QApplication.instance().thread()
            ):
                # invoke the function on the thread that the QtGui.QApplication was created on.
                return invoker.invoke(func, *args, **kwargs)
            else:
                # we're already on the main thread so lets just call our function:
                return func(*args, **kwargs)
        else:
            # we don't have an invoker so just call the function:
            return func(*args, **kwargs)

    def get_matching_commands(self, command_selectors):
        """
        Finds all the commands that match the given selectors.

        Command selector structures are typically found in engine configurations
        and are typically defined on the following form in yaml::

            menu_favourites:
            - {app_instance: tk-multi-workfiles, name: Shotgun File Manager...}
            - {app_instance: tk-multi-snapshot,  name: Snapshot...}
            - {app_instance: tk-multi-workfiles, name: Shotgun Save As...}
            - {app_instance: tk-multi-publish,   name: Publish...}

        Note that selectors that do not match a command will output a warning.

        :param command_selectors: A list of command selectors, with each
                                  selector having the following structure::

                                      {
                                        name: command-name,
                                        app_instance: instance-name
                                      }

                                  An empty name ("") will select all the
                                  commands of the given instance-name.

        :returns:                 A list of tuples for all commands that match
                                  the selectors. Each tuple has the format::

                                      (instance-name, command-name, callback)
        """
        # return a dictionary grouping all the commands by instance name
        commands_by_instance = {}
        for (name, value) in self.commands.items():
            app_instance = value["properties"].get("app")
            if app_instance is None:
                continue
            instance_name = app_instance.instance_name
            commands_by_instance.setdefault(instance_name, []).append(
                (name, value["callback"])
            )

        # go through the selectors and return any matching commands
        ret_value = []
        for selector in command_selectors:
            command_name = selector["name"]
            instance_name = selector["app_instance"]
            instance_commands = commands_by_instance.get(instance_name, [])

            # add the commands if the name of the settings is ''
            # or the name matches
            matching_commands = [
                (instance_name, name, callback)
                for (name, callback) in instance_commands
                if not command_name or (command_name == name)
            ]
            ret_value.extend(matching_commands)

            # give feedback if no commands were found
            if not matching_commands:
                self._engine.log_warning(
                    "The requested command '%s' from app instance '%s' could "
                    "not be matched.\nPlease make sure that you have the app "
                    "installed and that it has successfully initialized."
                    % (command_name, instance_name)
                )

        return ret_value

    ##########################################################################################
    # logging interfaces

    def log_debug(self, msg):
        """
        Logs a debug message.

        .. deprecated:: 0.18
            Use :meth:`Engine.logger` instead.

        .. note:: Toolkit will probe for this method and use it to determine if
                  the current engine supports the new :meth:`Engine.logger` based logging
                  or not. If you are developing an engine and want to upgrade it to
                  use the new logging capabilities, you should remove the
                  implementation of ``log_debug|error|info|...()`` methods and
                  instead sublcass :meth:`Engine._emit_log_message`.

        :param msg: Message to log.
        """
        if not self.__has_018_logging_support() and self.__log_handler.inside_dispatch:
            # special case: We are in legacy mode and all log messages are
            # dispatched to the log_xxx methods because this engine does not have an
            # _emit_log_message implementation. This is fine because typically old
            # engine implementations subclass the log_xxx class, meaning that this call
            # is never run, but instead the subclassed code in run. If however, this
            # could *would* run in that case for whatever reason (either it wasn't
            # subclassed or the subclassed code calls the baseclass), we need to be
            # careful not to end up in an infinite loop. Therefore, the log handler
            # sets a flag to indicate that this code is being called from the logger
            # and not from somewhere else. In that case we just exit early to avoid
            # the infinite recursion
            return
        self.logger.debug(msg)

    def log_info(self, msg):
        """
        Logs an info message.

        .. deprecated:: 0.18
            Use :meth:`Engine.logger` instead.

        :param msg: Message to log.
        """
        if not self.__has_018_logging_support() and self.__log_handler.inside_dispatch:
            # special case: We are in legacy mode and all log messages are
            # dispatched to the log_xxx methods because this engine does not have an
            # _emit_log_message implementation. This is fine because typically old
            # engine implementations subclass the log_xxx class, meaning that this call
            # is never run, but instead the subclassed code in run. If however, this
            # could *would* run in that case for whatever reason (either it wasn't
            # subclassed or the subclassed code calls the baseclass), we need to be
            # careful not to end up in an infinite loop. Therefore, the log handler
            # sets a flag to indicate that this code is being called from the logger
            # and not from somewhere else. In that case we just exit early to avoid
            # the infinite recursion
            return
        self.logger.info(msg)

    def log_warning(self, msg):
        """
        Logs an warning message.

        .. deprecated:: 0.18
            Use :meth:`Engine.logger` instead.

        :param msg: Message to log.
        """
        if not self.__has_018_logging_support() and self.__log_handler.inside_dispatch:
            # special case: We are in legacy mode and all log messages are
            # dispatched to the log_xxx methods because this engine does not have an
            # _emit_log_message implementation. This is fine because typically old
            # engine implementations subclass the log_xxx class, meaning that this call
            # is never run, but instead the subclassed code in run. If however, this
            # could *would* run in that case for whatever reason (either it wasn't
            # subclassed or the subclassed code calls the baseclass), we need to be
            # careful not to end up in an infinite loop. Therefore, the log handler
            # sets a flag to indicate that this code is being called from the logger
            # and not from somewhere else. In that case we just exit early to avoid
            # the infinite recursion
            return
        self.logger.warning(msg)

    def log_error(self, msg):
        """
        Logs an error message.

        .. deprecated:: 0.18
            Use :meth:`Engine.logger` instead.

        :param msg: Message to log.
        """
        if not self.__has_018_logging_support() and self.__log_handler.inside_dispatch:
            # special case: We are in legacy mode and all log messages are
            # dispatched to the log_xxx methods because this engine does not have an
            # _emit_log_message implementation. This is fine because typically old
            # engine implementations subclass the log_xxx class, meaning that this call
            # is never run, but instead the subclassed code in run. If however, this
            # could *would* run in that case for whatever reason (either it wasn't
            # subclassed or the subclassed code calls the baseclass), we need to be
            # careful not to end up in an infinite loop. Therefore, the log handler
            # sets a flag to indicate that this code is being called from the logger
            # and not from somewhere else. In that case we just exit early to avoid
            # the infinite recursion
            return
        self.logger.error(msg)

    def log_exception(self, msg):
        """
        Logs an exception message.

        .. deprecated:: 0.18
            Use :meth:`Engine.logger` instead.

        :param msg: Message to log.
        """
        if not self.__has_018_logging_support() and self.__log_handler.inside_dispatch:
            # special case: We are in legacy mode and all log messages are
            # dispatched to the log_xxx methods because this engine does not have an
            # _emit_log_message implementation. This is fine because typically old
            # engine implementations subclass the log_xxx class, meaning that this call
            # is never run, but instead the subclassed code in run. If however, this
            # could *would* run in that case for whatever reason (either it wasn't
            # subclassed or the subclassed code calls the baseclass), we need to be
            # careful not to end up in an infinite loop. Therefore, the log handler
            # sets a flag to indicate that this code is being called from the logger
            # and not from somewhere else. In that case we just exit early to avoid
            # the infinite recursion
            return
        self.logger.exception(msg)

    ##########################################################################################
    # debug for tracking Qt Widgets & Dialogs created by the provided methods

    def get_debug_tracked_qt_widgets(self):
        """
        Returns a dictionary of debug info about created Qt dialogs and widgets.

        The keys of the dictionary are the string representation of a widget and the
        corresponding value is a reference to that widget.
        """
        return self.__qt_debug_info

    def __debug_track_qt_widget(self, widget):
        """
        Add the qt widget to a list of objects to be tracked.
        """
        if widget:
            self.__qt_debug_info[widget.__repr__()] = weakref.ref(widget)

    ##########################################################################################
    # private and protected methods

    def _emit_event(self, event):
        """
        Called by the engine whenever an event is to be emitted to child
        apps of this engine.

        .. note:: Events will be emitted and child apps notified immediately.

        .. warning:: Some event types might be triggered quite frequently. Apps
                     that react to events should do so in a way that is aware of
                     the potential performance impact of their actions.

        :param event: The event object that will be emitted.
        :type event:  :class:`~sgtk.platform.events.EngineEvent`
        """
        if not isinstance(event, events.EngineEvent):
            raise TankEngineEventError(
                "Given object does not derive from EngineEvent: %r" % event
            )

        self.log_debug("Emitting event: %r" % event)

        for app_instance_name, app in self.__applications.items():
            self.log_debug("Sending event to %r..." % app)

            # We send the event to the generic engine event handler
            # as well as to the type-specific handler when we have
            # one. This mirror's Qt's event system's structure.
            app.event_engine(event)

            if isinstance(event, events.FileOpenEvent):
                app.event_file_open(event)
            elif isinstance(event, events.FileCloseEvent):
                app.event_file_close(event)

    def _emit_log_message(self, handler, record):
        """
        Called by the engine whenever a new log message is available.
        All log messages from the toolkit logging namespace will be passed to this method.

        .. note:: To implement logging in your engine implementation, subclass
                  this method and display the record in a suitable way - typically
                  this means sending it to a built-in DCC console. In addition to this,
                  ensure that your engine implementation *does not* subclass
                  the (old) :meth:`Engine.log_debug`, :meth:`Engine.log_info` family
                  of logging methods.

                  For a consistent output, use the formatter that is associated with
                  the log handler that is passed in. A basic implementation of
                  this method could look like this::

                      # call out to handler to format message in a standard way
                      msg_str = handler.format(record)

                      # display message
                      print msg_str

        .. warning:: This method may be executing called from worker threads. In DCC
                     environments, where it is important that the console/logging output
                     always happens in the main thread, it is recommended that you
                     use the :meth:`async_execute_in_main_thread` to ensure that your
                     logging code is writing to the DCC console in the main thread.

        :param handler: Log handler that this message was dispatched from
        :type handler: :class:`~python.logging.LogHandler`
        :param record: Std python logging record
        :type record: :class:`~python.logging.LogRecord`
        """
        # default implementation doesn't do anything.

    def _ensure_core_fonts_loaded(self):
        """
        Loads the Shotgun approved fonts that are bundled with tk-core.

        This method ensures that the Shotgun approved fonts bundled with core
        are loaded into Qt's font database. This allows them to be used by apps
        for a consistent look and feel.

        If a QApplication exists during engine initialization, it is not
        necessary to call this method. Similarly, subclasses that make use of
        core's bundled dark look and feel will have the bundled fonts loaded
        automatically.

        This method can/should be called by subclasses that meet the following
        criteria:

         * Create their own ``QApplication`` instance after engine init
         * Do not use the bundled dark look and feel.
         * Have overridden ``Engine._create_dialog()``.

        """

        # Note, the fonts are packed within core's resource directory with a
        # parent directory that is the name of the font. The directory contains
        # all the bundled font files. Example:
        #
        #       ``tank/platform/qt/fonts/OpenSans/OpenSans-*.ttf``

        if not self.has_ui:
            return

        from sgtk.platform.qt import QtGui

        # if the fonts have been loaded, no need to do anything else
        if self.__fonts_loaded:
            return

        if not QtGui:
            # it is possible that QtGui is not available (test suite).
            return

        if not QtGui.QApplication.instance():
            # there is a QApplication, so we can load fonts.
            return

        # fonts dir in the core resources dir
        fonts_parent_dir = self.__get_platform_resource_path("fonts")

        # in the parent directly, get all the font-specific directories
        for font_dir_name in os.listdir(fonts_parent_dir):

            # the specific font directory
            font_dir = os.path.join(fonts_parent_dir, font_dir_name)

            if os.path.isdir(font_dir):

                # iterate over the font files and attempt to load them
                #
                # NOTE: We're loading the ttf files in reverse order to work around
                # a Windows 10 oddity in Qt5/PySide2. It appears as though Windows
                # prefers the first ttf installed for a given font weight, so when
                # we're setting weight in qss (publish2 is a good example), if we're
                # going for a lighter-weight font, we end up getting condensed light
                # instead of the regular style. So...we're going to install these in
                # reverse order so that the regular light style is preferred.
                for font_file_name in reversed(list(os.listdir(font_dir))):

                    # only process actual font files. It appears as though .ttf
                    # is the most common extension for use on win/mac/linux so
                    # for now limit to those files.
                    if not font_file_name.endswith(".ttf"):
                        continue

                    # the actual font file
                    font_file = os.path.join(font_dir, font_file_name)

                    # rather than registering the file path with the QT
                    # font system, first load the font data into memory
                    # and then register that data.
                    #
                    # this is to avoid QT keeping an open file handle to
                    # the font files - this causes issues on windows and
                    # results in bootstrap changes sometimes not being
                    # picked up.
                    with open(font_file, "rb") as fh:
                        # load binary data into memory
                        font_data = fh.read()
                        # load the font into the font db
                        if (
                            QtGui.QFontDatabase.addApplicationFontFromData(font_data)
                            == -1
                        ):
                            self.log_warning(
                                "Unable to load font file: %s" % (font_file,)
                            )
                        else:
                            self.log_debug(
                                "Loaded font file into memory: %s" % (font_file,)
                            )

        self.__fonts_loaded = True

    def _get_dialog_parent(self):
        """
        Get the QWidget parent for all dialogs created through :meth:`show_dialog` :meth:`show_modal`.

        Can be overriden in derived classes to return the QWidget to be used as the parent
        for all TankQDialog's.

        :return: QT Parent window (:class:`PySide.QtGui.QWidget`)
        """
        # By default, this will return the QApplication's active window:
        from .qt import QtGui

        return QtGui.QApplication.activeWindow()

    def _create_dialog(self, title, bundle, widget, parent):
        """
        Create a TankQDialog with the specified widget embedded. This also connects to the
        dialogs dialog_closed event so that it can clean up when the dialog is closed.

        .. note:: For more information, see the documentation for :meth:`show_dialog()`.

        :param title: The title of the window
        :param bundle: The app, engine or framework object that is associated with this window
        :param widget: A QWidget instance to be embedded in the newly created dialog.
        :type widget: :class:`PySide.QtGui.QWidget`
        """
        from .qt import tankqdialog

        # TankQDialog uses the bundled core font. Make sure they are loaded
        # since know we have a QApplication at this point.
        self._ensure_core_fonts_loaded()

        # create a dialog to put it inside
        dialog = tankqdialog.TankQDialog(title, bundle, widget, parent)

        # keep a reference to all created dialogs to make GC happy
        self.__created_qt_dialogs.append(dialog)

        # watch for the dialog closing so that we can clean up
        dialog.dialog_closed.connect(self._on_dialog_closed)

        # keep track of some info for debugging object lifetime
        self.__debug_track_qt_widget(dialog)

        return dialog

    def _create_widget(self, widget_class, *args, **kwargs):
        """
        Create an instance of the specified widget_class.  This wraps the widget_class so that
        the TankQDialog it is embedded in can connect to it more easily in order to handle the
        close event.

        When overriding in a derived engine, be sure to call the base implementations of
        :meth:`_create_widget()` and :meth:`_create_dialog()` to ensure that all
        dialogs and widgets are tracked efficiently and safely.

        .. note:: For more information, see the documentation for :meth:`show_dialog()`.

        :param widget_class: The class of the UI to be constructed. This must derive from QWidget.
        :type widget_class: :class:`PySide.QtGui.QWidget`

        Additional parameters specified will be passed through to the widget_class constructor.
        """
        from .qt import tankqdialog

        # construct the widget object
        try:
            derived_widget_class = tankqdialog.TankQDialog.wrap_widget_class(
                widget_class
            )
            widget = derived_widget_class(*args, **kwargs)
        except Exception as exc:
            # We don't want exceptions from the instantiation of the widget to bubble
            # up since we don't know how the Python environment we're running in might
            # react.
            self.logger.exception(exc)

            import traceback
            from sgtk.platform.qt import QtGui, QtCore

            # A very simple widget that ensures that the exception is visible and
            # selectable should the user need to copy/paste it into a support
            # ticket.
            class _exc_widget(QtGui.QWidget):
                def __init__(self, msg, *args, **kwargs):
                    super(_exc_widget, self).__init__(*args, **kwargs)

                    self.setObjectName("SGTK_CORE_EXC_WIDGET")

                    self._label = QtGui.QLabel(
                        "<big>The requested dialog could not be built "
                        "due to an exception that was raised:</big>"
                    )
                    self._label.setTextFormat(QtCore.Qt.RichText)
                    self._text = QtGui.QTextEdit()
                    self._text.setReadOnly(True)
                    self._text.setLineWrapMode(QtGui.QTextEdit.NoWrap)
                    self._text.setText(msg)

                    self._layout = QtGui.QVBoxLayout(self)
                    self._layout.addWidget(self._label)
                    self._layout.addWidget(self._text)

            derived_widget_class = tankqdialog.TankQDialog.wrap_widget_class(
                _exc_widget
            )
            widget = derived_widget_class(traceback.format_exc())

        # keep track of some info for debugging object lifetime
        self.__debug_track_qt_widget(widget)

        return widget

    def _create_dialog_with_widget(self, title, bundle, widget_class, *args, **kwargs):
        """
        Convenience method to create an sgtk TankQDialog with a widget instantiated from
        widget_class embedded in the main section.

        .. note:: For more information, see the documentation for :meth:`show_dialog()`.

        :param title: The title of the window
        :param bundle: The app, engine or framework object that is associated with this window
        :param widget_class: The class of the UI to be constructed. This must derive from QWidget.
        :type widget_class: :class:`PySide.QtGui.QWidget`

        Additional parameters specified will be passed through to the widget_class constructor.
        """

        # get the parent for the dialog:
        parent = self._get_dialog_parent()

        # create the widget:
        widget = self._create_widget(widget_class, *args, **kwargs)

        # apply style sheet
        self._apply_external_stylesheet(bundle, widget)

        # create the dialog:
        dialog = self._create_dialog(title, bundle, widget, parent)

        return (dialog, widget)

    def _on_dialog_closed(self, dlg):
        """
        Called when a dialog created by this engine is closed.

        :param dlg: The dialog being closed
        :type dlg: :class:`PySide.QtGui.QWidget`

        Derived implementations of this method should be sure to call
        the base implementation
        """
        # first, detach the widget from the dialog.  This allows
        # the two objects to be cleaned up seperately menaing the
        # lifetime of the widget can be better managed
        widget = dlg.detach_widget()

        # add the dlg and it's contained widget to the list
        # of widgets to delete at some point!
        self.__qt_widget_trash.append(dlg)
        self.__qt_widget_trash.append(widget)

        if dlg in self.__created_qt_dialogs:
            # don't need to track this dialog any longer
            self.__created_qt_dialogs.remove(dlg)

        # disconnect from the dialog:
        dlg.dialog_closed.disconnect(self._on_dialog_closed)

        # clear temps
        dlg = None
        widget = None

        # finally, clean up the widget trash:
        self.__cleanup_widget_trash()

    def __cleanup_widget_trash(self):
        """
        Run through the widget trash and clean up any widgets
        that are no longer referenced by anything else.

        Notes:  This is pretty dumb and only looks at reference
        counts.  This means that if a widget has cyclic references
        then it will never get released.

        Better to be safe though as deleting/releasing a widget that
        still has events in the event queue will cause a hard crash!
        """
        still_trash = []
        for widget in self.__qt_widget_trash:
            # There should be 3 references:
            # 1. self.__qt_widget_trash[n]
            # 2. widget temporary
            # 3. temporary used by sys.getrefcount
            if sys.getrefcount(widget) <= 3:
                # we have the only references to the widget
                # so lets delete it!
                try:
                    widget.deleteLater()
                except RuntimeError:
                    # this is most likely because the Qt C++ widget has
                    # already been deleted elsewhere so we can safely
                    # ignore it!
                    pass
            else:
                # there are still other references to this widget
                # out there so we should still keep track of it
                still_trash.append(widget)

        # update widget trash
        self.__qt_widget_trash = still_trash
        self.log_debug(
            "Widget trash contains %d widgets" % (len(self.__qt_widget_trash))
        )

    def show_dialog(self, title, bundle, widget_class, *args, **kwargs):
        """
        Shows a non-modal dialog window in a way suitable for this engine.
        The engine will attempt to parent the dialog nicely to the host application.
        The dialog will be created with a standard Toolkit window title bar where
        the title will be displayed.

        .. note:: In some cases, it is necessary to hide the standard Toolkit title
                  bar. You can do this by adding a property to the widget class you are
                  displaying::

                        @property
                        def hide_tk_title_bar(self):
                            "Tell the system to not show the standard toolkit toolbar"
                            return True

        **Notes for engine developers**

        Qt dialog & widget management can be quite tricky in different engines/applications.
        Because of this, Sgtk provides a few overridable methods with the idea being that when
        developing a new engine, you only need to override the minimum amount necessary.

        Making use of these methods in the correct way allows the base Engine class to manage the
        lifetime of the dialogs and widgets efficiently and safely without you having to worry about it.

        The methods available are listed here in the hierarchy in which they are called::

            show_dialog()/show_modal()
                _create_dialog_with_widget()
                    _get_dialog_parent()
                    _create_widget()
                    _create_dialog()

        For example, if you just need to make sure that all dialogs use a specific parent widget
        then you only need to override _get_dialog_parent() (e.g. the tk-maya engine).
        However, if you need to implement a two-stage creation then you may need to re-implement
        show_dialog() and show_modal() to call _create_widget() and _create_dialog() directly rather
        than using the helper method _create_dialog_with_widget() (e.g. the tk-3dsmax engine).
        Finally, if the application you are writing an engine for is Qt based then you may not need
        to override any of these methods (e.g. the tk-nuke engine).

        :param title: The title of the window. This will appear in the Toolkit title bar.
        :param bundle: The app, engine or framework object that is associated with this window
        :param widget_class: The class of the UI to be constructed. This must derive from QWidget.
        :type widget_class: :class:`PySide.QtGui.QWidget`

        Additional parameters specified will be passed through to the widget_class constructor.

        :returns: the created widget_class instance
        """
        if not self.has_ui:
            self.log_error(
                "Sorry, this environment does not support UI display! Cannot show "
                "the requested window '%s'." % title
            )
            return None

        # create the dialog:
        dialog, widget = self._create_dialog_with_widget(
            title, bundle, widget_class, *args, **kwargs
        )

        # show the dialog
        dialog.show()

        # lastly, return the instantiated widget
        return widget

    def show_modal(self, title, bundle, widget_class, *args, **kwargs):
        """
        Shows a modal dialog window in a way suitable for this engine. The engine will attempt to
        integrate it as seamlessly as possible into the host application. This call is blocking
        until the user closes the dialog.
        The dialog will be created with a standard Toolkit window title bar where
        the title will be displayed.

        .. note:: In some cases, it is necessary to hide the standard Toolkit title
                  bar. You can do this by adding a property to the widget class you are
                  displaying::

                        @property
                        def hide_tk_title_bar(self):
                            "Tell the system to not show the standard toolkit toolbar"
                            return True

        :param title: The title of the window
        :param bundle: The app, engine or framework object that is associated with this window
        :param widget_class: The class of the UI to be constructed. This must derive from QWidget.
        :type widget_class: :class:`PySide.QtGui.QWidget`

        Additional parameters specified will be passed through to the widget_class constructor.

        :returns: (a standard QT dialog status return code, the created widget_class instance)
        """
        if not self.has_ui:
            self.log_error(
                "Sorry, this environment does not support UI display! Cannot show "
                "the requested window '%s'." % title
            )
            return None

        # create the dialog:
        dialog, widget = self._create_dialog_with_widget(
            title, bundle, widget_class, *args, **kwargs
        )

        # finally launch it, modal state
        status = dialog.exec_()

        # lastly, return the instantiated widget
        return (status, widget)

    def show_panel(self, panel_id, title, bundle, widget_class, *args, **kwargs):
        """
        Shows a panel in a way suitable for this engine. Engines should attempt to
        integrate panel support as seamlessly as possible into the host application.
        Some engines have extensive panel support and workflows, others have none at all.

        If the engine does not specifically implement panel support, the window will
        be shown as a modeless dialog instead and the call is equivalent to
        calling :meth:`show_dialog()`.

        The dialog will be created with a standard Toolkit window title bar where
        the title will be displayed.

        .. note:: In some cases, it is necessary to hide the standard Toolkit title
                  bar. You can do this by adding a property to the widget class you are
                  displaying::

                        @property
                        def hide_tk_title_bar(self):
                            "Tell the system to not show the standard toolkit toolbar"
                            return True

        :param panel_id: Unique identifier for the panel, as obtained by register_panel().
        :param title: The title of the panel
        :param bundle: The app, engine or framework object that is associated with this window
        :param widget_class: The class of the UI to be constructed. This must derive from QWidget.
        :type widget_class: :class:`PySide.QtGui.QWidget`

        Additional parameters specified will be passed through to the widget_class constructor.

        :returns: the created widget_class instance
        """
        # engines implementing panel support should subclass this method.
        # the core implementation falls back on a modeless window.
        self.log_warning(
            "Panel functionality not implemented. Falling back to showing "
            "panel '%s' in a modeless dialog" % panel_id
        )
        return self.show_dialog(title, bundle, widget_class, *args, **kwargs)

    def _resolve_sg_stylesheet_tokens(self, style_sheet):
        """
        Given a string containing a qt style sheet,
        perform replacements of key toolkit tokens.

        For example, "{{SG_HIGHLIGHT_COLOR}}" is converted to "#30A7E3"

        :param style_sheet: Stylesheet string to process
        :returns: Stylesheet string with replacements applied
        """
        processed_style_sheet = style_sheet
        for (token, value) in constants.SG_STYLESHEET_CONSTANTS.items():
            processed_style_sheet = processed_style_sheet.replace(
                "{{%s}}" % token, value
            )
        return processed_style_sheet

    def _apply_external_stylesheet(self, bundle, widget):
        """
        Apply an std external stylesheet, associated with a bundle, to a widget.

        This will check if a standard style.css file exists in the
        app/engine/framework root location on disk and if so load it from
        disk and apply to the given widget. The style sheet is cascading, meaning
        that it will affect all children of the given widget. Typically this is used
        at window creation in order to allow newly created dialogs to apply app specific
        styles easily.

        If the `SHOTGUN_QSS_FILE_WATCHER` env variable is set to "1", the style sheet
        will be reloaded and re-applied if changed. This can be useful when developing
        apps to do some interactive styling but shouldn't be used in production.

        :param bundle: app/engine/framework instance to load style sheet from
        :param widget: widget to apply stylesheet to
        """
        qss_file = os.path.join(bundle.disk_location, constants.BUNDLE_STYLESHEET_FILE)
        if not os.path.exists(qss_file):
            # Bail out if the file does not exist.
            return
        self.log_debug(
            "Detected std style sheet file '%s' - applying to widget %s"
            % (qss_file, widget)
        )
        try:
            self._apply_stylesheet_file(qss_file, widget)
        except Exception as e:
            # catch-all and issue a warning and continue.
            self.log_warning("Could not apply stylesheet '%s': %s" % (qss_file, e))

        # Set a style sheet file watcher which can be used for interactive styling.
        # File watchers can cause problems in production when accessing shared
        # storage, so we only set it if explicitly asked to do so.
        if os.getenv("SHOTGUN_QSS_FILE_WATCHER", False) == "1":
            try:
                self._add_stylesheet_file_watcher(qss_file, widget)
            except Exception as e:
                # We don't want the watcher to cause any problem, so we catch
                # errors but issue a warning so the developer knows that interactive
                # styling is off.
                self.log_warning("Unable to set qss file watcher: %s" % e)

    # Here we add backward compatibility for a typo that existed in core for a
    # while. The method was found to be used in some existing Engine subclasses
    # so we need this.
    _apply_external_styleshet = _apply_external_stylesheet

    def _apply_stylesheet_file(self, qss_file, widget):
        """
        Load and apply the given style sheet file to the given widget and all its
        children.

        :param str qss_file: Full path to the style sheet file.
        :param widget: The QWidget to apply the style sheet to.
        """
        f = open(qss_file, "rt")
        try:
            qss_data = f.read()
            # resolve tokens
            qss_data = self._resolve_sg_stylesheet_tokens(qss_data)
            # apply to widget (and all its children)
            widget.setStyleSheet(qss_data)
            # Post of widget repaint
            widget.update()
        finally:
            f.close()

    def _add_stylesheet_file_watcher(self, qss_file, widget):
        """
        Set a file watcher which will reload and re-apply the stylesheet file to
        the given widget if the file is modified.

        This can be useful when developping apps to perform interactive styling,
        but shouldn't be used in production because of the problems it can cause.

        :param qss_file: Full path to the style sheet file.
        :param widget: A QWidget to apply the stylesheet to.
        """
        from .qt import QtCore

        # We don't keep any reference to the watcher to let it be deleted with
        # the widget it is parented under.
        # Please note that QWidgets/QFileSystemWatcher don't seem to be actually
        # deleted, so if multiple dialogs are created, e.g. from tk-desktop, users
        # could end up having a *lot* of file watchers running. Another good reason
        # to *not* run these watchers in production, but only when developing apps.
        watcher = QtCore.QFileSystemWatcher([qss_file], parent=widget)
        watcher.fileChanged.connect(
            lambda x: self._on_external_stylesheet_changed(x, watcher, widget)
        )
        # We use log_info here instead of log_debug because the style sheet watcher
        # is meant to be used only when doing development and knowing that the
        # style sheet file watcher is activated is useful when the file is tweaked
        # but no visible changes happen. It can be useful as well to know that watchers
        # were activated by mistake in production.
        self.log_debug("Watching qss file %s for %s..." % (qss_file, widget))

    def _on_external_stylesheet_changed(self, qss_file, watcher, widget):
        """
        Called when the style sheet file has been modified and a watcher was set.
        Reload and re-apply the style sheet file to the given widget.

        :param qss_file: Full path to the style sheet file.
        :param watcher: The :class:`QtCore.QFileSystemWatcher` which triggered the
                        callback.
        :param widget: A QWidget to apply the stylesheet to.
        """
        # We use log_info here instead of log_debug because the style sheet watcher
        # is meant to be used only when doing development and knowing that the
        # style sheet file was reloaded but without any visible effect is useful
        # when tweaking it.
        self.log_info("Reloading style sheet %s..." % qss_file)
        # Unset styling
        widget.setStyleSheet("")
        # And reload it
        self._apply_stylesheet_file(qss_file, widget)
        # Some code editors rename files on save, so the watcher will
        # stop watching the file. Check if the file is being watched, re-attach
        # it if not.
        if qss_file not in watcher.files():
            watcher.addPath(qss_file)

    def _define_qt_base(self):
        """
        This will be called at initialisation time and will allow
        a user to control various aspects of how QT is being used
        by Tank. The method should return a dictionary with a number
        of specific keys, outlined below.

        * qt_core - the QtCore module to use
        * qt_gui - the QtGui module to use
        * wrapper - the Qt wrapper root module, e.g. PySide
        * dialog_base - base class for to use for Tank's dialog factory

        :returns: dict
        """
        base = {"qt_core": None, "qt_gui": None, "dialog_base": None}
        try:
            importer = QtImporter()
            base["qt_core"] = importer.QtCore
            base["qt_gui"] = importer.QtGui
            if importer.QtGui:
                base["dialog_base"] = importer.QtGui.QDialog
            else:
                base["dialog_base"] = None
            base["wrapper"] = importer.binding
            base["shiboken"] = importer.shiboken
        except:

            self.log_exception(
                "Default engine QT definition failed to find QT. "
                "This may need to be subclassed."
            )

        return base

    def __define_qt5_base(self):
        """
        This will be called at initialization to discover every PySide 2 modules. It should provide
        every Qt modules available as well as two extra attributes, ``__name__`` and
        ``__version__``, which refer to the name of the binding and it's version, e.g.
        PySide2 and 2.0.1.

        .. note:: PyQt5 not supported since it runs only on Python 3.

        :returns: A dictionary with all the modules, __version__ and __name__.
        """
        return QtImporter(interface_version_requested=QtImporter.QT5).base

    def __define_qt6_base(self):
        """
        This will be called at initialization to discover every PySide6 module. It should provide
        every Qt modules available as well as two extra attributes, ``__name__`` and
        ``__version__``, which refer to the name of the binding and it's version, e.g.
        PySide6 and 6.2.7

        :returns: A dictionary with all the modules, __version__ and __name__.
        """
        return QtImporter(interface_version_requested=QtImporter.QT6).base

    def _initialize_dark_look_and_feel(self):
        """
        Initializes a standard toolkit look and feel using a combination of
        QPalette and stylesheets.

        If your engine is running inside an environment which already has
        a dark style defined, do not call this method. The Toolkit apps are
        designed to work well with most dark themes.

        However, if you are for example creating your own QApplication instance
        you can execute this method to put the session into Toolkit's
        standard dark mode.

        This will initialize the plastique style (for Qt4) or the fusion style
        (for Qt5/Qt6), and set it up with a standard dark palette and supporting
        stylesheet.

        `Qt5 setStyle documentation <https://doc.qt.io/qt-5.10/qapplication.html#setStyle-1>`_
        `Qt6 setStyle documentation <https://doc.qt.io/qt-6/qapplication.html#setStyle-1>`_

        Apps and UIs can then extend this further by using further css.

        Due to restrictions in QT, this needs to run after a QApplication object
        has been instantiated.
        """
        if self.has_qt5 or self.has_qt6:
            self.log_debug("Applying Qt5/Qt6-specific styling (Fusion)...")
            self.__initialize_dark_look_and_feel_qt5_qt6()
        else:
            self.log_warning(
                "Neither Qt5 or Qt6 is available. Toolkit styling will not be applied."
            )

    def __initialize_dark_look_and_feel_qt5_qt6(self):
        """
        Applies a dark style for Qt5 environments. This sets the "fusion" style
        at the application level, and then constructs and applies a custom palette
        that emulates Maya 2017's color scheme.
        """
        from .qt import QtGui

        app = QtGui.QApplication.instance()

        # Set the fusion style, which gives us a good base to build on. With
        # this, we'll be sticking largely to the style and won't need to
        # introduce much qss to get a good look.
        app.setStyle("fusion")

        # Build ourselves a dark palette to assign to the application. This
        # will take the fusion style and darken it up.
        palette = QtGui.QPalette()

        # This closely resembles the color palette used in Maya 2017 with a
        # few minor tweaks.
        palette.setBrush(
            QtGui.QPalette.Disabled, QtGui.QPalette.Button, QtGui.QColor(80, 80, 80)
        )
        palette.setBrush(
            QtGui.QPalette.Disabled, QtGui.QPalette.Light, QtGui.QColor(97, 97, 97)
        )
        palette.setBrush(
            QtGui.QPalette.Disabled, QtGui.QPalette.Midlight, QtGui.QColor(59, 59, 59)
        )
        palette.setBrush(
            QtGui.QPalette.Disabled, QtGui.QPalette.Dark, QtGui.QColor(37, 37, 37)
        )
        palette.setBrush(
            QtGui.QPalette.Disabled, QtGui.QPalette.Mid, QtGui.QColor(45, 45, 45)
        )
        palette.setBrush(
            QtGui.QPalette.Disabled, QtGui.QPalette.Base, QtGui.QColor(42, 42, 42)
        )
        palette.setBrush(
            QtGui.QPalette.Disabled, QtGui.QPalette.Window, QtGui.QColor(68, 68, 68)
        )
        palette.setBrush(
            QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, QtGui.QColor(0, 0, 0)
        )
        palette.setBrush(
            QtGui.QPalette.Disabled,
            QtGui.QPalette.AlternateBase,
            palette.color(QtGui.QPalette.Disabled, QtGui.QPalette.Base).lighter(110),
        )
        palette.setBrush(
            QtGui.QPalette.Disabled,
            QtGui.QPalette.Text,
            palette.color(QtGui.QPalette.Disabled, QtGui.QPalette.Base).lighter(250),
        )
        palette.setBrush(
            QtGui.QPalette.Disabled,
            QtGui.QPalette.Link,
            palette.color(QtGui.QPalette.Disabled, QtGui.QPalette.Base).lighter(250),
        )
        palette.setBrush(
            QtGui.QPalette.Disabled,
            QtGui.QPalette.LinkVisited,
            palette.color(QtGui.QPalette.Disabled, QtGui.QPalette.Base).lighter(110),
        )

        palette.setBrush(
            QtGui.QPalette.Active,
            QtGui.QPalette.WindowText,
            QtGui.QColor(200, 200, 200),
        )
        palette.setBrush(
            QtGui.QPalette.Active, QtGui.QPalette.Button, QtGui.QColor(75, 75, 75)
        )
        palette.setBrush(
            QtGui.QPalette.Active,
            QtGui.QPalette.ButtonText,
            QtGui.QColor(200, 200, 200),
        )
        palette.setBrush(
            QtGui.QPalette.Active, QtGui.QPalette.Light, QtGui.QColor(97, 97, 97)
        )
        palette.setBrush(
            QtGui.QPalette.Active, QtGui.QPalette.Midlight, QtGui.QColor(59, 59, 59)
        )
        palette.setBrush(
            QtGui.QPalette.Active, QtGui.QPalette.Dark, QtGui.QColor(37, 37, 37)
        )
        palette.setBrush(
            QtGui.QPalette.Active, QtGui.QPalette.Mid, QtGui.QColor(45, 45, 45)
        )
        palette.setBrush(
            QtGui.QPalette.Active, QtGui.QPalette.Text, QtGui.QColor(200, 200, 200)
        )
        palette.setBrush(
            QtGui.QPalette.Active, QtGui.QPalette.Link, QtGui.QColor(200, 200, 200)
        )
        palette.setBrush(
            QtGui.QPalette.Active, QtGui.QPalette.LinkVisited, QtGui.QColor(97, 97, 97)
        )
        palette.setBrush(
            QtGui.QPalette.Active, QtGui.QPalette.BrightText, QtGui.QColor(37, 37, 37)
        )
        palette.setBrush(
            QtGui.QPalette.Active, QtGui.QPalette.Base, QtGui.QColor(42, 42, 42)
        )
        palette.setBrush(
            QtGui.QPalette.Active, QtGui.QPalette.Window, QtGui.QColor(68, 68, 68)
        )
        palette.setBrush(
            QtGui.QPalette.Active, QtGui.QPalette.Shadow, QtGui.QColor(0, 0, 0)
        )
        palette.setBrush(
            QtGui.QPalette.Active,
            QtGui.QPalette.AlternateBase,
            palette.color(QtGui.QPalette.Active, QtGui.QPalette.Base).lighter(110),
        )

        palette.setBrush(
            QtGui.QPalette.Inactive,
            QtGui.QPalette.WindowText,
            QtGui.QColor(200, 200, 200),
        )
        palette.setBrush(
            QtGui.QPalette.Inactive, QtGui.QPalette.Button, QtGui.QColor(75, 75, 75)
        )
        palette.setBrush(
            QtGui.QPalette.Inactive,
            QtGui.QPalette.ButtonText,
            QtGui.QColor(200, 200, 200),
        )
        palette.setBrush(
            QtGui.QPalette.Inactive, QtGui.QPalette.Light, QtGui.QColor(97, 97, 97)
        )
        palette.setBrush(
            QtGui.QPalette.Inactive, QtGui.QPalette.Midlight, QtGui.QColor(59, 59, 59)
        )
        palette.setBrush(
            QtGui.QPalette.Inactive, QtGui.QPalette.Dark, QtGui.QColor(37, 37, 37)
        )
        palette.setBrush(
            QtGui.QPalette.Inactive, QtGui.QPalette.Mid, QtGui.QColor(45, 45, 45)
        )
        palette.setBrush(
            QtGui.QPalette.Inactive, QtGui.QPalette.Text, QtGui.QColor(200, 200, 200)
        )
        palette.setBrush(
            QtGui.QPalette.Inactive, QtGui.QPalette.Link, QtGui.QColor(200, 200, 200)
        )
        palette.setBrush(
            QtGui.QPalette.Inactive,
            QtGui.QPalette.LinkVisited,
            QtGui.QColor(97, 97, 97),
        )
        palette.setBrush(
            QtGui.QPalette.Inactive, QtGui.QPalette.BrightText, QtGui.QColor(37, 37, 37)
        )
        palette.setBrush(
            QtGui.QPalette.Inactive, QtGui.QPalette.Base, QtGui.QColor(42, 42, 42)
        )
        palette.setBrush(
            QtGui.QPalette.Inactive, QtGui.QPalette.Window, QtGui.QColor(68, 68, 68)
        )
        palette.setBrush(
            QtGui.QPalette.Inactive, QtGui.QPalette.Shadow, QtGui.QColor(0, 0, 0)
        )
        palette.setBrush(
            QtGui.QPalette.Inactive,
            QtGui.QPalette.AlternateBase,
            palette.color(QtGui.QPalette.Inactive, QtGui.QPalette.Base).lighter(110),
        )

        app.setPalette(palette)

        # Finally, we just need to set the default font size for our widgets
        # deriving from QWidget. This also has the side effect of correcting
        # a couple of styling quirks in the tank dialog header when it's
        # used with the fusion style.
        app.setStyleSheet(".QWidget { font-size: 11px; }")

    def _get_standard_qt_stylesheet(self):
        """
        **********************************************************************
        THIS METHOD HAS BEEN DEPRECATED AND SHOULD NOT BE USED!
        Instead, call _initialize_standard_look_and_feel()
        **********************************************************************

        For environments which do not have a well defined QT style sheet,
        Toolkit maintains a "standard style" which is similar to the look and
        feel that Maya and Nuke has.

        This is intended to be used in conjunction with QTs cleanlooks mode.
        The init code inside an engine would typically look something like this:

            QtGui.QApplication.setStyle("cleanlooks")
            qt_application = QtGui.QApplication([])
            qt_application.setStyleSheet( self._get_standard_qt_stylesheet() )

        :returns: The style sheet data, as a string.
        """
        css_file = self.__get_platform_resource_path("toolkit_std_dark.css")
        with open(css_file) as f:
            return f.read()

    def _register_shared_framework(self, instance_name, fw_obj):
        """
        Registers a framework with the specified instance name.
        This allows framework instances to be shared between bundles.
        This method is exposed for use by the platform.framework module.

        :param instance_name: Name of framework instance, as defined in the
                              environment. For example 'tk-framework-widget_v1.x.x'
        :param fw_obj: Framework object.
        """
        self.__shared_frameworks[instance_name] = fw_obj

    def _get_shared_framework(self, instance_name):
        """
        Get a framework instance by name. If no framework with the specified
        name has been loaded yet, None is returned.
        This method is exposed for use by the platform.framework module.

        :param instance_name: Name of framework instance, as defined in the
                              environment. For example 'tk-framework-widget_v1.x.x'
        """
        return self.__shared_frameworks.get(instance_name, None)

    def __create_invokers(self):
        """
        Create the object used to invoke function calls on the main thread when
        called from a different thread.
        """
        invoker = None
        async_invoker = None
        if self.has_ui:
            from .qt import QtGui, QtCore

            # Classes are defined locally since Qt might not be available.
            if QtGui and QtCore:

                class Invoker(QtCore.QObject):
                    """
                    Invoker class - implements a mechanism to execute a function with arbitrary
                    args in the main thread.
                    """

                    def __init__(self):
                        """
                        Construction
                        """
                        QtCore.QObject.__init__(self)
                        self._lock = threading.Lock()
                        self._fn = None
                        self._res = None

                    def invoke(self, fn, *args, **kwargs):
                        """
                        Invoke the specified function with the specified args in the main thread

                        :param fn:          The function to execute in the main thread
                        :param *args:       Args for the function
                        :param **kwargs:    Named arguments for the function
                        :returns:           The result returned by the function
                        """
                        # acquire lock to ensure that the function and result are not overwritten
                        # by syncrounous calls to this method from different threads
                        self._lock.acquire()
                        try:
                            self._fn = lambda: fn(*args, **kwargs)
                            self._res = None

                            # invoke the internal _do_invoke method that will actually run the function.  Note that
                            # we are unable to pass/return arguments through invokeMethod as this isn't properly
                            # supported by PySide.
                            QtCore.QMetaObject.invokeMethod(
                                self, "_do_invoke", QtCore.Qt.BlockingQueuedConnection
                            )

                            return self._res
                        finally:
                            self._lock.release()

                    @qt.QtCore.Slot()
                    def _do_invoke(self):
                        """
                        Execute the function
                        """
                        self._res = self._fn()

                class AsyncInvoker(QtCore.QObject):
                    """
                    Invoker class - implements a mechanism to execute a function with arbitrary
                    args in the main thread asynchronously.
                    """

                    __signal = QtCore.Signal(object)

                    def __init__(self):
                        """
                        Construction
                        """
                        QtCore.QObject.__init__(self)
                        self.__signal.connect(self.__execute_in_main_thread)

                    def invoke(self, fn, *args, **kwargs):
                        """
                        Invoke the specified function with the specified args in the main thread

                        :param fn:          The function to execute in the main thread
                        :param *args:       Args for the function
                        :param **kwargs:    Named arguments for the function
                        :returns:           The result returned by the function
                        """

                        self.__signal.emit(lambda: fn(*args, **kwargs))

                    def __execute_in_main_thread(self, fn):
                        fn()

                # Make sure that the invoker exists in the main thread:
                invoker = Invoker()
                async_invoker = AsyncInvoker()
                if QtCore.QCoreApplication.instance():
                    invoker.moveToThread(QtCore.QCoreApplication.instance().thread())
                    async_invoker.moveToThread(
                        QtCore.QCoreApplication.instance().thread()
                    )

        return invoker, async_invoker

    ##########################################################################################
    # private

    def __load_apps(self, reuse_existing_apps=False, old_context=None):
        """
        Populate the __applications dictionary, skip over apps that fail to initialize.

        :param reuse_existing_apps:     Whether to use already-running apps rather than
                                        starting up a new instance. This is primarily
                                        used during context changes. Default is False.
        :param old_context:             In the event of a context change occurring, this
                                        represents the context being changed away from,
                                        which will be provided along with the current
                                        context to each reused app's post_context_change
                                        method.
        """
        # If this is a load as part of a context change, the applications
        # dict will already have stuff in it. We can explicitly clean that
        # out here since those apps also exist in self.__application_pool,
        # which is persistent.
        self.__applications = dict()

        # The commands dict will be repopulated either by new app inits,
        # or by pulling existing commands for reused apps from the persistant
        # cache of commands.
        self.__commands = dict()
        self.__register_reload_command()

        for app_instance_name in self.__env.get_apps(self.__engine_instance_name):
            # Get a handle to the app bundle.
            descriptor = self.__env.get_app_descriptor(
                self.__engine_instance_name, app_instance_name
            )

            if not descriptor.exists_local():
                self.log_error(
                    "Cannot start app! %s does not exist on disk." % descriptor
                )
                continue

            # Load settings for app - skip over the ones that don't validate
            try:
                # get the app settings data and validate it.
                app_schema = descriptor.configuration_schema
                app_settings = self.__env.get_app_settings(
                    self.__engine_instance_name, app_instance_name
                )

                # check that the context contains all the info that the app needs
                if self.__engine_instance_name != constants.SHOTGUN_ENGINE_NAME:
                    # special case! The shotgun engine is special and does not have a
                    # context until you actually run a command, so disable the validation.
                    validation.validate_context(descriptor, self.context)

                # make sure the current operating system platform is supported
                validation.validate_platform(descriptor)

                # for multi engine apps, make sure our engine is supported
                supported_engines = descriptor.supported_engines
                if supported_engines and self.name not in supported_engines:
                    raise TankError(
                        "The app could not be loaded since it only supports "
                        "the following engines: %s. Your current engine has been "
                        "identified as '%s'" % (supported_engines, self.name)
                    )

                # now validate the configuration
                validation.validate_settings(
                    app_instance_name, self.tank, self.context, app_schema, app_settings
                )

            except TankError as e:
                # validation error - probably some issue with the settings!
                # report this as an error message.
                self.log_error(
                    "App configuration Error for %s (configured in environment '%s'). "
                    "It will not be loaded: %s"
                    % (app_instance_name, self.__env.disk_location, e)
                )
                continue

            except Exception:
                # code execution error in the validation. Report this as an error
                # with the engire call stack!
                self.log_exception(
                    "A general exception was caught while trying to "
                    "validate the configuration loaded from '%s' for app %s. "
                    "The app will not be loaded."
                    % (self.__env.disk_location, app_instance_name)
                )
                continue

            # If we're told to reuse existing app instances, check for it and
            # continue if it's already there. This is most likely a context
            # change that's in progress, which means we only want to load apps
            # that aren't already up and running.
            install_path = descriptor.get_path()
            app_pool = self.__application_pool

            if reuse_existing_apps and install_path in app_pool:
                # If we were given an "old" context that's being switched away
                # from, we can run the post change method and do a bit of
                # reinitialization of certain portions of the app.
                if (
                    old_context is not None
                    and app_instance_name in app_pool[install_path]
                ):
                    app = self.__application_pool[install_path][app_instance_name]

                    try:
                        # Update the app's internal context pointer.
                        app._set_context(self.context)

                        # Update the app settings.
                        app._set_settings(app_settings)

                        # Set the instance name.
                        app.instance_name = app_instance_name

                        # Make sure our frameworks are up and running properly for
                        # the new context.
                        setup_frameworks(self, app, self.__env, descriptor)

                        # Repopulate the app's commands into the engine.
                        for command_name, command in self.__command_pool.items():
                            if app is command.get("properties", dict()).get("app"):
                                self.__commands[command_name] = command

                        # Run the post method in case there's custom logic implemented
                        # for the app.
                        app.post_context_change(old_context, self.context)
                    except Exception:
                        # If any of the reinitialization failed we will warn and
                        # continue on to a restart of the app via the normal means.
                        self.log_warning(
                            "App %r failed to change context and will be restarted: %s"
                            % (app, traceback.format_exc())
                        )
                    else:
                        # If the reinitialization of the reused app succeeded, we
                        # just have to add it to the apps list and continue on to
                        # the next app.
                        self.log_debug(
                            "App %s successfully reinitialized for new context %s."
                            % (app_instance_name, str(self.context))
                        )
                        self.__applications[app_instance_name] = app
                        continue

            # load the app
            try:
                # now get the app location and resolve it into a version object
                app_dir = descriptor.get_path()

                # create the object, run the constructor
                app = application.get_application(
                    self,
                    app_dir,
                    descriptor,
                    app_settings,
                    app_instance_name,
                    self.__env,
                )

                # load any frameworks required
                setup_frameworks(self, app, self.__env, descriptor)

                # track the init of the app
                self.__currently_initializing_app = app
                try:
                    app.init_app()
                finally:
                    self.__currently_initializing_app = None

            except TankError as e:
                self.log_error(
                    "App %s failed to initialize. It will not be loaded: %s"
                    % (app_dir, e)
                )

            except Exception:
                self.log_exception(
                    "App %s failed to initialize. It will not be loaded." % app_dir
                )
            else:
                # note! Apps are keyed by their instance name, meaning that we
                # could theoretically have multiple instances of the same app.
                self.__applications[app_instance_name] = app

            # For the sake of potetial context changes, apps and commands are cached
            # into a persistent pool such that they can be reused at some later time.
            # This is required because, during context changes, some apps that were
            # active in the old context might not be active in the new context. Because
            # we might then switch BACK to the old context at some later time, or some
            # future context might simply make use of some of the same apps, we want
            # to keep a running cache of everything that's been initialized over time.
            # This will allow us to reuse those (assuming they support on-the-fly
            # context changes) rather than having to import and instantiate the same
            # app(s) all over again, thereby hurting performance.

            # Likewise, with commands, those from the old context that are not associated
            # with apps that are active in the new context are filtered out of the engine's
            # list of commands. When switching back to the old context, or any time the
            # associated app is reused, we can then add back in the commands that the app
            # had previously registered. With that, we're not required to re-run the init
            # process for the app.

            # Update the persistent application pool for use in context changes.
            for app in self.__applications.values():
                # We will only track apps that we know can handle a context
                # change. Any that do not will not be treated as a persistent
                # app.
                if (
                    app.context_change_allowed
                    and app.instance_name == app_instance_name
                ):
                    app_path = app.descriptor.get_path()

                    if app_path not in self.__application_pool:
                        self.__application_pool[app_path] = dict()

                    self.__application_pool[app_path][app_instance_name] = app

            # Update the persistent commands pool for use in context changes.
            for command_name, command in self.__commands.items():
                self.__command_pool[command_name] = command

    def __destroy_frameworks(self):
        """
        Destroy frameworks
        """
        # Destroy engine's frameworks
        for fw in self.frameworks.values():
            if not fw.is_shared:
                fw._destroy_framework()

        # Destroy shared frameworks
        for fw in self.__shared_frameworks.values():
            fw._destroy_framework()
        self.__shared_frameworks = {}

    def __destroy_apps(self):
        """
        Call the destroy_app method on all loaded apps
        """

        for app in self.__applications.values():
            app._destroy_frameworks()
            self.log_debug("Destroying %s" % app)
            app.destroy_app()

    def __register_reload_command(self):
        """
        Registers a "Reload and Restart" command with the engine if any
        running apps are registered via a dev descriptor.
        """
        for app in self.__applications.values():
            if app.descriptor.is_dev():
                self.log_debug(
                    "App %s is registered via a dev descriptor. Will add a reload "
                    "button to the actions listings." % app
                )
                from . import restart

                self.register_command(
                    "Reload and Restart",
                    restart,
                    {
                        "short_name": "restart",
                        "icon": self.__get_platform_resource_path("reload_256.png"),
                        "type": "context_menu",
                    },
                )
                # only need one reload button, so don't keep iterating :)
                break

    def __get_platform_resource_path(self, filename):
        """
        Returns the full path to the given platform resource file or folder.
        Resources reside in the core/platform/qt folder.

        :return: full path
        """
        this_folder = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(this_folder, "qt", filename)

    def __run_post_engine_inits(self):
        """
        Executes the post_engine_init method for all running apps.
        """
        for app in self.__applications.values():
            try:
                app.post_engine_init()
            except TankError as e:
                self.log_error(
                    "App %s Failed to run its post_engine_init. It is loaded, but"
                    "may not operate in its desired state! Details: %s" % (app, e)
                )
            except Exception:
                self.log_exception(
                    "App %s failed run its post_engine_init. It is loaded, but"
                    "may not operate in its desired state!" % app
                )


##########################################################################################
# Engine management

g_current_engine = None


def set_current_engine(eng):
    """
    Sets the current engine

    :param eng: :class:`Engine` instance to set as current.
    """
    global g_current_engine
    g_current_engine = eng


def current_engine():
    """
    Returns the currently active engine.

    :returns: :class:`Engine` instance or None if no engine is running.
    """
    global g_current_engine
    return g_current_engine


def get_engine_path(engine_name, tk, context):
    """
    Returns the path to the engine corresponding to the given engine name or
    None if the engine could not be found.

    Similar to :meth:`start_engine`, but instead of starting an engine, this method
    returns the path to a suitable engine. This helper method is sometimes useful
    when initializing engines for applications that do not have a built in python interpreter.

    Example::

        >>> import sgtk
        >>> tk = sgtk.sgtk_from_path("/studio/project_root")
        >>> ctx = tk.context_empty()
        >>> sgtk.platform.get_engine_path('tk-maya', tk, ctx)
        /studio/sgtk/install/engines/app_store/tk-maya/v0.1.0


    :param engine_name: Name of the engine to launch, e.g. tk-maya
    :param tk: :class:`~sgtk.Sgtk` instance to associate the engine with
    :param context: :class:`~sgtk.Context` object of the context to launch the engine for.
    :returns: Path to where the engine code is located on disk.
    """
    # get environment and engine location
    try:
        (env, engine_descriptor) = get_env_and_descriptor_for_engine(
            engine_name, tk, context
        )
    except TankEngineInitError:
        return None

    # return path to engine code
    engine_path = engine_descriptor.get_path()
    return engine_path


def start_engine(engine_name, tk, context):
    """
    Creates an engine and makes it the current engine.
    Returns the newly created engine object. Example::

        >>> import sgtk
        >>> tk = sgtk.sgtk_from_path("/studio/project_root")
        >>> ctx = tk.context_empty()
        >>> engine = sgtk.platform.start_engine('tk-maya', tk, ctx)
        >>> engine
        <Sgtk Engine 0x10451b690: tk-maya, env: shotgun>

    .. note:: This is for advanced workflows. For standard use
        cases, use :meth:`~sgtk.bootstrap.ToolkitManager.bootstrap_engine`.
        For more information, see :ref:`init_and_startup`.

    :param engine_name: Name of the engine to launch, e.g. tk-maya
    :param tk: :class:`~sgtk.Sgtk` instance to associate the engine with
    :param context: :class:`~sgtk.Context` object of the context to launch the engine for.
    :returns: :class:`Engine` instance
    :raises: :class:`TankEngineInitError` if an engine could not be started
             for the passed context.
    """
    return _start_engine(engine_name, tk, None, context)


def _restart_engine(new_context):
    """
    Restarts an engine by destroying the previous one and creating a new one.

    :param new_context: Context for the new engine. If None, previous context will
        be reused.
    :type new_context: :class:`~sgtk.Context`
    """
    engine = current_engine()
    try:
        # Track some of the current state before restarting the engine.
        old_context = engine.context
        new_context = new_context or engine.context

        # Restart the engine. If we were given a new context to use,
        # use it, otherwise restart using the same context as before.
        current_engine_name = engine.instance_name
        with _CoreContextChangeHookGuard(engine.sgtk, old_context, new_context):
            engine.destroy()

            _start_engine(
                current_engine_name, new_context.tank, old_context, new_context
            )
    except TankError as e:
        engine.log_error("Could not restart the engine: %s" % e)
    except Exception:
        engine.log_exception("Could not restart the engine!")


class _CoreContextChangeHookGuard(object):
    """
    Used with the ``with`` statement, this guard will notify the context_change
    core hook with the pre_context_change event on entering and
    post_context_change even on exit if and only if the scope exits without
    an exception being raised.
    """

    _depth = 0

    def __init__(self, tk, old_context, new_context):
        """
        Constructor.

        :param tk: Toolkit instance.
        :param old_context: Current context.
        :param new_context: Context we're switching to.
        """
        self._tk = tk
        self._old_context = old_context
        self._new_context = new_context

    def __enter__(self):
        """
        Executes the pre context change hook if we're the first guard instance.
        """
        self.__class__._depth += 1
        # If we're the first instance of the guard, notify.
        if self._depth == 1:
            self._execute_pre_context_change(
                self._tk, self._old_context, self._new_context
            )

    # Made static so we can introspec the content of the guard during unit testing.
    @staticmethod
    def _execute_pre_context_change(tk, old_context, new_context):
        """
        Executes the pre context change hook.

        :param tk: Toolkit instance.
        :param old_context: Current context.
        :param new_context: Context we're switching to.
        """
        tk.execute_core_hook_method(
            constants.CONTEXT_CHANGE_HOOK,
            "pre_context_change",
            current_context=old_context,
            next_context=new_context,
        )

    def __exit__(self, ex_type, *_):
        """
        Executes the post context change hook if we're the last guard instance.

        :param ex_type: Type of the exception raised, if any.
        """
        # If we are the last instance of the guard and there's no exception, notify
        if self.__class__._depth == 1 and not ex_type:
            self._execute_post_context_change(
                self._tk, self._old_context, self._new_context
            )

        self.__class__._depth -= 1

    # Made static so we can introspec the content of the guard during unit testing.
    @staticmethod
    def _execute_post_context_change(tk, old_context, new_context):
        """
        Executes the post context change hook.

        :param tk: Toolkit instance.
        :param old_context: Current context.
        :param new_context: Context we're switching to.
        """
        tk.execute_core_hook_method(
            constants.CONTEXT_CHANGE_HOOK,
            "post_context_change",
            previous_context=old_context,
            current_context=new_context,
        )


def _start_engine(engine_name, tk, old_context, new_context):
    """
    Starts an engine for a given Toolkit instance and context.

    :param engine_name: Name of the engine to start.
    :param tk: Toolkit instance.
    :type tk: :class:`~sgtk.Sgtk`
    :param old_context: Context before the context change.
    :type old_context: :class:`~sgtk.Context`
    :param new_context: Context after the context change.
    :type new_context: :class:`~sgtk.Context`

    :returns: A new sgtk.platform.Engine object.
    """
    # first ensure that an engine is not currently running
    if current_engine():
        raise TankError(
            "An engine (%s) is already running! Before you can start a new engine, "
            "please shut down the previous one using the command "
            "tank.platform.current_engine().destroy()." % current_engine()
        )

    # begin writing log to disk, associated with the engine
    # only do this if a logger hasn't been previously set up.
    if LogManager().base_file_handler is None:
        LogManager().initialize_base_file_handler(engine_name)

    # get environment and engine location
    (env, engine_descriptor) = get_env_and_descriptor_for_engine(
        engine_name, tk, new_context
    )

    # make sure it exists locally
    if not engine_descriptor.exists_local():
        raise TankEngineInitError(
            "Cannot start engine! %s does not exist on disk" % engine_descriptor
        )

    # get path to engine code
    engine_path = engine_descriptor.get_path()
    plugin_file = os.path.join(engine_path, constants.ENGINE_FILE)
    class_obj = load_plugin(plugin_file, Engine)

    # Notify the context change and start the engine.
    with _CoreContextChangeHookGuard(tk, old_context, new_context):
        # Instantiate the engine
        engine = class_obj(tk, new_context, engine_name, env)
        # register this engine as the current engine
        set_current_engine(engine)

    metrics_cache.consume()

    return engine


def find_app_settings(engine_name, app_name, tk, context, engine_instance_name=None):
    """
    Utility method to find the settings for an app in an engine in the
    environment determined for the context by pick environment hook.

    :param engine_name: system name of the engine to look for, e.g tk-maya
    :param app_name: system name of the app to look for, e.g. tk-multi-publish
    :param tk: :class:`~sgtk.Sgtk` instance
    :param context: :class:`~sgtk.Context` object to use when picking environment
    :param engine_instance_name: The instance name of the engine to look for.

    :returns: list of dictionaries containing the engine name,
              application name and settings for any matching
              applications that are found and that have valid
              settings
    """
    app_settings = []

    # get the environment via the pick_environment hook
    env_name = __pick_environment(engine_name, tk, context)
    env = tk.pipeline_configuration.get_environment(env_name, context)

    # now find all engines whose names match the engine_name:
    for eng in env.get_engines():
        eng_desc = env.get_engine_descriptor(eng)
        eng_sys_name = eng_desc.system_name

        # Make sure that we get the right engine by comparing engine
        # name and instance name, if provided.
        if eng_sys_name != engine_name:
            continue
        if engine_instance_name and engine_instance_name != eng:
            continue

        # ok, found engine so look for app:
        for app in env.get_apps(eng):
            app_desc = env.get_app_descriptor(eng, app)
            if app_desc.system_name != app_name:
                continue

            # ok, found an app - lets validate the settings as
            # we want to ignore them if they're not valid
            try:
                schema = app_desc.configuration_schema
                settings = env.get_app_settings(eng, app)

                # Check that the context contains all the info that the app needs.
                validation.validate_context(app_desc, context)

                # Make sure the current operating system platform is supported.
                validation.validate_platform(app_desc)

                # For multi engine apps, make sure our engine is supported.
                supported_engines = app_desc.supported_engines
                if supported_engines and engine_name not in supported_engines:
                    raise TankError(
                        "The app doesn't support the engine %s. It supports "
                        "the following engines: %s" % (engine_name, supported_engines)
                    )

                # Finally validate the configuration.
                # Note: context is set to None as we don't
                # want to fail validation because of an
                # incomplete context at this stage!
                validation.validate_settings(app, tk, None, schema, settings)
            except TankError as e:
                core_logger.warning(
                    "Could not validate app settings for the "
                    '"%s" app instance in the "%s" environment '
                    'on the "%s" engine.\nError: %s' % (app, env_name, engine_name, e)
                )
                # Ignore any Tank exceptions to skip invalid apps.
                continue

            # settings are valid so add them to return list:
            app_settings.append(
                {"engine_instance": eng, "app_instance": app, "settings": settings}
            )

    return app_settings


def start_shotgun_engine(tk, entity_type, context):
    """
    Special, internal method that handles the shotgun engine.

    :param tk:          tank instance
    :param entity_type: type of the entity to use as a target for picking our
                        shotgun environment
    :param context:     context to use for the shotgun engine and its apps.

                        If some apps require a specific context to extract
                        information (e.g. they call a pick_environment hook to
                        get the environment to use based on the context), this
                        should be set to something other than the empty
                        context.
    """

    # begin writing log to disk, associated with the engine
    if LogManager().base_file_handler is None:
        LogManager().initialize_base_file_handler(constants.SHOTGUN_ENGINE_NAME)

    # bypass the get_environment hook and use a fixed set of environments
    # for this shotgun engine. This is required because of the action caching.
    env = tk.pipeline_configuration.get_environment(
        "shotgun_%s" % entity_type.lower(), context
    )

    # get the location for our engine
    if constants.SHOTGUN_ENGINE_NAME not in env.get_engines():
        raise TankMissingEngineError(
            "Cannot find a PTR engine in %s. Please contact support." % env
        )

    engine_descriptor = env.get_engine_descriptor(constants.SHOTGUN_ENGINE_NAME)

    # make sure it exists locally
    if not engine_descriptor.exists_local():
        raise TankEngineInitError(
            "Cannot start engine! %s does not exist on disk" % engine_descriptor
        )

    # get path to engine code
    engine_path = engine_descriptor.get_path()
    plugin_file = os.path.join(engine_path, constants.ENGINE_FILE)

    # Instantiate the engine
    class_obj = load_plugin(plugin_file, Engine)
    obj = class_obj(tk, context, constants.SHOTGUN_ENGINE_NAME, env)

    # register this engine as the current engine
    set_current_engine(obj)

    metrics_cache.consume()

    return obj


def get_environment_from_context(tk, context):
    """
    Returns an environment object given a context.
    Returns None if no environment was found.
    """
    try:
        env_name = tk.execute_core_hook(
            constants.PICK_ENVIRONMENT_CORE_HOOK_NAME, context=context
        )
    except Exception as e:
        raise TankError(
            "Could not resolve an environment for context '%s'. The pick "
            "environment hook reported the following error: %s" % (context, e)
        )

    if env_name is None:
        return None

    return tk.pipeline_configuration.get_environment(env_name, context)


def show_global_busy(title, details):
    """
    Convenience method.

    Displays or updates a global busy/progress indicator window tied to the currently running engine.
    For more details and documentation, see the engine class documentation of this method.

    :params title: Short descriptive title of what is happening
    :params details: Detailed message describing what is going on.
    """
    engine = current_engine()
    if engine:
        engine.show_busy(title, details)


def clear_global_busy():
    """
    Convenience method.

    Closes any open global progress indicator window tied to the currently running engine.
    For more details and documentation, see engine class documentation of this method.
    """
    engine = current_engine()
    if engine:
        engine.clear_busy()


##########################################################################################
# utilities


def get_env_and_descriptor_for_engine(engine_name, tk, context):
    """
    Utility method to return commonly needed objects when instantiating engines.

    :param engine_name: system name of the engine to look for, e.g tk-maya
    :param tk: :class:`~sgtk.Sgtk` instance
    :param context: :class:`~sgtk.Context` object to use when picking environment
    :returns: tuple with associated environment and engine descriptor)
    :raises: :class:`TankEngineInitError` if the engine name cannot be found.
    """
    # get the environment via the pick_environment hook
    env_name = __pick_environment(engine_name, tk, context)

    # get the env object based on the name in the pick env hook
    env = tk.pipeline_configuration.get_environment(env_name, context)

    # make sure that the environment has an engine instance with that name
    if engine_name not in env.get_engines():
        raise TankMissingEngineError(
            "Cannot find an engine instance %s in %s." % (engine_name, env)
        )

    # get the location for our engine
    engine_descriptor = env.get_engine_descriptor(engine_name)

    return (env, engine_descriptor)


def __pick_environment(engine_name, tk, context):
    """
    Call out to the pick_environment core hook to determine which environment we should load
    based on the current context. The Shotgun engine provides its own implementation.

    :param engine_name: system name of the engine to look for, e.g tk-maya
    :param tk: :class:`~sgtk.Sgtk` instance
    :param context: :class:`~sgtk.Context` object to use when picking environment
    :returns: name of environment.
    """

    try:
        env_name = tk.execute_core_hook(
            constants.PICK_ENVIRONMENT_CORE_HOOK_NAME, context=context
        )
    except Exception as e:
        raise TankEngineInitError(
            "Engine %s cannot initialize - the pick environment hook "
            "reported the following error: %s" % (engine_name, e)
        )

    if env_name is None:
        # the pick_environment hook could not determine an environment
        # this may be because an incomplete Context was passed.
        # without an environment, engine creation cannot succeed.
        # raise an exception with a message
        raise TankUnresolvedEnvironmentError(
            "Engine %s cannot initialize - the pick environment hook was not "
            "able to return an environment to use, given the context %s. "
            "Usually this is because the context contains insufficient information "
            "for an environment to be determined." % (engine_name, context)
        )

    return env_name


def _get_command_prefix(properties):
    """
    If multiple commands are registered with the same name, attempt to construct a unique
    prefix from other information in the command's properties dictionary to distinguish one
    command from another. Uses the properties' ``app`` and/or ``group`` keys to create the
    prefix.

    :param dict properties: Arbitrary key/value information related to a registered command.
    :returns: A unique identifier for the command as a str.
    """
    prefix_parts = []
    if properties.get("app"):
        # First, distinguish commands by app name.
        prefix_parts.append(properties["app"].instance_name)
    if properties.get("group"):
        # Second, distinguish commands by group name.
        prefix_parts.append(properties["group"])
    return ":".join(prefix_parts)
