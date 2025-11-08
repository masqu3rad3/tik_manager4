// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick
// Deliberately imported after QtQuick to avoid missing restoreMode property in Binding. Fix in Qt 6.
import QtQml
import QtQuick.VirtualKeyboard

PopupList {
    id: wordCandidatePopupList

    readonly property int preferredVisibleItems: {
        if (!currentItem)
            return 0
        var maxHeight = flipVertical ? Qt.inputMethod.cursorRectangle.y : parent.height - Qt.inputMethod.cursorRectangle.height - Qt.inputMethod.cursorRectangle.y
        var result = Math.min(count, maxVisibleItems)
        while (result > 2 && result * currentItem.height > maxHeight)
            --result
        return result
    }
    readonly property bool flipVertical: currentItem &&
                                         Qt.inputMethod.cursorRectangle.y + (Qt.inputMethod.cursorRectangle.height / 2) > (parent.height / 2) &&
                                         Qt.inputMethod.cursorRectangle.y + Qt.inputMethod.cursorRectangle.height + (currentItem.height * 2) > parent.height

    height: currentItem ? currentItem.height * preferredVisibleItems + (spacing * preferredVisibleItems - 1) : 0
    Binding {
        target: wordCandidatePopupList
        property: "x"
        value: Math.round(Qt.inputMethod.cursorRectangle.x -
               (wordCandidatePopupList.currentItem ?
                    (wordCandidatePopupList.currentItem.hasOwnProperty("cursorAnchor") ?
                         wordCandidatePopupList.currentItem.cursorAnchor : wordCandidatePopupList.currentItem.width) : 0))
        when: wordCandidatePopupList.visible
        restoreMode: Binding.RestoreBinding
    }
    Binding {
        target: wordCandidatePopupList
        property: "y"
        value: Math.round(wordCandidatePopupList.flipVertical ? Qt.inputMethod.cursorRectangle.y - wordCandidatePopupList.height : Qt.inputMethod.cursorRectangle.y + Qt.inputMethod.cursorRectangle.height)
        when: wordCandidatePopupList.visible
        restoreMode: Binding.RestoreBinding
    }
    model: enabled ? InputContext.inputEngine.wordCandidateListModel : null

    onContentWidthChanged: viewResizeTimer.restart()

    Timer {
        id: viewResizeTimer
        interval: 0
        repeat: false
        onTriggered: wordCandidatePopupList.width = wordCandidatePopupList.contentWidth
    }

    Connections {
        target: wordCandidatePopupList.model ? wordCandidatePopupList.model : null
        function onActiveItemChanged(index) { wordCandidatePopupList.currentIndex = index }
        function onItemSelected() { if (wordCandidatePopupList.currentItem) keyboard.soundEffect.play(wordCandidatePopupList.currentItem.soundEffect) }
    }
}
