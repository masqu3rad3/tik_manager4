// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick
import QtQuick.VirtualKeyboard

/*!
    \qmltype SymbolModeKey
    \inqmlmodule QtQuick.VirtualKeyboard.Components
    \ingroup qmlclass
    \ingroup qtvirtualkeyboard-components-qml
    \ingroup qtvirtualkeyboard-key-types
    \inherits Key

    \brief Symbol mode key for keyboard layouts.

    This key toggles between the symbol mode layout and the main layout.
*/

Key {
    keyType: QtVirtualKeyboard.KeyType.SymbolModeKey
    key: Qt.Key_Context1
    displayText: "&123"
    functionKey: true
    highlighted: true
    onClicked: keyboard.symbolMode = !keyboard.symbolMode
    keyPanelDelegate: keyboard.style ? keyboard.style.symbolKeyPanel : undefined
}
