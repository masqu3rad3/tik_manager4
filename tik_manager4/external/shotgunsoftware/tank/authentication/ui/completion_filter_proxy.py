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

from tank.util import sgre as re

from .qt_abstraction import QtGui


class FuzzyMatcher():
    """
    Implement an algorithm to rank strings via fuzzy matching.

    Based on the analysis at
    http://crossplatform.net/sublime-text-ctrl-p-fuzzy-matching-in-python
    """
    def __init__(self, pattern):
        # construct a pattern that matches the letters in order
        # for example "aad" turns into "(a).*?(a).*?(d)".
        re_pattern = ".*?".join("(%s)" % re.escape(char) for char in pattern)
        self._re = re.compile(re_pattern, re.IGNORECASE)

    def score(self, string):
        match = self._re.search(string)
        if match is None:
            # letters did not appear in order
            return 0
        else:
            # have a match, scores are higher for matches near the beginning
            # or that are clustered together
            return 100.0 / ((1 + match.start()) * (match.end() - match.start() + 1))


class CompletionFilterProxy(QtGui.QSortFilterProxyModel):
    """
    Filters rows based on fuzzy matching and sorts them based on their score.
    """
    def __init__(self, parent):
        super(CompletionFilterProxy, self).__init__(parent)
        self.set_filter("")

    def set_filter(self, text):
        """
        Sets the text to use for the fuzzy match.

        :param str text: Text to use for fuzzy matching.
        """
        self._fuzzy_matcher = FuzzyMatcher(text)
        self.invalidateFilter()
        self.sort(0)
        self.layoutChanged.emit()

    def filterAcceptsRow(self, row, source_parent):
        """
        Filters out rows that do not match the fuzzy matcher.

        :param int row: Row under a model index that needs to be filtered.
        :param source_parent: Model item under which we want to filter a row.

        :returns: ``True`` if the row is accepted, ``False`` otherwise.
        """
        index = self.sourceModel().index(row, 0, source_parent)
        return self._fuzzy_matcher.score(self.sourceModel().data(index)) > 0

    def lessThan(self, left, right):
        """
        Sorts items based on how high they score in the fuzzy match. The higher the score,
        the earlier results show up.

        :param left: Model index of the first item to compare.
        :param right: Model index of the second item to compare.
        """
        left_data = self.sourceModel().data(left)
        right_data = self.sourceModel().data(right)

        left_score = self._fuzzy_matcher.score(left_data)
        right_score = self._fuzzy_matcher.score(right_data)

        if left_score != right_score:
            # The higher the score, the earlier the result should be in the list.
            return left_score > right_score
        else:
            # Score is the same, so sort alphabetically
            return left_data < right_data
