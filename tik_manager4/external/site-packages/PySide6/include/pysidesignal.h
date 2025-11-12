// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDE_SIGNAL_H
#define PYSIDE_SIGNAL_H

#include <pysidemacros.h>

#include <sbkpython.h>
#include <basewrapper.h>

#include <QtCore/qlist.h>
#include <QtCore/qmetaobject.h>

QT_BEGIN_NAMESPACE
struct QMetaObject;
class QObject;
QT_END_NAMESPACE

extern "C"
{
    extern PYSIDE_API PyTypeObject *PySideSignal_TypeF(void);
    extern PYSIDE_API PyTypeObject *PySideSignalInstance_TypeF(void);

    // Internal object
    struct PYSIDE_API PySideSignal;

    struct PySideSignalInstancePrivate;
    struct PYSIDE_API PySideSignalInstance
    {
        PyObject_HEAD
        PySideSignalInstancePrivate *d;
    };
}; // extern "C"

namespace PySide::Signal {

/**
 * This function checks for the PySideSignal type.
 *
 * @param   pyObj
 * @return  whether pyObj is a PySideSignal
 **/
PYSIDE_API bool checkType(PyObject *pyObj);

/**
 * This function checks for the PySideSignalInstanceType type.
 *
 * @param   pyObj
 * @return  Whether pyObj is a PySideSignalInstance
 **/
PYSIDE_API bool checkInstanceType(PyObject *pyObj);

/**
 * Register all C++ signals of a QObject on Python type.
 */
PYSIDE_API void registerSignals(PyTypeObject *pyObj, const QMetaObject *metaObject);

/**
 * This function creates a Signal object which stays attached to QObject class based on a list of QMetaMethods
 *
 * @param   source of the Signal to be registered on meta object
 * @param   methods a list of QMetaMethod wich contains the supported signature
 * @return  Return a new reference to PyObject* of type  PySideSignal
 **/
PYSIDE_API PySideSignalInstance *newObjectFromMethod(QObject *sourceQObject, PyObject *source,
                                                     const QList<QMetaMethod> &methods);

/**
 * This function initializes the Signal object by creating a PySideSignalInstance
 *
 * @param   self a Signal object used as base to PySideSignalInstance
 * @param   name the name to be used on PySideSignalInstance
 * @param   object the PyObject where the signal will be attached
 * @return  Return a new reference to PySideSignalInstance
 **/
PYSIDE_API PySideSignalInstance *initialize(PySideSignal *signal, PyObject *name, PyObject *object);

/**
 * This function is used to retrieve the object in which the signal is attached
 *
 * @param   self The Signal object
 * @return  Return the internal reference to the parent object of the signal
 **/
PYSIDE_API PyObject *getObject(PySideSignalInstance *signal);

/**
 * This function is used to retrieve the signal signature
 *
 * @param   self The Signal object
 * @return  Return the signal signature
 **/
PYSIDE_API const char *getSignature(PySideSignalInstance *signal);

struct EmitterData
{
    QObject *emitter = nullptr;
    int methodIndex = -1;
};

/// A convenience to retrieve the emitter data from a signal instance
///
/// @param   signal The Signal object
/// @return  Data structure
PYSIDE_API EmitterData getEmitterData(PySideSignalInstance *signal);

/**
 * This function is used to retrieve the signal signature
 *
 * @param   self The Signal object
 * @return  Return the signal signature
 **/
PYSIDE_API void updateSourceObject(PyObject *source);

/**
 * This function verifies if the signature is a QtSignal base on SIGNAL flag
 * @param   signature   The signal signature
 * @return  Return true if this is a Qt Signal, otherwise return false
 **/
PYSIDE_API bool isQtSignal(const char *signature);

/**
 * This function is similar to isQtSignal, however if it fails, it'll raise a Python error instead.
 *
 * @param   signature   The signal signature
 * @return  Return true if this is a Qt Signal, otherwise return false
 **/
PYSIDE_API bool checkQtSignal(const char *signature);

/**
 * This function is used to retrieve the signature base on Signal and receiver callback
 * @param   signature   The signal signature
 * @param   receiver    The QObject which will receive the signal
 * @param   callback    Callback function which will connect to the signal
 * @param   encodeName  Used to specify if the returned signature will be encoded with Qt signal/slot style
 * @return  Return the callback signature
 **/
PYSIDE_API QByteArray getCallbackSignature(QMetaMethod signal, QObject *receiver,
                                           PyObject *callback, bool encodeName);
} // namespace PySide::Signal

#endif
