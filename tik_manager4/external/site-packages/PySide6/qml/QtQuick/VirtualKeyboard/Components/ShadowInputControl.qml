// Copyright (C) 2017 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick
// Deliberately imported after QtQuick to avoid missing restoreMode property in Binding. Fix in Qt 6.
import QtQml
import QtQuick.VirtualKeyboard
import QtQuick.VirtualKeyboard.Settings

Item {
    id: control
    property alias textEdit: shadowInput

    enabled: keyboard.active && VirtualKeyboardSettings.fullScreenMode

    MouseArea {
        anchors.fill: parent
    }

    onXChanged: InputContext.priv.shadow.updateSelectionProperties()
    onYChanged: InputContext.priv.shadow.updateSelectionProperties()

    Loader {
        sourceComponent: keyboard.style.fullScreenInputContainerBackground
        anchors.fill: parent
        Loader {
            id: fullScreenInputBackground
            sourceComponent: keyboard.style.fullScreenInputBackground
            anchors.fill: parent
            anchors.margins: keyboard.style.fullScreenInputMargins
            z: 1
            Flickable {
                id: flickable
                clip: true
                z: 2
                width: parent.width
                height: parent.height
                flickableDirection: Flickable.HorizontalFlick
                interactive: contentWidth > width
                contentWidth: shadowInput.width
                onContentXChanged: InputContext.priv.shadow.updateSelectionProperties()

                function ensureVisible(rectangle) {
                    if (contentX >= rectangle.x)
                        contentX = rectangle.x
                    else if (contentX + width <= rectangle.x + rectangle.width)
                        contentX = rectangle.x + rectangle.width - width;
                }

                TextInput {
                    id: shadowInput
                    objectName: "shadowInput"
                    property bool blinkStatus: true
                    width: Math.max(flickable.width, implicitWidth)
                    height: implicitHeight
                    anchors.verticalCenter: parent.verticalCenter
                    leftPadding: keyboard.style.fullScreenInputPadding
                    rightPadding: keyboard.style.fullScreenInputPadding
                    activeFocusOnPress: false
                    font: keyboard.style.fullScreenInputFont
                    inputMethodHints: InputContext.inputMethodHints
                    cursorDelegate: keyboard.style.fullScreenInputCursor
                    passwordCharacter: keyboard.style.fullScreenInputPasswordCharacter
                    color: keyboard.style.fullScreenInputColor
                    selectionColor: keyboard.style.fullScreenInputSelectionColor
                    selectedTextColor: keyboard.style.fullScreenInputSelectedTextColor
                    echoMode: (InputContext.inputMethodHints & Qt.ImhHiddenText) ? TextInput.Password : TextInput.Normal
                    selectByMouse: !!InputContext.inputItem && !!InputContext.inputItem.selectByMouse
                    onCursorPositionChanged: {
                        cursorSyncTimer.restart()
                        blinkStatus = true
                        if (cursorTimer.running)
                            cursorTimer.restart()
                    }
                    onSelectionStartChanged: cursorSyncTimer.restart()
                    onSelectionEndChanged: cursorSyncTimer.restart()
                    onCursorRectangleChanged: flickable.ensureVisible(cursorRectangle)

                    function getAnchorPosition() {
                        if (selectionStart == selectionEnd)
                            return cursorPosition
                        else if (selectionStart == cursorPosition)
                            return selectionEnd
                        else
                            return selectionStart
                    }

                    Timer {
                        id: cursorSyncTimer
                        interval: 0
                        onTriggered: {
                            var anchorPosition = shadowInput.getAnchorPosition()
                            if (anchorPosition !== InputContext.anchorPosition || shadowInput.cursorPosition !== InputContext.cursorPosition)
                                InputContext.priv.forceCursorPosition(anchorPosition, shadowInput.cursorPosition)
                        }
                    }

                    Timer {
                        id: cursorTimer
                        interval: Qt.styleHints.cursorFlashTime / 2
                        repeat: true
                        running: control.visible
                        onTriggered: shadowInput.blinkStatus = !shadowInput.blinkStatus
                    }
                }
            }
        }
    }

    Component.onCompleted: {
        if (VirtualKeyboardSettings.fullScreenMode) {
            InputContext.priv.shadow.inputItem = shadowInput
        }
    }
    Connections {
        target: VirtualKeyboardSettings
        function onFullScreenModeChanged() {
            InputContext.priv.shadow.inputItem = VirtualKeyboardSettings.fullScreenMode ? shadowInput : null
        }
    }
    Connections {
        target: InputContext.priv.shadow
        function onInputItemChanged() {
            cursorSyncTimer.stop()
            if (!InputContext.priv.shadow.inputItem)
                shadowInput.clear()
        }
    }
}
