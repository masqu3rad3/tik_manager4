// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick
import QtQuick.VirtualKeyboard

/*!
    \qmltype EnterKey
    \inqmlmodule QtQuick.VirtualKeyboard.Components
    \ingroup qmlclass
    \ingroup qtvirtualkeyboard-components-qml
    \ingroup qtvirtualkeyboard-key-types
    \inherits BaseKey

    \brief Enter key for keyboard layouts.

    Sends an enter key for input method processing.
*/

BaseKey {
    /*! This property holds the action id for the enter key.

    */
    readonly property int actionId: InputContext.priv.hasEnterKeyAction(InputContext.priv.inputItem) ? InputContext.priv.inputItem.EnterKeyAction.actionId : EnterKeyAction.None

    keyType: QtVirtualKeyboard.KeyType.EnterKey
    text: "\n"
    displayText: InputContext.priv.hasEnterKeyAction(InputContext.priv.inputItem) ? InputContext.priv.inputItem.EnterKeyAction.label : ""
    key: Qt.Key_Return
    showPreview: false
    highlighted: true
    enabled: InputContext.priv.hasEnterKeyAction(InputContext.priv.inputItem) ? InputContext.priv.inputItem.EnterKeyAction.enabled : true
    keyPanelDelegate: keyboard.style ? keyboard.style.enterKeyPanel : undefined
}
