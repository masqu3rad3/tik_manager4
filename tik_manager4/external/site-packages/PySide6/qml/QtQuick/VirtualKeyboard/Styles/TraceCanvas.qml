// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick
import "TraceUtils.js" as TraceUtils
import QtQuick.VirtualKeyboard

/*!
    \qmltype TraceCanvas
    \inqmlmodule QtQuick.VirtualKeyboard.Styles
    \brief A specialized Canvas type for rendering Trace objects.
    \ingroup qmlclass
    \ingroup qtvirtualkeyboard-styles-qml
    \inherits Canvas
    \since QtQuick.VirtualKeyboard 2.0

    This type provides capabilities for rendering Trace objects on the screen.

    To make the Trace rendering available in the keyboard, this type must be
    declared as the \l {KeyboardStyle::traceCanvasDelegate}
    {KeyboardStyle.traceCanvasDelegate} component.

    \code
        traceCanvasDelegate: TraceCanvas {
        }
    \endcode

    Custom drawing attributes can be initialized in the Canvas.available
    signal. For example:

    \code
        onAvailableChanged: {
            if (!available)
                return;
            var ctx = getContext("2d")
            ctx.lineWidth = 8 * scaleHint
            ctx.lineCap = "round"
            ctx.strokeStyle = Qt.rgba(0xFF, 0xFF, 0xFF)
            ctx.fillStyle = ctx.strokeStyle
        }
    \endcode

    The type offers built-in options for Trace rendering. Currently
    the following rendering options are available:

    \list
        \li \c renderSmoothedLine Renders smoothed line with round corners (the default)
    \endlist

    The rendering function can be changed with the renderFunction property.

    \code
        renderFunction: renderSmoothedLine
    \endcode

    Custom rendering function is also supported. Consider the following example:

    \code
        renderFunction: renderCustomLine

        function renderCustomLine() {
            getContext("2d")
            var points = trace.points()

            ...
        }
    \endcode
*/

Canvas {
    id: canvas

    /*! Provides access to \l Trace object.
    */
    property Trace trace

    /*! Enables auto destruction mode.

        If enabled, this item will be destroyed when the \c trace object is
        destroyed.

        The default value is false. In this case the canvas can be reused after
        onRecycle signal is triggered.
    */
    property bool autoDestroy

    /*! Specifies the approximate delay in milliseconds, counted from the beginning of the
        auto destruction, before the object is to be destroyed or recycled.

        This delay makes it possible, for example, to animate the item before destruction.

        The default value is 0.
    */
    property int autoDestroyDelay

    /*! This property defines the rendering function.

        The default value is \c renderSmoothedLine
    */
    property var renderFunction: renderSmoothedLine

    property int __renderPos

    property bool __renderingEnabled

    /*! Renders smoothed line with round corners.

        This function is incremental and renders only the new part added to the Trace.

        This function does not alter any of the canvas attributes (i.e. they can be set elsewhere.)
    */
    function renderSmoothedLine() {
        __renderPos = TraceUtils.renderSmoothedLine(getContext("2d"), trace, __renderPos)
    }

    /*! Clears screen and resets the rendering.

        \since QtQuick.VirtualKeyboard.Styles 6.1
    */
    function renderClear() {
        var ctx = getContext("2d")
        ctx.clearRect(0, 0, width, height)
        __renderPos = 0
    }

    /*! Recycles trace canvas by clearing all drawings and resetting the variables.

        The function triggers onRecycle signal after completed (before the return).

        The function returns true when recycling is successful.

        \since QtQuick.VirtualKeyboard.Styles 6.1
    */
    function recycle() {
        if (!available) {
            destroy()
            return false
        }

        trace = null
        recycleTimer.stop()
        opacity = Qt.binding(function() {
            return trace ? trace.opacity : 1.0
        })
        requestAnimationFrame(renderClear)
        onRecycle(canvas)

        return true
    }

    /*! Emitted when the \a traceCanvas is recycled.

        \since QtQuick.VirtualKeyboard.Styles 6.1
    */
    signal onRecycle(var traceCanvas)

    Timer {
        id: recycleTimer
        interval: canvas.autoDestroyDelay
        onTriggered: canvas.recycle()
    }

    onTraceChanged: {
        if (trace === null) {
            if (autoDestroy || !available)
                destroy(autoDestroyDelay)
            else
                recycleTimer.restart()
        }
    }

    onAvailableChanged: {
        __renderingEnabled = available
        if (__renderingEnabled)
            requestAnimationFrame(renderFunction)
    }

    Connections {
        target: canvas.__renderingEnabled && trace ? trace : null
        function onLengthChanged() { if (renderFunction) canvas.requestAnimationFrame(renderFunction) }
        function onFinalChanged() { if (renderFunction) canvas.requestAnimationFrame(renderFunction) }
    }

    opacity: trace ? trace.opacity : 1.0

    Behavior on opacity {
        NumberAnimation {
            duration: 1500
            easing.type: Easing.InOutQuad
        }
    }
}
