// Copyright (C) 2024 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef DYNAMICSLOT_P_H
#define DYNAMICSLOT_P_H

#include <sbkpython.h>

#include <QtCore/qcompare.h>
#include <QtCore/qmetaobject.h>

QT_FORWARD_DECLARE_CLASS(QDebug)

namespace PySide
{

class DynamicSlot
{
    Q_DISABLE_COPY_MOVE(DynamicSlot)
public:
    enum SlotType
    {
        Callable,
        Method,
        CompiledMethod,
        C_Function
    };

    virtual ~DynamicSlot() = default;

    virtual void call(const QByteArrayList &parameterTypes, const char *returnType,
                      void **cppArgs) = 0;
    virtual void formatDebug(QDebug &debug) const = 0;

    static SlotType slotType(PyObject *callback);
    static DynamicSlot *create(PyObject *callback);

protected:
    DynamicSlot() noexcept = default;
};

QDebug operator<<(QDebug debug, const DynamicSlot *ds);

void registerSlotConnection(QObject *source, int signalIndex, PyObject *callback,
                            const QMetaObject::Connection &connection);
bool disconnectSlot(QObject *source, int signalIndex, PyObject *callback);

}

#endif // DYNAMICSLOT_P_H
