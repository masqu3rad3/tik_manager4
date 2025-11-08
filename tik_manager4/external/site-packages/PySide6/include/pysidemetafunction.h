// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDE_METAFUNCTION_H
#define PYSIDE_METAFUNCTION_H

#include <pysidemacros.h>

#include <sbkpython.h>

#include <QtCore/qobject.h>

extern "C"
{
    extern PYSIDE_API PyTypeObject *PySideMetaFunction_TypeF(void);

    struct PySideMetaFunctionPrivate;
    struct PYSIDE_API PySideMetaFunction
    {
        PyObject_HEAD
        PySideMetaFunctionPrivate *d;
    };
}; //extern "C"

namespace PySide::MetaFunction {

/**
 * This function creates a MetaFunction object
 *
 * @param   obj the QObject witch this fuction is part of
 * @param   methodIndex The index of this function on MetaObject
 * @return  Return a new reference of PySideMetaFunction
 **/
PYSIDE_API PySideMetaFunction *newObject(QObject *obj, int methodIndex);

} //namespace PySide::MetaFunction

#endif
