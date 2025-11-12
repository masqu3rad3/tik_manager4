// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDEQMLMACROS_H
#define PYSIDEQMLMACROS_H

#include <shibokenmacros.h>

#define PYSIDEQML_EXPORT LIBSHIBOKEN_EXPORT
#define PYSIDEQML_IMPORT LIBSHIBOKEN_IMPORT

#ifdef BUILD_LIBPYSIDEQML
#  define PYSIDEQML_API PYSIDEQML_EXPORT
#else
#  define PYSIDEQML_API PYSIDEQML_IMPORT
#endif

#endif // PYSIDEQMLMACROS_H
