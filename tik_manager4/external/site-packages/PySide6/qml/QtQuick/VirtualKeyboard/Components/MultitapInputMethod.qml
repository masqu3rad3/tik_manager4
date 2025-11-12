// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick
import QtQuick.VirtualKeyboard

InputMethod {
    property string multitapSequence
    property int multitapIndex: -1

    onMultitapSequenceChanged: selectionListChanged(SelectionListModel.Type.WordCandidateList)
    onMultitapIndexChanged: selectionListActiveItemChanged(SelectionListModel.Type.WordCandidateList, multitapIndex)

    property variant multiTapTimer: Timer {
        interval: 1200
        onTriggered: {
            update()
        }
    }

    function inputModes(locale) {
        return [InputEngine.InputMode.Latin, InputEngine.InputMode.Numeric, InputEngine.InputMode.Dialable];
    }

    function setInputMode(locale, inputMode) {
        return true
    }

    function setTextCase(textCase) {
        return true
    }

    function reset() {
        multiTapTimer.stop()
        multitapIndex = -1
        multitapSequence = ""
    }

    function update() {
        multiTapTimer.stop()
        multitapIndex = -1
        multitapSequence = ""
        if (inputContext !== null && inputContext.preeditText.length > 0) {
            inputContext.commit()
        }
    }

    function keyEvent(key, text, modifiers) {
        var accept = false
        switch (key) {
        case Qt.Key_Enter:
        case Qt.Key_Return:
        case Qt.Key_Tab:
            update()
            break
        case Qt.Key_Backspace:
            if (inputContext.preeditText.length > 0) {
                inputContext.clear()
                update()
                accept = true
            }
            break
        default:
            if (key !== inputEngine.previousKey) {
                update()
            }
            multitapSequence = text
            if (multitapSequence.length > 1) {
                multitapIndex = multiTapTimer.running ? (multitapIndex + 1) % multitapSequence.length : 0
                inputContext.preeditText = multitapSequence.charAt(multitapIndex)
                multiTapTimer.restart()
            } else {
                inputContext.commit(text)
            }
            accept = true
            break
        }
        return accept;
    }

    function selectionLists() {
        return [SelectionListModel.Type.WordCandidateList];
    }

    function selectionListItemCount(type) {
        return multitapSequence.length > 1 ? multitapSequence.length : 0
    }

    function selectionListData(type, index, role) {
        var result = null
        switch (role) {
        case SelectionListModel.Role.Display:
            result = multitapSequence.charAt(index)
            break
        default:
            break
        }
        return result
    }

    function selectionListItemSelected(type, index) {
        multitapIndex = index
        inputContext.preeditText = multitapSequence.charAt(multitapIndex)
        update()
    }
}
