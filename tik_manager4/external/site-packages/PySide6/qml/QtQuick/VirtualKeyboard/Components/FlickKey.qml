// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick
import QtQuick.VirtualKeyboard

/*!
    \qmltype FlickKey
    \inqmlmodule QtQuick.VirtualKeyboard.Components
    \ingroup qmlclass
    \ingroup qtvirtualkeyboard-components-qml
    \ingroup qtvirtualkeyboard-key-types
    \inherits Key
    \since QtQuick.VirtualKeyboard 6.1

    \brief Flick key for keyboard layouts.

    Allows to enter an alternative character in a four-way gesture.
    Characters are taken from the alternate keys starting with the
    key at index \c 0 (excluding the main key text) and the positions
    are filled in the following order: left, top, bottom, right.
*/

Key {

    property int __key
    property string __text
    property point pt1
    readonly property real __centerRadius: width * 0.4
    readonly property var flickKeys: {
        var keys = InputContext.uppercase ? alternativeKeys.toUpperCase() : alternativeKeys.toLowerCase()
        var textIndex = keys.indexOf(InputContext.uppercase ? __text.toUpperCase() : __text.toLowerCase())
        if (textIndex === -1)
            return keys
        return keys.slice(0, textIndex).concat(keys.slice(textIndex + 1))
    }
    property string flickLeft: flickKeys.length > 0 ? flickKeys[0] : ""
    property string flickTop: flickKeys.length > 2 ? flickKeys[1] : ""
    property string flickBottom: flickKeys.length > 3 ? flickKeys[3] : (flickKeys.length > 2 ? flickKeys[2] : "")
    property string flickRight: flickKeys.length > 3 ? flickKeys[2] : (flickKeys.length === 2 ? flickKeys[1] : "")

    keyType: QtVirtualKeyboard.KeyType.FlickKey

    Component.onCompleted: {
        __key = key
        __text = text
    }

    onActiveChanged: {
        key = __key
        text = __text
    }

    function __angle(pt2) {
        var dx = pt2.x - pt1.x
        var dy = pt2.y - pt1.y
        var theta = Math.atan2(-dy, dx) * 360 / (2 * Math.PI)
        var theta_normalized = theta < 0 ? theta + 360 : theta
        return theta_normalized >= 360 ? 0 : theta_normalized
    }

    function __distance(pt2) {
        var dx = pt2.x - pt1.x
        dx = dx * dx
        var dy = pt2.y - pt1.y
        dy = dy * dy
        return Math.sqrt(dx + dy)
    }

    function press(x, y) {
        pt1 = Qt.point(x, y)
    }

    function update(x, y) {
        var pt = Qt.point(x, y)
        var distance = __distance(pt)
        if (distance < __centerRadius) {
            return
        }
        var currentText
        var angle = __angle(pt)
        if (angle < 45 || angle > 315) {
            currentText = flickRight
        } else if (angle < 135) {
            currentText = flickTop
        } else if (angle < 225) {
            currentText = flickLeft
        } else {
            currentText = flickBottom
        }
        if (currentText.length === 1 && text !== currentText) {
            key = currentText.toUpperCase().charCodeAt(0)
            text = currentText
        }
    }
}
