// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only


#ifndef SBK_QTOPENGLWIDGETS_PYTHON_H
#define SBK_QTOPENGLWIDGETS_PYTHON_H

#include <sbkpython.h>
#include <sbkmodule.h>
#include <sbkconverter.h>
// Module Includes
#include <pyside6_qtcore_python.h>
#include <pyside6_qtgui_python.h>
#include <pyside6_qtwidgets_python.h>

// Bound library includes
#include <QtOpenGLWidgets/qopenglwidget.h>

QT_BEGIN_NAMESPACE
QT_END_NAMESPACE

// Type indices
enum [[deprecated]] : int {
    SBK_QOPENGLWIDGET_UPDATEBEHAVIOR_IDX                     = 4,
    SBK_QOPENGLWIDGET_TARGETBUFFER_IDX                       = 2,
    SBK_QOPENGLWIDGET_IDX                                    = 0,
    SBK_QTOPENGLWIDGETS_IDX_COUNT                            = 6,
};

// Type indices
enum : int {
    SBK_QOpenGLWidget_UpdateBehavior_IDX                     = 2,
    SBK_QOpenGLWidget_TargetBuffer_IDX                       = 1,
    SBK_QOpenGLWidget_IDX                                    = 0,
    SBK_QtOpenGLWidgets_IDX_COUNT                            = 3,
};

// This variable stores all Python types exported by this module.
extern Shiboken::Module::TypeInitStruct *SbkPySide6_QtOpenGLWidgetsTypeStructs;

// This variable stores all Python types exported by this module in a backwards compatible way with identical indexing.
[[deprecated]] extern PyTypeObject **SbkPySide6_QtOpenGLWidgetsTypes;

// This variable stores the Python module object exported by this module.
extern PyObject *SbkPySide6_QtOpenGLWidgetsModuleObject;

// This variable stores all type converters exported by this module.
extern SbkConverter **SbkPySide6_QtOpenGLWidgetsTypeConverters;

// Converter indices
enum [[deprecated]] : int {
    SBK_QTOPENGLWIDGETS_QLIST_INT_IDX                        = 0, // QList<int>
    SBK_QTOPENGLWIDGETS_QLIST_QVARIANT_IDX                   = 2, // QList<QVariant>
    SBK_QTOPENGLWIDGETS_QLIST_QSTRING_IDX                    = 4, // QList<QString>
    SBK_QTOPENGLWIDGETS_QMAP_QSTRING_QVARIANT_IDX            = 6, // QMap<QString,QVariant>
    SBK_QTOPENGLWIDGETS_CONVERTERS_IDX_COUNT                 = 8,
};

// Converter indices
enum : int {
    SBK_QtOpenGLWidgets_QList_int_IDX                        = 0, // QList<int>
    SBK_QtOpenGLWidgets_QList_QVariant_IDX                   = 1, // QList<QVariant>
    SBK_QtOpenGLWidgets_QList_QString_IDX                    = 2, // QList<QString>
    SBK_QtOpenGLWidgets_QMap_QString_QVariant_IDX            = 3, // QMap<QString,QVariant>
    SBK_QtOpenGLWidgets_CONVERTERS_IDX_COUNT                 = 4,
};
// Macros for type check

QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
template<> inline PyTypeObject *SbkType< ::QOpenGLWidget::UpdateBehavior >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLWidgetsTypeStructs[SBK_QOpenGLWidget_UpdateBehavior_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLWidget::TargetBuffer >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLWidgetsTypeStructs[SBK_QOpenGLWidget_TargetBuffer_IDX]); }
template<> inline PyTypeObject *SbkType< ::QOpenGLWidget >() { return Shiboken::Module::get(SbkPySide6_QtOpenGLWidgetsTypeStructs[SBK_QOpenGLWidget_IDX]); }

} // namespace Shiboken

QT_WARNING_POP
#endif // SBK_QTOPENGLWIDGETS_PYTHON_H

