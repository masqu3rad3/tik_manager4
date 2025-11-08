// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick
import QtQuick.VirtualKeyboard

/*!
    \qmltype FillerKey
    \inqmlmodule QtQuick.VirtualKeyboard.Components
    \ingroup qmlclass
    \ingroup qtvirtualkeyboard-components-qml
    \ingroup qtvirtualkeyboard-key-types
    \inherits BaseKey

    \brief Filler key for keyboard layouts.

    This key can be used as a filler in the keyboard layout.
*/

BaseKey {
    keyType: QtVirtualKeyboard.KeyType.FillerKey
    showPreview: false
}
