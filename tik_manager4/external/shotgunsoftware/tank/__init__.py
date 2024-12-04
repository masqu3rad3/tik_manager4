# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

# Toolkit core API version
__version__ = "HEAD"

########################################################################
# Establish pipeline configuration context if needed
#
# When the tank command executes, or when the python API is imported
# via the API proxy that is available with every non-localized pipeline config,
# an environment variable TANK_CURRENT_PC, is set, pointing at the configuration
# associated with the currently running config. This is to ensure that the right
# version of the code is associated with the currently running project
# configuration.
#
# However, in the case when a cloned configuration has been localized,
# the API proxy has been replaced by the actual core API code.
# In this case, we will set the TANK_CURRENT_PC explicitly.
#
# The logic below is fundamentally to avoid the issue that when a cloned localized
# configuration has its python sgtk/tank module imported directly, it will associate
# itself with the primary config rather than with the config where the code is located.

import os
import sys
import uuid
import inspect

if sys.version_info < (3, 7):
    raise Exception("This module requires Python version 3.7 or higher.")

def __fix_tank_vendor():
    # Older versions of Flow Production Tracking left copies of tank_vendor in sys.modules,
    # which means we might not be importing our copy but someone else's,
    # so strip it out!
    if "tank_vendor" not in sys.modules:
        return

    # Figure out where our tank_vendor is.
    our_tank_vendor = os.path.normpath(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "tank_vendor")
    )

    tank_vendor = sys.modules["tank_vendor"]

    # If the tank_vendor that is loaded is ours, we're good!
    if os.path.normpath(inspect.getsourcefile(tank_vendor)) == our_tank_vendor:
        return

    __prefix = "_tank_vendor_swap_%s" % uuid.uuid4().hex

    # We've loaded another tank_vendor, so let's strip out every single
    # module that starts with tank_vendor
    for name, module in list(sys.modules.items()):
        # sys.modules can be assigned anything, even None or a number
        # so avoid those.
        if isinstance(name, str) is False or name.startswith("tank_vendor") is False:
            continue

        # Move tank_vendor out of the way instead of simply removing it from sys.modules.
        # If the modules are still in use, removing them from sys.modules seems to do
        # some cleanup of the modules themselves, which we do not want. For example,
        # if a Shotgun connection is still used from the old tank_vendor after the swap
        # happened, then the global methods from shotgun.py like _translate_filters
        # will turn to None. It's all a bit mysterious to be honest, but considering we're
        # also following the same pattern in bootstrap/import_handler.py, it seems
        # like this is the safe way to fix this.
        sys.modules[__prefix + name] = sys.modules.pop(name)


__fix_tank_vendor()

del __fix_tank_vendor


if "TANK_CURRENT_PC" not in os.environ:
    # find the pipeline configuration root, probe for a key file
    # (templates.yml) and use this test to determine if this code is
    # a core API located inside a pipeline configuration.
    #
    # NOTE! This is a very particular piece of logic, which is also
    # duplicated inside the tank command and the python proxy wrappers.
    # it is intentionally left here in the init method to highlight that
    # is unique and special.
    #
    from . import constants

    current_folder = os.path.abspath(os.path.dirname(__file__))
    pipeline_config = os.path.abspath(
        os.path.join(current_folder, "..", "..", "..", "..")
    )
    roots_file = os.path.join(
        pipeline_config, "config", "core", constants.STORAGE_ROOTS_FILE
    )
    if os.path.exists(roots_file):
        os.environ["TANK_CURRENT_PC"] = pipeline_config

########################################################################

# first import the log manager since a lot of modules require this.
from .log import LogManager

# make sure that all sub-modules are imported at the same as the main module
from . import authentication
from . import descriptor
from . import bootstrap
from . import commands
from . import deploy
from . import folder
from . import platform
from . import util

# core functionality
from .api import (
    Tank,
    tank_from_path,
    tank_from_entity,
    set_authenticated_user,
    get_authenticated_user,
)
from .api import Sgtk, sgtk_from_path, sgtk_from_entity
from .pipelineconfig_utils import (
    get_python_interpreter_for_config,
    get_core_python_path_for_config,
    get_sgtk_module_path,
)

from .context import Context

from .errors import (
    TankError,
    TankErrorProjectIsSetup,
    TankHookMethodDoesNotExistError,
    TankFileDoesNotExistError,
    TankUnreadableFileError,
    TankInvalidInterpreterLocationError,
    TankInvalidCoreLocationError,
    TankNotPipelineConfigurationError,
)

# note: TankEngineInitError used to reside in .errors but was moved into platform.errors
from .platform.errors import TankEngineInitError
from .template import Template, TemplatePath, TemplateString
from .hook import Hook, get_hook_baseclass

from .commands import list_commands, get_command, SgtkSystemCommand, CommandInteraction

from .templatekey import TemplateKey, SequenceKey, IntegerKey, StringKey, TimestampKey

# expose the support url
from .constants import (
  DEFAULT_STORAGE_ROOT_HOOK_NAME,
  SUPPORT_URL as support_url,
)
