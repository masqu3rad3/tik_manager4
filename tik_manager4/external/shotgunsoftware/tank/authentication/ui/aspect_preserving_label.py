# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from .qt_abstraction import QtGui
from .qt_abstraction import QtCore


class AspectPreservingLabel(QtGui.QLabel):
    """
    Label that displays a scaled down version of an image if it is bigger
    than the label.
    """
    def __init__(self, parent=None):
        """
        Constructor

        :params parent: Parent widget.
        """
        QtGui.QLabel.__init__(self, parent)

        self._pix = None

    def setPixmap(self, pixmap):
        """
        Sets the pixmap for the label.

        :param pixmap: Pixmap to display in the label.
        """
        self._pix = pixmap
        scaled_pixmap = self._pix.scaled(
            self.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        QtGui.QLabel.setPixmap(self, scaled_pixmap)

    def heightForWidth(self, width):
        """
        Computes the height for a given width while preserving aspect ratio.

        :param width: Width we want to get the height for.

        :returns: The height.
        """
        if self._pix is None:
            return self._pix.height() * width / self._pix.width()
        return QtGui.QLabel.heightForWidth(self, width)

    def sizeHint(self):
        """
        Computes the aspect-ratio preserving size hint for this label.
        """
        width = min(self.width(), self.pixmap().width())
        return QtCore.QSize(width, self.heightForWidth(width))

    def resizeEvent(self, e):
        """
        Rescales the pixmap when the widget size is changed.

        :param e: Resize event payload.
        """
        if self._pix is None:
            return

        scaled_pixmap = self._pix.scaled(
            self.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        QtGui.QLabel.setPixmap(self, scaled_pixmap)
        QtGui.QApplication.instance().processEvents()
