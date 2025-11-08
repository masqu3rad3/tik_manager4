// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDEQAPP_H
#define PYSIDEQAPP_H

#include <pysidemacros.h>

namespace PySide
{

PYSIDE_API void initQApp();

/// Destroy a QCoreApplication taking care of destroy all instances of QObject first.
PYSIDE_API void destroyQCoreApplication();

} //namespace PySide

#endif // PYSIDEQPP_H
