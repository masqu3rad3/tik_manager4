// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only


#ifndef SBK_QTCONCURRENT_PYTHON_H
#define SBK_QTCONCURRENT_PYTHON_H

#include <sbkpython.h>
#include <sbkmodule.h>
#include <sbkconverter.h>
// Module Includes
#include <pyside6_qtcore_python.h>

// Bound library includes
#include <QtConcurrent/qtaskbuilder.h>
#include <QtConcurrent/qtconcurrentreducekernel.h>
#include <QtConcurrent/qtconcurrentrunbase.h>
#include <QtConcurrent/qtconcurrentthreadengine.h>
#if QT_CONFIG(future)
#include <QtCore/qfuture.h>
#include <QtCore/qfuturewatcher.h>
#endif

QT_BEGIN_NAMESPACE
QT_END_NAMESPACE

// Type indices
enum [[deprecated]] : int {
    SBK_QFUTUREQSTRING_IDX                                   = 2,
    SBK_QFUTURE_QSTRING_IDX                                  = 2,
    SBK_QFUTUREVOID_IDX                                      = 4,
    SBK_QFUTURE_VOID_IDX                                     = 4,
    SBK_QFUTUREWATCHERQSTRING_IDX                            = 6,
    SBK_QFUTUREWATCHER_QSTRING_IDX                           = 6,
    SBK_QFUTUREWATCHERVOID_IDX                               = 8,
    SBK_QFUTUREWATCHER_VOID_IDX                              = 8,
    SBK_QTCONCURRENT_FUTURERESULT_IDX                        = 12,
    SBK_QTCONCURRENT_THREADFUNCTIONRESULT_IDX                = 16,
    SBK_QTCONCURRENT_REDUCEOPTION_IDX                        = 14,
    SBK_QFLAGS_QTCONCURRENT_REDUCEOPTION_IDX                 = 0,
    SBK_QTCONCURRENTQTCONCURRENT_IDX                         = 10,
    SBK_QTCONCURRENT_IDX_COUNT                               = 18,
};

// Type indices
enum : int {
    SBK_QFutureQString_IDX                                   = 1,
    SBK_QFuture_QString_IDX                                  = 1,
    SBK_QFutureVoid_IDX                                      = 2,
    SBK_QFuture_void_IDX                                     = 2,
    SBK_QFutureWatcherQString_IDX                            = 3,
    SBK_QFutureWatcher_QString_IDX                           = 3,
    SBK_QFutureWatcherVoid_IDX                               = 4,
    SBK_QFutureWatcher_void_IDX                              = 4,
    SBK_QtConcurrent_FutureResult_IDX                        = 6,
    SBK_QtConcurrent_ThreadFunctionResult_IDX                = 8,
    SBK_QtConcurrent_ReduceOption_IDX                        = 7,
    SBK_QFlags_QtConcurrent_ReduceOption_IDX                 = 0,
    SBK_QtConcurrentQtConcurrent_IDX                         = 5,
    SBK_QtConcurrent_IDX_COUNT                               = 9,
};

// This variable stores all Python types exported by this module.
extern Shiboken::Module::TypeInitStruct *SbkPySide6_QtConcurrentTypeStructs;

// This variable stores all Python types exported by this module in a backwards compatible way with identical indexing.
[[deprecated]] extern PyTypeObject **SbkPySide6_QtConcurrentTypes;

// This variable stores the Python module object exported by this module.
extern PyObject *SbkPySide6_QtConcurrentModuleObject;

// This variable stores all type converters exported by this module.
extern SbkConverter **SbkPySide6_QtConcurrentTypeConverters;

// Converter indices
enum [[deprecated]] : int {
    SBK_QTCONCURRENT_QLIST_INT_IDX                           = 0, // QList<int>
    SBK_QTCONCURRENT_QLIST_QVARIANT_IDX                      = 2, // QList<QVariant>
    SBK_QTCONCURRENT_QLIST_QSTRING_IDX                       = 4, // QList<QString>
    SBK_QTCONCURRENT_QMAP_QSTRING_QVARIANT_IDX               = 6, // QMap<QString,QVariant>
    SBK_QTCONCURRENT_CONVERTERS_IDX_COUNT                    = 8,
};

// Converter indices
enum : int {
    SBK_QtConcurrent_QList_int_IDX                           = 0, // QList<int>
    SBK_QtConcurrent_QList_QVariant_IDX                      = 1, // QList<QVariant>
    SBK_QtConcurrent_QList_QString_IDX                       = 2, // QList<QString>
    SBK_QtConcurrent_QMap_QString_QVariant_IDX               = 3, // QMap<QString,QVariant>
    SBK_QtConcurrent_CONVERTERS_IDX_COUNT                    = 4,
};

// typedef entries
using QFutureQString = QFuture<QString>;
using QFutureVoid = QFuture<void>;
using QFutureWatcherQString = QFutureWatcher<QString>;
using QFutureWatcherVoid = QFutureWatcher<void>;

// Macros for type check

QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
#if QT_CONFIG(future)
template<> inline PyTypeObject *SbkType< QFutureQString >() { return Shiboken::Module::get(SbkPySide6_QtConcurrentTypeStructs[SBK_QFutureQString_IDX]); }
#endif
#if QT_CONFIG(future)
template<> inline PyTypeObject *SbkType< QFutureVoid >() { return Shiboken::Module::get(SbkPySide6_QtConcurrentTypeStructs[SBK_QFutureVoid_IDX]); }
#endif
#if QT_CONFIG(future)
template<> inline PyTypeObject *SbkType< QFutureWatcherQString >() { return Shiboken::Module::get(SbkPySide6_QtConcurrentTypeStructs[SBK_QFutureWatcherQString_IDX]); }
#endif
#if QT_CONFIG(future)
template<> inline PyTypeObject *SbkType< QFutureWatcherVoid >() { return Shiboken::Module::get(SbkPySide6_QtConcurrentTypeStructs[SBK_QFutureWatcherVoid_IDX]); }
#endif
template<> inline PyTypeObject *SbkType< ::QtConcurrent::FutureResult >() { return Shiboken::Module::get(SbkPySide6_QtConcurrentTypeStructs[SBK_QtConcurrent_FutureResult_IDX]); }
template<> inline PyTypeObject *SbkType< ::QtConcurrent::ThreadFunctionResult >() { return Shiboken::Module::get(SbkPySide6_QtConcurrentTypeStructs[SBK_QtConcurrent_ThreadFunctionResult_IDX]); }
template<> inline PyTypeObject *SbkType< ::QtConcurrent::ReduceOption >() { return Shiboken::Module::get(SbkPySide6_QtConcurrentTypeStructs[SBK_QtConcurrent_ReduceOption_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QtConcurrent::ReduceOption> >() { return Shiboken::Module::get(SbkPySide6_QtConcurrentTypeStructs[SBK_QFlags_QtConcurrent_ReduceOption_IDX]); }

} // namespace Shiboken

QT_WARNING_POP
#endif // SBK_QTCONCURRENT_PYTHON_H

