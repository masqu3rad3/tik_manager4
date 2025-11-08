// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick
import QtQuick.VirtualKeyboard

/*!
    \qmltype NumberKey
    \inqmlmodule QtQuick.VirtualKeyboard.Components
    \ingroup qmlclass
    \ingroup qtvirtualkeyboard-components-qml
    \ingroup qtvirtualkeyboard-key-types
    \inherits Key

    \brief Specialized number key for keyboard layouts.

    This key emits the key code and key text for input method processing.
    A NumberKey differs from a normal \l Key in that it does not show a
    character preview.
*/

Key {
    showPreview: false
    keyType: QtVirtualKeyboard.KeyType.NumberKey
}
