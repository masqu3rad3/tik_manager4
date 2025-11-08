// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick

/*!
    \qmltype KeyIcon
    \inqmlmodule QtQuick.VirtualKeyboard.Styles
    \brief Key icon with adjustable color.
    \ingroup qmlclass
    \ingroup qtvirtualkeyboard-styles-qml

    The KeyIcon item displays an icon with adjustable color.
*/

Item {
    /*! The icon color. */
    property alias color: overlay.color
    /*! The source image. */
    property alias source: icon.source
    Image {
        id: icon
        sourceSize.height: parent.height
        sourceSize.width: parent.width
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        visible: false
    }
    ShaderEffect {
        id: overlay
        property color color
        property variant texture: icon
        anchors.fill: icon
        fragmentShader: "
            uniform lowp vec4 color;
            uniform lowp float qt_Opacity;
            uniform lowp sampler2D texture;
            varying highp vec2 qt_TexCoord0;
            void main() {
                highp vec4 sample = texture2D(texture, qt_TexCoord0) * qt_Opacity;
                gl_FragColor = vec4(color.rgb, 1.0) * sample.a;
            }
            "
    }
}
