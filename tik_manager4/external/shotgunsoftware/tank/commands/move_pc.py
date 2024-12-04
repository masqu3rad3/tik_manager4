# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from . import constants
from ..errors import TankError

from .action_base import Action

import os
import shutil
from tank_vendor.shotgun_api3.lib import sgsix
from tank_vendor.six.moves import input


class MovePCAction(Action):
    """
    Action that moves a pipeline configuration from one location to another
    """

    def __init__(self):
        Action.__init__(
            self,
            "move_configuration",
            Action.TK_INSTANCE,
            (
                "Moves this configuration from its current disk location to a new location."
            ),
            "Admin",
        )

    def _cleanup_old_location(self, log, path):

        found_storage_lookup_file = False
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                if name == "tank_configs.yml":
                    found_storage_lookup_file = True

                else:
                    full_path = os.path.join(root, name)
                    log.debug("Removing %s..." % full_path)
                    try:
                        os.remove(full_path)
                    except Exception as e:
                        log.warning(
                            "Could not delete file %s. Error Reported: %s"
                            % (full_path, e)
                        )

            for name in dirs:
                full_path = os.path.join(root, name)
                if found_storage_lookup_file and full_path == os.path.join(
                    path, "config"
                ):
                    log.debug(
                        "Not deleting folder %s since we have a storage lookup file"
                        % full_path
                    )

                else:
                    log.debug("Deleting folder %s..." % full_path)
                    try:
                        os.rmdir(full_path)
                    except Exception as e:
                        log.warning(
                            "Could not remove folder %s. Error Reported: %s"
                            % (full_path, e)
                        )

    def _copy_folder(self, log, level, src, dst):
        """
        Alternative implementation to shutil.copytree
        Copies recursively with very open permissions.
        Creates folders if they don't already exist.
        """
        if not os.path.exists(dst):
            log.debug("mkdir 0777 %s" % dst)
            os.mkdir(dst, 0o777)

        names = os.listdir(src)
        for name in names:

            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)

            if os.path.isdir(srcname):
                if level < 3:
                    log.info("Copying %s..." % srcname)
                self._copy_folder(log, level + 1, srcname, dstname)
            else:
                if dstname.endswith("tank_configs.yml") and os.path.dirname(
                    dstname
                ).endswith("config"):
                    log.debug("NOT COPYING CONFIG FILE %s -> %s" % (srcname, dstname))
                else:
                    shutil.copy(srcname, dstname)
                    log.debug("Copy %s -> %s" % (srcname, dstname))
                    # if the file extension is sh, set executable permissions
                    if dstname.endswith(".sh") or dstname.endswith(".bat"):
                        # make it readable and executable for everybody
                        os.chmod(dstname, 0o777)
                        log.debug("CHMOD 777 %s" % dstname)

    def run_interactive(self, log, args):

        if self.tk.pipeline_configuration.is_unmanaged():
            log.error("Cannot move unmanaged configurations!")
            return

        pipeline_config_id = self.tk.pipeline_configuration.get_shotgun_id()
        current_paths = self.tk.pipeline_configuration.get_all_os_paths()

        if len(args) != 3:
            log.info("Syntax: move_configuration linux_path windows_path mac_path")
            log.info("")
            log.info("This will move the location of the given pipeline configuation.")
            log.info(
                "You can also use this command to add a new platform to the pipeline configuration."
            )
            log.info("")
            log.info("Current Paths")
            log.info("--------------------------------------------------------------")
            log.info("")
            log.info("Current Linux Path:   '%s'" % current_paths.linux)
            log.info("Current Windows Path: '%s'" % current_paths.windows)
            log.info("Current Mac Path:     '%s'" % current_paths.macosx)
            log.info("")
            log.info("")
            log.info("You typically need to quote your paths, like this:")
            log.info("")
            log.info(
                '> tank move_configuration "/linux_root/my_config" "p:\\configs\\my_config" "/mac_root/my_config"'
            )
            log.info("")
            log.info(
                "If you want to leave a platform blank, just just empty quotes. For example, "
                "if you want a configuration which only works on windows, do like this: "
            )
            log.info("")
            log.info('> tank move_configuration "" "p:\\configs\\my_config" ""')
            log.info("")
            log.info("")
            raise TankError("Please specify three target locations!")

        linux_path = args[0]
        windows_path = args[1]
        mac_path = args[2]
        new_paths = {"darwin": mac_path, "win32": windows_path, "linux2": linux_path}

        # check which paths are different
        modifications = {
            "darwin": (current_paths.macosx != mac_path),
            "win32": (current_paths.windows != windows_path),
            "linux2": (current_paths.linux != linux_path),
        }

        log.info("")
        log.info("Current Paths")
        log.info("--------------------------------------------------------------")
        log.info("Current Linux Path:   '%s'" % current_paths.linux)
        log.info("Current Windows Path: '%s'" % current_paths.windows)
        log.info("Current Mac Path:     '%s'" % current_paths.macosx)
        log.info("")
        log.info("New Paths")
        log.info("--------------------------------------------------------------")
        if modifications["linux2"]:
            log.info("New Linux Path:   '%s'" % linux_path)
        else:
            log.info("New Linux Path:   No change")

        if modifications["win32"]:
            log.info("New Windows Path: '%s'" % windows_path)
        else:
            log.info("New Windows Path: No change")

        if modifications["darwin"]:
            log.info("New Mac Path:     '%s'" % mac_path)
        else:
            log.info("New Mac Path:     No change")

        log.info("")
        log.info("")

        if modifications[sgsix.platform]:
            copy_files = True
            log.info(
                "The configuration will be moved to reflect the specified path changes."
            )
        else:
            copy_files = False
            # we are not modifying current OS
            log.info(
                "Looks like you are not modifying the location for this operating system. Therefore, "
                "no files will be moved around, only configuration files will be updated."
            )

        log.info("")
        log.info(
            "Note for advanced users: If your configuration is localized and you have other projects which "
            "are linked to the core API embedded in this configuration, these links must be manually "
            "updated after the move operation."
        )

        log.info("")
        val = input("Are you sure you want to move your configuration? [Yes/No] ")
        if not val.lower().startswith("y"):
            raise TankError("Aborted by User.")

        # ok let's do it!
        local_source_path = self.tk.pipeline_configuration.get_path()
        local_target_path = new_paths[sgsix.platform]

        if copy_files:

            # check that files exists and that we can carry out the copy etc.
            if not os.path.exists(local_source_path):
                raise TankError(
                    "The path %s does not exist on disk!" % local_source_path
                )
            if os.path.exists(local_target_path):
                raise TankError(
                    "The path %s already exists on disk!" % local_target_path
                )

            # sanity check target folder
            parent_target = os.path.dirname(local_target_path)
            if not os.path.exists(parent_target):
                raise TankError("The path '%s' does not exist!" % parent_target)
            if not os.access(parent_target, os.W_OK | os.R_OK | os.X_OK):
                raise TankError(
                    "The permissions setting for '%s' is too strict. The current user "
                    "cannot create folders in this location." % parent_target
                )

        # first copy the data across
        old_umask = os.umask(0)
        try:

            # first copy the files - this is where things can go wrong so start with this
            if copy_files:
                log.info(
                    "Copying '%s' -> '%s'" % (local_source_path, local_target_path)
                )
                self._copy_folder(log, 0, local_source_path, local_target_path)
                sg_code_location = os.path.join(
                    local_target_path, "config", "core", "install_location.yml"
                )
            else:
                sg_code_location = os.path.join(
                    local_source_path, "config", "core", "install_location.yml"
                )

            # now updated config files
            log.info("Updating cached locations in %s..." % sg_code_location)
            os.chmod(sg_code_location, 0o666)
            fh = open(sg_code_location, "wt")
            fh.write("# Flow Production Tracking Toolkit configuration file\n")
            fh.write("# This file reflects the paths in the pipeline configuration\n")
            fh.write("# entity which is associated with this location\n")
            fh.write("\n")
            fh.write("Windows: '%s'\n" % windows_path)
            fh.write("Darwin: '%s'\n" % mac_path)
            fh.write("Linux: '%s'\n" % linux_path)
            fh.write("\n")
            fh.write("# End of file.\n")
            fh.close()

        except Exception as e:
            raise TankError(
                "Could not copy configuration! This may be because of system "
                "permissions or system setup. This configuration will "
                "still be functional, however data may have been partially copied "
                "to '%s' so we recommend that that location is cleaned up. "
                "Error Details: %s" % (local_target_path, e)
            )
        finally:
            os.umask(old_umask)

        log.info("Updating PTR Configuration Record...")
        self.tk.shotgun.update(
            constants.PIPELINE_CONFIGURATION_ENTITY,
            pipeline_config_id,
            {
                "mac_path": new_paths["darwin"],
                "windows_path": new_paths["win32"],
                "linux_path": new_paths["linux2"],
            },
        )

        # finally clean up the previous location
        if copy_files:
            log.info("Deleting original configuration files...")
            self._cleanup_old_location(log, local_source_path)
        log.info("")
        log.info("All done! Your configuration has been successfully moved.")
