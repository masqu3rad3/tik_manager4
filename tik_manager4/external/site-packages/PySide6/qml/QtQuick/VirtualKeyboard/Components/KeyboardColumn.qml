// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick
import QtQuick.Layouts

/*!
    \qmltype KeyboardColumn
    \inqmlmodule QtQuick.VirtualKeyboard.Components
    \ingroup qmlclass
    \ingroup qtvirtualkeyboard-components-qml
    \inherits ColumnLayout

    \brief Keyboard column for keyboard layouts.

    This type can be used in special cases where multiple columns
    are added to a single keyboard layout.
*/

ColumnLayout {
    /*! Sets the key weight for all children keys.

        The default value is inherited from the parent element
        in the layout hierarchy.
    */
    property real keyWeight: parent ? parent.keyWeight : undefined

    /*! \since QtQuick.VirtualKeyboard 2.0

        Sets the \c smallTextVisible for all children keys.

        The default value is inherited from the parent element
        in the layout hierarchy.
    */
    property bool smallTextVisible: parent ? parent.smallTextVisible : false

    spacing: 0
}
