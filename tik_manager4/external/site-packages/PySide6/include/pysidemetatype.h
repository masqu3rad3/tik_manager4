// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDEMETATYPE_H
#define PYSIDEMETATYPE_H

#include <sbkpython.h>

#include <pysidemacros.h>

#include <QtCore/qtconfigmacros.h>

QT_FORWARD_DECLARE_CLASS(QMetaType)

namespace PySide
{

/// Returns the QMetaType matching a PyTypeObject
/// \param
/// \param type TypeObject
/// \return QMetaType
PYSIDE_API QMetaType qMetaTypeFromPyType(PyTypeObject *type);

} //namespace PySide

#endif // PYSIDEMETATYPE_H
