// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDEQHASH_H
#define PYSIDEQHASH_H

#include <sbkpython.h>

#include <QtCore/qhash.h>

namespace PySide
{

/// Hash function used to enable hash on objects not supported by the native Qt
/// library which have a toString() function.
template<class T>
[[deprecated]] inline Py_ssize_t hash(const T& value)
{
    return qHash(value.toString());
}

} //namespace PySide

#endif // PYSIDEQHASH_H
