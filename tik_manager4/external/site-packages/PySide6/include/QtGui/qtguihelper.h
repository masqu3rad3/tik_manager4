// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef QTGUIHELPER_H
#define QTGUIHELPER_H

#include <QtGui/QGuiApplication>

QT_BEGIN_NAMESPACE
namespace QtGuiHelper {

    class QOverrideCursorGuard
    {
    public:
        Q_DISABLE_COPY_MOVE(QOverrideCursorGuard)

        QOverrideCursorGuard() = default;
        ~QOverrideCursorGuard() = default;

        void restoreOverrideCursor()
        {
            if (m_guard) {
                QGuiApplication::restoreOverrideCursor();
                m_guard = false;
            }
        }

    private:
        bool m_guard = true;
    };

} // namespace QtGuiHelper
QT_END_NAMESPACE

#endif // QTGUIHELPER_H
