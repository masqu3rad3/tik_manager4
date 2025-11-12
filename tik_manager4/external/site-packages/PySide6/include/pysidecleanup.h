// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDECLEANUP_H
#define PYSIDECLEANUP_H

#include <pysidemacros.h>

namespace PySide
{

using CleanupFunction = void(*)();

/// Register a function to be called before python dies
PYSIDE_API void registerCleanupFunction(CleanupFunction func);
PYSIDE_API void runCleanupFunctions();

} //namespace PySide

#endif // PYSIDECLEANUP_H
