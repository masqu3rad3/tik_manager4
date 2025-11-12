// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDE_QSIGNAL_P_H
#define PYSIDE_QSIGNAL_P_H

#include <sbkpython.h>

#include <QtCore/qbytearray.h>
#include <QtCore/qlist.h>
#include <QtCore/qobject.h>
#include <QtCore/qpointer.h>

#include <memory>

struct PySideSignalData
{
    struct Signature
    {
        QByteArray signature; // ','-separated list of parameter types
        unsigned short attributes;
        short argCount;
    };

    QByteArray signalName;
    QList<Signature> signatures;
    QByteArrayList signalArguments;
};

extern "C"
{
    extern PyTypeObject *PySideSignal_TypeF(void);

    struct PySideSignal {
        PyObject_HEAD
        PySideSignalData *data;
        PyObject *homonymousMethod;
    };

    struct PySideSignalInstance;
}; //extern "C"

struct PySideSignalInstanceShared
{
    QPointer<QObject> source;
    PyTypeObject *sourceType = nullptr;
};

using PySideSignalInstanceSharedPtr = std::shared_ptr<PySideSignalInstanceShared>;

struct PySideSignalInstancePrivate
{
    QByteArray signalName;
    QByteArray signature;
    PySideSignalInstanceSharedPtr shared;
    PyObject *homonymousMethod = nullptr;
    PySideSignalInstance *next = nullptr;
    unsigned short attributes = 0;
    short argCount = 0;
};

namespace PySide::Signal {

    void            init(PyObject *module);
    bool            connect(PyObject *source, const char *signal, PyObject *callback);
    QByteArray      getTypeName(PyObject *);
    QByteArray      codeCallbackName(PyObject *callback, const QByteArray &funcName);
    QByteArray      voidType();

} // namespace PySide::Signal

#endif
