// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick

/*!
    \qmltype SelectionListItem
    \inqmlmodule QtQuick.VirtualKeyboard.Styles
    \brief A base type for selection list item delegates.
    \ingroup qmlclass
    \ingroup qtvirtualkeyboard-styles-qml

    The SelectionListItem enables mouse handling for the selection list item
    delegates.
*/

Item {
    id: selectionListItem
    height: ListView.view.height

    /*!
        \since QtQuick.VirtualKeyboard.Styles 1.1

        Sets the sound effect to be played on touch event.
    */
    property url soundEffect
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        onClicked: {
            if (index === -1)
                return
            selectionListItem.ListView.view.currentIndex = index
            selectionListItem.ListView.view.model.selectItem(index)
        }
        onPressAndHold: {
            if (index === -1)
                return
            if (typeof selectionListItem.ListView.view.longPressItem != "function")
                return
            selectionListItem.ListView.view.longPressItem(index)
        }
    }
}
