// Copyright (C) 2018 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDE_P_H
#define PYSIDE_P_H

#include <pysidemacros.h>

#include <dynamicqmetaobject.h>

namespace PySide
{

// Struct associated with QObject's via Shiboken::Object::getTypeUserData()
struct TypeUserData
{
    explicit TypeUserData(PyTypeObject* type,  const QMetaObject* metaobject, std::size_t size) :
        mo(type, metaobject), cppObjSize(size) {}

    MetaObjectBuilder mo;
    std::size_t cppObjSize;
};

TypeUserData *retrieveTypeUserData(PyTypeObject *pyTypeObj);
TypeUserData *retrieveTypeUserData(PyObject *pyObj);
// For QML
PYSIDE_API const QMetaObject *retrieveMetaObject(PyTypeObject *pyTypeObj);
PYSIDE_API const QMetaObject *retrieveMetaObject(PyObject *pyObj);

} //namespace PySide

#endif // PYSIDE_P_H
