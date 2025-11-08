// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick
import QtQuick.VirtualKeyboard

/*!
    \qmltype HandwritingModeKey
    \inqmlmodule QtQuick.VirtualKeyboard.Components
    \ingroup qmlclass
    \ingroup qtvirtualkeyboard-components-qml
    \ingroup qtvirtualkeyboard-key-types
    \inherits Key
    \since QtQuick.VirtualKeyboard 2.0

    \brief Hand writing mode key for keyboard layouts.

    This key toggles between the handwriting mode layout and the main layout.

    The key is automatically hidden from the keyboard layout if handwriting support
    is not enabled for the virtual keyboard.
*/

Key {
    keyType: QtVirtualKeyboard.KeyType.HandwritingModeKey
    key: Qt.Key_Context2
    displayText: "HWR"
    functionKey: true
    highlighted: true
    visible: keyboard.isKeyboardFunctionAvailable(QtVirtualKeyboard.KeyboardFunction.ToggleHandwritingMode)
    onClicked: keyboard.doKeyboardFunction(QtVirtualKeyboard.KeyboardFunction.ToggleHandwritingMode)
    keyPanelDelegate: keyboard.style ? keyboard.style.handwritingKeyPanel : undefined
}
