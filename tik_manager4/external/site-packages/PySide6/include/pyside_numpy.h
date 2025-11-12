// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDE_NUMPY_H
#define PYSIDE_NUMPY_H

#include <sbkpython.h>
#include <sbknumpycheck.h>

#include <pysidemacros.h>

#include <QtCore/qlist.h>
#include <QtCore/qpoint.h>
#include <QtCore/qpoint.h>

namespace PySide::Numpy
{

/// Create a list of QPointF from 2 equally sized numpy array of x and y data
/// (float,double).
/// \param pyXIn X data array
/// \param pyYIn Y data array
/// \return List of QPointF

PYSIDE_API QList<QPointF> xyDataToQPointFList(PyObject *pyXIn, PyObject *pyYIn);

/// Create a list of QPoint from 2 equally sized numpy array of x and y data
/// (int).
/// \param pyXIn X data array
/// \param pyYIn Y data array
/// \return List of QPoint

PYSIDE_API QList<QPoint> xyDataToQPointList(PyObject *pyXIn, PyObject *pyYIn);

} //namespace PySide::Numpy

#endif // PYSIDE_NUMPY_H
