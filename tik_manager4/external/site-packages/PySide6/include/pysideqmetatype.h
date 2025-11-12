// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDEQMETATYPE_H
#define PYSIDEQMETATYPE_H

#include <QtCore/qmetatype.h>

namespace PySide
{

/// If the type \p T was registered on Qt meta type system with Q_DECLARE_METATYPE macro,
/// this class will initialize the meta type.
///
/// Initialize a meta type means register it on Qt meta type system, Qt itself only do this
/// on the first call of qMetaTypeId, and this is exactly what we do to init it. If we don't
/// do that, calls to QMetaType::type("QMatrix2x2") could return zero, causing QVariant to
/// not recognize some C++ types, like QMatrix2x2.

template<typename T, bool OK = QMetaTypeId<T>::Defined >
struct initQtMetaType {
    initQtMetaType()
    {
        qMetaTypeId<T>();
    }
};

// Template specialization to do nothing when the type wasn't registered on Qt meta type system.
template<typename T>
struct initQtMetaType<T, false> {
};

} //namespace PySide

#endif // PYSIDEQMETATYPE_H
