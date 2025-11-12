// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef QTDBUSHELPER_H
#define QTDBUSHELPER_H

#include <QtDBus/qdbusmessage.h>
#include <QtDBus/qdbuspendingcall.h>
#include <QtDBus/qdbusreply.h>

QT_BEGIN_NAMESPACE
namespace QtDBusHelper {

// A Python-bindings friendly, non-template QDBusReply

class QDBusReply {
public:
    QDBusReply();

    // Enable constructing QDBusReply from a QDBusMessage which is returned by
    // call().
    explicit QDBusReply(const QDBusMessage &reply) :
        m_error(reply),
        m_data(reply.arguments().value(0, {}))
    {
    }

    // Enable constructing QDBusReply from an original Qt QDBusReply for
    // the functions we declare (QDBusConnectionInterface::registeredServiceNames())
    template <class T>
    explicit QDBusReply(const ::QDBusReply<T> &qr) :
        m_error(qr.error()),
        m_data(QVariant(qr.value()))
    {
    }

    explicit QDBusReply(const ::QDBusReply<void> &qr) :
        m_error(qr.error())
    {
    }

    bool isValid() const { return !m_error.isValid(); }

    QVariant value() const
    {
        return m_data;
    }

    const QDBusError &error() const { return m_error; }

private:
    QDBusError m_error;
    QVariant m_data;
};

inline QDBusReply::QDBusReply() = default;

} // namespace QtDBusHelper

QT_END_NAMESPACE

#endif // QTDBUSHELPER_H
