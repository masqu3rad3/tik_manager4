# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import shutil
import sys

from . import QtCore, QtGui
from .ui_item import Ui_Item
from ..bundle import resolve_default_value
from ..engine import current_engine


class ConfigItem(QtGui.QWidget):
    """
    Describes a configuration setting with data and methods
    """

    def __init__(self, setting, params, value, bundle, parent=None):
        QtGui.QWidget.__init__(self, parent)

        # set up the UI
        self.ui = Ui_Item()
        self.ui.setupUi(self)

        engine_name = None
        if current_engine():
            engine_name = current_engine().name

        default_val = resolve_default_value(params, engine_name=engine_name)
        param_type = params.get("type")

        self.ui.name.setText("Setting %s" % setting)

        self.ui.type.setText("<B>Type:</b> %s" % param_type)

        desc = str(params.get("description", "No description given."))
        self.ui.description.setText("<b>Description:</b> %s" % desc)

        # special cases for some things:
        value_str = ""

        if type(value) == str and value.startswith("hook:"):
            # this is the generic hook override that any type can have
            value_str = "<b>Value:</b> <code>%s</code>" % value
            value_str += "<br><br>"
            value_str += "This value uses a dynamic, hook based setting. When the value is computed, "
            value_str += "Toolkit is calling the core hook specified in the setting. "
            value_str += "<br><br>The value is currently being computed by the "
            value_str += "hook to <code>'%s'</code>" % str(bundle.get_setting(setting))

        elif param_type == "hook":
            # resolve the hook path
            if value == "default":
                value_str = "<b>Value:</b> Using the default hook that comes bundled with the app."
            else:
                # user hook
                value_str = "<b>Value:</b> <code>%s</code>" % value

        elif param_type == "template":
            # resolve the template
            value_str = "<b>Value:</b> %s<br>" % value
            template_value = bundle.tank.templates.get(value)
            template_def = template_value.definition if template_value else "None"
            value_str += "<b>Resolved Value:</b> <code>%s</code><br>" % template_def

        elif param_type in ["dict", "list"]:
            # code block
            value_str = "<b>Value:</b> <code>%s</code>" % value

        elif param_type == "str":
            # value in quotes
            value_str = "<b>Value:</b> '%s'" % value

        else:
            # all others
            value_str = "<b>Value:</b> %s" % value

        # colour all non-default values in blue
        if default_val == value or (param_type == "hook" and value == "default"):
            self.ui.value.setText(value_str)
            self.ui.value.setToolTip("This setting is using the default value.")
        else:
            # non-default value - indicate in blue
            self.ui.value.setText("<div style='color: #76A4E0'>%s</div>" % value_str)
            self.ui.value.setToolTip("This setting is using a non-default value.")
