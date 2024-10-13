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
Defines the base class for all Tank Apps.

"""

import os
import sys

from ..util.loader import load_plugin
from . import constants

from .bundle import TankBundle
from ..util.metrics import EventMetric


class Application(TankBundle):
    """
    Base class for all Applications (Apps) running in Toolkit.
    """

    def __init__(self, engine, descriptor, settings, instance_name, env):
        """
        Application instances are constructed by the toolkit launch process
        and various factory methods such as :meth:`start_engine`.

        :param engine: The engine instance to connect this app to
        :param app_name: The short name of this app (e.g. tk-nukepublish)
        :param settings: a settings dictionary for this app
        """
        self.__engine = engine
        self.__instance_name = instance_name

        # create logger for this app
        # log will be parented in a sgtk.env.environment_name.engine_instance_name.app_instance_name hierarchy
        logger = self.__engine.get_child_logger(self.__instance_name)

        # init base class
        TankBundle.__init__(
            self, engine.tank, engine.context, settings, descriptor, env, logger
        )

        self.log_debug("App init: Instantiating %s" % self)

        # now if a folder named python is defined in the app, add it to the pythonpath
        app_path = os.path.dirname(sys.modules[self.__module__].__file__)
        python_path = os.path.join(app_path, constants.BUNDLE_PYTHON_FOLDER)
        if os.path.exists(python_path):
            # only append to python path if __init__.py does not exist
            # if __init__ exists, we should use the special tank import instead
            init_path = os.path.join(python_path, "__init__.py")
            if not os.path.exists(init_path):
                self.log_debug("Appending to PYTHONPATH: %s" % python_path)
                sys.path.append(python_path)

    def __repr__(self):
        return "<Sgtk App 0x%08x: %s, engine: %s>" % (id(self), self.name, self.engine)

    def _destroy_frameworks(self):
        """
        Called on destroy, prior to calling destroy_app
        """
        for fw in self.frameworks.values():
            # don't destroy shared frameworks
            # the engine is responsible for this
            if not fw.is_shared:
                fw._destroy_framework()

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
            self.tank.shotgun.tk_user_agent_handler.set_current_app(
                self.name, self.version, self.engine.name, self.engine.version
            )
        except AttributeError:
            # looks like this sg instance for some reason does not have a
            # tk user agent handler associated.
            pass

        return self.tank.shotgun

    def _get_instance_name(self):
        """
        The name for this app instance.
        """
        return self.__instance_name

    def _set_instance_name(self, instance_name):
        """
        Sets the instance name of the app.
        """
        self.__instance_name = instance_name

    instance_name = property(_get_instance_name, _set_instance_name)

    @property
    def engine(self):
        """
        The engine that this app is connected to.
        """
        return self.__engine

    def get_metrics_properties(self):
        """
        Returns a dictionary with properties to use when emitting a metric event
        for this application in the current engine.

        The dictionary contains information about this application, about the
        current engine, and about the application hosting the engine. For each of
        them, a name and a version string are available::

            {
                'Host App': 'Maya',
                'Host App Version': '2017',
                'Engine': 'tk-maya',
                'Engine Version': 'v0.4.1',
                'App': 'tk-multi-about',
                'App Version': '1.2.3'
            }

        :returns: Dictionary with info per above.
        """
        properties = self.engine.get_metrics_properties()
        properties.update(
            {EventMetric.KEY_APP: self.name, EventMetric.KEY_APP_VERSION: self.version}
        )
        return properties

    ##########################################################################################
    # init, destroy, and context changing

    def init_app(self):
        """
        Implemented by deriving classes in order to initialize the app
        Called by the engine as it loads the app.
        """
        pass

    def post_engine_init(self):
        """
        Implemented by deriving classes in order to run code after the engine
        has completely finished initializing itself and all its apps.
        At this point, the engine has a fully populated apps dictionary and
        all loaded apps have been fully initialized and validated.
        """
        pass

    def destroy_app(self):
        """
        Implemented by deriving classes in order to tear down the app
        Called by the engine as it is being destroyed.
        """
        pass

    ##########################################################################################
    # event handling

    def event_engine(self, event):
        """
        Called when the parent engine emits an event. This method
        is intended to be overridden by deriving classes in order to
        implement event-specific behavior.

        .. note:: This method is called for all engine event types. If
                  overriding this method to implement an event handler
                  in a specific app, the event object received will need
                  to be checked via isinstance (or via its event_type
                  property) to know what event has been triggered. As
                  there are also type specific event handlers available,
                  it is considered best practice to use those in all
                  cases except those where a generic handler is absolutely
                  required.

        .. warning:: It is possible that events will be triggered quite
                     frequently. It is important to keep performance in
                     mind when writing an event handler.

        :param event:   The event object that was emitted.
        :type event:    :class:`~sgtk.platform.events.EngineEvent`
        """
        pass

    def event_file_open(self, event):
        """
        Called when the parent engine emits a file-open event. This method
        is intended to be overridden by deriving classes.

        .. warning:: It is possible that events will be triggered quite
                     frequently. It is important to keep performance in
                     mind when writing an event handler.

        :param event:   The event object that was emitted.
        :type event:    :class:`~sgtk.platform.events.FileOpenEvent`
        """
        pass

    def event_file_close(self, event):
        """
        Called when the parent engine emits a file-close event. This method
        is intended to be overridden by deriving classes.

        .. warning:: It is possible that events will be triggered quite
                     frequently. It is important to keep performance in
                     mind when writing an event handler.

        :param event:   The event object that was emitted.
        :type event:    :class:`~sgtk.platform.events.FileCloseEvent`
        """
        pass

    ##########################################################################################
    # logging methods

    def log_debug(self, msg):
        """
        Logs a debug message.

        .. deprecated:: 0.18
            Use :meth:`Engine.logger` instead.

        :param msg: Message to log.
        """
        self.logger.debug(msg)

    def log_info(self, msg):
        """
        Logs an info message.

        .. deprecated:: 0.18
            Use :meth:`Engine.logger` instead.

        :param msg: Message to log.
        """
        self.logger.info(msg)

    def log_warning(self, msg):
        """
        Logs an warning message.

        .. deprecated:: 0.18
            Use :meth:`Engine.logger` instead.

        :param msg: Message to log.
        """
        self.logger.warning(msg)

    def log_error(self, msg):
        """
        Logs an error message.

        .. deprecated:: 0.18
            Use :meth:`Engine.logger` instead.

        :param msg: Message to log.
        """
        self.logger.error(msg)

    def log_exception(self, msg):
        """
        Logs an exception message.

        .. deprecated:: 0.18
            Use :meth:`Engine.logger` instead.

        :param msg: Message to log.
        """
        self.logger.exception(msg)


def get_application(engine, app_folder, descriptor, settings, instance_name, env):
    """
    Internal helper method.
    (Removed from the engine base class to make it easier to run unit tests).
    Returns an application object given an engine and app settings.

    :param engine: the engine this app should run in
    :param app_folder: the folder on disk where the app is located
    :param descriptor: descriptor for the app
    :param settings: a settings dict to pass to the app
    """
    plugin_file = os.path.join(app_folder, constants.APP_FILE)

    # Instantiate the app
    class_obj = load_plugin(plugin_file, Application)
    obj = class_obj(engine, descriptor, settings, instance_name, env)
    return obj
