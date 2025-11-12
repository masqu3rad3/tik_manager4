// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only


#ifndef SBK_QTQUICKCONTROLS2_PYTHON_H
#define SBK_QTQUICKCONTROLS2_PYTHON_H

#include <sbkpython.h>
#include <sbkmodule.h>
#include <sbkconverter.h>
// Module Includes
#include <pyside6_qtquick_python.h>
#include <pyside6_qtcore_python.h>
#include <pyside6_qtnetwork_python.h>
#include <pyside6_qtgui_python.h>
#include <pyside6_qtopengl_python.h>
#include <pyside6_qtqml_python.h>

// Bound library includes

QT_BEGIN_NAMESPACE
class QQuickAttachedPropertyPropagator;
class QQuickStyle;
QT_END_NAMESPACE

// Type indices
enum [[deprecated]] : int {
    SBK_QQUICKATTACHEDPROPERTYPROPAGATOR_IDX                 = 0,
    SBK_QQUICKSTYLE_IDX                                      = 2,
    SBK_QTQUICKCONTROLS2_IDX_COUNT                           = 4,
};

// Type indices
enum : int {
    SBK_QQuickAttachedPropertyPropagator_IDX                 = 0,
    SBK_QQuickStyle_IDX                                      = 1,
    SBK_QtQuickControls2_IDX_COUNT                           = 2,
};

// This variable stores all Python types exported by this module.
extern Shiboken::Module::TypeInitStruct *SbkPySide6_QtQuickControls2TypeStructs;

// This variable stores all Python types exported by this module in a backwards compatible way with identical indexing.
[[deprecated]] extern PyTypeObject **SbkPySide6_QtQuickControls2Types;

// This variable stores the Python module object exported by this module.
extern PyObject *SbkPySide6_QtQuickControls2ModuleObject;

// This variable stores all type converters exported by this module.
extern SbkConverter **SbkPySide6_QtQuickControls2TypeConverters;

// Converter indices
enum [[deprecated]] : int {
    SBK_QTQUICKCONTROLS2_QLIST_INT_IDX                       = 0, // QList<int>
    SBK_QTQUICKCONTROLS2_QLIST_QQUICKATTACHEDPROPERTYPROPAGATORPTR_IDX = 2, // QList<QQuickAttachedPropertyPropagator*>
    SBK_QTQUICKCONTROLS2_QLIST_QVARIANT_IDX                  = 4, // QList<QVariant>
    SBK_QTQUICKCONTROLS2_QLIST_QSTRING_IDX                   = 6, // QList<QString>
    SBK_QTQUICKCONTROLS2_QMAP_QSTRING_QVARIANT_IDX           = 8, // QMap<QString,QVariant>
    SBK_QTQUICKCONTROLS2_CONVERTERS_IDX_COUNT                = 10,
};

// Converter indices
enum : int {
    SBK_QtQuickControls2_QList_int_IDX                       = 0, // QList<int>
    SBK_QtQuickControls2_QList_QQuickAttachedPropertyPropagatorPTR_IDX = 1, // QList<QQuickAttachedPropertyPropagator*>
    SBK_QtQuickControls2_QList_QVariant_IDX                  = 2, // QList<QVariant>
    SBK_QtQuickControls2_QList_QString_IDX                   = 3, // QList<QString>
    SBK_QtQuickControls2_QMap_QString_QVariant_IDX           = 4, // QMap<QString,QVariant>
    SBK_QtQuickControls2_CONVERTERS_IDX_COUNT                = 5,
};
// Macros for type check

QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
template<> inline PyTypeObject *SbkType< ::QQuickAttachedPropertyPropagator >() { return Shiboken::Module::get(SbkPySide6_QtQuickControls2TypeStructs[SBK_QQuickAttachedPropertyPropagator_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickStyle >() { return Shiboken::Module::get(SbkPySide6_QtQuickControls2TypeStructs[SBK_QQuickStyle_IDX]); }

} // namespace Shiboken

QT_WARNING_POP
#endif // SBK_QTQUICKCONTROLS2_PYTHON_H

