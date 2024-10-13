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
from .action_base import Action


class CopyAppsAction(Action):
    """
    Action for copying a set of apps from one engine to another
    """

    def __init__(self):
        Action.__init__(
            self,
            "copy_apps",
            Action.TK_INSTANCE,
            "Copies apps from one engine to another, overwriting any apps that already exist.",
            "Configuration",
        )

        # this method can be executed via the API
        self.supports_api = True

        # no tank command support for this one
        self.supports_tank_command = False

        self.parameters = {}

        self.parameters["environment"] = {
            "description": "Name of environment to install into.",
            "default": None,
            "type": "str",
        }
        self.parameters["src_engine_instance"] = {
            "description": "Name of the engine instance to copy apps from.",
            "default": None,
            "type": "str",
        }
        self.parameters["dst_engine_instance"] = {
            "description": "Name of the engine instance to write apps to.",
            "default": None,
            "type": "str",
        }

    def run_noninteractive(self, log, parameters):
        """
        Tank command API accessor.
        Called when someone runs a tank command through the core API.

        :param log: std python logger
        :param parameters: dictionary with tank command parameters
        """
        computed_params = self._validate_parameters(parameters)

        return self._run(
            log,
            computed_params["environment"],
            computed_params["src_engine_instance"],
            computed_params["dst_engine_instance"],
        )

    def run_interactive(self, log, args):
        """
        Tank command accessor

        :param log: std python logger
        :param args: command line args
        """

        if len(args) != 3:
            log.info(
                "Syntax: copy_apps environment src_engine_instance_name dst_engine_instance_name"
            )
            log.info("")
            log.info("> tank copy_apps project tk-shell tk-desktop")
            log.info("")
            raise TankError("Please specify all three arguments")

        env_name = args[0]
        src_engine_instance_name = args[1]
        dst_engine_instance_name = args[2]

        self._run(log, env_name, src_engine_instance_name, dst_engine_instance_name)

    def _run(self, log, env_name, src_engine_instance_name, dst_engine_instance_name):
        try:
            env = self.tk.pipeline_configuration.get_environment(
                env_name, writable=True
            )
        except Exception as e:
            raise TankError(
                "Environment '%s' could not be loaded! Error reported: %s"
                % (env_name, e)
            )

        if src_engine_instance_name not in env.get_engines():
            raise TankError(
                "Environment %s has no engine named %s!"
                % (env_name, src_engine_instance_name)
            )
        if dst_engine_instance_name not in env.get_engines():
            raise TankError(
                "Environment %s has no engine named %s!"
                % (env_name, dst_engine_instance_name)
            )

        env.copy_apps(src_engine_instance_name, dst_engine_instance_name)
