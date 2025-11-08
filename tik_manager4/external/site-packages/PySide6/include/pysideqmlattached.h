// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDEQMLATTACHED_H
#define PYSIDEQMLATTACHED_H

#include <sbkpython.h>

#include "pysideqmlmacros.h"

#include <QtCore/qtconfigmacros.h>

QT_FORWARD_DECLARE_CLASS(QObject)

namespace PySide::Qml
{

/// PySide implementation of qmlAttachedPropertiesObject<T> function.
/// \param typeObject attaching type
/// \param obj        attachee
/// \param create     Whether to create the Attachment object
/// \return           Attachment object instance
PYSIDEQML_API QObject *qmlAttachedPropertiesObject(PyObject *typeObject, QObject *obj,
                                                   bool create = true);

} // namespace PySide::Qml

#endif // PYSIDEQMLATTACHED_H
