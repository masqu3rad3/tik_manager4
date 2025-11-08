// Copyright (C) 2019 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDESTRINGS_H
#define PYSIDESTRINGS_H

#include <sbkpython.h>
#include <pysidemacros.h>

namespace PySide
{
namespace PySideName
{
PYSIDE_API PyObject *qtConnect();
PYSIDE_API PyObject *qtDisconnect();
PYSIDE_API PyObject *qtEmit();
PYSIDE_API PyObject *dict_ring();
PYSIDE_API PyObject *fset();
PYSIDE_API PyObject *im_func();
PYSIDE_API PyObject *im_self();
PYSIDE_API PyObject *name();
PYSIDE_API PyObject *orig_dict();
PYSIDE_API PyObject *parameters();
PYSIDE_API PyObject *property();
PYSIDE_API PyObject *select_id();
} // namespace PyName
namespace PySideMagicName
{
PYSIDE_API PyObject *code();
PYSIDE_API PyObject *doc();
PYSIDE_API PyObject *func();
PYSIDE_API PyObject *name();
PYSIDE_API PyObject *property_methods();
PYSIDE_API PyObject *slot_list_attr();
} // namespace PyMagicName
} // namespace PySide

#endif // PYSIDESTRINGS_H
