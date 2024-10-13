# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from ..util import ShotgunPath
from ..errors import TankError
from . import constants
from ..util import filesystem
from ..util import is_linux, is_macos, is_windows

from tank_vendor import yaml

from .action_base import Action

import os
import shutil


class CloneConfigAction(Action):
    """
    Action that looks at the config and validates all parameters
    """

    def __init__(self):
        Action.__init__(
            self,
            "clone_configuration",
            Action.TK_INSTANCE,
            "Clones the current configuration.",
            "Configuration",
        )

        # no tank command support for this one
        self.supports_tank_command = False

        # this method can be executed via the API
        self.supports_api = True

        self.parameters = {}

        self.parameters["source_id"] = {
            "description": "Id of source Pipeline Configuration to use.",
            "default": None,
            "type": "int",
        }

        self.parameters["user_id"] = {
            "description": "PTR user id to associate the cloned configuration with.",
            "default": None,
            "type": "int",
        }

        self.parameters["name"] = {
            "description": "The name of the new pipeline configuration.",
            "default": None,
            "type": "str",
        }

        # note how the current platform's default value is None in order to make that required
        self.parameters["path_mac"] = {
            "description": "Path to the new configuration on Macosx.",
            "default": (None if is_macos() else ""),
            "type": "str",
        }

        self.parameters["path_win"] = {
            "description": "Path to the new configuration on Windows.",
            "default": (None if is_windows() else ""),
            "type": "str",
        }

        self.parameters["path_linux"] = {
            "description": "Path to the new configuration on Linux.",
            "default": (None if is_linux() else ""),
            "type": "str",
        }

        self.parameters["return_value"] = {
            "description": "Returns the id of the created Pipeline Configuration",
            "type": "int",
        }

    def run_noninteractive(self, log, parameters):
        """
        Tank command API accessor.
        Called when someone runs a tank command through the core API.

        :param log: std python logger
        :param parameters: dictionary with tank command parameters
        """

        # validate params and seed default values
        computed_params = self._validate_parameters(parameters)
        # execute
        data = _do_clone(
            log,
            self.tk,
            computed_params["source_id"],
            computed_params["user_id"],
            computed_params["name"],
            computed_params["path_linux"],
            computed_params["path_mac"],
            computed_params["path_win"],
        )

        return data["id"]

    def run_interactive(self, log, args):
        """
        Tank command accessor

        :param log: std python logger
        :param args: command line args
        """
        raise TankError("This Action does not support command line access")


def clone_pipeline_configuration_html(
    log,
    tk,
    source_pc_id,
    user_id,
    new_name,
    target_linux,
    target_mac,
    target_win,
    is_localized,
):
    """
    Clones a pipeline configuration, not necessarily the one associated with the current tk handle.

    This script is called from the tank command directly and is what gets executed if someone
    tries to run the clone command from inside of Shotgun by right clicking on a Pipeline
    Configuration entry and go select the clone action.
    """

    data = _do_clone(
        log, tk, source_pc_id, user_id, new_name, target_linux, target_mac, target_win
    )

    source_folder = data["source"]
    target_folder = data["target"]

    log.info("<b>Clone Complete!</b>")
    log.info("")
    log.info(
        "Your configuration has been copied from <code>%s</code> "
        "to <code>%s</code>." % (source_folder, target_folder)
    )

    # if this new clone is using a shared core API, tell people how to localize.
    if not is_localized:
        log.info("")
        log.info("")
        log.info(
            "Note: You are running a shared version of the Toolkit Core API for this new clone. "
            "This means that when you make an upgrade to that shared API, all "
            "the different projects that share it will be upgraded. This makes the upgrade "
            "process quick and easy. However, sometimes you also want to break out of a shared "
            "environment, for example if you want to test a new version of the Flow Production Tracking. "
        )
        log.info("")
        log.info(
            "In order to change this pipeline configuration to use its own independent version "
            "of the Toolkit API, you can execute the following command: "
        )

        if is_windows():
            tank_cmd = os.path.join(target_folder, "tank.bat")
        else:
            tank_cmd = os.path.join(target_folder, "tank")

        log.info("")
        code_css_block = "display: block; padding: 0.5em 1em; border: 1px solid #bebab0; background: #faf8f0;"
        log.info("<code style='%s'>%s localize</code>" % (code_css_block, tank_cmd))


###################################################################################################
# private methods


@filesystem.with_cleared_umask
def _do_clone(
    log, tk, source_pc_id, user_id, new_name, target_linux, target_mac, target_win
):
    """
    Clones the current configuration
    """

    curr_os = ShotgunPath.get_shotgun_storage_key()
    source_pc = tk.shotgun.find_one(
        constants.PIPELINE_CONFIGURATION_ENTITY,
        [["id", "is", source_pc_id]],
        ["code", "project", "linux_path", "windows_path", "mac_path"],
    )
    source_folder = source_pc.get(curr_os)

    target_folder = None
    if is_windows():
        target_folder = target_win
    elif is_macos():
        target_folder = target_mac
    elif is_linux():
        target_folder = target_linux

    log.debug("Cloning %s -> %s" % (source_folder, target_folder))

    if not os.path.exists(source_folder):
        raise TankError(
            "Cannot clone! Source folder '%s' does not exist!" % source_folder
        )

    if os.path.exists(target_folder):
        raise TankError(
            "Cannot clone! Target folder '%s' already exists!" % target_folder
        )

    # Register the new entity in Shotgun. This is being done first, because one
    # common problem is the user's permissions not being sufficient to allow them
    # to create the PC entity. In this situation, we want to fail quickly and not
    # leave garbage files on disk. As such, we do this first, then copy the config
    # on disk.
    data = {
        "linux_path": target_linux,
        "windows_path": target_win,
        "mac_path": target_mac,
        "code": new_name,
        "project": source_pc["project"],
        "users": [{"type": "HumanUser", "id": user_id}],
    }
    log.debug("Create sg: %s" % str(data))
    pc_entity = tk.shotgun.create(constants.PIPELINE_CONFIGURATION_ENTITY, data)
    log.debug("Created in PTR: %s" % str(pc_entity))

    # copy files and folders across
    try:
        os.mkdir(target_folder, 0o777)
        os.mkdir(os.path.join(target_folder, "cache"), 0o777)
        filesystem.copy_folder(
            os.path.join(source_folder, "config"),
            os.path.join(target_folder, "config"),
            skip_list=[],
        )
        filesystem.copy_folder(
            os.path.join(source_folder, "install"),
            os.path.join(target_folder, "install"),
        )
        shutil.copy(
            os.path.join(source_folder, "tank"), os.path.join(target_folder, "tank")
        )
        shutil.copy(
            os.path.join(source_folder, "tank.bat"),
            os.path.join(target_folder, "tank.bat"),
        )
        os.chmod(os.path.join(target_folder, "tank.bat"), 0o777)
        os.chmod(os.path.join(target_folder, "tank"), 0o777)

        sg_code_location = os.path.join(
            target_folder, "config", "core", "install_location.yml"
        )
        if os.path.exists(sg_code_location):
            os.chmod(sg_code_location, 0o666)
            os.remove(sg_code_location)
        fh = open(sg_code_location, "wt")
        fh.write("# Flow Production Tracking Toolkit configuration file\n")
        fh.write("# This file was automatically created by tank clone\n")
        fh.write("# This file reflects the paths in the pipeline configuration\n")
        fh.write("# entity which is associated with this location (%s).\n" % new_name)
        fh.write("\n")
        fh.write("Windows: '%s'\n" % target_win)
        fh.write("Darwin: '%s'\n" % target_mac)
        fh.write("Linux: '%s'\n" % target_linux)
        fh.write("\n")
        fh.write("# End of file.\n")
        fh.close()

    except Exception as e:
        raise TankError("Could not create file system structure: %s" % e)

    # lastly, update the pipeline_configuration.yml file
    try:

        sg_pc_location = os.path.join(
            target_folder, "config", "core", constants.PIPELINECONFIG_FILE
        )

        # read the file first
        fh = open(sg_pc_location, "rt")
        try:
            data = yaml.load(fh, Loader=yaml.FullLoader)
        finally:
            fh.close()

        # now delete it
        if os.path.exists(sg_pc_location):
            os.chmod(sg_pc_location, 0o666)
            os.remove(sg_pc_location)

        # now update some fields
        data["pc_id"] = pc_entity["id"]
        data["pc_name"] = new_name

        # and write the new file
        fh = open(sg_pc_location, "wt")

        # using safe_dump instead of dump ensures that we
        # don't serialize any non-std yaml content. In particular,
        # this causes issues if a unicode object containing a 7-bit
        # ascii string is passed as part of the data. in this case,
        # dump will write out a special format which is later on
        # *loaded in* as a unicode object, even if the content doesn't
        # need unicode handling. And this causes issues down the line
        # in toolkit code, assuming strings:
        #
        # >>> yaml.dump({"foo": u"bar"})
        # "{foo: !!python/unicode 'bar'}\n"
        # >>> yaml.safe_dump({"foo": u"bar"})
        # '{foo: bar}\n'
        #
        yaml.safe_dump(data, fh)
        fh.close()

    except Exception as e:
        raise TankError("Could not update pipeline_configuration.yml file: %s" % e)

    return {"source": source_folder, "target": target_folder, "id": pc_entity["id"]}
