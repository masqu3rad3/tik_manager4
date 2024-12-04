# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.


# this class contains QT adapters and functionality for application agnostic QT usage.
# at engine initialization, the variables QtCore and QtGui are created by the engine
# init method and set to appropriate libraries.

# in apps and frameworks, for an agnostic qt access, you can then go:

# from tank.platform.qt import QtCore, QtGui
