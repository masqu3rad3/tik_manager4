// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick
import QtQuick.Layouts
import QtQuick.VirtualKeyboard

/*!
    \qmltype KeyboardLayout
    \inqmlmodule QtQuick.VirtualKeyboard.Components
    \ingroup qmlclass
    \ingroup qtvirtualkeyboard-components-qml
    \inherits ColumnLayout

    \brief Keyboard layout.

    This type is the root element of the keyboard layout.
    Use this element to build a new keyboard layout.

    Example:

    \code
    import QtQuick
    import QtQuick.Layouts
    import QtQuick.VirtualKeyboard

    // file: layouts/en_GB/main.qml

    KeyboardLayout {
        KeyboardRow {
            Key {
                key: Qt.Key_Q
                text: "q"
            }
            Key {
                key: Qt.Key_W
                text: "w"
            }
            Key {
                key: Qt.Key_E
                text: "e"
            }
            Key {
                key: Qt.Key_R
                text: "r"
            }
            Key {
                key: Qt.Key_T
                text: "t"
            }
            Key {
                key: Qt.Key_Y
                text: "y"
            }
        }
    }
    \endcode
*/

ColumnLayout {
    id: root

    /*! Sets the input method to be used in this layout.

        This property allows a custom input method to be
        used in this layout.
    */
    property var inputMethod

    /*! This function may be overridden by the keyboard layout
        to create the input method object dynamically. The default
        implementation returns \c null.

        The input method object created by this function can outlive
        keyboard layout transitions in certain cases. In particular,
        this applies to the transitions between the layouts listed in
        the sharedLayouts property.
    */
    function createInputMethod() {
        return null
    }

    /*! List of layout names which share the input method created
        by the createInputMethod() function.

        If the list is empty (the default) the input method is not
        shared with any other layout and will be destroyed when the
        layout changes.

        The list should contain only the name of the layout type,
        e.g., ['symbols']. The current layout does not have to be
        included in the list.
    */
    property var sharedLayouts

    /*! Sets the input mode to be used in this layout.

        By default, the virtual keyboard attempts to preserve
        the current input mode when switching to a different
        keyboard layout.

        If the current input mode is not valid in the current
        context, the default input mode is specified by the
        input method.
    */
    property int inputMode: -1

    /*! Sets the key weight for all children keys.

        The default value is inherited from the parent element
        in the layout hierarchy.
    */
    property real keyWeight

    /*! \since QtQuick.VirtualKeyboard 2.0

        Sets the \c smallTextVisible for all children keys.

        The default value is inherited from the parent element
        in the layout hierarchy.
    */
    property bool smallTextVisible

    spacing: 0

    function scanLayout() {
        var layout = {
            width: root.width,
            height: root.height,
            keys: []
        }
        __scanLayoutRecursive(this, layout)
        return layout
    }

    function __scanLayoutRecursive(parent, layout) {
        for (var i in parent.children) {
            var child = parent.children[i]
            if (child.keyType !== undefined) {
                var pos = mapFromItem(child, 0, 0)
                var key = {
                    left: pos.x,
                    top: pos.y,
                    width: child.width,
                    height: child.height,
                    keyType: child.keyType,
                    key: child.key,
                    text: child.text,
                    altKeys: child.effectiveAlternativeKeys,
                    isFunctionKey: child.functionKey,
                    noKeyEvent: child.noKeyEvent
                }
                if (key.left + key.width > layout.width)
                    layout.width = key.left + key.width
                if (key.top + key.height > layout.height)
                    layout.height = key.top + key.height
                layout.keys.push(key)
            } else {
                __scanLayoutRecursive(child, layout)
            }
        }
    }
}
