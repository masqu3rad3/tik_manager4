// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only


#ifndef SBK_QTSVG_PYTHON_H
#define SBK_QTSVG_PYTHON_H

#include <sbkpython.h>
#include <sbkmodule.h>
#include <sbkconverter.h>
// Module Includes
#include <pyside6_qtgui_python.h>
#include <pyside6_qtcore_python.h>

// Bound library includes
#include <QtSvg/qsvggenerator.h>
#include <QtSvg/qtsvgglobal.h>

QT_BEGIN_NAMESPACE
class QSvgRenderer;
QT_END_NAMESPACE

// Type indices
enum [[deprecated]] : int {
    SBK_QSVGGENERATOR_SVGVERSION_IDX                         = 4,
    SBK_QSVGGENERATOR_IDX                                    = 2,
    SBK_QSVGRENDERER_IDX                                     = 6,
    SBK_QTSVG_OPTION_IDX                                     = 10,
    SBK_QFLAGS_QTSVG_OPTION_IDX                              = 0,
    SBK_QTSVGQTSVG_IDX                                       = 8,
    SBK_QTSVG_IDX_COUNT                                      = 12,
};

// Type indices
enum : int {
    SBK_QSvgGenerator_SvgVersion_IDX                         = 2,
    SBK_QSvgGenerator_IDX                                    = 1,
    SBK_QSvgRenderer_IDX                                     = 3,
    SBK_QtSvg_Option_IDX                                     = 5,
    SBK_QFlags_QtSvg_Option_IDX                              = 0,
    SBK_QtSvgQtSvg_IDX                                       = 4,
    SBK_QtSvg_IDX_COUNT                                      = 6,
};

// This variable stores all Python types exported by this module.
extern Shiboken::Module::TypeInitStruct *SbkPySide6_QtSvgTypeStructs;

// This variable stores all Python types exported by this module in a backwards compatible way with identical indexing.
[[deprecated]] extern PyTypeObject **SbkPySide6_QtSvgTypes;

// This variable stores the Python module object exported by this module.
extern PyObject *SbkPySide6_QtSvgModuleObject;

// This variable stores all type converters exported by this module.
extern SbkConverter **SbkPySide6_QtSvgTypeConverters;

// Converter indices
enum [[deprecated]] : int {
    SBK_QTSVG_QLIST_INT_IDX                                  = 0, // QList<int>
    SBK_QTSVG_QLIST_QVARIANT_IDX                             = 2, // QList<QVariant>
    SBK_QTSVG_QLIST_QSTRING_IDX                              = 4, // QList<QString>
    SBK_QTSVG_QMAP_QSTRING_QVARIANT_IDX                      = 6, // QMap<QString,QVariant>
    SBK_QTSVG_CONVERTERS_IDX_COUNT                           = 8,
};

// Converter indices
enum : int {
    SBK_QtSvg_QList_int_IDX                                  = 0, // QList<int>
    SBK_QtSvg_QList_QVariant_IDX                             = 1, // QList<QVariant>
    SBK_QtSvg_QList_QString_IDX                              = 2, // QList<QString>
    SBK_QtSvg_QMap_QString_QVariant_IDX                      = 3, // QMap<QString,QVariant>
    SBK_QtSvg_CONVERTERS_IDX_COUNT                           = 4,
};
// Macros for type check

QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
template<> inline PyTypeObject *SbkType< ::QSvgGenerator::SvgVersion >() { return Shiboken::Module::get(SbkPySide6_QtSvgTypeStructs[SBK_QSvgGenerator_SvgVersion_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSvgGenerator >() { return Shiboken::Module::get(SbkPySide6_QtSvgTypeStructs[SBK_QSvgGenerator_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSvgRenderer >() { return Shiboken::Module::get(SbkPySide6_QtSvgTypeStructs[SBK_QSvgRenderer_IDX]); }
template<> inline PyTypeObject *SbkType< ::QtSvg::Option >() { return Shiboken::Module::get(SbkPySide6_QtSvgTypeStructs[SBK_QtSvg_Option_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QtSvg::Option> >() { return Shiboken::Module::get(SbkPySide6_QtSvgTypeStructs[SBK_QFlags_QtSvg_Option_IDX]); }

} // namespace Shiboken

QT_WARNING_POP
#endif // SBK_QTSVG_PYTHON_H

