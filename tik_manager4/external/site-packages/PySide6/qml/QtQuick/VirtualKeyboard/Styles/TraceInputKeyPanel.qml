// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick

/*!
    \qmltype TraceInputKeyPanel
    \inqmlmodule QtQuick.VirtualKeyboard.Styles
    \brief A base type of the trace input key.
    \ingroup qmlclass
    \ingroup qtvirtualkeyboard-styles-qml
    \since QtQuick.VirtualKeyboard 2.0

    This type provides panel for decorating TraceInputKey
    items in the keyboard layout.
*/

Item {
    /*! Provides access to properties in TraceInputKey.

        A list of available properties in control:
        \list
            \li \c patternRecognitionMode Pattern recognition mode of this input area
            \li \c horizontalRulers A list of horizontal rulers
            \li \c verticalRulers A list of vertical rulers
            \li \c boundingBox Bounding box for the trace input
        \endlist
    */
    property Item control

    /*! Sets margins of the trace input area.

        The margins affect to the bounding box of the trace input area.
    */
    property real traceMargins
}
