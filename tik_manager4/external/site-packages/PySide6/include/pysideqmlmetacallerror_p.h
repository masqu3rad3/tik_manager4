// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDEQMLMETACALLERROR_P_H
#define PYSIDEQMLMETACALLERROR_P_H

#include <optional>

#include <QtCore/qtclasshelpermacros.h>

QT_FORWARD_DECLARE_CLASS(QObject)

namespace PySide::Qml {

// Helper for SignalManager::qt_metacall():
// Bubbles Python exceptions up to the Javascript engine, if called from one
std::optional<int> qmlMetaCallErrorHandler(QObject *object);

} // namespace PySide::Qml

#endif // PYSIDEQMLMETACALLERROR_P_H
