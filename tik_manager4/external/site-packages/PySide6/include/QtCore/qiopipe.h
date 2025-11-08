// Copyright (C) 2024 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef QIOPIPE_H
#define QIOPIPE_H

#include <QtCore/qiodevicebase.h>
#include <QtCore/qobject.h>

QT_BEGIN_NAMESPACE

class QIODevice;

namespace QtCoreHelper
{

class QIOPipePrivate;
class QIOPipe : public QObject
{
    Q_OBJECT
    Q_DECLARE_PRIVATE(QIOPipe)

public:
    QIOPipe(QObject *parent = nullptr);

    bool open(QIODeviceBase::OpenMode mode);

    QIODevice *end1() const;
    QIODevice *end2() const;
};

} // namespace QtCoreHelper

QT_END_NAMESPACE

#endif // QIOPIPE_H
