# Copyright (c) 2020 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sys

# import the proper implementation into the module namespace depending on the
# current python version.  PyYAML supports python 2/3 by forking the code rather
# than with a single cross-compatible module. Rather than modify third party code,
# we'll just import the appropriate branch here.
if sys.version_info[0] == 2:
    from .python2 import *
else:
    from .python3 import *
