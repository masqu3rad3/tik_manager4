// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick
import QtQuick.Layouts

/*!
    \qmltype TraceInputKey
    \inqmlmodule QtQuick.VirtualKeyboard.Components
    \ingroup qmlclass
    \ingroup qtvirtualkeyboard-components-qml
    \ingroup qtvirtualkeyboard-key-types
    \inherits Item
    \since QtQuick.VirtualKeyboard 2.0

    \brief A specialized key for collecting touch input data.

    This type can be placed in the keyboard layout. It collects
    and renders touch input data (trace) from the key area.
*/

Item {
    id: traceInputKey

    /*! Sets the key weight value which determines the relative size of the key.

        Use this property to change the key size in the layout.

        The default value is inherited from the parent element
        of the key in the layout hierarchy.
    */
    property real weight: parent.keyWeight

    /*! Pattern recognition mode of this input area.

        The default value is \l {InputEngine::patternRecognitionModes} {InputEngine.PatternRecognitionMode.None}.
    */
    property alias patternRecognitionMode: traceInputArea.patternRecognitionMode

    /*! List of horizontal rulers in the input area.

        The rulers are defined as a number of pixels from the top edge of the bounding box.

        Here is an example that demonstrates how to define rulers:

        \code
            horizontalRulers: [boundingBox.height / 3, boundingBox.height / 3 * 2]
            verticalRulers: [boundingBox.width / 3, boundingBox.width / 3 * 2]
        \endcode
    */
    property alias horizontalRulers: traceInputArea.horizontalRulers

    /*! List of vertical rulers in the input area.

        The rulers are defined as a number of pixels from the left edge of the bounding box.
    */
    property alias verticalRulers: traceInputArea.verticalRulers

    /*! Bounding box for the trace input.

        This property is readonly and is automatically updated based on the item size
        and margins.
    */
    readonly property alias boundingBox: traceInputArea.boundingBox

    /*! Canvas type of this trace input area.

        This property can be used to distinguish between different types of canvases.
        The default value is \c "keyboard".
    */
    property alias canvasType: traceInputArea.canvasType

    Layout.minimumWidth: traceInputKeyPanel.implicitWidth
    Layout.minimumHeight: traceInputKeyPanel.implicitHeight
    Layout.preferredWidth: weight
    Layout.fillWidth: true
    Layout.fillHeight: true
    canvasType: "keyboard"

    Loader {
        id: traceInputKeyPanel
        sourceComponent: keyboard.style.traceInputKeyPanelDelegate
        anchors.fill: parent
        onLoaded: traceInputKeyPanel.item.control = traceInputKey
    }

    TraceInputArea {
        id: traceInputArea
        anchors.fill: traceInputKeyPanel
        anchors.margins: traceInputKeyPanel.item ? traceInputKeyPanel.item.traceMargins : 0
    }
}
