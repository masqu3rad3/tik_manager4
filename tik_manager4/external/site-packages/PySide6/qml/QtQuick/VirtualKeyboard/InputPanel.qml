// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick
// Deliberately imported after QtQuick to avoid missing restoreMode property in Binding. Fix in Qt 6.
import QtQml
import QtQuick.VirtualKeyboard
import QtQuick.VirtualKeyboard.Components

/*!
    \qmltype InputPanel
    \inqmlmodule QtQuick.VirtualKeyboard

    \brief Provides the virtual keyboard UI.
    \ingroup qmlclass
    \ingroup qtvirtualkeyboard-qml

    The keyboard size is automatically calculated from the available
    width; that is, the keyboard maintains the aspect ratio specified by the current
    style. Therefore the application should only set the \l {Item::}{width} and \l {Item::}{y}
    coordinates of the InputPanel, and not the \l {Item::}{height}.

    As with \l {Qt Virtual Keyboard QML Types}{all other QML types} provided by
    the module, the \c QT_IM_MODULE environment variable must be set to
    \c qtvirtualkeyboard before using InputPanel. For more information, see
    \l {Loading the Plugin}.

    \note You can have only one InputPanel instance in your application. The panel
    will not be blocked by modal dialogs, but it can be obscured by items with a higher
    \l {Item::}{z} value.
*/

Item {
    id: inputPanel

    /*!
        \qmlproperty bool InputPanel::active
        \since QtQuick.VirtualKeyboard 2.0

        This property reflects the active status of the input panel.
        The keyboard should be made visible to the user when this property is
        \c true.
    */
    property alias active: keyboard.active

    /*!
        \qmlproperty bool InputPanel::externalLanguageSwitchEnabled
        \since QtQuick.VirtualKeyboard 2.4

        This property enables the external language switch mechanism.
        When this property is \c true, the virtual keyboard will not show
        the built-in language popup, but will emit the \l externalLanguageSwitch
        signal instead. The application can handle this signal and show a
        custom language selection dialog instead.
    */
    property bool externalLanguageSwitchEnabled

    /*!
        \qmlsignal InputPanel::externalLanguageSwitch(var localeList, int currentIndex)
        \since QtQuick.VirtualKeyboard 2.4

        This signal is emitted when \l externalLanguageSwitchEnabled is \c true
        and the \l {user-guide-language}{language switch key} is pressed by the user.

        It serves as a hook to display a custom language dialog instead of
        the built-in language popup in the virtual keyboard.

        The \a localeList parameter contains a list of locale names to choose
        from. To get more information about a particular language, use the
        \l[QtQml]{Qt::locale()}{Qt.locale()} function. The \a currentIndex
        is the index of current locale in the \a localeList. This item should
        be highlighted as the current item in the UI.

        To select a new language, use the \l {VirtualKeyboardSettings::locale}
        {VirtualKeyboardSettings.locale} property.

        Below is an example that demonstrates a custom language dialog implementation:

        \snippet qtvirtualkeyboard-custom-language-popup.qml popup

        The dialog would then be declared:

        \snippet qtvirtualkeyboard-custom-language-popup.qml declaring

        In the application's InputPanel, add the following code:

        \snippet qtvirtualkeyboard-custom-language-popup.qml using

        The custom dialog will now be shown when the language switch key is pressed.
    */
    signal externalLanguageSwitch(var localeList, int currentIndex)

    /*! \internal */
    property alias keyboard: keyboard

    /*! \internal */
    property bool desktopPanel: false

    /*! \internal */
    property point screenPos: desktopPanel ? Qt.point(keyboard.x, keyboard.y) : Qt.point(x, y)

    SelectionControl {
        objectName: "selectionControl"
        x: -parent.x
        y: -parent.y
        enabled: active && !keyboard.fullScreenMode && !desktopPanel
    }

    implicitHeight: keyboard.height - keyboard.wordCandidateView.currentYOffset
    Keyboard {
        id: keyboard
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
    }
    MouseArea {
        z: -1
        anchors.fill: keyboard
        enabled: active
        hoverEnabled: active
    }

    Binding {
        target: InputContext.priv
        property: "keyboardRectangle"
        value: keyboardRectangle()
        when: !InputContext.animating
        restoreMode: Binding.RestoreBinding
    }

    /*! \internal */
    function keyboardRectangle() {
        var rect = Qt.rect(0, 0, keyboard.width, keyboard.height - keyboard.wordCandidateView.currentYOffset)
        const screenPosX = screenPos.x
        const screenPosY = screenPos.y + keyboard.wordCandidateView.currentYOffset
        if (desktopPanel) {
            rect.x += screenPosX
            rect.y += screenPosY
        }
        return mapToItem(null, rect)
    }
}
