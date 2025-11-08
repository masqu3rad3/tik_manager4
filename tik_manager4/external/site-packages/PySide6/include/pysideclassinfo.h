// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDE_CLASSINFO_H
#define PYSIDE_CLASSINFO_H

#include <pysidemacros.h>

#include <sbkpython.h>

#include <QtCore/qbytearray.h>
#include <QtCore/qlist.h>

namespace PySide::ClassInfo {

struct ClassInfo
{
    QByteArray key;
    QByteArray value;
};

using ClassInfoList = QList<ClassInfo>;

PYSIDE_API bool checkType(PyObject* pyObj);
PYSIDE_API ClassInfoList getClassInfoList(PyObject *decorator);

PYSIDE_API bool setClassInfo(PyTypeObject *type, const QByteArray &key,
                             const QByteArray &value);
PYSIDE_API bool setClassInfo(PyTypeObject *type, const ClassInfoList &list);

} // namespace PySide::ClassInfo

#endif
