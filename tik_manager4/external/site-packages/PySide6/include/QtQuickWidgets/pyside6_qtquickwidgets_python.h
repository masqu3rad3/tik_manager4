// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only


#ifndef SBK_QTQUICKWIDGETS_PYTHON_H
#define SBK_QTQUICKWIDGETS_PYTHON_H

#include <sbkpython.h>
#include <sbkmodule.h>
#include <sbkconverter.h>
// Module Includes
#include <pyside6_qtcore_python.h>
#include <pyside6_qtgui_python.h>
#include <pyside6_qtquick_python.h>
#include <pyside6_qtnetwork_python.h>
#include <pyside6_qtopengl_python.h>
#include <pyside6_qtqml_python.h>
#include <pyside6_qtwidgets_python.h>

// Bound library includes
#include <QtQuickWidgets/qquickwidget.h>

QT_BEGIN_NAMESPACE
QT_END_NAMESPACE

// Type indices
enum [[deprecated]] : int {
    SBK_QQUICKWIDGET_RESIZEMODE_IDX                          = 2,
    SBK_QQUICKWIDGET_STATUS_IDX                              = 4,
    SBK_QQUICKWIDGET_IDX                                     = 0,
    SBK_QTQUICKWIDGETS_IDX_COUNT                             = 6,
};

// Type indices
enum : int {
    SBK_QQuickWidget_ResizeMode_IDX                          = 1,
    SBK_QQuickWidget_Status_IDX                              = 2,
    SBK_QQuickWidget_IDX                                     = 0,
    SBK_QtQuickWidgets_IDX_COUNT                             = 3,
};

// This variable stores all Python types exported by this module.
extern Shiboken::Module::TypeInitStruct *SbkPySide6_QtQuickWidgetsTypeStructs;

// This variable stores all Python types exported by this module in a backwards compatible way with identical indexing.
[[deprecated]] extern PyTypeObject **SbkPySide6_QtQuickWidgetsTypes;

// This variable stores the Python module object exported by this module.
extern PyObject *SbkPySide6_QtQuickWidgetsModuleObject;

// This variable stores all type converters exported by this module.
extern SbkConverter **SbkPySide6_QtQuickWidgetsTypeConverters;

// Converter indices
enum [[deprecated]] : int {
    SBK_QTQUICKWIDGETS_QLIST_INT_IDX                         = 0, // QList<int>
    SBK_QTQUICKWIDGETS_QLIST_QQMLERROR_IDX                   = 2, // QList<QQmlError>
    SBK_QTQUICKWIDGETS_QMAP_QSTRING_QVARIANT_IDX             = 4, // QMap<QString,QVariant>
    SBK_QTQUICKWIDGETS_QLIST_QVARIANT_IDX                    = 6, // QList<QVariant>
    SBK_QTQUICKWIDGETS_QLIST_QSTRING_IDX                     = 8, // QList<QString>
    SBK_QTQUICKWIDGETS_CONVERTERS_IDX_COUNT                  = 10,
};

// Converter indices
enum : int {
    SBK_QtQuickWidgets_QList_int_IDX                         = 0, // QList<int>
    SBK_QtQuickWidgets_QList_QQmlError_IDX                   = 1, // QList<QQmlError>
    SBK_QtQuickWidgets_QMap_QString_QVariant_IDX             = 2, // QMap<QString,QVariant>
    SBK_QtQuickWidgets_QList_QVariant_IDX                    = 3, // QList<QVariant>
    SBK_QtQuickWidgets_QList_QString_IDX                     = 4, // QList<QString>
    SBK_QtQuickWidgets_CONVERTERS_IDX_COUNT                  = 5,
};
// Macros for type check

QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
template<> inline PyTypeObject *SbkType< ::QQuickWidget::ResizeMode >() { return Shiboken::Module::get(SbkPySide6_QtQuickWidgetsTypeStructs[SBK_QQuickWidget_ResizeMode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickWidget::Status >() { return Shiboken::Module::get(SbkPySide6_QtQuickWidgetsTypeStructs[SBK_QQuickWidget_Status_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQuickWidget >() { return Shiboken::Module::get(SbkPySide6_QtQuickWidgetsTypeStructs[SBK_QQuickWidget_IDX]); }

} // namespace Shiboken

QT_WARNING_POP
#endif // SBK_QTQUICKWIDGETS_PYTHON_H

