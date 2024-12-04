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
Base class for Abstract classes for Engines, Apps and Frameworks

"""

import os
import sys
import imp
import uuid

from .. import hook
from ..util import sgre as re
from ..util.metrics import EventMetric
from ..log import LogManager
from ..errors import TankError, TankNoDefaultValueError
from .errors import TankContextChangeNotSupportedError
from . import constants
from .import_stack import ImportStack
from tank_vendor import six

core_logger = LogManager.get_logger(__name__)


class TankBundle(object):
    """
    Abstract Base class for any engine, framework app etc in tank
    """

    def __init__(self, tk, context, settings, descriptor, env, log):
        """
        Constructor.

        :param tk: :class:`~sgtk.Sgtk` instance
        :param context: A context object to define the context on disk where the engine is operating
        :type context: :class:`~sgtk.Context`
        :param settings: dictionary of settings to associate with this object
        :param descriptor: Descriptor pointing at associated code.
        :param env: An Environment object to associate with this bundle.
        :param log: A python logger to associate with this bundle
        """
        self.__tk = tk
        self.__context = context
        self.__settings = settings
        self.__sg = None
        self.__cache_location = {}
        self.__module_uid = None
        self.__descriptor = descriptor
        self.__frameworks = {}
        self.__environment = env
        self.__log = log

        # emit an engine started event
        tk.execute_core_hook(constants.TANK_BUNDLE_INIT_HOOK_NAME, bundle=self)

    ##########################################################################################
    # internal API

    def log_metric(self, action, log_version=False, log_once=False, command_name=None):
        """
        Log metrics for this bundle and the given action.

        :param str action: Action string to log, e.g. 'Opened Workfile'.
        :param log_version: Deprecated and ignored, but kept for backward compatibility.
        :param bool log_once: ``True`` if this metric should be ignored if it
            has already been logged. Defaults to ``False``.
        :param str command_name: A Toolkit command name to add to the metric properties.

        Internal Use Only - We provide no guarantees that this method
        will be backwards compatible.
        """
        properties = {}
        if command_name:
            properties[EventMetric.KEY_COMMAND] = command_name

        EventMetric.log(
            EventMetric.GROUP_TOOLKIT,
            action,
            properties=properties,
            log_once=log_once,
            bundle=self,
        )

    ##########################################################################################
    # properties used by internal classes, not part of the public interface

    @property
    def descriptor(self):
        """
        Internal method - not part of Tank's public interface.
        This method may be changed or even removed at some point in the future.
        We leave no guarantees that it will remain unchanged over time, so
        do not use in any app code.
        """
        return self.__descriptor

    @property
    def settings(self):
        """
        Internal method - not part of Tank's public interface.
        This method may be changed or even removed at some point in the future.
        We leave no guarantees that it will remain unchanged over time, so
        do not use in any app code.
        """
        return self.__settings

    ##########################################################################################
    # methods used by internal classes, not part of the public interface

    def get_setting_from(self, other_settings, key, default=None):
        """
        Internal method - not part of Tank's public interface.

        Get a value from the settings dictionary passed in
        using the logic from this application

        :param other_settings: dictionary to use to find setting
        :param key: setting name
        :param default: default value to return
        """
        return self.__resolve_setting_value(other_settings, key, default)

    def get_template_from(self, other_settings, key):
        """
        Internal method - not part of Tank's public interface.

        A shortcut for looking up which template is referenced in the given setting from
        the settings dictionary passed in.  It then calls get_template_by_name() on it.

        :param other_settings: dictionary to use to find setting
        :param key: setting name
        """
        template_name = self.get_setting_from(other_settings, key)
        return self.get_template_by_name(template_name)

    ##########################################################################################
    # properties

    @property
    def name(self):
        """
        The short name for the item (e.g. tk-maya)

        :returns: name as string
        """
        return self.__descriptor.system_name

    @property
    def display_name(self):
        """
        The display name for the item (e.g. Maya Engine)

        :returns: display name as string
        """
        return self.__descriptor.display_name

    @property
    def description(self):
        """
        A short description of the item

        :returns: string
        """
        return self.__descriptor.description

    @property
    def version(self):
        """
        The version of the item (e.g. 'v0.2.3')

        :returns: string representing the version
        """
        return self.__descriptor.version

    @property
    def icon_256(self):
        """
        Path to a 256x256 pixel png file which describes the item
        """
        return self.__descriptor.icon_256

    @property
    def style_constants(self):
        """
        Returns a dictionary of style constants. These can be used to build
        UIs using standard colors and other style components. All keys returned
        in this dictionary can also be used inside a style.qss that lives
        at the root level of the app, engine or framework. Use a
        ``{{DOUBLE_BACKET}}`` syntax in the stylesheet file, for example::

            QWidget
            {
                color: {{SG_FOREGROUND_COLOR}};
            }

        This property returns the values for all constants, for example::

            {
              "SG_HIGHLIGHT_COLOR": "#18A7E3",
              "SG_ALERT_COLOR": "#FC6246",
              "SG_FOREGROUND_COLOR": "#C8C8C8"
            }

        :returns: Dictionary. See above for example
        """
        return constants.SG_STYLESHEET_CONSTANTS

    @property
    def documentation_url(self):
        """
        Return the relevant documentation url for this item.

        :returns: url string, None if no documentation was found
        """
        return self.__descriptor.documentation_url

    @property
    def support_url(self):
        """
        Return the relevant support url for this item.

        :returns: url string, None if no documentation was found
        """
        return self.__descriptor.support_url

    @property
    def disk_location(self):
        """
        The folder on disk where this item is located.
        This can be useful if you want to write app code
        to retrieve a local resource::

            app_font = os.path.join(self.disk_location, "resources", "font.fnt")
        """
        # note: the reason we don't call __file__ directly is because
        #       we don't want to return the location of the 'bundle.py'
        #       base class but rather the location of object that
        #       has been derived from this class.
        path_to_this_file = os.path.abspath(sys.modules[self.__module__].__file__)
        return os.path.dirname(path_to_this_file)

    @property
    def cache_location(self):
        """
        An item-specific location on disk where the app or engine can store
        random cache data. This location is guaranteed to exist on disk.

        This location is configurable via the ``cache_location`` hook.
        It typically points at a path in the local filesystem, e.g on a mac::

            ~/Library/Caches/Shotgun/SITENAME/PROJECT_ID/BUNDLE_NAME

        This can be used to store cache data that the app wants to reuse across
        sessions::

            stored_query_data_path = os.path.join(self.cache_location, "query.dat")
        """
        project_id = self.__tk.pipeline_configuration.get_project_id()
        return self.get_project_cache_location(project_id)

    @property
    def site_cache_location(self):
        """
        A site location on disk where the app or engine can store
        random cache data. This location is guaranteed to exist on disk.

        This location is configurable via the ``cache_location`` hook.
        It typically points at a path in the local filesystem, e.g on a mac::

            ~/Library/Caches/Shotgun/SITENAME/BUNDLE_NAME

        This can be used to store cache data that the app wants to reuse across
        sessions and can be shared across a site::

            stored_query_data_path = os.path.join(self.site_cache_location, "query.dat")
        """
        # this method is memoized for performance since it is being called a lot!
        if self.__cache_location.get("site") is None:

            self.__cache_location["site"] = self.__tk.execute_core_hook_method(
                constants.CACHE_LOCATION_HOOK_NAME,
                "get_bundle_data_cache_path",
                project_id=None,
                plugin_id=None,
                pipeline_configuration_id=None,
                bundle=self,
            )

        return self.__cache_location["site"]

    @property
    def context(self):
        """
        The context associated with this item.

        :returns: :class:`~sgtk.Context`
        """
        return self.__context

    @property
    def context_change_allowed(self):
        """
        Whether a context change is allowed without the need for a restart.
        If a bundle supports on-the-fly context changing, this property should
        be overridden in the deriving class and forced to return True.

        :returns: bool
        """
        return False

    @property
    def tank(self):
        """
        Returns the Toolkit API instance associated with this item

        :returns: :class:`~sgtk.Tank`
        """
        return self.__tk

    # new name compatibility
    sgtk = tank

    @property
    def frameworks(self):
        """
        List of all frameworks associated with this item

        :returns: List of framework objects
        """
        return self.__frameworks

    @property
    def logger(self):
        """
        Standard python :class:`~logging.Logger` for this engine, app or framework.

        Use this whenever you want to emit or process
        log messages. If you are developing an app,
        engine or framework, call this method for generic logging.

        .. note:: Inside the ``python`` area of your app, engine or framework,
                  we recommend that you use :meth:`sgtk.platform.get_logger`
                  for your logging.

        Logging will be dispatched to a logger parented under the
        main toolkit logging namespace::

            # pattern
            sgtk.env.environment_name.engine_instance_name

            # for example
            sgtk.env.asset.tk-maya

        .. note:: If you want all log messages that you are emitting in your
                  app, engine or framework to be written to a log file or
                  to a logging console, you can attach a std log handler here.
        """
        return self.__log

    ##########################################################################################
    # public methods

    def change_context(self, new_context):
        """
        Abstract method for context changing.

        Implemented by deriving classes that wish to support context changes and
        require specific logic to do so safely.

        :param new_context: The context being changed to.
        :type context: :class:`~sgtk.Context`
        """
        if not self.context_change_allowed:
            self.log_debug("Bundle %r does not allow context changes." % self)
            raise TankContextChangeNotSupportedError()

    def pre_context_change(self, old_context, new_context):
        """
        Called before a context change.

        Implemented by deriving classes.

        :param old_context:     The context being changed away from.
        :type old_context: :class:`~sgtk.Context`
        :param new_context:     The context being changed to.
        :type new_context: :class:`~sgtk.Context`
        """
        pass

    def post_context_change(self, old_context, new_context):
        """
        Called after a context change.

        Implemented by deriving classes.

        :param old_context:     The context being changed away from.
        :type old_context: :class:`~sgtk.Context`
        :param new_context:     The context being changed to.
        :type new_context: :class:`~sgtk.Context`
        """
        pass

    def import_module(self, module_name):
        r"""
        Special import command for Toolkit bundles. Imports the python folder inside
        an app and returns the specified module name that exists inside the python folder.

        Each Toolkit App or Engine can have a python folder which contains additional
        code. In order to ensure that Toolkit can run multiple versions of the same app,
        as well as being able to reload app code if it changes, it is recommended that
        this method is used whenever you want to access code in the python location.

        For example, imagine you had the following structure::

            tk-multi-mybundle
               |- app.py or engine.py or framework.py
               |- info.yml
               \- python
                   |- __init__.py   <--- Needs to contain 'from . import tk_multi_mybundle'
                   \- tk_multi_mybundle

        The above structure is a standard Toolkit app outline. ``app.py`` is a
        light weight wrapper and the python module
        ``tk_multi_myapp`` module contains the actual code payload.
        In order to import this in a Toolkit friendly way, you need to run
        the following when you want to load the payload module inside of app.py::

            module_obj = self.import_module("tk_multi_myapp")

        """
        # local import to avoid cycles

        # first, set the module we are currently processing
        ImportStack.push_current_bundle(self)

        try:

            # get the python folder
            python_folder = os.path.join(
                self.disk_location, constants.BUNDLE_PYTHON_FOLDER
            )
            if not os.path.exists(python_folder):
                raise TankError(
                    "Cannot import - folder %s does not exist!" % python_folder
                )

            # and import
            if self.__module_uid is None:
                self.log_debug("Importing python modules in %s..." % python_folder)
                # alias the python folder with a UID to ensure it is unique every time it is imported
                self.__module_uid = "tkimp%s" % uuid.uuid4().hex
                imp.load_module(
                    self.__module_uid, None, python_folder, ("", "", imp.PKG_DIRECTORY)
                )

            # we can now find our actual module in sys.modules as GUID.module_name
            mod_name = "%s.%s" % (self.__module_uid, module_name)
            if mod_name not in sys.modules:
                raise TankError(
                    "Cannot find module %s as part of %s!"
                    % (module_name, python_folder)
                )

            # lastly, append our own object to the added module. This is to make it easier to
            # do elegant imports in the class scope via the tank.platform.import_framework method
            sys.modules[mod_name]._tank_bundle = self

        finally:
            # no longer processing this one
            ImportStack.pop_current_bundle()

        return sys.modules[mod_name]

    def get_project_cache_location(self, project_id):
        """
        Gets the bundle's cache-location path for the given project id.

        :param project_id:  The project Entity id number.
        :type project_id:   int

        :returns:           Cache location directory path.
        :rtype str:
        """
        # this method is memoized for performance since it is being called a lot!
        if self.__cache_location.get(project_id) is None:

            self.__cache_location[project_id] = self.__tk.execute_core_hook_method(
                constants.CACHE_LOCATION_HOOK_NAME,
                "get_bundle_data_cache_path",
                project_id=project_id,
                plugin_id=self.__tk.pipeline_configuration.get_plugin_id(),
                pipeline_configuration_id=self.__tk.pipeline_configuration.get_shotgun_id(),
                bundle=self,
            )

        return self.__cache_location[project_id]

    def get_setting(self, key, default=None):
        """
        Get a value from the item's settings::

            >>> app.get_setting('entity_types')
            ['Sequence', 'Shot', 'Asset', 'Task']

        :param key: config name
        :param default: default value to return
        :returns: Value from the environment configuration
        """
        return self.__resolve_setting_value(self.__settings, key, default)

    def get_template(self, key):
        """
        Returns a template object for a particular template setting in the Framework configuration.
        This method will look at the app configuration, determine which template is being referred to
        in the setting, go into the main platform Template API and fetch that particular template object.

        This is a convenience method. Shorthand for ``self.sgtk.templates[ self.get_setting(key) ]``.

        :param key: Setting to retrieve template for
        :returns: :class:`~Template` object
        """
        template_name = self.get_setting(key)
        return self.get_template_by_name(template_name)

    def get_template_by_name(self, template_name):
        """
        Note: This is for advanced use cases - Most of the time you should probably use
        :meth:`get_template()`. Find a particular template, the way it is named in the master
        config file ``templates.yml``. This method will access the master templates file
        directly and pull out a specifically named template without using the app config.
        Note that using this method may result in code which is less portable across
        studios, since it makes assumptions about how templates are named and defined in
        the master config. Generally speaking, it is often better to access templates using
        the app configuration and the get_template() method.

        This is a convenience method. Shorthand for ``self.sgtk.templates[template_name]``.

        :param template_name
        :returns: :class:`~Template` object
        """
        return self.tank.templates.get(template_name)

    def execute_hook(self, key, base_class=None, **kwargs):
        """
        Execute a hook that is part of the environment configuration for the current bundle.

        Convenience method that calls :meth:`execute_hook_method()` with the
        method_name parameter set to "execute".

        .. warning:: This method is present for backwards compatibility. For
                     all new hooks, we recommend using :meth:`execute_hook_method`
                     instead.

        You simply pass the name of the hook setting that you want to execute and
        the accompanying arguments, and toolkit will find the correct hook file based
        on the currently configured setting and then execute the execute() method for
        that hook.

        An optional ``base_class`` can be provided to override the default :class:`~sgtk.Hook`
        base class. This is useful for bundles that want to define and document a strict
        interface for hooks. The classes defined in the hook have to derived from this classes.

        .. note:: For more information about hooks, see :class:`~sgtk.Hook`

        :param key: The name of the hook setting you want to execute.
        :param base_class: A python class to use as the base class for the created
            hook. This will override the default hook base class, ``Hook``.
        :returns: The return value from the hook
        """
        hook_name = self.get_setting(key)
        resolved_hook_paths = self.__resolve_hook_expression(key, hook_name)
        return hook.execute_hook_method(
            resolved_hook_paths, self, None, base_class=base_class, **kwargs
        )

    def execute_hook_method(self, key, method_name, base_class=None, **kwargs):
        """
        Execute a specific method in a hook that is part of the
        environment configuration for the current bundle.

        You simply pass the name of the hook setting that you want to execute, the
        name of the method you want to execute and the accompanying arguments.
        Toolkit will find the correct hook file based on the currently configured
        setting and then execute the specified method.

        Hooks form a flexible way to extend and make toolkit apps or engines configurable.
        A hook acts like a setting in that it needs to be configured as part of the app's
        configuration, but instead of being a simple value, it is a code snippet contained
        inside a class.

        Apps typically provide default hooks to make installation and overriding easy.
        Each hook is represented by a setting, similar to the ones you access via
        the :meth:`get_setting()` method, however instead of retrieving a fixed value,
        you execute code which generates a value.

        This method will execute a specific method for a given hook setting. Toolkit will
        find the actual python hook file and handle initialization and execution for you,
        by looking at the configuration settings and resolve a path based on this.

        Arguments should always be passed in by name. This is to make it easy to add new
        parameters without breaking backwards compatibility, for example
        ``execute_hook_method("validator", "pre_check", name=curr_scene, version=curr_ver).``

        An optional ``base_class`` can be provided to override the default :class:`~sgtk.Hook`
        base class. This is useful for bundles that want to define and document a strict
        interface for hooks. The classes defined in the hook have to derived from this classes.

        .. note:: For more information about hooks, see :class:`~sgtk.Hook`

        :param key: The name of the hook setting you want to execute.
        :param method_name: Name of the method to execute
        :param base_class: A python class to use as the base class for the created
            hook. This will override the default hook base class, ``Hook``.
        :returns: The return value from the hook
        """
        hook_name = self.get_setting(key)
        resolved_hook_paths = self.__resolve_hook_expression(key, hook_name)
        return hook.execute_hook_method(
            resolved_hook_paths, self, method_name, base_class=base_class, **kwargs
        )

    def execute_hook_expression(
        self, hook_expression, method_name, base_class=None, **kwargs
    ):
        """
        Execute an arbitrary hook via an expression. While the methods execute_hook
        and execute_hook_method allows you to execute a particular hook setting as
        specified in the app configuration manifest, this methods allows you to
        execute a hook directly by passing a hook expression, for example
        ``{config}/path/to/my_hook.py``

        This is useful if you are doing rapid app development and don't necessarily
        want to expose a hook as a configuration setting just yet. It is also useful
        if you have app settings that are nested deep inside of lists or dictionaries.
        In that case, you cannot use execute_hook, but instead will have to retrieve
        the value specifically and then run it.

        An optional ``base_class`` can be provided to override the default :class:`~sgtk.Hook`
        base class. This is useful for bundles that want to define and document a strict
        interface for hooks. The classes defined in the hook have to derived from this classes.

        .. note:: For more information about hooks, see :class:`~sgtk.Hook`

        :param hook_expression: Path to hook to execute. See above for syntax details.
        :param method_name: Method inside the hook to execute.
        :param base_class: A python class to use as the base class for the created
            hook. This will override the default hook base class, ``Hook``.
        :returns: The return value from the hook
        """
        resolved_hook_paths = self.__resolve_hook_expression(None, hook_expression)
        return hook.execute_hook_method(
            resolved_hook_paths, self, method_name, base_class=base_class, **kwargs
        )

    def execute_hook_by_name(self, hook_name, **kwargs):
        """
        Execute an arbitrary hook located in the hooks folder for this project.
        The hook_name is the name of the python file in which the hook resides,
        without the file extension.

        In most use cases, the execute_hook method is the preferred way to
        access a hook from an app.

        .. warning:: Now deprecated - Please use :meth:`execute_hook_expression`
                  instead.

        This method is typically only used when you want to execute an arbitrary
        list of hooks, for example if you want to run a series of arbitrary
        user defined pre-publish validation hooks.

        .. note:: For more information about hooks, see :class:`~sgtk.Hook`

        :param hook_name: name of the legacy hook file to execute.
        """
        hook_folder = self.tank.pipeline_configuration.get_hooks_location()
        hook_path = os.path.join(hook_folder, "%s.py" % hook_name)
        return hook.execute_hook(hook_path, self, **kwargs)

    def create_hook_instance(self, hook_expression, base_class=None):
        """
        Returns the instance of a hook object given an expression.

        This is useful for complex workflows where it is beneficial to
        maintain a handle to a hook instance. Normally, hooks are stateless
        and every time a hook is called, a new instance is returned. This method
        provides a standardized way to retrieve an instance of a hook::

            self._plugin = app_object.create_hook_instance("{config}/path/to/my_hook.py")
            self._plugin.execute_method_x()
            self._plugin.execute_method_y()
            self._plugin.execute_method_z()

        The hook expression is the raw value that is specified in the configuration file.
        If you want to access a configuration setting instead (like how for example
        :meth:`execute_hook_method` works), simply call :meth:`get_setting()` to retrieve
        the value and then pass the settings value to this method.

        .. note:: For more information about hook syntax, see :class:`~sgtk.Hook`

        An optional ``base_class`` can be provided to override the default :class:`~sgtk.Hook`
        base class. This is useful for bundles that create hook instances at
        execution time and wish to provide default implementation without the need
        to configure the base hook. The supplied class must inherit from Hook.

        :param hook_expression: Path to hook to execute. See above for syntax details.
        :param base_class: A python class to use as the base class for the created
            hook. This will override the default hook base class, ``Hook``.
        :returns: :class:`Hook` instance.
        """
        resolved_hook_paths = self.__resolve_hook_expression(None, hook_expression)
        return hook.create_hook_instance(
            resolved_hook_paths, self, base_class=base_class
        )

    def ensure_folder_exists(self, path):
        """
        Make sure that the given folder exists on disk.
        Convenience method to make it easy for apps and engines to create folders in a
        standardized fashion. While the creation of high level folder structure such as
        Shot and Asset folders is typically handled by the folder creation system in
        Toolkit, Apps tend to need to create leaf-level folders such as publish folders
        and work areas. These are often created just in time of the operation.

        .. note:: This method calls out to the ``ensure_folder_exists`` core hook, making
                  the I/O operation user configurable. We recommend using this method
                  over the methods provided in ``sgtk.util.filesystem``.

        :param path: path to create
        """
        try:
            self.__tk.execute_core_hook(
                "ensure_folder_exists", path=path, bundle_obj=self
            )
        except Exception as e:
            raise TankError("Error creating folder %s: %s" % (path, e))

    def get_metrics_properties(self):
        """
        Should be re-implemented in deriving classes and return a dictionary with
        the properties needed to log a metric event for this bundle.

        :raises: NotImplementedError
        """
        raise NotImplementedError

    ##########################################################################################
    # internal helpers

    def _set_context(self, new_context):
        """
        Sets the current context associated with this item.

        :param new_context: The new context to associate with the bundle.
        """
        self.__context = new_context

    def _set_settings(self, settings):
        """
        Sets the bundle's internal settings dictionary.

        :param settings:    The new settings dict to store.
        """
        self.__settings = settings

    def __resolve_hook_path(self, settings_name, hook_expression):
        """
        Resolves a hook settings path into an absolute path.

        :param settings_name: The name of the hook setting in the configuration. If the
                              hook expression passed in to this method is not directly
                              associated with a configuration setting, for example if it
                              comes from a nested settings structure and is resolved via
                              execute_hook_by_name, this parameter will be None.

        :param hook_expression: The hook expression value that should be resolved.

        :returns: A full path to a hook file.
        """

        if hook_expression is None:
            raise TankError(
                "%s config setting %s: Configuration value cannot be None!"
                % (self, settings_name)
            )

        path = None

        # make sure to replace the `{engine_name}` token if it exists.
        if constants.TANK_HOOK_ENGINE_REFERENCE_TOKEN in hook_expression:
            engine_name = self._get_engine_name()
            if not engine_name:
                raise TankError(
                    "No engine could be determined for hook expression '%s'. "
                    "The hook could not be resolved." % (hook_expression,)
                )
            else:
                hook_expression = hook_expression.replace(
                    constants.TANK_HOOK_ENGINE_REFERENCE_TOKEN, engine_name
                )

        # first the legacy, old-style hooks case
        if hook_expression == constants.TANK_BUNDLE_DEFAULT_HOOK_SETTING:
            # hook settings points to the default one.
            # find the name of the hook from the manifest

            manifest = self.__descriptor.configuration_schema
            engine_name = self._get_engine_name()

            # Entries are on the following form
            #
            # hook_publish_file:
            #    type: hook
            #    description: Called when a file is published, e.g. copied from a work area to a publish area.
            #    default_value: maya_publish_file
            #
            resolved_hook_name = resolve_default_value(
                manifest.get(settings_name), engine_name=engine_name
            )

            # get the full path for the resolved hook name:
            if resolved_hook_name.startswith("{self}"):
                # new format hook:
                #  default_value: '{self}/my_hook.py'
                hooks_folder = os.path.join(self.disk_location, "hooks")
                path = resolved_hook_name.replace("{self}", hooks_folder)
                path = path.replace("/", os.path.sep)
            else:
                # old style hook:
                #  default_value: 'my_hook'
                path = os.path.join(
                    self.disk_location, "hooks", "%s.py" % resolved_hook_name
                )

            # if the hook uses the engine name then output a more useful error message if a hook for
            # the engine can't be found.
            if engine_name and not os.path.exists(path):
                # produce user friendly error message
                raise TankError(
                    "%s config setting %s: This hook is using an engine specific "
                    "hook setup (e.g '%s') but no hook '%s' has been provided with the app. "
                    "In order for this app to work with engine %s, you need to provide a "
                    "custom hook implementation. Please contact support for more "
                    "information"
                    % (self, settings_name, resolved_hook_name, path, engine_name)
                )

        elif hook_expression.startswith("{self}"):
            # bundle local reference
            hooks_folder = os.path.join(self.disk_location, "hooks")
            path = hook_expression.replace("{self}", hooks_folder)
            path = path.replace("/", os.path.sep)

        elif hook_expression.startswith("{config}"):
            # config hook
            hooks_folder = self.tank.pipeline_configuration.get_hooks_location()
            path = hook_expression.replace("{config}", hooks_folder)
            path = path.replace("/", os.path.sep)

        elif hook_expression.startswith("{engine}"):
            # look for the hook in the currently running engine
            try:
                engine = self.engine
            except AttributeError:
                raise TankError(
                    "%s config setting %s: Could not determine the current "
                    "engine. Unable to resolve hook path for: '%s'"
                    % (self, settings_name, hook_expression)
                )

            hooks_folder = os.path.join(engine.disk_location, "hooks")
            path = hook_expression.replace("{engine}", hooks_folder)
            path = path.replace("/", os.path.sep)

        elif hook_expression.startswith("{$") and "}" in hook_expression:
            # environment variable: {$HOOK_PATH}/path/to/foo.py
            env_var = re.match(r"^\{\$([^\}]+)\}", hook_expression).group(1)
            if env_var not in os.environ:
                raise TankError(
                    "%s config setting %s: This hook is referring to the configuration value '%s', "
                    "but no environment variable named '%s' can be "
                    "found!" % (self, settings_name, hook_expression, env_var)
                )
            env_var_value = os.environ[env_var]
            path = hook_expression.replace("{$%s}" % env_var, env_var_value)
            path = path.replace("/", os.path.sep)

        elif hook_expression.startswith("{") and "}" in hook_expression:
            # bundle instance (e.g. '{tk-framework-perforce_v1.x.x}/foo/bar.py' )
            # first find the bundle instance
            instance = re.match(r"^\{([^\}]+)\}", hook_expression).group(1)
            # for now, only look at framework instance names. Later on,
            # if the request ever comes up, we could consider extending
            # to supporting app instances etc. However we would need to
            # have some implicit rules for handling ambiguity since
            # there can be multiple items (engines, apps etc) potentially
            # having the same instance name.
            fw_instances = self.__environment.get_frameworks()
            if instance not in fw_instances:
                raise TankError(
                    "%s config setting %s: This hook is referring to the configuration value '%s', "
                    "but no framework with instance name '%s' can be found in the currently "
                    "running environment. The currently loaded frameworks "
                    "are %s."
                    % (
                        self,
                        settings_name,
                        hook_expression,
                        instance,
                        ", ".join(fw_instances),
                    )
                )

            fw_desc = self.__environment.get_framework_descriptor(instance)
            if not (fw_desc.exists_local()):
                raise TankError(
                    "%s config setting %s: This hook is referring to the configuration value '%s', "
                    "but the framework with instance name '%s' does not exist on disk. Please run "
                    "the tank cache_apps command."
                    % (self, settings_name, hook_expression, instance)
                )

            # get path to framework on disk
            hooks_folder = os.path.join(fw_desc.get_path(), "hooks")
            # create the path to the file
            path = hook_expression.replace("{%s}" % instance, hooks_folder)
            path = path.replace("/", os.path.sep)

        else:
            # old school config hook name, e.g. just 'foo'
            hook_folder = self.tank.pipeline_configuration.get_hooks_location()
            path = os.path.join(hook_folder, "%s.py" % hook_expression)

        return path

    def __resolve_hook_expression(self, settings_name, hook_expression):
        """
        Internal method for resolving hook expressions. This method handles
        resolving an environment configuration value into a path on disk.

        There are two generations of hook formats - old-style and new-style.

        Old style formats:

        - hook_setting: foo     -- Resolves 'foo' to CURRENT_PC/hooks/foo.py
        - hook_setting: default -- Resolves the value from the info.yml manifest and uses
          the default hook code supplied by the bundle.

        New style formats:

        - hook_setting: {$HOOK_PATH}/path/to/foo.py  -- environment variable.
        - hook_setting: {self}/path/to/foo.py   -- looks in the hooks folder in the local bundle
        - hook_setting: {config}/path/to/foo.py -- looks in the hooks folder in the config
        - hook_setting: {engine}/path/to/foo.py -- looks in the hooks folder of the current engine.
        - hook_setting: {tk-framework-perforce_v1.x.x}/path/to/foo.py -- looks in the hooks folder of a
          framework instance that exists in the current environment. Basically, each entry inside the
          frameworks section in the current environment can be specified here - all these entries are
          on the form frameworkname_versionpattern, for example tk-framework-widget_v0.1.2 or
          tk-framework-shotgunutils_v1.3.x.

        :param settings_name: If this hook is associated with a setting in the bundle, this is the
                              name of that setting. This is used to identify the inheritance relationships
                              between the hook expression that is evaluated and if this hook derives from
                              a hook inside an app.
        :param hook_expression: The path expression to a hook.
        :returns: List of paths to hooks files.
        """
        # split up the config value into distinct items
        unresolved_hook_paths = hook_expression.split(":")

        # first of all, see if we should add a base class hook to derive from:
        #
        # Basically, any overridden hook implicitly derives from the default hook.
        # specified in the manifest.
        # if the settings value is not {self} add this to the inheritance chain.
        # Examples:
        #
        # Manifest: {self}/foo_{engine_name}.py
        # In config: {config}/my_custom_hook.py
        # The my_custom_hook.py implicitly derives from the python class defined
        # in the manifest, so prepend it:
        # hook_paths: ["{self}/foo_tk-maya.py", "{config}/my_custom_hook.py" ]
        #
        # Check only new-style hooks. All new style hooks start with a {
        if unresolved_hook_paths[0].startswith("{") and not unresolved_hook_paths[
            0
        ].startswith("{self}"):
            # this is a new style hook that is not the default hook value.
            # now prepend the default hook first in the list
            manifest = self.__descriptor.configuration_schema

            default_value = None

            if settings_name:
                default_value = resolve_default_value(
                    manifest.get(settings_name), engine_name=self._get_engine_name()
                )

            if default_value:  # possible not to have a default value!

                # expand the default value to be referenced from {self} and with the .py suffix
                # for backwards compatibility with the old syntax where the default value could
                # just be 'hook_name' with implicit '{self}' and no suffix!
                if not default_value.startswith("{self}"):
                    default_value = "{self}/%s.py" % default_value

                # so now we have a path to a potential default hook inside the app or engine
                # There is however one possibility when there may not be a hook, and this is
                # when {engine_name} is defined as part of the default value, but no default hook
                # exists for the engine that we are currently running. In this case, we don't want
                # to wedge in this non-existing hook file into the inheritance chain because it does
                # not exist!
                full_path = self.__resolve_hook_path(settings_name, default_value)
                if os.path.exists(full_path):
                    # add to inheritance path
                    unresolved_hook_paths.insert(0, default_value)

        # resolve paths into actual file paths
        resolved_hook_paths = [
            self.__resolve_hook_path(settings_name, x) for x in unresolved_hook_paths
        ]

        core_logger.debug(
            "%s: Resolved hook expression (associated with setting '%s'): '%s' -> %s"
            % (self, settings_name, hook_expression, resolved_hook_paths)
        )

        return resolved_hook_paths

    def __resolve_setting_value(self, settings, key, default):
        """
        Resolve a setting value.  Exposed to allow values to be resolved for
        settings derived outside of the app.

        :param settings: the settings dictionary source
        :param key: setting name
        :param default: a default value to use for the setting
        """
        # An old use case exists whereby the key does not exist in the
        # config schema so we need to account for that.
        schema = self.__descriptor.configuration_schema.get(key, None)
        return resolve_setting_value(
            self.__tk, self._get_engine_name(), schema, settings, key, default, self
        )

    def _get_engine_name(self):
        """
        Returns the bundle's engine name if available. None otherwise.
        Convenience method to avoid try/except everywhere.

        :return: The engine name or None
        """
        # note - this technically violates the generic nature of the bundle
        # base class implementation because the engine member is not defined
        # in the bundle base class (only in App and Framework, not Engine) - an
        # engine trying to define a hook using the {engine_name} construct will
        # therefore get an error.
        try:
            engine_name = self.engine.name
        except:
            engine_name = None

        return engine_name


def _post_process_settings_r(tk, key, value, schema, bundle=None):
    """
    Recursive post-processing of settings values

    :param tk: Toolkit API instance
    :param key: setting name
    :param value: Input value to resolve using specified schema
    :param schema: A schema defining types and defaults for settings.
    :param bundle: The bundle object. This is only used in the case
        the value argument is a string starting with "hook:", which
        then requires the use of a core hook to resolve the setting.

    :returns: Processed value for key setting
    """
    settings_type = schema.get("type")

    # first check for procedural overrides where instead of getting a value,
    # directly from the config, we call a hook to evaluate a config value
    # at runtime:
    if isinstance(value, six.string_types) and value.startswith("hook:"):
        # handle the special form where the value is computed in a hook.
        #
        # if the template parameter is on the form
        # a) hook:foo_bar
        # b) hook:foo_bar:testing1:testing2
        #
        # The following hook will be called
        # a) core hook 'foo_bar' with parameters []
        # b) core hook 'foo_bar' with parameters ['testing1', 'testing2']
        #
        chunks = value.split(":")
        hook_name = chunks[1]
        params = chunks[2:]
        processed_val = tk.execute_core_hook(
            hook_name, setting=key, bundle_obj=bundle, extra_params=params
        )
        return processed_val

    # No procedural overrides in place - instead handle the value based on type
    if settings_type == "list":
        processed_val = []
        value_schema = schema["values"]
        for x in value:
            processed_val.append(
                _post_process_settings_r(
                    tk=tk, key=key, value=x, schema=value_schema, bundle=bundle
                )
            )

    elif settings_type == "dict":
        items = schema.get("items", {})
        # note - we assign the original values here because we
        processed_val = value
        for (key, value_schema) in items.items():
            processed_val[key] = _post_process_settings_r(
                tk=tk, key=key, value=value[key], schema=value_schema, bundle=bundle
            )

    elif settings_type == "config_path":
        # this is a config path. Stored on the form
        # foo/bar/baz.png, we should translate that into
        # PROJECT_PATH/tank/config/foo/bar/baz.png
        config_folder = tk.pipeline_configuration.get_config_location()
        adjusted_value = value.replace("/", os.path.sep)
        processed_val = os.path.join(config_folder, adjusted_value)

    else:
        # pass-through
        processed_val = value

    return processed_val


def resolve_setting_value(tk, engine_name, schema, settings, key, default, bundle=None):
    """
    Resolve a setting value.  Exposed to allow values to be resolved for
    settings derived outside of the app.

    :param tk: :class:`~sgtk.Sgtk` Toolkit API instance
    :param str engine_name: Name of Toolkit engine instance.
    :param dict schema: A schema defining types and defaults for settings.
                        The post processing code requires the schema to
                        introspect the settings' types, defaults, etc.
    :param dict settings: the settings dictionary source
    :param str key: setting name
    :param default: a default value to use for the setting
    :param bundle: The bundle object. This is only used in situations where
        a setting's value must be resolved via calling a hook.

    :returns: Resolved value of input setting key
    """
    # Get the value for the supplied key
    if key in settings:
        # Value provided by the settings
        value = settings[key]

    elif schema:
        # Resolve a default value from the schema. This checks various
        # legacy default value forms in the schema keys.
        value = resolve_default_value(schema, default, engine_name)

    else:
        # Nothing in the settings, no schema, fallback to the supplied
        # default value
        value = default

    # We have a value of some kind and a schema. Allow the post
    # processing code to further resolve the value.
    if value and schema:
        value = _post_process_settings_r(tk, key, value, schema, bundle)

    return value


def resolve_default_value(
    schema, default=None, engine_name=None, raise_if_missing=False
):
    """
    Extract a default value from the supplied schema.

    Fall back on the supplied default value if no default could be
    determined from the schema.

    :param schema: The schema for the setting default to resolve
    :param default: Optional fallback default value.
    :param engine_name: Optional name of the current engine if there is one.
    :param raise_if_missing: If True, raise TankNoDefaultValueError if no
        default value is found.
    :return: The resolved default value
    """
    default_missing = False

    # Engine-specific default value keys are allowed (ex:
    # "default_value_tk-maya"). If an engine name was supplied,
    # build the corresponding engine-specific default value key.
    engine_default_key = None
    if engine_name:
        engine_default_key = "%s_%s" % (
            constants.TANK_SCHEMA_DEFAULT_VALUE_KEY,
            engine_name,
        )

    # Now look for a default value to use.
    if engine_default_key and engine_default_key in schema:
        # An engine specific key exists, use it.
        value = schema[engine_default_key]
    elif constants.TANK_SCHEMA_DEFAULT_VALUE_KEY in schema:
        # The standard default value key
        value = schema[constants.TANK_SCHEMA_DEFAULT_VALUE_KEY]
    else:
        # No default value found, fall back on the supplied default.
        default_missing = True
        value = default

    # ---- type specific checks

    setting_type = schema.get("type")

    # special case handling for list params - check if
    # allows_empty is True, in that case set default value to []
    if setting_type == "list" and value is None and schema.get("allows_empty"):
        value = []

    # special case handling for dict params - check if
    # allows_empty is True, in that case set default value to {}
    if setting_type == "dict" and value is None and schema.get("allows_empty"):
        value = {}

    # special case for template params. if allows_empty is True, then we allow
    # a value of None. make sure we don't raise in the "raise_if_missing" case.
    if setting_type == "template" and value is None and schema.get("allows_empty"):
        value = None
        default_missing = False

    if setting_type == "hook":
        value = _resolve_default_hook_value(value, engine_name)

    if value is None and default_missing and raise_if_missing:
        # calling code requested an exception if no default value exists.
        # the value may have been overridden by one of the special cases above,
        # so only raise if the value is None.
        raise TankNoDefaultValueError("No default value found.")

    return value


def _resolve_default_hook_value(value, engine_name=None):
    """
    Given a hook value, evaluate any special keys or legacy values.

    :param value: The unresolved default value for the hook
    :param engine_name: The name of the engine for engine-specific hook values
    :return: The resolved hook default value.
    """

    if not value:
        return value

    # Replace the engine reference token if it exists and there is an engine.
    # In some instances, such as during engine startup, as apps are being
    # validated, the engine instance name may not be available. This might be ok
    # since hooks are actually evaluated just before they are executed. We'll
    # simply return the value with the engine name token intact.
    if engine_name and constants.TANK_HOOK_ENGINE_REFERENCE_TOKEN in value:
        value = value.replace(constants.TANK_HOOK_ENGINE_REFERENCE_TOKEN, engine_name)

    if not value.startswith("{"):
        # This is an old-style hook. In order to maintain backward
        #  compatibility, return the value in the new style.
        value = "{self}/%s.py" % (value,)

    # the remaining tokens ({self}, {config}, {tk-framework-...}) will be
    # resolved at runtime just before the hook is executed.
    return value
