// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick
import QtQuick.VirtualKeyboard

/*!
    \qmltype ShiftKey
    \inqmlmodule QtQuick.VirtualKeyboard.Components
    \ingroup qmlclass
    \ingroup qtvirtualkeyboard-components-qml
    \ingroup qtvirtualkeyboard-key-types
    \inherits BaseKey

    \brief Shift key for keyboard layouts.

    This key changes the shift state of the keyboard.
*/

BaseKey {
    id: shiftKey
    keyType: QtVirtualKeyboard.KeyType.ShiftKey
    key: Qt.Key_Shift
    enabled: InputContext.priv.shiftHandler.toggleShiftEnabled
    highlighted: true
    functionKey: true
    keyPanelDelegate: keyboard.style ? keyboard.style.shiftKeyPanel : undefined
    onClicked: InputContext.priv.shiftHandler.toggleShift()
}
