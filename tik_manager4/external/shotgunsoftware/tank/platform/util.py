# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import logging

from .import_stack import ImportStack
from ..errors import TankError
from .errors import TankContextChangeNotSupportedError, TankCurrentModuleNotFoundError
from .engine import current_engine, _restart_engine
from ..log import LogManager


def _get_current_bundle():
    """
    The current import bundle is set by bundle.import_module() and
    and is a way to defuse the chicken/egg situation which happens
    when trying to do an import_framework inside a module that is being
    loaded by import_module. The crux is that the module._tank_bundle reference
    that import_module() sets is constructed at the end of the call,
    meaning that the frameworks import cannot find this during the import
    this variable is the fallback in this case and it contains a reference
    to the current bundle.

    :returns: :class:`Application`, :class:`Engine` or :class:`Framework` instance
    """

    import sys

    current_bundle = ImportStack.get_current_bundle()
    if not current_bundle:
        # try to figure out the associated bundle using module trickery,
        # looking for the module which called this command and looking for
        # a ._tank_module property on the module object.

        try:
            # get the caller's stack frame
            caller = sys._getframe(2)
            # get the package name from the caller
            # for example: 0b3d7089471e42a998027fa668adfbe4.tk_multi_about.environment_browser
            calling_name_str = caller.f_globals["__name__"]
            # now the module imported by Bundle.import_module is
            # 0b3d7089471e42a998027fa668adfbe4.tk_multi_about
            # e.g. always the two first items in the name
            chunks = calling_name_str.split(".")
            calling_package_str = "%s.%s" % (chunks[0], chunks[1])
            # get the caller's module from sys.modules
            parent_module = sys.modules[calling_package_str]
        except Exception:
            raise TankCurrentModuleNotFoundError(
                "import_framework could not determine the calling module layout! "
                "You can only use this method on items imported using the import_module() "
                "method!"
            )

        # ok we got our module
        try:
            current_bundle = parent_module._tank_bundle
        except Exception:
            raise TankCurrentModuleNotFoundError(
                "import_framework could not access current app/engine on calling module %s. "
                "You can only use this method on items imported using the import_module() "
                "method!" % parent_module
            )

    return current_bundle


def change_context(new_context):
    """
    Running change_context will attempt to change the context the engine and
    its apps are running in on the fly. The current engine must accept the
    context change, otherwise a full restart of the engine will be run instead.

    The determination of whether an engine supports context changing comes from
    its "context_change_allowed" property. If that property returns True, then
    the context change will be allowed to proceed. If it returns False, then
    the engine's "change_context" method will raise
    :class:`TankContextChangeNotSupportedError`, which will then trigger a restart of
    the engine and all of its apps.

    In the event that the engine does support context changes, any apps that
    support context changing will do so, as well. Any that do not will themselves
    be restarted within the new context.

    The benefit of supporting context changes in engines and apps is speed. The
    end result of this routine should be identical to that of a restart, but
    will require less time to complete.

    For more information on supporting context changing, see the following:

    - :meth:`Engine.context_change_allowed`
    - :meth:`Application.context_change_allowed`
    - :meth:`change_context`
    - :meth:`Application.change_context`

    :param new_context: The new Context to change to.
    :type new_context: :class:`~sgtk.Context`
    """
    engine = current_engine()

    if engine is None:
        raise TankError("No engine is currently running! Run start_engine instead.")

    try:
        engine.log_debug("Changing context to %r." % new_context)

        engine.change_context(new_context)
        engine.log_debug("Context changed successfully.")
    except TankContextChangeNotSupportedError:
        engine.log_debug("Context change not allowed by engine, restarting instead.")
        restart(new_context)


def restart(new_context=None):
    """
    Restarts the currently running Toolkit platform. This includes reloading all
    configuration files as well as reloading the code for all apps and engines.
    (The Core API, however, is not reloaded). The call does not take any parameters
    and does not return any value.

    Any open windows will remain open and will use the old code base and settings.
    In order to access any changes that have happened as part of a reload, you need
    to start up new app windows (typically done via the Shotgun menu) and these will
    use the fresh code and configs.

    :param new_context: The new Context to start the engine in, if desired. Default behavior
                        is to restart the engine with its current context.
    :type new_context: :class:`~sgtk.Context`
    """
    engine = current_engine()

    if engine is None:
        raise TankError("No engine is currently running! Run start_engine instead.")

    try:
        # first, reload the template defs
        engine.tank.reload_templates()
        engine.log_debug("Template definitions were reloaded.")
    except TankError as e:
        engine.log_error(e)

    _restart_engine(new_context or engine.context)

    engine.log_info("Toolkit platform was restarted.")


def current_bundle():
    """
    Returns the bundle (app, engine or framework) instance for the
    app that the calling code is associated with. This is a special method, designed to
    be used inside python modules that belong to apps, engines or frameworks.

    The calling code needs to have been imported using toolkit's standard import
    mechanism, :meth:`Application.import_module()`, otherwise an exception will be raised.

    This special helper method can be useful when code deep inside an app needs
    to reach out to for example grab a configuration value. Then you can simply do::

        app = sgtk.platform.current_bundle()
        app.get_setting("frame_range")

    :returns: :class:`Application`, :class:`Engine` or :class:`Framework` instance
    """
    return _get_current_bundle()


def get_framework(framework):
    """
    Convenience method that returns a framework instance given a framework name.

    This is a special method, designed to
    be used inside python modules that belong to apps, engines or frameworks.

    The calling code needs to have been imported using toolkit's standard import
    mechanism, import_module(), otherwise an exception will be raised.

    For example, if your app code requires the tk-framework-helpers framework, and you
    need to retrieve a configuration setting from this framework, then you can
    simply do::

        fw = sgtk.platform.get_framework("tk-framework-helpers")
        fw.get_setting("frame_range")

    :param framework: name of the framework object to access, as defined in the app's
                      info.yml manifest.
    :returns: framework instance
    :type: :class:`Framework`
    """

    current_bundle = _get_current_bundle()

    if framework not in current_bundle.frameworks:
        raise Exception(
            "import_framework: %s does not have a framework %s associated!"
            % (current_bundle, framework)
        )

    fw = current_bundle.frameworks[framework]

    return fw


def import_framework(framework, module):
    """
    Convenience method for using frameworks code inside of apps, engines and other frameworks.

    This method is intended to replace an import statement.
    Instead of typing::

        from . import foo_bar

    You use the following syntax to load a framework module::

        foo_bar = tank.platform.import_framework("tk-framework-mystuff", "foo_bar")

    This is a special method, designed to
    be used inside python modules that belong to apps, engines or frameworks.

    The calling code needs to have been imported using toolkit's standard import
    mechanism, :meth:`Bundle.import_module()`, otherwise an exception will be raised.

    :param framework: name of the framework object to access, as defined in the app's
                      info.yml manifest.
    :param module: module to load from framework
    """

    current_bundle = _get_current_bundle()

    if framework not in current_bundle.frameworks:
        raise Exception(
            "import_framework: %s does not have a framework %s associated!"
            % (current_bundle, framework)
        )

    fw = current_bundle.frameworks[framework]

    mod = fw.import_module(module)

    return mod


def get_logger(module_name):
    """
    Standard sgtk logging access for python code that runs inside apps.

    We recommend that you use this method for all logging that takes place
    inside of the ``python`` folder inside your app, engine or framework.

    We recommend that the following pattern is used - at the top of your
    python files, include the following code::

        import sgtk
        logger = sgtk.platform.get_logger(__name__)

    All subsequent code in the file then simply calls this object for logging.

    Following this pattern will generate a standard logger that is parented
    under the correct bundle.

    :param module_name: Pass ``__name__`` to this parameter
    :return: Standard python logger
    """
    try:
        curr_bundle = _get_current_bundle()
        full_log_path = "%s.%s" % (curr_bundle.logger.name, module_name)
        return logging.getLogger(full_log_path)
    except TankCurrentModuleNotFoundError:
        return LogManager.get_logger("no_current_bundle.%s" % (module_name,))
