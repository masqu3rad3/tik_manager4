// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDE_PROPERTY_H
#define PYSIDE_PROPERTY_H

#include <pysidemacros.h>

#include <sbkpython.h>

#include <QtCore/qmetaobject.h>

class PySidePropertyPrivate;

extern "C"
{
    extern PYSIDE_API PyTypeObject *PySideProperty_TypeF(void);

    struct PYSIDE_API PySideProperty
    {
        PyObject_HEAD
        PySidePropertyPrivate* d;
    };
};

namespace PySide::Property {

PYSIDE_API bool checkType(PyObject *pyObj);

/**
 * This function call set property function and pass value as arg
 * This function does not check the property object type
 *
 * @param   self The property object
 * @param   source The QObject witch has the property
 * @param   value The value to set in property
 * @return  Return 0 if ok or -1 if this function fail
 **/
PYSIDE_API int setValue(PySideProperty *self, PyObject *source, PyObject *value);

/**
 * This function call get property function
 * This function does not check the property object type
 *
 * @param   self The property object
 * @param   source The QObject witch has the property
 * @return  Return the result of property get function or 0 if this fail
 **/
PYSIDE_API PyObject *getValue(PySideProperty *self, PyObject *source);

/**
 * This function return the notify name used on this property
 *
 * @param   self The property object
 * @return  Return a const char with the notify name used
 **/
PYSIDE_API const char *getNotifyName(PySideProperty *self);


/**
 * This function search in the source object for desired property
 *
 * @param   source The QObject object
 * @param   name The property name
 * @return  Return a new reference to property object
 **/
PYSIDE_API PySideProperty *getObject(PyObject *source, PyObject *name);

PYSIDE_API void setTypeName(PySideProperty *self, const char *typeName);

} //namespace PySide::Property

#endif
