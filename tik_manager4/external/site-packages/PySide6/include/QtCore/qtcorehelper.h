// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef QTCOREHELPER_H
#define QTCOREHELPER_H

#include <QtCore/qdirlisting.h>
#include <QtCore/qmutex.h>
#include <QtCore/qobjectdefs.h>

#include <memory>

QT_BEGIN_NAMESPACE

namespace QtCoreHelper {

    using MutexLocker = QT_PREPEND_NAMESPACE(QMutexLocker<QMutex>);
    using RecursiveMutexLocker = QT_PREPEND_NAMESPACE(QMutexLocker<QRecursiveMutex>);

    // ::QMutexLocker is a template with the QMutex class as parameter which can
    // only be represented by different type names in Python. Provide a common API.
    class QMutexLocker
    {
    public:
        Q_DISABLE_COPY_MOVE(QMutexLocker)

        explicit QMutexLocker(QMutex *m)
            : m_mutexLocker(new MutexLocker(m))
        {
        }

        explicit QMutexLocker(QRecursiveMutex *m)
            : m_recursiveMutexLocker(new RecursiveMutexLocker(m))
        {
        }

        void unlock()
        {
            if (m_mutexLocker)
                m_mutexLocker->unlock();
            else
                m_recursiveMutexLocker->unlock();
        }

        void relock()
        {
            if (m_mutexLocker)
                m_mutexLocker->relock();
            else
                m_recursiveMutexLocker->relock();
        }

        QMutex *mutex() const
        {
            return m_mutexLocker ? m_mutexLocker->mutex() : nullptr;
        }

        QRecursiveMutex *recursiveMutex() const
        {
            return m_recursiveMutexLocker ? m_recursiveMutexLocker->mutex() : nullptr;
        }

        ~QMutexLocker()
        {
            delete m_mutexLocker;
            delete m_recursiveMutexLocker;
        }

    private:
        MutexLocker *m_mutexLocker = nullptr;
        RecursiveMutexLocker *m_recursiveMutexLocker = nullptr;
    };

    class QGenericArgumentData;

    // Return value of function Q_ARG() to be passed to QMetaObject::invokeMethod.
    // Frees the data if it is an allocated, primitive type.
    class QGenericArgumentHolder {
    public:
        QGenericArgumentHolder();
        explicit QGenericArgumentHolder(const QMetaType &type, const void *aData);
        QGenericArgumentHolder(const QGenericArgumentHolder &);
        QGenericArgumentHolder(QGenericArgumentHolder &&);
        QGenericArgumentHolder &operator=(const QGenericArgumentHolder &);
        QGenericArgumentHolder &operator=(QGenericArgumentHolder &&);
        ~QGenericArgumentHolder();

        QGenericArgument toGenericArgument() const;

        QMetaType metaType() const;
        const void *data() const;

    private:
        std::shared_ptr<QGenericArgumentData> d;
    };

    class QGenericReturnArgumentData;

    // Return value of function Q_RETURN_ARG() to be passed to QMetaObject::invokeMethod.
    // Frees the data if it is an allocated, primitive type.
    class QGenericReturnArgumentHolder  {
    public:
        explicit QGenericReturnArgumentHolder(const QMetaType &type, void *aData);
        QGenericReturnArgumentHolder(const QGenericReturnArgumentHolder &);
        QGenericReturnArgumentHolder(QGenericReturnArgumentHolder &&);
        QGenericReturnArgumentHolder &operator=(const QGenericReturnArgumentHolder &);
        QGenericReturnArgumentHolder &operator=(QGenericReturnArgumentHolder &&);
        ~QGenericReturnArgumentHolder();

        QGenericReturnArgument toGenericReturnArgument() const;

        QMetaType metaType() const;
        const void *data() const;

    private:
        std::shared_ptr<QGenericReturnArgumentData> d;
    };

    struct QDirListingIteratorPrivate;

    class QDirListingIterator
    {
    public:
        explicit QDirListingIterator(const QDirListing &dl);
        QDirListingIterator();

        QDirListingIterator(const QDirListingIterator &);
        QDirListingIterator &operator=(const QDirListingIterator &);
        QDirListingIterator(QDirListingIterator &&) noexcept;
        QDirListingIterator &operator=(QDirListingIterator &&) noexcept;
        ~QDirListingIterator();

        bool next();
        const QDirListing::DirEntry &value() const;
        bool atEnd() const;

    private:
        std::shared_ptr<QDirListingIteratorPrivate> d;
    };

} // namespace QtCoreHelper

QT_END_NAMESPACE

#endif // QTCOREHELPER_H
