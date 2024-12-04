# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
This class is for backwards compatibility only!

Please use the authentication module found in sgtk.authentication for
new code. This compatibility wrapper will be removed at some point in the future.
"""

# this is to support code that imports private parts of the API,
# like this:
#
# from tank_vendor.shotgun_authentication.user import ShotgunUser
#
from tank.authentication.user import *


