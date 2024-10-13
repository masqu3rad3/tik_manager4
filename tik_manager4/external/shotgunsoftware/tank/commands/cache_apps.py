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


class CacheAppsAction(Action):
    """
    Action that ensures that all apps and engines exist locally.
    """

    def __init__(self):
        Action.__init__(
            self,
            "cache_apps",
            Action.TK_INSTANCE,
            (
                "Toolkit manages a bundle cache to ensure that all versions of apps and "
                "engines that are specified in the environments exists locally. This "
                "cache is normally automatically managed by the update and install "
                "commands, but if you are manually editing version numbers inside "
                "the environment configuration, you may need to run the cache_apps command "
                "to ensure that all necessary code exists in the cache. "
            ),
            "Admin",
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
        log.info(
            "This command will traverse the entire configuration and ensure that all "
            "apps and engines code is correctly cached in your local installation."
        )

        num_downloads = 0

        for env_name in self.tk.pipeline_configuration.get_environments():
            log.info("")
            log.info("Environment %s" % env_name)
            log.info("------------------------------------------")

            env = self.tk.pipeline_configuration.get_environment(env_name)

            log.info("Environment path: %s" % (env.disk_location))
            log.info("")

            for eng in env.get_engines():
                if self._terminate_requested:
                    break

                desc = env.get_engine_descriptor(eng)
                if not desc.exists_local():
                    log.info("Engine %s - Downloading..." % eng)
                    num_downloads += 1
                    desc.download_local()
                else:
                    log.info("Engine %s - OK!" % eng)
                for app in env.get_apps(eng):
                    if self._terminate_requested:
                        break

                    desc = env.get_app_descriptor(eng, app)
                    if not desc.exists_local():
                        log.info("App %s (Engine %s) - Downloading..." % (app, eng))
                        num_downloads += 1
                        desc.download_local()
                    else:
                        log.info("App %s (Engine %s) - OK!" % (app, eng))

            for framework in env.get_frameworks():
                if self._terminate_requested:
                    break

                desc = env.get_framework_descriptor(framework)
                if not desc.exists_local():
                    log.info("Framework %s - Downloading..." % framework)
                    num_downloads += 1
                    desc.download_local()
                else:
                    log.info("Framework %s - OK!" % framework)

        log.info("")
        log.info("Cache apps completed! %d items downloaded." % num_downloads)
