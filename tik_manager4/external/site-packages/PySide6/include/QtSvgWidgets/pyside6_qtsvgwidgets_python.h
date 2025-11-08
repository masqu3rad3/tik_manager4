// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only


#ifndef SBK_QTSVGWIDGETS_PYTHON_H
#define SBK_QTSVGWIDGETS_PYTHON_H

#include <sbkpython.h>
#include <sbkmodule.h>
#include <sbkconverter.h>
// Module Includes
#include <pyside6_qtsvg_python.h>
#include <pyside6_qtgui_python.h>
#include <pyside6_qtcore_python.h>
#include <pyside6_qtwidgets_python.h>

// Bound library includes

QT_BEGIN_NAMESPACE
class QGraphicsSvgItem;
class QSvgWidget;
QT_END_NAMESPACE

// Type indices
enum [[deprecated]] : int {
    SBK_QGRAPHICSSVGITEM_IDX                                 = 0,
    SBK_QSVGWIDGET_IDX                                       = 2,
    SBK_QTSVGWIDGETS_IDX_COUNT                               = 4,
};

// Type indices
enum : int {
    SBK_QGraphicsSvgItem_IDX                                 = 0,
    SBK_QSvgWidget_IDX                                       = 1,
    SBK_QtSvgWidgets_IDX_COUNT                               = 2,
};

// This variable stores all Python types exported by this module.
extern Shiboken::Module::TypeInitStruct *SbkPySide6_QtSvgWidgetsTypeStructs;

// This variable stores all Python types exported by this module in a backwards compatible way with identical indexing.
[[deprecated]] extern PyTypeObject **SbkPySide6_QtSvgWidgetsTypes;

// This variable stores the Python module object exported by this module.
extern PyObject *SbkPySide6_QtSvgWidgetsModuleObject;

// This variable stores all type converters exported by this module.
extern SbkConverter **SbkPySide6_QtSvgWidgetsTypeConverters;

// Converter indices
enum [[deprecated]] : int {
    SBK_QTSVGWIDGETS_QLIST_INT_IDX                           = 0, // QList<int>
    SBK_QTSVGWIDGETS_QLIST_QVARIANT_IDX                      = 2, // QList<QVariant>
    SBK_QTSVGWIDGETS_QLIST_QSTRING_IDX                       = 4, // QList<QString>
    SBK_QTSVGWIDGETS_QMAP_QSTRING_QVARIANT_IDX               = 6, // QMap<QString,QVariant>
    SBK_QTSVGWIDGETS_CONVERTERS_IDX_COUNT                    = 8,
};

// Converter indices
enum : int {
    SBK_QtSvgWidgets_QList_int_IDX                           = 0, // QList<int>
    SBK_QtSvgWidgets_QList_QVariant_IDX                      = 1, // QList<QVariant>
    SBK_QtSvgWidgets_QList_QString_IDX                       = 2, // QList<QString>
    SBK_QtSvgWidgets_QMap_QString_QVariant_IDX               = 3, // QMap<QString,QVariant>
    SBK_QtSvgWidgets_CONVERTERS_IDX_COUNT                    = 4,
};
// Macros for type check

QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
template<> inline PyTypeObject *SbkType< ::QGraphicsSvgItem >() { return Shiboken::Module::get(SbkPySide6_QtSvgWidgetsTypeStructs[SBK_QGraphicsSvgItem_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSvgWidget >() { return Shiboken::Module::get(SbkPySide6_QtSvgWidgetsTypeStructs[SBK_QSvgWidget_IDX]); }

} // namespace Shiboken

QT_WARNING_POP
#endif // SBK_QTSVGWIDGETS_PYTHON_H

