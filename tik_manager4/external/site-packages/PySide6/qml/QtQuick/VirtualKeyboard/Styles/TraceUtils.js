// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

.pragma library

function renderSmoothedLine(ctx, trace, renderPos) {

    if (!trace)
        return renderPos

    if (renderPos >= trace.length)
        return renderPos

    // Fetch points and draw the initial "dot"
    var points, tp
    if (renderPos === 0) {
        points = trace.points()
        tp = points[renderPos++]
        ctx.beginPath()
        ctx.moveTo(tp.x, tp.y)
        ctx.lineTo(tp.x, tp.y + 0.000001)
        ctx.stroke()
    } else {
        points = trace.points(renderPos - 1)
    }

    // Draw smoothed line using quadratic curve
    var i = 1
    if (i + 1 < points.length) {
        var pt1, pt2
        if (renderPos === 1) {
            tp = points[i - 1]
        } else {
            pt1 = points[i - 1]
            pt2 = points[i]
            tp = Qt.point((pt1.x + pt2.x) / 2, (pt1.y + pt2.y) / 2)
        }
        ctx.beginPath()
        ctx.moveTo(tp.x, tp.y)
        while (i + 1 < points.length) {
            pt1 = points[i++]
            pt2 = points[i]
            tp = Qt.point((pt1.x + pt2.x) / 2, (pt1.y + pt2.y) / 2)
            ctx.quadraticCurveTo(pt1.x, pt1.y, tp.x, tp.y)
            ctx.moveTo(tp.x, tp.y)
        }
        ctx.stroke()
    }

    // Draw the remainder of the line
    if (trace.final) {
        if (i < points.length) {
            tp = points[i - 1]
            ctx.beginPath()
            ctx.moveTo(tp.x, tp.y)
            tp = points[i++]
            ctx.lineTo(tp.x, tp.y)
            ctx.stroke()
        }
    }

    return renderPos + i - 1
}
