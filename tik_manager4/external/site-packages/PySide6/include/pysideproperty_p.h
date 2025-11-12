// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDE_QPROPERTY_P_H
#define PYSIDE_QPROPERTY_P_H

#include <sbkpython.h>

#include "pysideproperty.h"
#include <pysidemacros.h>

#include <QtCore/qbytearray.h>
#include <QtCore/qtclasshelpermacros.h>
#include <QtCore/qmetaobject.h>

struct PySideProperty;

class PYSIDE_API PySidePropertyPrivate
{
public:

    Q_DISABLE_COPY_MOVE(PySidePropertyPrivate)

    PySidePropertyPrivate() noexcept;
    virtual ~PySidePropertyPrivate();

    virtual void metaCall(PyObject *source, QMetaObject::Call call, void **args);

    PyObject *getValue(PyObject *source) const;
    int setValue(PyObject *source, PyObject *value);
    int reset(PyObject *source);

    QByteArray typeName;
    // Type object: A real PyTypeObject ("@Property(int)") or a string
    // "@Property('QVariant')".
    PyObject *pyTypeObject = nullptr;
    PyObject *fget = nullptr;
    PyObject *fset = nullptr;
    PyObject *freset = nullptr;
    PyObject *fdel = nullptr;
    PyObject *notify = nullptr;
    bool getter_doc = false;
    QByteArray notifySignature;
    QByteArray doc;
    bool designable = true;
    bool scriptable = true;
    bool stored = true;
    bool user = false;
    bool constant = false;
    bool final = false;
};

namespace PySide::Property {

/**
 * Init PySide QProperty support system
 */
void init(PyObject* module);

/**
 * This function call reset property function
 * This function does not check the property object type
 *
 * @param   self The property object
 * @param   source The QObject witch has the property
 * @return  Return 0 if ok or -1 if this function fail
 **/
int reset(PySideProperty* self, PyObject* source);


/**
 * This function return the property type
 * This function does not check the property object type
 *
 * @param   self The property object
 * @return  Return the property type name
 **/
const char* getTypeName(const PySideProperty* self);

/**
 * This function check if property has read function
 * This function does not check the property object type
 *
 * @param   self The property object
 * @return  Return a boolean value
 **/
bool isReadable(const PySideProperty* self);

/**
 * This function check if property has write function
 * This function does not check the property object type
 *
 * @param   self The property object
 * @return  Return a boolean value
 **/
bool isWritable(const PySideProperty* self);

/**
 * This function check if property has reset function
 * This function does not check the property object type
 *
 * @param   self The property object
 * @return  Return a boolean value
 **/
bool hasReset(const PySideProperty* self);

/**
 * This function check if property has the flag DESIGNABLE setted
 * This function does not check the property object type
 *
 * @param   self The property object
 * @return  Return a boolean value
 **/
bool isDesignable(const PySideProperty* self);

/**
 * This function check if property has the flag SCRIPTABLE setted
 * This function does not check the property object type
 *
 * @param   self The property object
 * @return  Return a boolean value
 **/
bool isScriptable(const PySideProperty* self);

/**
 * This function check if property has the flag STORED setted
 * This function does not check the property object type
 *
 * @param   self The property object
 * @return  Return a boolean value
 **/
bool isStored(const PySideProperty* self);

/**
 * This function check if property has the flag USER setted
 * This function does not check the property object type
 *
 * @param   self The property object
 * @return  Return a boolean value
 **/
bool isUser(const PySideProperty* self);

/**
 * This function check if property has the flag CONSTANT setted
 * This function does not check the property object type
 *
 * @param   self The property object
 * @return  Return a boolean value
 **/
bool isConstant(const PySideProperty* self);

/**
 * This function check if property has the flag FINAL setted
 * This function does not check the property object type
 *
 * @param   self The property object
 * @return  Return a boolean value
 **/
bool isFinal(const PySideProperty* self);

/// This function returns the type object of the property. It is either a real
/// PyTypeObject ("@Property(int)") or a string "@Property('QVariant')".
/// @param  self The property object
/// @return type object
PyObject *getTypeObject(const PySideProperty* self);

} // namespace PySide::Property

#endif
