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
Methods for handling of the tank command

"""

import logging

from .action_base import Action
from .interaction import RawInputCommandInteraction, YesToEverythingInteraction
from . import folders
from . import misc
from . import move_pc
from . import pc_overview
from . import path_cache
from . import update
from . import push_pc
from . import setup_project
from . import setup_project_wizard
from . import dump_config
from . import validate_config
from . import cache_apps
from . import switch
from . import app_info
from . import core_upgrade
from . import core_localize
from . import install
from . import clone_configuration
from . import copy_apps
from . import unregister_folders
from . import desktop_migration
from . import cache_yaml
from . import get_entity_commands
from . import constants


from .. import constants as constants_global
from .. import LogManager
from ..platform.engine import start_engine, get_environment_from_context
from ..errors import TankError

log = LogManager.get_logger(__name__)


###############################################################################################
# Built in actions (all in the tank_commands sub module)

BUILT_IN_ACTIONS = [
    setup_project.SetupProjectAction,
    setup_project_wizard.SetupProjectFactoryAction,
    core_upgrade.CoreUpdateAction,
    core_localize.CoreLocalizeAction,
    core_localize.ShareCoreAction,
    core_localize.AttachToCoreAction,
    dump_config.DumpConfigAction,
    validate_config.ValidateConfigAction,
    cache_apps.CacheAppsAction,
    misc.ClearCacheAction,
    switch.SwitchAppAction,
    app_info.AppInfoAction,
    misc.InteractiveShellAction,
    install.InstallAppAction,
    push_pc.PushPCAction,
    install.InstallEngineAction,
    update.AppUpdatesAction,
    folders.CreateFoldersAction,
    folders.PreviewFoldersAction,
    move_pc.MovePCAction,
    pc_overview.PCBreakdownAction,
    path_cache.SynchronizePathCache,
    path_cache.PathCacheMigrationAction,
    unregister_folders.UnregisterFoldersAction,
    clone_configuration.CloneConfigAction,
    copy_apps.CopyAppsAction,
    desktop_migration.DesktopMigration,
    cache_yaml.CacheYamlAction,
    get_entity_commands.GetEntityCommandsAction,
]


def _get_built_in_actions():
    """
    Returns a list of built in actions
    """
    actions = []
    for ClassObj in BUILT_IN_ACTIONS:
        actions.append(ClassObj())
    return actions


###############################################################################################
# Shell engine tank commands - adapter for creating an action from an app


class ShellEngineAction(Action):
    """
    Action wrapper around a shell engine command
    """

    def __init__(self, name, description, command_key):
        Action.__init__(self, name, Action.ENGINE, description, "Shell Engine")
        self._command_key = command_key

    def run_interactive(self, log, args):
        self.engine.execute_command(self._command_key, args)


def get_shell_engine_actions(engine_obj):
    """
    Returns a list of shell engine actions
    """

    actions = []
    for c in engine_obj.commands:

        # custom properties dict
        props = engine_obj.commands[c]["properties"]

        # the properties dict contains some goodies here that we can use
        # look for a short_name, if that does not exist, fall back on the command name
        # prefix will hold a prefix that guarantees uniqueness, if needed
        cmd_name = c
        if "short_name" in props:
            if props["prefix"]:
                # need a prefix to produce a unique command
                cmd_name = "%s:%s" % (props["prefix"], props["short_name"])
            else:
                # unique without a prefix
                cmd_name = props["short_name"]

        description = engine_obj.commands[c]["properties"].get(
            "description", "No description available."
        )

        actions.append(ShellEngineAction(cmd_name, description, c))

    return actions


###############################################################################################
# Complete public API definitions for accessing toolkit commands
# ------------------------------------------------------------
# - The list_commands returns a list of available command names
# - The create_command factory returns a SgtkSystemCommand class instance
#   for a given command
# - The SgtkSystemCommand class wraps around a command implementation and
#   forms the actual interface which we expose via the interface.


def list_commands(tk=None):
    """
    Lists the system commands registered with the system.

    If you leave the optional tk parameter as None, a list of
    global commands will be returned. These commands can be executed
    at any point and do not require a project or a configuration to
    be present. Examples of such commands are the core upgrade
    check and the setup_project commands::

        >>> import sgtk
        >>> sgtk.list_commands()
        ['setup_project', 'core']

    If you do pass in a tk API handle (or alternatively use the
    convenience method :meth:`Sgtk.list_commands`), all commands which
    are available in the context of a project configuration will be returned.
    This includes for example commands for configuration management,
    anything app or engine related and validation and overview functionality.
    In addition to these commands, the global commands will also be returned::

        >>> import sgtk
        >>> tk = sgtk.sgtk_from_path("/studio/project_root")
        >>> tk.list_commands()
        ['setup_project', 'core', 'localize', 'validate', 'cache_apps', 'clear_cache',
         'app_info', 'install_app', 'install_engine', 'updates', 'configurations', 'clone_configuration']


    :param tk: Optional Toolkit API instance
    :type tk: :class:`Sgtk`
    :returns: list of command names
    """
    action_names = []
    for a in _get_built_in_actions():

        # check if this tank command has API support
        if a.supports_api:

            # if we don't have a tk API instance, we can only access GLOBAL commands
            if tk is None and a.mode != Action.GLOBAL:
                continue

            action_names.append(a.name)

    return action_names


def get_command(command_name, tk=None):
    """
    Returns an instance of a command object that can be used to execute a command.

    Once you have retrieved the command instance, you can perform introspection to
    check for example the required parameters for the command, name, description etc.
    Lastly, you can execute the command by running the execute() method.

    In order to get a list of the available commands, use the :meth:`list_commands` method.

    Certain commands require a project configuration context in order to operate. This
    needs to be passed on in the form of a toolkit API instance via the tk parameter.
    See the list_command() documentation for more details.

    :param command_name: Name of command to execute. Get a list of all available commands
                         using the :meth:`list_commands` method.
    :param tk: Optional Toolkit API instance
    :type tk: :class:`Sgtk`
    :returns: :class:`SgtkSystemCommand`
    """
    if command_name not in list_commands(tk):
        # not found
        raise TankError(
            "The command '%s' does not exist. Use the sgtk.list_commands() method to "
            "see a list of all commands available via the API." % command_name
        )

    for x in _get_built_in_actions():
        if x.name == command_name and x.supports_api:
            return SgtkSystemCommand(x, tk)


class SgtkSystemCommand(object):
    """
    Represents a toolkit system command.

    You can use this object to introspect command properties such as
    name, description, parameters etc. Execution is carried out by calling the :meth:`execute` method.

    For a global command which doesn't require an active configuration,
    execution typically looks like this::


        >>> import sgtk

        >>> sgtk.list_commands()
        ['setup_project', 'core']

        >>> cmd = sgtk.get_command("core")
        >>> cmd
        <tank.deploy.tank_command.SgtkSystemCommand object at 0x106d9f090>

        >>> cmd.execute({})

    """

    # this class wraps around a tank.deploy.tank_commands.action_base.Action class
    # and exposes the "official" interface for it.

    def __init__(self, internal_action_object, tk):
        """
        Instances should be constructed using the :meth:`get_command` factory method.
        """
        self.__internal_action_obj = internal_action_object

        # only commands of type GLOBAL, TK_INSTANCE are currently supported
        if self.__internal_action_obj.mode not in (Action.GLOBAL, Action.TK_INSTANCE):
            raise TankError(
                "The command %r is not of a type which is supported by Toolkit. "
                "Please contact support at %s."
                % (self.__internal_action_obj, constants_global.SUPPORT_URL)
            )

        # make sure we pass a tk api for actions that require it
        if self.__internal_action_obj.mode == Action.TK_INSTANCE and tk is None:
            raise TankError(
                "This command requires a Toolkit API instance to execute. Please "
                "provide this either as a parameter to the sgtk.get_command() method "
                "or alternatively execute the tk.get_command() method directly from "
                "a Toolkit API instance."
            )

        if tk:
            self.__internal_action_obj.tk = tk

        # set up a default logger which can be overridden via the set_logger method
        # for the default logger, use the standard toolkit logging standard based on __name__
        self.__log = log
        # make sure that we have exactly one handler
        if len(self.__log.handlers) == 0:
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            formatter = logging.Formatter("%(levelname)s %(message)s")
            ch.setFormatter(formatter)
            self.__log.addHandler(ch)

    @property
    def parameters(self):
        """
        The different parameters that needs to be specified and if a
        parameter has any default values. For example::

            { "parameter_name": { "description": "Parameter info",
                                "default": None,
                                "type": "str" },

             ...

             "return_value": { "description": "Return value (optional)",
                               "type": "str" }
            }
        """
        return self.__internal_action_obj.parameters

    @property
    def description(self):
        """
        A brief description of this command.
        """
        return self.__internal_action_obj.description

    @property
    def name(self):
        """
        The name of this command.
        """
        return self.__internal_action_obj.name

    @property
    def category(self):
        """
        The category for this command. This is typically a short string like "Admin".
        """
        return self.__internal_action_obj.category

    @property
    def logger(self):
        """
        The python :class:`~logging.Logger` associated with this tank command
        """
        return self.__log

    def set_logger(self, log):
        """
        Specify a standard python log instance to send logging output to.
        If this is not specify, the standard output mechanism will be used.

        .. warning:: We strongly recommend using the :meth:`logger` property
                     to retrieve the default logger for the tank command
                     and attaching a handler to this rather than passing in
                     an explicit log object via this method. This method
                     may be deprecated at some point in the future.

        :param log: Standard python logging instance
        """
        self.__log = log

    def execute(self, params, interaction_interface=None):
        """
        Execute this command.

        :param params: dictionary of parameters to pass to this command.
                       the dictionary key is the name of the parameter and the value
                       is the value you want to pass. You can query which parameters
                       can be passed in via the parameters property.
        :param interaction_interface: Optional interaction interface. This will be used
            whenever the command needs to interact with the user. Should be an
            instance deriving from :class:`CommandInteraction`.
        :returns: Whatever the command returns. Data type and description for the return
                  value can be introspected via the :meth:`parameters` property.
        """
        interaction_interface = interaction_interface or YesToEverythingInteraction()
        self.__internal_action_obj.set_interaction_interface(interaction_interface)

        return self.__internal_action_obj.run_noninteractive(self.__log, params)

    def terminate(self):
        """
        Instructs the command to attempt to terminate its execution.
        Not all commands are able to terminate and execution normally
        does not terminate straight away.
        """
        self.__internal_action_obj.terminate()


###############################################################################################
# Main entry points for accessing tank commands from the tank command / shell engine


def get_actions(log, tk, ctx):
    """
    Returns a list of Action objects given the current context, api etc.
    tk and ctx may be none, indicating that tank is running in a 'partial' state.
    """
    engine = None

    if tk is not None and ctx is not None:
        # we have all the necessary pieces needed to start an engine

        # check if there is an environment object for our context
        env = get_environment_from_context(tk, ctx)
        log.debug(
            "Probing for a shell engine. ctx '%s' --> environment '%s'" % (ctx, env)
        )
        if env and constants.SHELL_ENGINE in env.get_engines():
            log.debug(
                "Looks like the environment has a tk-shell engine. Trying to start it."
            )
            # we have an environment and a shell engine. Looking good.
            engine = start_engine(constants.SHELL_ENGINE, tk, ctx)
            log.debug("Started engine %s" % engine)
            log.info("- Started Shell Engine version %s" % engine.version)
            log.info("- Environment: %s." % engine.environment["disk_location"])

    actions = []

    # get all actions regardless of current scope first
    all_actions = _get_built_in_actions()
    if engine:
        all_actions.extend(get_shell_engine_actions(engine))

    # now only pick the ones that are working with our current state
    for a in all_actions:

        if not a.supports_tank_command:
            # this action does not support tank command mode
            continue

        if a.mode == Action.GLOBAL:
            # globals are always possible to run
            actions.append(a)
        if tk and a.mode == Action.TK_INSTANCE:
            # we have a PC!
            actions.append(a)
        if ctx and a.mode == Action.CTX:
            # we have a command that needs a context
            actions.append(a)
        if engine and a.mode == Action.ENGINE:
            # needs the engine
            actions.append(a)

    return (actions, engine)


def run_action(log, tk, ctx, command, args):
    """
    Find an action and start execution. This method is tightly coupled with the tank_cmd script.

    The command handles multiple states and contains logic for validating that the mode of the desired command
    is actually compatible with the state which is passed in.

    Because tank commands can run in environments with varying degrees of completeness (ranging from only
    knowing the code location to having a fully qualified context), some of the parameters deliberately overlap.

    :param log: Python logger to pass command output to
    :param tk: API instance to pass to command. For a state where no notion of a pipeline config/current project
               exists, this will be None.
    :param ctx: Context object. For a state where a current context is not known, this will be none.
    :param args: list of strings forming additional arguments to be passed to the command.

    """
    engine = None

    # first see if we can find the action without starting the engine
    found_action = None
    for x in _get_built_in_actions():
        if x.name == command:
            found_action = x
            break

    if found_action and found_action.wants_running_shell_engine == False:
        log.debug("No need to load up the engine for this command.")
    else:
        # try to load the engine.
        if tk is not None and ctx is not None:
            # we have all the necessary pieces needed to start an engine
            # check if there is an environment object for our context
            env = get_environment_from_context(tk, ctx)
            log.debug(
                "Probing for a shell engine. ctx '%s' --> environment '%s'" % (ctx, env)
            )
            if env and constants.SHELL_ENGINE in env.get_engines():
                log.debug(
                    "Looks like the environment has a tk-shell engine. Trying to start it."
                )
                # we have an environment and a shell engine. Looking good.
                engine = start_engine(constants.SHELL_ENGINE, tk, ctx)
                log.debug("Started engine %s" % engine)
                log.info("- Started Shell Engine version %s" % engine.version)
                log.info("- Environment: %s." % engine.environment["disk_location"])

                # now keep looking for our command
                if (
                    found_action is None
                ):  # may already be found (a core cmd which needs and engine)
                    for x in get_shell_engine_actions(engine):
                        if x.name == command:
                            found_action = x
                            break

    # ok we now have all the pieces we need
    if found_action is None:
        log.info("")
        log.info("")
        log.error("The action '%s' could not be found!" % command)
        log.info("")
        log.info(
            "In order to list all action that are available, try running the same command, "
            "but omit the '%s' part at the end." % command
        )
        log.info("")

    else:

        # seed the action object with all the handles it may need
        found_action.tk = tk
        found_action.context = ctx
        found_action.engine = engine

        # now check that we actually have passed enough stuff to work with this mode
        if (
            found_action.mode in (Action.TK_INSTANCE, Action.CTX, Action.ENGINE)
            and tk is None
        ):
            # we are missing a tk instance
            log.debug("Trying to launch %r without an Toolkit instance." % found_action)
            raise TankError(
                "The command '%s' needs a project to run. For example, if you want "
                "to run it for project XYZ, execute "
                "'tank Project XYZ %s'" % (found_action.name, found_action.name)
            )

        if found_action.mode in (Action.CTX, Action.ENGINE) and ctx is None:
            # we have a command that needs a context
            log.debug("Trying to launch %r without a context." % found_action)
            raise TankError(
                "The command '%s' needs a work area to run." % found_action.name
            )

        if found_action.mode == Action.ENGINE and engine is None:
            # we have a command that needs an engine
            log.debug("Trying to launch %r without an engine." % found_action)
            raise TankError(
                "The command '%s' needs the shell engine running." % found_action.name
            )

        # ok all good
        log.info("- Running command %s..." % found_action.name)
        log.info("")
        log.info("")
        log.info("-" * 70)
        log.info("Command: %s" % found_action.name.replace("_", " ").capitalize())
        log.info("-" * 70)
        log.info("")

        found_action.set_interaction_interface(RawInputCommandInteraction())

        return found_action.run_interactive(log, args)
