// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDEUTILS_H
#define PYSIDEUTILS_H

#include <sbkpython.h>

#include <pysidemacros.h>

#include <QtCore/qtclasshelpermacros.h>

QT_FORWARD_DECLARE_CLASS(QDebug)
QT_FORWARD_DECLARE_CLASS(QString)
QT_FORWARD_DECLARE_CLASS(QStringView)

namespace PySide
{

/// Check if self inherits from class_name
/// \param self Python object
/// \param class_name strict with the class name
/// \return Returns true if self object inherits from class_name, otherwise returns false
PYSIDE_API bool inherits(PyTypeObject *self, const char *class_name);

/// Given A PyObject representing Unicode data, returns an equivalent QString.
PYSIDE_API QString pyUnicodeToQString(PyObject *str);

/// Given a QString, return the PyObject repeesenting Unicode data.
PYSIDE_API PyObject *qStringToPyUnicode(QStringView s);

/// Given A PyObject representing ASCII or Unicode data, returns an equivalent QString.
PYSIDE_API QString pyStringToQString(PyObject *str);

/// Provide an efficient, correct PathLike interface.
PYSIDE_API QString pyPathToQString(PyObject *path);

/// Returns whether \a method is a compiled method (Nuitka).
/// \sa Shiboken::isCompiledMethod()
PYSIDE_API bool isCompiledMethod(PyObject *callback);

struct debugPyTypeObject
{
    PYSIDE_API explicit debugPyTypeObject(const PyTypeObject *o) noexcept;

    const PyTypeObject *m_object;
};

PYSIDE_API QDebug operator<<(QDebug debug, const debugPyTypeObject &o);

struct debugPyObject
{
    PYSIDE_API explicit debugPyObject(PyObject *o) noexcept;

    PyObject *m_object;
};

PYSIDE_API QDebug operator<<(QDebug debug, const debugPyObject &o);

struct debugPyBuffer
{
    PYSIDE_API explicit debugPyBuffer(Py_buffer *b) noexcept;

    Py_buffer *m_buffer;
};

PYSIDE_API QDebug operator<<(QDebug debug, const debugPyBuffer &b);

} //namespace PySide

#endif // PYSIDESTRING_H
