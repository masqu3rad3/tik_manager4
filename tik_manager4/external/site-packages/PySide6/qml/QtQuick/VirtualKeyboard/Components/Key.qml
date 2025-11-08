// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick
import QtQuick.VirtualKeyboard

/*!
    \qmltype Key
    \inqmlmodule QtQuick.VirtualKeyboard.Components
    \ingroup qmlclass
    \ingroup qtvirtualkeyboard-components-qml
    \ingroup qtvirtualkeyboard-key-types
    \inherits BaseKey

    \brief Regular character key for keyboard layouts.

    This key emits the key code and key text for input method processing.
*/

BaseKey {
    id: keyItem
    keyType: QtVirtualKeyboard.KeyType.Key
    key: !functionKey && text.length > 0 ? text.toUpperCase().charCodeAt(0) : Qt.Key_unknown
    keyPanelDelegate: keyboard.style ? keyboard.style.keyPanel : undefined
}
