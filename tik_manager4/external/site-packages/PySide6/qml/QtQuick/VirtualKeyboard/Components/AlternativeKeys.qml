// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick
import QtQuick.VirtualKeyboard

Item {
    property bool active: listView.currentIndex != -1
    property int highlightIndex: -1
    property alias listView: listView
    property int keyCode
    property point origin
    signal clicked
    LayoutMirroring.enabled: false
    LayoutMirroring.childrenInherit: true

    z: 1
    visible: active
    anchors.fill: parent

    ListModel {
        id: listModel
    }

    ListView {
        id: listView
        spacing: 0
        model: listModel
        delegate: keyboard.style.alternateKeysListDelegate
        highlight: keyboard.style.alternateKeysListHighlight ? keyboard.style.alternateKeysListHighlight : defaultHighlight
        highlightMoveDuration: 0
        highlightResizeDuration: 0
        keyNavigationWraps: true
        orientation: ListView.Horizontal
        height: keyboard.style ? keyboard.style.alternateKeysListItemHeight : 0
        x: origin.x
        y: keyboard.style ? origin.y - height - keyboard.style.alternateKeysListBottomMargin : 0
        Component {
            id: defaultHighlight
            Item {}
        }
    }

    Loader {
        id: backgroundLoader
        sourceComponent: keyboard.style.alternateKeysListBackground
        anchors.fill: listView
        z: -1
        states: State {
            name: "highlighted"
            when: highlightIndex !== -1 && highlightIndex === listView.currentIndex &&
                  backgroundLoader.item !== null && backgroundLoader.item.hasOwnProperty("currentItemHighlight")
            PropertyChanges {
                target: backgroundLoader.item
                currentItemHighlight: true
            }
        }
    }

    onClicked: {
        if (active && listView.currentIndex >= 0 && listView.currentIndex < listView.model.count) {
            var activeKey = listView.model.get(listView.currentIndex)
            InputContext.inputEngine.virtualKeyClick(keyCode, activeKey.data,
                                                     InputContext.uppercase ? Qt.ShiftModifier : 0)
        }
    }

    function open(key, originX, originY) {
        keyCode = key.key
        var alternativeKeys = key.effectiveAlternativeKeys
        var displayAlternativeKeys = key.displayAlternativeKeys
        if (alternativeKeys.length > 0 && displayAlternativeKeys.length === alternativeKeys.length) {
            for (var i = 0; i < alternativeKeys.length; i++) {
                listModel.append({
                                     "text": InputContext.uppercase ? displayAlternativeKeys[i].toUpperCase() : displayAlternativeKeys[i],
                                     "data": InputContext.uppercase ? alternativeKeys[i].toUpperCase() : alternativeKeys[i]
                                 })
            }
            listView.width = keyboard.style.alternateKeysListItemWidth * listModel.count
            listView.forceLayout()
            highlightIndex = key.effectiveAlternativeKeysHighlightIndex
            if (highlightIndex === -1) {
                console.log("AlternativeKeys: active key \"" + key.text + "\" not found in alternativeKeys \"" + alternativeKeys + ".\"")
                highlightIndex = 0
            }
            listView.currentIndex = highlightIndex
            var currentItemOffset = (listView.currentIndex + 0.5) * keyboard.style.alternateKeysListItemWidth
            origin = Qt.point(Math.min(Math.max(keyboard.style.alternateKeysListLeftMargin, originX - currentItemOffset), width - listView.width - keyboard.style.alternateKeysListRightMargin), originY)
            if (backgroundLoader.item && backgroundLoader.item.hasOwnProperty("currentItemOffset")) {
                backgroundLoader.item.currentItemOffset = currentItemOffset
            }
        }
        return active
    }

    function move(mouseX) {
        var newIndex = listView.indexAt(Math.max(1, Math.min(listView.width - 1, mapToItem(listView, mouseX, 0).x)), 1)
        if (newIndex !== listView.currentIndex) {
            listView.currentIndex = newIndex
        }
    }

    function close() {
        listView.currentIndex = -1
        listModel.clear()
    }
}
