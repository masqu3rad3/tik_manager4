// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef CLASS_PROPERTY_H
#define CLASS_PROPERTY_H

#include "pysidemacros.h"
#include <sbkpython.h>

extern "C" {

struct propertyobject {
    PyObject_HEAD
    PyObject *prop_get;
    PyObject *prop_set;
    PyObject *prop_del;
    PyObject *prop_doc;
    int getter_doc;
};

struct propertyobject310 {
    PyObject_HEAD
    PyObject *prop_get;
    PyObject *prop_set;
    PyObject *prop_del;
    PyObject *prop_doc;
    // Note: This is a problem with Limited API: We have no direct access.
    //       You need to pick it from runtime info.
    PyObject *prop_name;
    int getter_doc;
};

PYSIDE_API PyTypeObject *PyClassProperty_TypeF();

} // extern "C"

namespace PySide::ClassProperty {

PYSIDE_API void init(PyObject *module);

} // namespace PySide::ClassProperty

#endif // CLASS_PROPERTY_H
