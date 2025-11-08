// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDEMACROS_H
#define PYSIDEMACROS_H

#include <shibokenmacros.h>

#define PYSIDE_EXPORT LIBSHIBOKEN_EXPORT
#define PYSIDE_IMPORT LIBSHIBOKEN_IMPORT

#ifdef BUILD_LIBPYSIDE
#  define PYSIDE_API PYSIDE_EXPORT
#else
#  define PYSIDE_API PYSIDE_IMPORT
#endif

#endif // PYSIDEMACROS_H
