# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from . import QtCore, QtGui
from .ui_busy_dialog import Ui_BusyDialog


class BusyDialog(QtGui.QWidget):
    """
    Global progress dialog. Displays a dialog that contains a small progress message.
    This is handled by the engine.display_global_progress() and engine.clear_global_progress()
    methods and is typically used when for example the Core API wants to display some progress
    information back to the user during long running tasks or processing.
    """

    def __init__(self):
        """
        Constructor
        """
        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self)

        # now load in the UI that was created in the UI designer
        self.ui = Ui_BusyDialog()
        self.ui.setupUi(self)

    def set_contents(self, title, details):
        """
        Set the message to be displayed in the progress dialog

        :param title: Title text to display
        :param details: detailed message to display
        """
        self.ui.title.setText(title)
        self.ui.details.setText(details)

    def mousePressEvent(self, event):
        """
        Called when the mouse is clicked in the widget

        :param event: QEvent
        """
        QtGui.QWidget.mousePressEvent(self, event)
        # close the window if someone clicks it
        self.close()

    @property
    def hide_tk_title_bar(self):
        """
        Tell the system to not show the std toolbar
        """
        return True
