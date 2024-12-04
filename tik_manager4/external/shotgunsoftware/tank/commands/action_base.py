# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from ..errors import TankError


class Action(object):
    """
    Describes an executable action. Base class that all tank command actions derive from.

    The execution payload should be defined in the run_* methods, which will be called
    by the system, either via a tank command or via an API accessor.

    The action runs in an operational state controlled by the mode parameter.
    At the point when one of the run_* method are called by the system, certain member
    variables are guaranteed to have been populated, depending on the *mode*.

    Action.GLOBAL
    -------------
    No state is set up. Basically, you don't even have access to a tk interface at this point.
    Commands that run in this state are commands that handle things that happen outside a project.
    Examples are project setup and upgrading the core api.

    Action.TK_INSTANCE
    ------------------
    A TK API instance exists. This implicitly means that a pipeline configuration also exists.
    An executing action can access the associated tk instance via the self.tk member variable.
    This is the most common state in which toolkit commands run. Examples include all commands
    which operate on a project (install_app, updates, validation, cloning, etc).

    Action.CTX
    ----------
    A TK API instance exists and a context has been established. Your command can access the
    member variables self.tk and self.context. An example of an Action / tank command that
    uses this mode is the folder creation and folder preview commands.

    Action.ENGINE
    -------------
    A TK API instance exists, a context has been established and an engine has been started.
    The engine can be accessed via self.engine. An example of a command running using this level
    is the Action brigde which connects App commands with tank commands; this is how app commands
    are executed when you run the inside the Shell engine.
    """

    GLOBAL, TK_INSTANCE, CTX, ENGINE = range(4)

    def __init__(self, name, mode, description, category):
        self.name = name
        self.mode = mode
        self.description = description
        self.category = category

        self._interaction_interface = None
        self._terminate_requested = False

        # set this property to False if your command doesn't support tank command access
        self.supports_tank_command = True

        # set this property to True if your command supports API access
        self.supports_api = False

        # when using the API mode, need to specify the parameters
        # this should be a dictionary on the form
        #
        # { "parameter_name": { "description": "Parameter info",
        #                    "default": None,
        #                    "type": "str" },
        #
        #  ...
        #
        #  "return_value": { "description": "Return value (optional)",
        #                   "type": "str" }
        # }
        #
        self.parameters = {}

        # special flag for commands that run in multiple contexts where an engine
        # is optional, but beneficial. This is so that the system can determine
        # whether it is worth starting the engine or not.
        self.wants_running_shell_engine = False
        if self.mode == Action.ENGINE:
            self.wants_running_shell_engine = True

        # these need to be filled in by calling code prior to execution
        self.tk = None
        self.context = None
        self.engine = None

    def __repr__(self):
        mode_str = "UNKNOWN"
        if self.mode == Action.GLOBAL:
            mode_str = "GLOBAL"
        elif self.mode == Action.TK_INSTANCE:
            mode_str = "TK_INSTANCE"
        elif self.mode == Action.CTX:
            mode_str = "CTX"
        elif self.mode == Action.ENGINE:
            mode_str = "ENGINE"

        return "<Action Cmd: '%s' Category: '%s' MODE:%s>" % (
            self.name,
            self.category,
            mode_str,
        )

    def __str__(self):
        return "Command %s (Category %s)" % (self.name, self.category)

    def _validate_parameters(self, parameters):
        """
        Helper method typically executed inside run_noninteractive.
        validate the given parameters dict based on the self.parameters definition.

        { "parameter_name": { "description": "Parameter info",
                            "default": None,
                            "type": "str" },

         ...

         "return_value": { "description": "Return value (optional)",
                           "type": "str" }
        }

        :returns: A dictionary which is a full and validated list of parameters, keyed by parameter name.
                  Values not supplied by the user will have default values instead.
        """
        new_param_values = {}

        # pass 1 - first get both user supplied and default values
        # into target dictionary
        for name in self.parameters:

            if name == "return_value":
                continue

            if name in parameters:
                # get param from input data
                new_param_values[name] = parameters[name]

            elif "default" in self.parameters[name]:
                # no user defined value, but a default value
                # use default value from param def
                new_param_values[name] = self.parameters[name]["default"]

        # pass 2 - make sure all params are defined
        for name in self.parameters:

            if name == "return_value":
                continue

            if name not in new_param_values:
                raise TankError(
                    "Cannot execute %s - parameter '%s' not specified!" % (self, name)
                )

        # pass 3 - check types of all params.
        for name in new_param_values:
            val = new_param_values[name]
            val_type = val.__class__.__name__
            req_type = self.parameters[name].get("type")
            if val is not None and val_type != req_type:
                raise TankError(
                    "Cannot execute %s - parameter '%s' not of required type %s"
                    % (self, name, req_type)
                )

        return new_param_values

    def set_interaction_interface(self, interaction_interface):
        """
        Specifies the interface to be used to request values
        and ask the user questions. This needs to be set
        before the run methods can be executed.

        :param interaction_interface: Interaction interface. An
            instance deriving from :class:`CommandInteraction`.
        """
        self._interaction_interface = interaction_interface

    def terminate(self):
        """
        Requests that the current command should be terminated.
        Please note that not all commands are able to terminate.
        """
        self._terminate_requested = True

    def run_interactive(self, log, args):
        """
        Run this API in interactive mode.
        This mode may prompt the user for input via stdin.

        :param log: Logger to use.
        :param args: list of strings forming additional arguments
            to be passed to the command.
        """
        raise NotImplementedError

    def run_noninteractive(self, log, parameters):
        """
        Run command in non-interactive (API) mode.

        Needs to be implemented if the supports_api property is set to True.

        :param log: Logger to use.
        :param parameters: dictionary of parameters to pass to this command.
            the dictionary key is the name of the parameter and the value
            is the value you want to pass. You can query which parameters
            can be passed in via the parameters property.
        :returns: Whatever the command specifies
        """
        raise NotImplementedError
