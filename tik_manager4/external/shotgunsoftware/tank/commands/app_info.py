# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from .action_base import Action
from ..errors import TankError


class AppInfoAction(Action):
    """
    Action that gives a breakdown of all engines and apps in an environment
    """

    def __init__(self):
        Action.__init__(
            self,
            "app_info",
            Action.TK_INSTANCE,
            "Shows a breakdown of your installed apps.",
            "Developer",
        )

        # this method can be executed via the API
        self.supports_api = True

    def run_noninteractive(self, log, parameters):
        """
        Tank command API accessor.
        Called when someone runs a tank command through the core API.

        This command takes no parameters, so an empty dictionary
        should be passed. The parameters argument is there because
        we are deriving from the Action base class which requires
        this parameter to be present.

        :param log: std python logger
        :param parameters: dictionary with tank command parameters
        """
        return self._run(log)

    def run_interactive(self, log, args):
        """
        Tank command accessor

        :param log: std python logger
        :param args: command line args
        """
        if len(args) != 0:
            raise TankError("This command takes no arguments!")

        return self._run(log)

    def _run(self, log):
        """
        Actual execution payload
        """

        log.info("This command lists details about Apps and Engines")
        log.info("--------------------------------------------------")
        log.info("")
        log.info("Your current configuration is located here:")
        log.info(self.tk.pipeline_configuration.get_path())

        log.info("")
        log.info("This command will list all apps in all environments.")
        log.info("The following environments exist:")
        for env_name in self.tk.pipeline_configuration.get_environments():
            log.info(" - %s" % env_name)
        log.info("")
        log.info("")

        for env_name in self.tk.pipeline_configuration.get_environments():
            self._env_breakdown(log, env_name)

        log.info("")
        log.info("")
        log.info("")
        log.info("- To install a new app, use the command tank install_app")
        log.info("- To switch an app location, use the command tank switch")
        log.info("")

    def _env_breakdown(self, log, env_name):

        log.info("")
        log.info("")
        log.info("=" * 70)
        log.info("Environment: %s" % env_name)

        env = self.tk.pipeline_configuration.get_environment(env_name)

        log.info("Location:    %s" % env.disk_location)
        log.info("Description: %s" % env.description)

        log.info("=" * 70)
        for eng in env.get_engines():
            log.info("")
            log.info("-" * 70)
            log.info("Engine %s" % eng)
            log.info("-" * 70)
            log.info("")
            for app in env.get_apps(eng):
                descriptor = env.get_app_descriptor(eng, app)
                log.info("App %s" % app)
                log.info("-" * (4 + len(app)))
                for (k, v) in descriptor.get_dict().items():
                    log.info(" %s: %s" % (k.capitalize(), v))
                log.info(" Docs: %s" % descriptor.documentation_url)
                log.info("")

        log.info("")
        log.info("")
