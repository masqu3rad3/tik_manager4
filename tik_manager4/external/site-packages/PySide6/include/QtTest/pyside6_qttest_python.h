// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only


#ifndef SBK_QTTEST_PYTHON_H
#define SBK_QTTEST_PYTHON_H

#include <sbkpython.h>
#include <sbkmodule.h>
#include <sbkconverter.h>
// Module Includes
#include <pyside6_qtcore_python.h>
#include <pyside6_qtgui_python.h>
#include <pyside6_qtwidgets_python.h>

// Bound library includes
#include <QtTest/qabstractitemmodeltester.h>
#include <QtTest/qbenchmarkmetric.h>
#include <QtTest/qtestkeyboard.h>
#include <QtTest/qtestmouse.h>
#include <QtTest/qttestglobal.h>

QT_BEGIN_NAMESPACE
class QSignalSpy;

namespace QTest {
    class PySideQTouchEventSequence;
}
QT_END_NAMESPACE

// Type indices
enum [[deprecated]] : int {
    SBK_QABSTRACTITEMMODELTESTER_FAILUREREPORTINGMODE_IDX    = 2,
    SBK_QABSTRACTITEMMODELTESTER_IDX                         = 0,
    SBK_QSIGNALSPY_IDX                                       = 4,
    SBK_QTEST_TESTFAILMODE_IDX                               = 18,
    SBK_QTEST_COMPARISONOPERATION_IDX                        = 8,
    SBK_QTEST_QBENCHMARKMETRIC_IDX                           = 16,
    SBK_QTEST_KEYACTION_IDX                                  = 10,
    SBK_QTEST_MOUSEACTION_IDX                                = 12,
    SBK_QTTESTQTEST_IDX                                      = 6,
    SBK_QTEST_PYSIDEQTOUCHEVENTSEQUENCE_IDX                  = 14,
    SBK_QTTEST_IDX_COUNT                                     = 20,
};

// Type indices
enum : int {
    SBK_QAbstractItemModelTester_FailureReportingMode_IDX    = 1,
    SBK_QAbstractItemModelTester_IDX                         = 0,
    SBK_QSignalSpy_IDX                                       = 2,
    SBK_QTest_TestFailMode_IDX                               = 9,
    SBK_QTest_ComparisonOperation_IDX                        = 4,
    SBK_QTest_QBenchmarkMetric_IDX                           = 8,
    SBK_QTest_KeyAction_IDX                                  = 5,
    SBK_QTest_MouseAction_IDX                                = 6,
    SBK_QtTestQTest_IDX                                      = 3,
    SBK_QTest_PySideQTouchEventSequence_IDX                  = 7,
    SBK_QtTest_IDX_COUNT                                     = 10,
};

// This variable stores all Python types exported by this module.
extern Shiboken::Module::TypeInitStruct *SbkPySide6_QtTestTypeStructs;

// This variable stores all Python types exported by this module in a backwards compatible way with identical indexing.
[[deprecated]] extern PyTypeObject **SbkPySide6_QtTestTypes;

// This variable stores the Python module object exported by this module.
extern PyObject *SbkPySide6_QtTestModuleObject;

// This variable stores all type converters exported by this module.
extern SbkConverter **SbkPySide6_QtTestTypeConverters;

// Converter indices
enum [[deprecated]] : int {
    SBK_QTTEST_QLIST_INT_IDX                                 = 0, // QList<int>
    SBK_QTTEST_QLIST_QVARIANT_IDX                            = 2, // QList<QVariant>
    SBK_QTTEST_QLIST_QSTRING_IDX                             = 4, // QList<QString>
    SBK_QTTEST_QMAP_QSTRING_QVARIANT_IDX                     = 6, // QMap<QString,QVariant>
    SBK_QTTEST_CONVERTERS_IDX_COUNT                          = 8,
};

// Converter indices
enum : int {
    SBK_QtTest_QList_int_IDX                                 = 0, // QList<int>
    SBK_QtTest_QList_QVariant_IDX                            = 1, // QList<QVariant>
    SBK_QtTest_QList_QString_IDX                             = 2, // QList<QString>
    SBK_QtTest_QMap_QString_QVariant_IDX                     = 3, // QMap<QString,QVariant>
    SBK_QtTest_CONVERTERS_IDX_COUNT                          = 4,
};
// Macros for type check

QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
template<> inline PyTypeObject *SbkType< ::QAbstractItemModelTester::FailureReportingMode >() { return Shiboken::Module::get(SbkPySide6_QtTestTypeStructs[SBK_QAbstractItemModelTester_FailureReportingMode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QAbstractItemModelTester >() { return Shiboken::Module::get(SbkPySide6_QtTestTypeStructs[SBK_QAbstractItemModelTester_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSignalSpy >() { return Shiboken::Module::get(SbkPySide6_QtTestTypeStructs[SBK_QSignalSpy_IDX]); }
template<> inline PyTypeObject *SbkType< ::QTest::TestFailMode >() { return Shiboken::Module::get(SbkPySide6_QtTestTypeStructs[SBK_QTest_TestFailMode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QTest::ComparisonOperation >() { return Shiboken::Module::get(SbkPySide6_QtTestTypeStructs[SBK_QTest_ComparisonOperation_IDX]); }
template<> inline PyTypeObject *SbkType< ::QTest::QBenchmarkMetric >() { return Shiboken::Module::get(SbkPySide6_QtTestTypeStructs[SBK_QTest_QBenchmarkMetric_IDX]); }
template<> inline PyTypeObject *SbkType< ::QTest::KeyAction >() { return Shiboken::Module::get(SbkPySide6_QtTestTypeStructs[SBK_QTest_KeyAction_IDX]); }
template<> inline PyTypeObject *SbkType< ::QTest::MouseAction >() { return Shiboken::Module::get(SbkPySide6_QtTestTypeStructs[SBK_QTest_MouseAction_IDX]); }
template<> inline PyTypeObject *SbkType< ::QTest::PySideQTouchEventSequence >() { return Shiboken::Module::get(SbkPySide6_QtTestTypeStructs[SBK_QTest_PySideQTouchEventSequence_IDX]); }

} // namespace Shiboken

QT_WARNING_POP
#endif // SBK_QTTEST_PYTHON_H

