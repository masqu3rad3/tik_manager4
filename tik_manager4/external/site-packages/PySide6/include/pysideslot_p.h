// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
#ifndef PYSIDE_SLOT_P_H
#define PYSIDE_SLOT_P_H

#include <sbkpython.h>

#include <QtCore/qbytearray.h>
#include <QtCore/qlist.h>

namespace PySide::Slot {

struct Data {
    QByteArray signature;
    QByteArray resultType;
    QByteArray tag; // QMetaMethod::tag()
};

// This list is set as an attribute named PySide::PySideMagicName::slot_list_attr()
// by the decorator for usage by MetaObjectBuilder.
using DataList = QList<Data>;

DataList *dataListFromCapsule(PyObject *capsule);

void init(PyObject* module);
} // namespace PySide::Slot

#endif // PYSIDE_SLOT_P_H
