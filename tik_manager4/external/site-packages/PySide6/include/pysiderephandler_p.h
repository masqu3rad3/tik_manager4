// Copyright (C) 2025 Ford Motor Company
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDE_REPHANDLER_P_H
#define PYSIDE_REPHANDLER_P_H

#include <sbkpython.h>

#include <QtRemoteObjects/repparser.h>

#include <QtCore/qstringlist.h>

struct PySideRepFilePrivate
{
    AST ast;
    PyObject *podDict{};
    PyObject *replicaDict{};
    PyObject *sourceDict{};
    QStringList classes;
    QStringList pods;
};

extern "C"
{
    extern PyTypeObject *PySideRepFile_TypeF(void);

    // Internal object
    struct PySideRepFile
    {
        PyObject_HEAD
        PySideRepFilePrivate *d;
    };
}; // extern "C"

#endif // PYSIDE_REPHANDLER_P_H
