// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDEQOBJECT_H
#define PYSIDEQOBJECT_H

#include <sbkpython.h>

#include <pysidemacros.h>

#include <QtCore/qtclasshelpermacros.h>

#include <cstddef>

QT_FORWARD_DECLARE_CLASS(QObject)
QT_FORWARD_DECLARE_STRUCT(QMetaObject)
QT_FORWARD_DECLARE_CLASS(QMutex)

namespace PySide
{

/// Fill QObject properties and do signal connections using the values found in \p kwds dictionary.
/// \param qObj PyObject fot the QObject.
/// \param metaObj QMetaObject of \p qObj.
/// \param kwds key->value dictonary.
/// \return True if everything goes well, false with a Python error set otherwise.
PYSIDE_API bool fillQtProperties(PyObject *qObj, const QMetaObject *metaObj,
                                 PyObject *kwds, bool allowErrors);

PYSIDE_API void initDynamicMetaObject(PyTypeObject *type, const QMetaObject *base,
                                      std::size_t cppObjSize);
PYSIDE_API void initQObjectSubType(PyTypeObject *type, PyObject *args, PyObject *kwds);

/// Return the size in bytes of a type that inherits QObject.
PYSIDE_API std::size_t getSizeOfQObject(PyTypeObject *type);

/// Check if a PyTypeObject or its bases contains a QObject
/// \param pyType is the PyTypeObject to check
/// \param raiseError controls if a TypeError is raised when an object does not
/// inherit QObject
PYSIDE_API bool isQObjectDerived(PyTypeObject *pyType, bool raiseError);

/// Convenience to convert a PyObject to QObject
PYSIDE_API QObject *convertToQObject(PyObject *object, bool raiseError);

/// Check for properties and signals registered on MetaObject and return these.
/// Also handle Python properties when true_property was selected.
/// \param cppSelf Is the QObject which contains the metaobject
/// \param self Python object of cppSelf
/// \param name Name of the argument which the function will try retrieve from MetaData
/// \return The Python object which contains the Data obtained in metaObject or the Python
/// method pulled out of a Python property.
PYSIDE_API PyObject *getHiddenDataFromQObject(QObject *cppSelf, PyObject *self, PyObject *name);

/// Mutex for accessing QObject memory helpers from multiple threads
PYSIDE_API QMutex &nextQObjectMemoryAddrMutex();
PYSIDE_API void *nextQObjectMemoryAddr();
/// Set the address where to allocate the next QObject (for QML)
PYSIDE_API void setNextQObjectMemoryAddr(void *addr);

PYSIDE_API PyObject *getWrapperForQObject(QObject *cppSelf, PyTypeObject *sbk_type);

/// Return the best-matching type for a QObject (Helper for QObject.findType())
/// \param cppSelf QObject instance
/// \return type object
PYSIDE_API PyTypeObject *getTypeForQObject(const QObject *cppSelf);

} //namespace PySide

#endif // PYSIDEQOBJECT_H
