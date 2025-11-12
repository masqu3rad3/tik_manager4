// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick
import QtQuick.VirtualKeyboard

/*!
    \qmltype BackspaceKey
    \inqmlmodule QtQuick.VirtualKeyboard.Components
    \ingroup qmlclass
    \ingroup qtvirtualkeyboard-components-qml
    \ingroup qtvirtualkeyboard-key-types
    \inherits BaseKey

    \brief Backspace key for keyboard layouts.

    Sends a backspace key for input method processing.
    This key is repeatable.
*/

BaseKey {
    key: Qt.Key_Backspace
    keyType: QtVirtualKeyboard.KeyType.BackspaceKey
    repeat: true
    functionKey: true
    highlighted: true
    keyPanelDelegate: keyboard.style ? keyboard.style.backspaceKeyPanel : undefined
}
