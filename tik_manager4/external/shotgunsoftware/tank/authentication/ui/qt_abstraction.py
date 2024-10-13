# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Imports Qt without having to worry which version of Qt we are using.
"""

from ...util.qt_importer import QtImporter

_importer = QtImporter()
QtCore = _importer.QtCore
QtGui = _importer.QtGui
QtWebKit = _importer.QtWebKit
QtNetwork = _importer.QtNetwork
QtWebEngineWidgets = _importer.QtWebEngineWidgets
qt_version_tuple = _importer.qt_version_tuple
del _importer
