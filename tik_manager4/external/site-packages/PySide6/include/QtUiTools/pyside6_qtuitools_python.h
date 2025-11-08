// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only


#ifndef SBK_QTUITOOLS_PYTHON_H
#define SBK_QTUITOOLS_PYTHON_H

#include <sbkpython.h>
#include <sbkmodule.h>
#include <sbkconverter.h>
// Module Includes
#include <pyside6_qtwidgets_python.h>
#include <pyside6_qtgui_python.h>
#include <pyside6_qtcore_python.h>

// Bound library includes

QT_BEGIN_NAMESPACE
class QUiLoader;
QT_END_NAMESPACE

// Type indices
enum [[deprecated]] : int {
    SBK_QUILOADER_IDX                                        = 0,
    SBK_QTUITOOLS_IDX_COUNT                                  = 2,
};

// Type indices
enum : int {
    SBK_QUiLoader_IDX                                        = 0,
    SBK_QtUiTools_IDX_COUNT                                  = 1,
};

// This variable stores all Python types exported by this module.
extern Shiboken::Module::TypeInitStruct *SbkPySide6_QtUiToolsTypeStructs;

// This variable stores all Python types exported by this module in a backwards compatible way with identical indexing.
[[deprecated]] extern PyTypeObject **SbkPySide6_QtUiToolsTypes;

// This variable stores the Python module object exported by this module.
extern PyObject *SbkPySide6_QtUiToolsModuleObject;

// This variable stores all type converters exported by this module.
extern SbkConverter **SbkPySide6_QtUiToolsTypeConverters;

// Converter indices
enum [[deprecated]] : int {
    SBK_QTUITOOLS_QLIST_INT_IDX                              = 0, // QList<int>
    SBK_QTUITOOLS_QLIST_QVARIANT_IDX                         = 2, // QList<QVariant>
    SBK_QTUITOOLS_QLIST_QSTRING_IDX                          = 4, // QList<QString>
    SBK_QTUITOOLS_QMAP_QSTRING_QVARIANT_IDX                  = 6, // QMap<QString,QVariant>
    SBK_QTUITOOLS_CONVERTERS_IDX_COUNT                       = 8,
};

// Converter indices
enum : int {
    SBK_QtUiTools_QList_int_IDX                              = 0, // QList<int>
    SBK_QtUiTools_QList_QVariant_IDX                         = 1, // QList<QVariant>
    SBK_QtUiTools_QList_QString_IDX                          = 2, // QList<QString>
    SBK_QtUiTools_QMap_QString_QVariant_IDX                  = 3, // QMap<QString,QVariant>
    SBK_QtUiTools_CONVERTERS_IDX_COUNT                       = 4,
};
// Macros for type check

QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
template<> inline PyTypeObject *SbkType< ::QUiLoader >() { return Shiboken::Module::get(SbkPySide6_QtUiToolsTypeStructs[SBK_QUiLoader_IDX]); }

} // namespace Shiboken

QT_WARNING_POP
#endif // SBK_QTUITOOLS_PYTHON_H

