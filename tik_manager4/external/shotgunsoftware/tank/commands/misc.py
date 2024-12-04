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

import code
import sys
import os


class ClearCacheAction(Action):
    """
    Action that clears the configuration caches
    """

    def __init__(self):
        Action.__init__(
            self,
            "clear_shotgun_menu_cache",
            Action.TK_INSTANCE,
            (
                "Clears the PTR Menu Cache associated with this Configuration. "
                "This is sometimes useful after complex configuration changes if new "
                "or modified Toolkit menu items are not appearing inside Flow Production Tracking."
            ),
            "Admin",
        )

        # this method can be executed via the API
        self.supports_api = True

    def run_noninteractive(self, log, parameters):
        """
        Tank command API accessor.
        Called when someone runs a tank command through the core API.

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
        cache_folder = self.tk.pipeline_configuration.get_shotgun_menu_cache_location()
        # cache files are on the form shotgun_mac_project.txt
        for f in os.listdir(cache_folder):
            if f.startswith("shotgun") and f.endswith(".txt"):
                full_path = os.path.join(cache_folder, f)
                log.debug("Deleting cache file %s..." % full_path)
                try:
                    os.remove(full_path)
                except:
                    log.warning("Could not delete cache file '%s'!" % full_path)

        log.info("The PTR menu cache has been cleared.")


class InteractiveShellAction(Action):
    """
    Action that starts an interactive shell
    """

    def __init__(self):
        Action.__init__(
            self,
            "shell",
            Action.TK_INSTANCE,
            "Starts an interactive Python shell for the current location.",
            "Developer",
        )

        # hint that the shell engine should be started for this action, if possible
        self.wants_running_shell_engine = True

    def run_interactive(self, log, args):

        if len(args) != 0:
            raise TankError("This command takes no arguments!")

        msg = []
        msg.append("Welcome to Flow Production Tracking Toolkit Python!")
        msg.append(sys.version)
        msg.append("Running on %s" % sys.platform)
        msg.append("")

        tk_locals = {}

        # add sgtk module to locals:
        import sgtk

        tk_locals["sgtk"] = sgtk

        # add some useful variables:
        if self.tk:
            tk_locals["tk"] = self.tk
            tk_locals["shotgun"] = self.tk.shotgun
            msg.append("- A tk API handle is available via the tk variable")
            msg.append("- A Shotgun API handle is available via the shotgun variable")

        if self.context:
            tk_locals["context"] = self.context
            msg.append("- Your current context is stored in the context variable")

        if self.engine:
            tk_locals["engine"] = self.engine
            msg.append("- The shell engine can be accessed via the engine variable")

        # attempt install tab command completion
        try:
            import rlcompleter
            import readline

            if "libedit" in readline.__doc__:
                # macosx, some versions - see
                # http://stackoverflow.com/questions/7116038
                readline.parse_and_bind("bind ^I rl_complete")
            else:
                readline.parse_and_bind("tab: complete")
        except:
            pass

        code.interact(banner="\n".join(msg), local=tk_locals)
