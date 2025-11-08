// Copyright (C) 2018 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

// @snippet qtquick
PySide::initQuickSupport(module);
// @snippet qtquick

// @snippet qsgeometry-vertexdataaspoint2d
auto *points = %CPPSELF->vertexDataAsPoint2D();
const Py_ssize_t vertexCount = %CPPSELF->vertexCount();
%PYARG_0 = PyList_New(vertexCount);
for (Py_ssize_t i = 0; i < vertexCount; ++i) {
    QSGGeometry::Point2D p = points[i];
    PyList_SetItem(%PYARG_0, i, %CONVERTTOPYTHON[QSGGeometry::Point2D](p));
}
// @snippet qsgeometry-vertexdataaspoint2d

// @snippet qsgeometry-setvertexdataaspoint2d
const qsizetype vertexCount = %CPPSELF->vertexCount();
if (vertexCount != %1.size()) {
    PyErr_SetString(PyExc_RuntimeError, "size mismatch");
    return {};
}

QSGGeometry::Point2D *points = %CPPSELF->vertexDataAsPoint2D();
std::copy(%1.cbegin(), %1.cend(), points);
// @snippet qsgeometry-setvertexdataaspoint2d
