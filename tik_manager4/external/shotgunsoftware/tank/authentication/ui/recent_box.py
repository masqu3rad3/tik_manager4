# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
QT Login dialog for authenticating to a Shotgun server.

--------------------------------------------------------------------------------
NOTE! This module is part of the authentication library internals and should
not be called directly. Interfaces and implementation of this module may change
at any point.
--------------------------------------------------------------------------------
"""

from .qt_abstraction import QtGui
from .completion_filter_proxy import CompletionFilterProxy


class RecentBox(QtGui.QComboBox):
    """
    Combo box specialisation that handles all the filtering, sorting and auto-completion
    for a list of recent items. Items are sorted alphabetically so they can be found easily
    in the UI.
    """

    def __init__(self, parent):
        super(RecentBox, self).__init__(parent)

        self.setEditable(True)

        # Using QLineEdit so we have a placeholder even when the line edit is selected.
        self.setLineEdit(QtGui.QLineEdit(self))

        # Create a model sorted alphabetically for the recent items.
        self._recent_items_model = QtGui.QStringListModel(self)
        self._drop_down_model = QtGui.QSortFilterProxyModel(self)
        self._drop_down_model.setSourceModel(self._recent_items_model)
        self.setModel(self._drop_down_model)

        # We'll use a completer that shows all results and we'll do the matching ourselves, as the completion
        # engine can only work from the beginning of a string...
        self._completer = QtGui.QCompleter(self)
        self._completer.setCompletionMode(QtGui.QCompleter.UnfilteredPopupCompletion)

        # We'll do our own filtering.
        self._filter_model = CompletionFilterProxy(self)
        self._filter_model.setSourceModel(self._drop_down_model)
        self._completer.setModel(self._filter_model)
        self.setCompleter(self._completer)

        # Each time the user types something, we'll update the filter.
        self.lineEdit().textEdited.connect(self._current_text_changed)

    def set_style_sheet(self, style_sheet):
        """
        Allows to the the completer's pop-up widget style sheet.

        :param str style_sheet: Style sheet for the completer's pop-up widget.
        """
        self.completer().popup().setStyleSheet(style_sheet)

    def set_recent_items(self, items):
        """
        Sets the list of recent items.

        :param list(str): List of strings to display.
        """
        self._recent_items_model.setStringList(items)

    def set_selection(self, item):
        """
        Sets the currently selected item in the drop down.

        :param str item: String to select in the recent box.
        """
        for idx in range(self._drop_down_model.rowCount()):
            if self._drop_down_model.data(self._drop_down_model.index(idx, 0)) == item:
                self.setCurrentIndex(idx)
                break

    def _current_text_changed(self, text):
        """
        Updates the filter each time the user types something.

        :param str text: Text the user has just typed in.
        """
        self._filter_model.set_filter(text)

    def set_placeholder_text(self, text):
        """
        Sets the placeholder text to display in the combo box's line edit.
        """
        # Older versions of Qt don't support this method.
        if hasattr(self.lineEdit(), "setPlaceholderText"):
            self.lineEdit().setPlaceholderText(text)
