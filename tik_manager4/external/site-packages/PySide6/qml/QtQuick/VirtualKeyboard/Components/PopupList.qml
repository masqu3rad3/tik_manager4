// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick
import QtQuick.VirtualKeyboard

ListView {
    property int maxVisibleItems: 5
    readonly property int preferredVisibleItems: count < maxVisibleItems ? count : maxVisibleItems
    readonly property real contentWidth: contentItem.childrenRect.width
    property alias defaultHighlight: defaultHighlight

    clip: true
    visible: enabled && count > 0
    width: contentWidth
    height: currentItem ? currentItem.height * preferredVisibleItems + (spacing * preferredVisibleItems - 1) : 0
    orientation: ListView.Vertical
    snapMode: ListView.SnapToItem
    delegate: keyboard.style.popupListDelegate
    highlight: keyboard.style.popupListHighlight ? keyboard.style.popupListHighlight : defaultHighlight
    highlightMoveDuration: 0
    highlightResizeDuration: 0
    add: !keyboard.noAnimations ? keyboard.style.popupListAdd : null
    remove: !keyboard.noAnimations ? keyboard.style.popupListRemove : null
    keyNavigationWraps: true

    onCurrentItemChanged: if (currentItem) keyboard.soundEffect.register(currentItem.soundEffect)

    Component {
        id: defaultHighlight
        Item {}
    }
}
