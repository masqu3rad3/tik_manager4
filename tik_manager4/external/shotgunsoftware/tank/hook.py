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
Defines the base class for all Tank Hooks.
"""
import os
import sys
import logging
import inspect
import threading
from .util.loader import load_plugin
from . import LogManager
from .errors import (
    TankError,
    TankFileDoesNotExistError,
    TankHookMethodDoesNotExistError,
)

log = LogManager.get_logger(__name__)


class Hook(object):
    """
    Hooks are implemented in a python file and they all derive from a :class:`Hook` base class.

    If you are writing an app that loads files into Maya, Nuke or other DCCs, a hook is a good
    way to expose the actual loading logic, so that not only can be customized by a user, but
    so that you could even add support for a new DCC to your load app without having to update it.

    First, you would create a ``hooks/actions.py`` file in your app. This would contain a hook class::

        import sgtk
        HookBaseClass = sgtk.get_hook_baseclass()

        class Actions(HookBaseClass):

            def list_actions(self, sg_publish_data):
                '''
                Given some Shotgun publish data, return a list of
                actions that can be performed

                :param sg_publish_data: Dictionary of publish data from Shotgun
                :returns: List of action strings
                '''
                # The base implementation implements an action to show
                # the item in Shotgun
                return ["show_in_sg"]

            def run_action(self, action, sg_publish_data):
                '''
                Execute the given action

                :param action: name of action. One of the items returned by list_actions.
                :param sg_publish_data: Dictionary of publish data from Shotgun
                '''
                if action == "show_in_sg":

                    url = "%s/detail/%s/%d" % (
                        self.parent.shotgun.base_url,
                        sg_publish_data["type"],
                        sg_publish_data["id"]
                        )
                    QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))

    The above code forms a generic base for your hook with a basic implementation that works
    everywhere.

    In the app manifest (``info.yml``), where we define all the basic configuration properties for the app,
    we define an actions hook::

        configuration:

            actions_hook:
                type: hook
                default_value: "{self}/actions.py"
                description: Hook which contains all methods for action management.

    From the app code itself, you can now use :meth:`~sgtk.platform.Application.execute_hook_method()`
    to call out to the hook::

        # when creating a list of items in the UI for your app -
        # given a shotgun publish, build a menu of avaialable actions:
        actions = self.execute_hook_method("actions_hook", "list_actions", sg_data)

        # in a callback method once a user has selected an action -
        # call out to the hook to execute the action
        self.execute_hook_method("actions_hook", "run_action", action_name, sg_data)

    In the configuration for your app, you can now 'glue together' different functionality
    for different scenarios. For example, when you install the app to run inside the Maya
    engine, you want to be able to import maya files into maya. We implement this by adding a
    custom publish hook for maya. This can either be placed with the app itself, in the ``hooks``
    folder in the configuration, or in the maya engine. In this case, we'll add a ``hooks/actions.py``
    to the maya engine. This file looks like this::

        import sgtk
        HookBaseClass = sgtk.get_hook_baseclass()

        class MayaActions(HookBaseClass):

            def list_actions(self, sg_publish_data):
                '''
                Given some Shotgun publish data, return a list of
                actions that can be performed

                :param sg_publish_data: Dictionary of publish data from Shotgun
                :returns: List of action strings
                '''
                # first get base class actions
                actions = HookBaseClass.list_actions(sg_publish_data)

                # Add maya actions
                if sg_publish_data["published_file_type"]["name"] == "Maya Scene":
                    actions += ["reference", "import"]

            def run_action(self, action, sg_publish_data):
                '''
                Execute the given action

                :param action: name of action. One of the items returned by list_actions.
                :param sg_publish_data: Dictionary of publish data from Shotgun
                '''
                if action == "reference":
                    # do maya reference operation

                elif action == "import":
                    # do maya import operation

                else:
                    # pass on to base class
                    return HookBaseClass.run_action(action, sg_publish_data)

    The above hook implements a couple of actions that are designed to work in Maya.
    Lastly, we need to tell the app to pick up this file. In the environment configuration for the app
    running inside of maya, we point it at our engine specific hook::

        tk-maya:
            tk-multi-myapp:
                actions_hook: '{engine}/actions.py'

    When we are running the app configuration in maya, the actions hook will automatically
    resolve the hook code distributed with the maya engine. The base class will be automatically
    determined to be the default value set in the manifest, allowing for the app to carry a default
    base implementation that is always taken into account.

    .. _hook-formats:

    **Resolving paths to hooks**

    Several different path formats exist, making this a very powerful configuration mechanism:

    - ``{self}/path/to/foo.py`` -- looks in the ``hooks`` folder in the local app, engine of framework.

    - ``{self}/{engine_name}_publish.py`` -- If running in maya, looks for a ``tk-maya_publish.py`` in
      the ``hooks`` folder in the local app, engine of framework. If running in Nuke, it would instead
      look for ``BUNDLE_ROOT/hooks/tk-nuke_publish.py``.

    - ``{config}/path/to/foo.py`` -- Looks in the ``hooks`` folder in the configuration.

    - ``{$HOOK_PATH}/path/to/foo.py``  -- expression based around an environment variable.

    - ``{engine}/path/to/foo.py`` -- looks in the ``hooks`` folder of the current engine.

    - ``{tk-framework-perforce_v1.x.x}/path/to/foo.py`` -- looks in the ``hooks`` folder of a
      framework instance that exists in the current environment. Basically, each entry inside the
      frameworks section in the current environment can be specified here - all these entries are
      on the form frameworkname_versionpattern, for example ``tk-framework-widget_v0.1.2`` or
      ``tk-framework-shotgunutils_v1.3.x``.

    Supported legacy formats:

    - ``foo`` -- Equivalent to ``{config}/foo.py``

    You can also provide your own inheritance chains. For example, if you wanted to add your own,
    project specific maya hooks to this app, you could do this by creating a hook file, placing
    it in your configuration's ``hooks`` folder and then configure it like this::

        tk-maya:
            tk-multi-myapp:
                actions_hook: '{engine}/actions.py:{config}/maya_actions.py'

    This would execute your ``maya_actions.py`` hook and make sure that that hook inherits from the
    engine specific hook, making sure that you get both your custom actions, the engine default actions
    and the app's built-in actions.
    """

    # default method to execute on hooks
    DEFAULT_HOOK_METHOD = "execute"

    def __init__(self, parent):
        self.__parent = parent

    @property
    def sgtk(self):
        """
        The sgtk core API instance associated with the Hook parent.

        This is a convenience method for easy core API instance access.
        In the case of app, engine and framework hooks, this is equivalent
        to ``parent.sgtk`` and in the case of core hooks it simply returns
        ``parent``.

        .. note:: Some low level hooks do not have a parent defined. In
                  such cases, ``None`` is returned.
        """
        # local import to avoid cycles
        from .api import Sgtk

        if self.parent is None:
            # system hook
            return None
        if isinstance(self.parent, Sgtk):
            # core hook
            return self.parent
        else:
            # look for sgtk instance on parent
            try:
                return self.parent.sgtk
            except AttributeError:
                return None

    @property
    def tank(self):
        """
        The sgtk core API instance associated with the Hook parent.

        .. deprecated:: v0.18.70
           Use :meth:`sgtk` instead.
        """
        return self.sgtk

    @property
    def parent(self):
        """
        The parent object to the executing hook. This varies with the type of
        hook that is being executed. For a hook that runs inside an app or an engine,
        the parent object will be the :class:`~sgtk.platform.Application` or
        :class:`~sgtk.platform.Engine` instance. For core hooks, the
        parent object will be :class:`sgtk`.

        .. note:: If you need to access Shotgun inside your hook, you can do this by
                  calling ``self.parent.shotgun`` since both Apps, Engines and the Core API
                  has a ``shotgun`` property.
        """
        return self.__parent

    def get_publish_path(self, sg_publish_data):
        """
        Returns the path on disk for a publish entity in Shotgun.

        Convenience method that calls :meth:`sgtk.util.resolve_publish_path`.

        :param sg_publish_data: Dictionaries containing Shotgun publish data.
            Each dictionary needs to at least contain a code, type, id and a path key.

        :returns: A path on disk to existing file or file sequence.

        :raises: :class:`~sgtk.util.PublishPathNotDefinedError` if the path isn't defined.
        :raises: :class:`~sgtk.util.PublishPathNotSupported` if the path cannot be resolved.
        """
        # avoid cyclic refs
        from .util import resolve_publish_path

        return resolve_publish_path(self.sgtk, sg_publish_data)

    def get_publish_paths(self, sg_publish_data_list):
        """
        Returns several local paths on disk given a
        list of shotgun data dictionaries representing publishes.

        Convenience method that calls :meth:`sgtk.util.resolve_publish_path`.

        .. deprecated:: 0.18.64
           Use :meth:`get_publish_path` instead.

        :param sg_publish_data_list: List of shotgun data dictionaries
                                     containing publish data. Each dictionary
                                     needs to at least contain a code, type,
                                     id and a path key.

        :returns: List of paths on disk to existing files or file sequences.

        :raises: :class:`~sgtk.util.PublishPathNotDefinedError` if any of the paths aren't defined.
        :raises: :class:`~sgtk.util.PublishPathNotSupported` if any of the paths cannot be resolved.
        """
        # avoid cyclic refs
        from .util import resolve_publish_path

        paths = []
        for sg_publish_data in sg_publish_data_list:
            paths.append(resolve_publish_path(self.sgtk, sg_publish_data))
        return paths

    @property
    def disk_location(self):
        """
        The folder on disk where this item is located.
        This can be useful if you want to write hook code
        to retrieve a local resource::

            hook_icon = os.path.join(self.disk_location, "icon.png")
        """
        # NOTE: this method contains complex logic to correctly handle
        # the following inheritance case:
        #
        # A. Hook base class >
        # B. general implementation (hook_b.py) >
        # C. custom implementation  (hook_c.py)
        #
        # in (B), there is a method which returns an icon:
        # return os.path.join(self.disk_location, "icon.png")
        #
        # in this case, we want the code in B to return a path
        # relative to hook_b.py.
        #
        # However, although intended to be primarily used
        # from within a hook, the disk_location is a public method.
        # Whenever called from an external location, the
        # disk location is computed to be relative to
        # the leaf inheritance, e.g. hook_c.py in this case.

        # in order to handle the case above, we look for the
        # caller. If the caller is part of the inheritance
        # chain, we simply compute the path relative to
        # the caller method.
        #
        # however if the caller is external, we compute the path
        # relative to self. Self represents the leaf in the
        # inheritance tree.
        #
        path_to_file = None

        current_frame = inspect.currentframe()
        all_frames = inspect.getouterframes(current_frame)
        parent_frame = all_frames[1]
        if "self" in parent_frame[0].f_locals:
            # the calling method is a class instance method
            path_to_calling_file = parent_frame[1]
            if parent_frame[0].f_locals["self"] is self:
                # this call is coming from within the
                # class hierarchy
                path_to_file = path_to_calling_file

        # first check failed. fall back on computing
        # the location relative to self
        if path_to_file is None:
            path_to_file = os.path.abspath(sys.modules[self.__module__].__file__)

        return os.path.dirname(path_to_file)

    @property
    def logger(self):
        """
        Standard python :class:`~logging.Logger` handle for this hook.

        The logger can be used to report
        progress back to the app in a standardized fashion
        and will be parented under the app/engine/framework logger::

            # pattern
            sgtk.env.environment_name.engine_name.app_name.hook.hook_file_name

            # for example
            sgtk.env.asset.tk-maya.tk-multi-loader2.hook.filter_publishes


        In the case of core hooks, the logger will be parented
        under ``sgtk.core.hook``. For more information, see :ref:`logging`

        """
        # see if the hook parent object exists and has a logger property
        # in that case make this the parent of our logger.
        #
        # note: core hooks have the tk instance as their parent and
        # app/engine/fw hooks have the bundle as their parent.
        # There are some special edge cases where we construct
        # parentless hooks: the PipelineConfigurationInit hook runs
        # before a tk instance exists and some of the older "studio
        # hooks" such as project_name.py and sg_connection.py also exists
        # with states where no parent can be defined easily.
        try:
            logger = self.parent.logger
        except AttributeError:
            # parent doesn't exist or doesn't have a logger.
            # in this case use the logger for this file as a
            # parent - e.g. 'sgtk.core.hook'
            log_prefix = log.name
        else:
            log_prefix = "%s.hook" % logger.name

        # name the logger after the name of the hook filename
        path_to_this_file = os.path.abspath(sys.modules[self.__module__].__file__)
        hook_name = os.path.splitext(os.path.basename(path_to_this_file))[0]
        full_log_path = "%s.%s" % (log_prefix, hook_name)
        return logging.getLogger(full_log_path)

    def load_framework(self, framework_instance_name):
        """
        Loads and returns a framework given an environment instance name.

        .. note:: This method only works for hooks that are executed from apps and frameworks.

        If you have complex logic and functionality and want to manage (and version it) as part
        of a framework rather than in a hook, you can do this by calling a configured framework
        from inside a hook::

            import sgtk
            HookBaseClass = sgtk.get_hook_baseclass()

            class SomeHook(HookBaseClass):

                def some_method(self):

                    # first get a framework handle. This object is similar to an app or engine object
                    fw = self.load_framework("tk-framework-library_v1.x.x")

                    # now just like with an app or an engine, if you want to access code in the python
                    # folder, you can do import_plugin
                    module = fw.import_module("some_module")

                    module.do_stuff()


        Note how we are accessing the framework instance ``tk-framework-library_v1.x.x`` above.
        This needs to be defined in the currently running environment, as part of the ``frameworks`` section::

            engines:
              # all engine and app defs here...

            frameworks:
             # define the framework that we are using in the hook
             tk-framework-library_v1.x.x:
                location: {type: git, path: 'https://github.com/foo/tk-framework-library.git', version: v1.2.6}

        :param framework_instance_name: Name of the framework instance to load from the environment.
        """
        # avoid circular refs
        from .platform import framework

        try:
            engine = self.__parent.engine
        except:
            raise TankError(
                "Cannot load framework %s for %r - it does not have a "
                "valid engine property!" % (framework_instance_name, self.__parent)
            )

        return framework.load_framework(
            engine, engine.get_env(), framework_instance_name
        )

    def execute(self):
        """
        Legacy support for old style hooks
        """
        return None


class _HooksCache(object):
    """
    A thread-safe cache of loaded hooks.  This uses the hook file path
    and base class as the key to cache all hooks loaded by Toolkit in
    the current session.
    """

    def __init__(self):
        """
        Construction
        """
        self._cache = {}
        self._cache_lock = threading.Lock()

    def thread_exclusive(func):
        """
        function decorator to ensure multiple threads can't access the cache
        at the same time.

        :param func:    The function to wrap
        :returns:       The return value from func
        """

        def inner(self, *args, **kwargs):
            """
            Decorator inner function - executes the function within a lock.
            :returns:    The return value from func
            """
            lock = self._cache_lock
            lock.acquire()
            try:
                return func(self, *args, **kwargs)
            finally:
                lock.release()

        return inner

    @thread_exclusive
    def clear(self):
        """
        Clear the hook cache
        """
        self._cache = {}

    @thread_exclusive
    def find(self, hook_path, hook_base_class):
        """
        Find a hook in the cache using the hook path and base class

        :param hook_path:       The path to the hook to find
        :param hook_base_class: The base class for the hook to find
        :returns:               The Hook class if found, None if not
        """
        # The unique cache key is a tuple of the path and the base class to allow
        # loading of classes with different bases from the same file
        key = (hook_path, hook_base_class)
        return self._cache.get(key, None)

    @thread_exclusive
    def add(self, hook_path, hook_base_class, hook_class):
        """
        Add the specified hook to the cache if it isn't already present

        :param hook_path:       The path to the hook to add
        :param hook_base_class: The base class for the hook to add
        :param hook_class:      The Hook class to add
        """
        # The unique cache key is a tuple of the path and the base class to allow
        # loading of classes with different bases from the same file
        key = (hook_path, hook_base_class)
        if key not in self._cache:
            self._cache[key] = hook_class

    @thread_exclusive
    def __len__(self):
        """
        Return the number of items currently in the hook cache
        """
        return len(self._cache)


_hooks_cache = _HooksCache()
_current_hook_baseclass = threading.local()


def clear_hooks_cache():
    """
    Clears the cache where tank keeps hook classes
    """
    _hooks_cache.clear()


def execute_hook(hook_path, parent, **kwargs):
    """
    Executes a hook, old-school style.

    A hook is a python file which
    contains exactly one class which derives (at some point
    in its inheritance tree) from the Hook base class.

    Once the file has been loaded (and cached), the execute()
    method will be called and any optional arguments pass to
    this method will be forwarded on to that execute() method.

    :param hook_path: Full path to the hook python file
    :param parent: Parent object. This will be accessible inside
                   the hook as self.parent, and is typically an
                   app, engine or core object.
    :returns: Whatever the hook returns.
    """
    return execute_hook_method([hook_path], parent, None, **kwargs)


def execute_hook_method(hook_paths, parent, method_name, base_class=None, **kwargs):
    """
    New style hook execution, with method arguments and support for inheritance.

    This method takes a list of hook paths and will load each of the classes
    in, while maintaining the correct state of the class returned via
    get_hook_baseclass(). Once all classes have been successfully loaded,
    the last class in the list is instantiated and the specified method
    is executed.

        Example: ["/tmp/a.py", "/tmp/b.py", "/tmp/c.py"]

        1. The code in a.py is loaded in. get_hook_baseclass() will return Hook
           at this point. class HookA is returned from our plugin loader.

        2. /tmp/b.py is loaded in. get_hook_baseclass() now returns HookA, so
           if the hook code in B utilises get_hook_baseclass, this will will
           set up an inheritance relationship with A

        3. /tmp/c.py is finally loaded in, get_hook_baseclass() now returns HookB.

        4. HookC class is instantiated and method method_name is executed.

    An optional `base_class` can be provided to override the default ``Hook``
    base class. This is useful for bundles that wish to execute a hook method
    while providing a default implementation without the need to configure a
    base hook.

    :param hook_paths: List of full paths to hooks, in inheritance order.
    :param parent: Parent object. This will be accessible inside
                   the hook as self.parent, and is typically an
                   app, engine or core object.
    :param method_name: method to execute. If None, the default method will be executed.
    :param base_class: A python class to use as the base class for the hook
        class. This will override the default hook base class, ``Hook``. The
        class should derive from ``Hook``.
    :returns: Whatever the hook returns.
    """
    hook = create_hook_instance(hook_paths, parent, base_class=base_class)

    # get the method
    method_name = method_name or Hook.DEFAULT_HOOK_METHOD
    try:
        hook_method = getattr(hook, method_name)
    except AttributeError:
        raise TankHookMethodDoesNotExistError(
            "Cannot execute hook '%s' - the hook class does not have a '%s' "
            "method!" % (hook, method_name)
        )

    # execute the method
    ret_val = hook_method(**kwargs)

    return ret_val


def create_hook_instance(hook_paths, parent, base_class=None):
    """
    New style hook execution, with method arguments and support for inheritance.

    This method takes a list of hook paths and will load each of the classes
    in, while maintaining the correct state of the class returned via
    get_hook_baseclass(). Once all classes have been successfully loaded,
    an instance of the last class in the list is returned.

        Example: ["/tmp/a.py", "/tmp/b.py", "/tmp/c.py"]

        1. The code in a.py is loaded in. get_hook_baseclass() will return Hook
           at this point (or a custom base class, if supplied, that derives from
           Hook). class HookA is returned from our plugin loader.

        2. /tmp/b.py is loaded in. get_hook_baseclass() now returns HookA, so
           if the hook code in B utilises get_hook_baseclass, this will will
           set up an inheritance relationship with A

        3. /tmp/c.py is finally loaded in, get_hook_baseclass() now returns HookB.

        4. An instance of the HookC class is returned.

    An optional `base_class` can be provided to override the default ``Hook``
    base class. This is useful for bundles that create hook instances at
    execution time and wish to provide default implementation without the need
    to configure the base hook.

    :param hook_paths: List of full paths to hooks, in inheritance order.
    :param base_class: A python class to use as the base class for the created
        hook. This will override the default hook base class, ``Hook``.
    :returns: Instance of the hook.
    """

    if base_class:
        # ensure the supplied base class is a subclass of Hook
        if not issubclass(base_class, Hook):
            raise TankError(
                "Invalid custom hook base class. The supplied class '%s' does "
                "not inherit from Hook." % (Hook,)
            )
    else:
        base_class = Hook

    # keep track of the current base class - this is used when loading hooks to dynamically
    # inherit from the correct base.
    _current_hook_baseclass.value = base_class

    for hook_path in hook_paths:

        if not os.path.exists(hook_path):
            raise TankFileDoesNotExistError(
                "Cannot execute hook '%s' - this file does not exist on disk!"
                % hook_path
            )

        # look to see if we've already loaded this hook into the cache
        found_hook_class = _hooks_cache.find(hook_path, _current_hook_baseclass.value)
        if not found_hook_class:
            # load the hook class from the hook file and cache it - this explicitly looks for a
            # single class from the hook file that is derived from the current base (or 'Hook' for
            # backwards compatibility).

            # determine any alternate base classes to look for in addition to the current base:
            alternate_base_classes = []
            if _current_hook_baseclass.value != Hook:
                # allow deriving from the Hook base class - this is to support the legacy method of
                # overriding hooks but without sub-classing them.
                alternate_base_classes.append(Hook)

            # try to load the hook class:
            loaded_hook_class = load_plugin(
                hook_path,
                valid_base_class=_current_hook_baseclass.value,
                alternate_base_classes=alternate_base_classes,
            )

            # add it to the cache...
            _hooks_cache.add(
                hook_path, _current_hook_baseclass.value, loaded_hook_class
            )

            # ...and find it again - this is to avoid different threads ending up using
            # different instances of the loaded class.
            found_hook_class = _hooks_cache.find(
                hook_path, _current_hook_baseclass.value
            )

        # keep track of the current base class:
        _current_hook_baseclass.value = found_hook_class

    # all class construction done. _current_hook_baseclass contains the last
    # class we iterated over. An instance of this is what we want to return
    return _current_hook_baseclass.value(parent)


def get_hook_baseclass():
    """
    Returns the base class to use for the hook currently
    being loaded. For more details and examples, see the :class:`Hook` documentation.
    """
    return _current_hook_baseclass.value
