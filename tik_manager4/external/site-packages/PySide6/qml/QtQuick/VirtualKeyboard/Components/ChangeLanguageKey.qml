// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick
import QtQuick.VirtualKeyboard
import QtQuick.VirtualKeyboard.Settings

/*!
    \qmltype ChangeLanguageKey
    \inqmlmodule QtQuick.VirtualKeyboard.Components
    \ingroup qmlclass
    \ingroup qtvirtualkeyboard-components-qml
    \ingroup qtvirtualkeyboard-key-types
    \inherits BaseKey

    \brief Change language key for keyboard layouts.

    This key changes the current input language in the list of supported
    languages. The key has two function modes:

    \list
        \li Popup mode
        \li Toggle mode
    \endlist

    The popup mode is enabled by the \l {KeyboardStyle::languagePopupListEnabled} property.
    If enabled, a key press will open a popup list with available languages. Otherwise
    it will cycle to the next available input language.
*/

BaseKey {
    /*! If this property is true, the input language is only
        changed between the languages providing custom layout.

        For example, if only the English and Arabic languages
        provide digits layout, then other locales using the
        shared default layout are ignored.

        The default is false.
    */
    property bool customLayoutsOnly: false

    id: changeLanguageKey
    keyType: QtVirtualKeyboard.KeyType.ChangeLanguageKey
    objectName: "changeLanguageKey"
    functionKey: true
    highlighted: true
    displayText: keyboard.locale.split("_")[0]
    keyPanelDelegate: keyboard.style ? keyboard.style.languageKeyPanel : undefined
    onClicked: keyboard.doKeyboardFunction(QtVirtualKeyboard.KeyboardFunction.ChangeLanguage, customLayoutsOnly)
    enabled: keyboard.isKeyboardFunctionAvailable(QtVirtualKeyboard.KeyboardFunction.ChangeLanguage, customLayoutsOnly)
    visible: VirtualKeyboardSettings.visibleFunctionKeys & QtVirtualKeyboard.KeyboardFunctionKeys.Language
}
