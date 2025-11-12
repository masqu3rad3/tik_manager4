// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick
import QtQuick.VirtualKeyboard
import QtQuick.VirtualKeyboard.Settings

Item {
    property bool active
    property alias listView: listView
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
        currentIndex: -1
        delegate: keyboard.style.functionPopupListDelegate
        highlight: keyboard.style.functionPopupListHighlight ? keyboard.style.functionPopupListHighlight : defaultHighlight
        highlightMoveDuration: 0
        highlightResizeDuration: 0
        keyNavigationWraps: true
        orientation: ListView.Horizontal
        width: contentItem.childrenRect.width
        height: contentItem.childrenRect.height
        x: {
            var result = origin.x
            if (count > 0) {
                const item = itemAtIndex(0)
                if (item) {
                    result -= Math.round(item.width / 2)
                }
            }
            return result
        }
        y: origin.y - height
        Component {
            id: defaultHighlight
            Item {}
        }
    }

    Loader {
        id: backgroundLoader
        sourceComponent: keyboard.style.functionPopupListBackground
        anchors.fill: listView
        z: -1
        Binding {
            target: backgroundLoader.item
            property: "view"
            value: listView
            when: backgroundLoader.item && backgroundLoader.item.hasOwnProperty("view")
        }
    }

    onClicked: {
        if (active && listView.currentIndex >= 0 && listView.currentIndex < listView.model.count) {
            const listElement = listView.model.get(listView.currentIndex)
            keyboard.doKeyboardFunction(listElement.keyboardFunction)
        }
    }

    function open(key, originX, originY) {
        listModel.clear()
        for (const keyboardFunction of [
                 QtVirtualKeyboard.KeyboardFunction.HideInputPanel,
                 QtVirtualKeyboard.KeyboardFunction.ChangeLanguage,
                 QtVirtualKeyboard.KeyboardFunction.ToggleHandwritingMode,
             ]) {
            const functionKey = InputContext.priv.keyboardFunctionKey(keyboardFunction)
            if (keyboard.isKeyboardFunctionAvailable(keyboardFunction) &&
                    !(VirtualKeyboardSettings.visibleFunctionKeys & functionKey)) {
                const listElement = {
                    keyboardFunction: keyboardFunction
                }
                listModel.append(listElement)
            }
        }
        listView.currentIndex = (listModel.count > 0) ? 0 : -1
        origin = Qt.binding(function() {
            return Qt.point(Math.min(Math.max(0, originX), width - listView.width), originY)
        })
        active = listView.currentIndex !== -1
        return active
    }

    function move(pt) {
        var listPt = mapToItem(listView, pt.x, pt.y)
        var newIndex = listView.indexAt(listPt.x, Math.max(1, Math.min(listView.height - 1, listPt.y)))
        if (newIndex !== listView.currentIndex) {
            listView.currentIndex = newIndex
        }
    }

    function close() {
        listView.currentIndex = -1
        active = false
    }
}
