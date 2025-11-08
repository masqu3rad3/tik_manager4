// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick

/*!
    \qmltype KeyPanel
    \inqmlmodule QtQuick.VirtualKeyboard.Styles
    \brief A base type of the styled keys.
    \ingroup qmlclass
    \ingroup qtvirtualkeyboard-styles-qml

    All the key delegates provided by the style should be based on this type.
*/

Item {
    /*! Provides access to properties in BaseKey.

        A list of available properties in control:
        \list
            \li \c control.key Unicode code of the key.
            \li \c control.text Unicode text of the key.
            \li \c control.displayText Display text of the key.
            \li \c control.smallText Small text of the key, usually rendered in the corner of the key.
            \li \c control.smallTextVisible Visibility of the small text.
            \li \c control.alternativeKeys List of alternative key sequences.
            \li \c control.enabled Set to true when the key is enabled.
            \li \c control.pressed Set to true when the key is currently pressed.
            \li \c control.uppercased Set to true when the key is uppercased.
        \endlist
    */
    property Item control

    /*!
        \since QtQuick.VirtualKeyboard.Styles 1.1

        Sets the sound effect to be played on key press.
    */
    property url soundEffect

    // Uncomment the following to reveal the key sizes
    /*
    Rectangle {
        id: root
        z: 1
        color: "transparent"
        border.color: "white"
        anchors.fill: parent
        Rectangle {
            color: "black"
            opacity: 0.6
            anchors.top: parent.top
            anchors.topMargin: 1
            anchors.left: parent.left
            anchors.leftMargin: 1
            implicitWidth: keyPanelInfoText.width + 4
            implicitHeight: keyPanelInfoText.height + 4
            Text {
                id: keyPanelInfoText
                property point pos: keyboard.keyboardLayoutLoader.item.mapFromItem(root.parent, 0, 0)
                text: "(%1,%2)\n%3x%4\nweight: %5".arg(pos.x).arg(pos.y).arg(root.parent.width).arg(root.parent.height).arg(root.parent.control.weight)
                font.pixelSize: 12
                color: "white"
                anchors.centerIn: parent
            }
        }
    }
    */
}
