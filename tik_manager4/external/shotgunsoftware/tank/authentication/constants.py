# Copyright (c) 2023 Autodesk.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

METHOD_BASIC = 0x01
METHOD_WEB_LOGIN = 0x02
METHOD_ASL = 0x03

method_resolve = {
    METHOD_BASIC: "credentials",
    METHOD_WEB_LOGIN: "qt_web_login",
    METHOD_ASL: "app_session_launcher",
}


def method_resolve_reverse(m):
    global method_resolve

    for (k, v) in method_resolve.items():
        if v == m:
            return k
