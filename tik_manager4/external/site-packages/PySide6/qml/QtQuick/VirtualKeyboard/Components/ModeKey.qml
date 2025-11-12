// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick
import QtQuick.VirtualKeyboard

/*!
    \qmltype ModeKey
    \inqmlmodule QtQuick.VirtualKeyboard.Components
    \ingroup qmlclass
    \ingroup qtvirtualkeyboard-components-qml
    \ingroup qtvirtualkeyboard-key-types
    \inherits Key
    \since QtQuick.VirtualKeyboard 2.0

    \brief Generic mode key for keyboard layouts.

    This key provides generic mode button functionality.

    A key press toggles the current mode without emitting key event
    for input method processing.

    ModeKey can be used in situations where a particular mode is switched
    "ON / OFF", and where the mode change does not require changing the
    keyboard layout. When this component is used, the \l { BaseKey::displayText } { displayText } should
    remain the same regardless of the mode, because the keyboard style
    visualizes the status.
*/

Key {
    /*! This property provides the current mode.

        The default is false.
    */
    property bool mode
    keyType: QtVirtualKeyboard.KeyType.ModeKey
    noKeyEvent: true
    functionKey: true
    highlighted: true
    onClicked: mode = !mode
    keyPanelDelegate: keyboard.style ? keyboard.style.modeKeyPanel : undefined
}
