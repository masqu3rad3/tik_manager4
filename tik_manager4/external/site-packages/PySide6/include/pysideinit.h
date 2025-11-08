// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDEINIT_H
#define PYSIDEINIT_H

#include <sbkpython.h>

#include <pysidemacros.h>

namespace PySide
{

PYSIDE_API void init(PyObject *module);

/// Registers a dynamic "qt.conf" file with the Qt resource system.
///
/// This is used in a standalone build, to inform QLibraryInfo of the Qt prefix
/// (where Qt libraries are installed) so that plugins can be successfully loaded.
///
/// This is also used if PySide runs from inside a conda environment to solve
/// conflicts with the qt.conf installed by Anaconda Qt packages.
PYSIDE_API bool registerInternalQtConf();

} //namespace PySide

#endif // PYSIDEINIT_H
