// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick
import QtQuick.VirtualKeyboard

/*!
    \qmltype KeyboardLayoutLoader
    \inqmlmodule QtQuick.VirtualKeyboard.Components
    \ingroup qmlclass
    \ingroup qtvirtualkeyboard-components-qml
    \inherits Loader
    \since QtQuick.VirtualKeyboard 1.1

    \brief Allows dynamic loading of keyboard layout.

    This type is useful for keyboard layouts consisting of multiple pages of keys.

    A single keyboard layout (a page) is defined by using the Component
    as a container. The active keyboard layout can then be changed by
    setting the sourceComponent property to a different value.

    Example:

    \code
    import QtQuick
    import QtQuick.Layouts
    import QtQuick.VirtualKeyboard

    // file: layouts/en_GB/symbols.qml

    KeyboardLayoutLoader {
        property bool secondPage
        onVisibleChanged: if (!visible) secondPage = false
        sourceComponent: secondPage ? page2 : page1
        Component {
            id: page1
            KeyboardLayout {
                // Keyboard layout definition for page 1
            }
        }
        Component {
            id: page2
            KeyboardLayout {
                // Keyboard layout definition for page 2
            }
        }
    }
    \endcode
*/

Loader {
    /*! Sets the input method for all the keyboard layouts loaded
        in this context.

        The input method can either be set separately for each keyboard
        layout, or commonly at this context. If set separately, then this
        property should not be modified.
    */
    property var inputMethod: item ? item.inputMethod : null

    /*! This function may be overridden by the keyboard layout
        to create the input method object dynamically. The default
        implementation forwards the call to the child keyboard
        layout.

        The input method object created by this function can outlive
        keyboard layout transitions in certain cases. In particular,
        this applies to the transitions between the layouts listed in
        the sharedLayouts property.
    */
    function createInputMethod() {
        return item ? item.createInputMethod() : null
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
    property var sharedLayouts: item ? item.sharedLayouts : null

    /*! Sets the input mode for all the keyboard layouts loaded
        in this context.

        The input mode can either be set separately for each keyboard
        layout, or commonly at this context. If set separately, then this
        property should not be modified.
    */
    property int inputMode: item ? item.inputMode : -1

    property int __updateCount

    active: parent !== null

    onItemChanged: {
        if (parent && item && __updateCount++ > 0) {
            if (!keyboard.inputMethodNeedsReset)
                keyboard.updateInputMethod()
            keyboard.notifyLayoutChanged()
        }
    }

    function scanLayout() {
        if (item === null)
            return null
        return item.scanLayout()
    }
}
