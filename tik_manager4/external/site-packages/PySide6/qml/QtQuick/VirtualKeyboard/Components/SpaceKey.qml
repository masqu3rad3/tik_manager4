// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick
import QtQuick.VirtualKeyboard

/*!
    \qmltype SpaceKey
    \inqmlmodule QtQuick.VirtualKeyboard.Components
    \ingroup qmlclass
    \ingroup qtvirtualkeyboard-components-qml
    \ingroup qtvirtualkeyboard-key-types
    \inherits Key

    \brief Space key for keyboard layouts.

    This key emits a space for input method processing.
*/

Key {
    keyType: QtVirtualKeyboard.KeyType.SpaceKey
    text: " "
    displayText: ""
    repeat: true
    showPreview: false
    highlighted: true
    key: Qt.Key_Space
    keyPanelDelegate: keyboard.style ? keyboard.style.spaceKeyPanel : undefined
}
