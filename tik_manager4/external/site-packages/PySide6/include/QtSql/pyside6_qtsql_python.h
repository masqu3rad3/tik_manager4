// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only


#ifndef SBK_QTSQL_PYTHON_H
#define SBK_QTSQL_PYTHON_H

#include <sbkpython.h>
#include <sbkmodule.h>
#include <sbkconverter.h>
// Module Includes
#include <pyside6_qtwidgets_python.h>
#include <pyside6_qtgui_python.h>
#include <pyside6_qtcore_python.h>

// Bound library includes
#include <QtSql/qsqldriver.h>
#include <QtSql/qsqlerror.h>
#include <QtSql/qsqlfield.h>
#include <QtSql/qsqlquery.h>
#include <QtSql/qsqlrelationaltablemodel.h>
#include <QtSql/qsqlresult.h>
#include <QtSql/qsqltablemodel.h>
#include <QtSql/qtsqlglobal.h>

QT_BEGIN_NAMESPACE
class QSqlDatabase;
class QSqlDriverCreatorBase;
class QSqlIndex;
class QSqlQueryModel;
class QSqlRecord;
class QSqlRelation;
class QSqlRelationalDelegate;
QT_END_NAMESPACE

// Type indices
enum [[deprecated]] : int {
    SBK_QSQL_LOCATION_IDX                                    = 4,
    SBK_QSQL_PARAMTYPEFLAG_IDX                               = 8,
    SBK_QFLAGS_QSQL_PARAMTYPEFLAG_IDX                        = 0,
    SBK_QSQL_TABLETYPE_IDX                                   = 10,
    SBK_QSQL_NUMERICALPRECISIONPOLICY_IDX                    = 6,
    SBK_QTSQLQSQL_IDX                                        = 2,
    SBK_QSQLDATABASE_IDX                                     = 12,
    SBK_QSQLDRIVER_DRIVERFEATURE_IDX                         = 18,
    SBK_QSQLDRIVER_STATEMENTTYPE_IDX                         = 24,
    SBK_QSQLDRIVER_IDENTIFIERTYPE_IDX                        = 20,
    SBK_QSQLDRIVER_NOTIFICATIONSOURCE_IDX                    = 22,
    SBK_QSQLDRIVER_DBMSTYPE_IDX                              = 16,
    SBK_QSQLDRIVER_IDX                                       = 14,
    SBK_QSQLDRIVERCREATORBASE_IDX                            = 26,
    SBK_QSQLERROR_ERRORTYPE_IDX                              = 30,
    SBK_QSQLERROR_IDX                                        = 28,
    SBK_QSQLFIELD_REQUIREDSTATUS_IDX                         = 34,
    SBK_QSQLFIELD_IDX                                        = 32,
    SBK_QSQLINDEX_IDX                                        = 36,
    SBK_QSQLQUERY_BATCHEXECUTIONMODE_IDX                     = 40,
    SBK_QSQLQUERY_IDX                                        = 38,
    SBK_QSQLQUERYMODEL_IDX                                   = 42,
    SBK_QSQLRECORD_IDX                                       = 44,
    SBK_QSQLRELATION_IDX                                     = 46,
    SBK_QSQLRELATIONALDELEGATE_IDX                           = 48,
    SBK_QSQLRELATIONALTABLEMODEL_JOINMODE_IDX                = 52,
    SBK_QSQLRELATIONALTABLEMODEL_IDX                         = 50,
    SBK_QSQLRESULT_BINDINGSYNTAX_IDX                         = 56,
    SBK_QSQLRESULT_VIRTUALHOOKOPERATION_IDX                  = 58,
    SBK_QSQLRESULT_IDX                                       = 54,
    SBK_QSQLTABLEMODEL_EDITSTRATEGY_IDX                      = 62,
    SBK_QSQLTABLEMODEL_IDX                                   = 60,
    SBK_QTSQL_IDX_COUNT                                      = 64,
};

// Type indices
enum : int {
    SBK_QSql_Location_IDX                                    = 2,
    SBK_QSql_ParamTypeFlag_IDX                               = 4,
    SBK_QFlags_QSql_ParamTypeFlag_IDX                        = 0,
    SBK_QSql_TableType_IDX                                   = 5,
    SBK_QSql_NumericalPrecisionPolicy_IDX                    = 3,
    SBK_QtSqlQSql_IDX                                        = 1,
    SBK_QSqlDatabase_IDX                                     = 6,
    SBK_QSqlDriver_DriverFeature_IDX                         = 9,
    SBK_QSqlDriver_StatementType_IDX                         = 12,
    SBK_QSqlDriver_IdentifierType_IDX                        = 10,
    SBK_QSqlDriver_NotificationSource_IDX                    = 11,
    SBK_QSqlDriver_DbmsType_IDX                              = 8,
    SBK_QSqlDriver_IDX                                       = 7,
    SBK_QSqlDriverCreatorBase_IDX                            = 13,
    SBK_QSqlError_ErrorType_IDX                              = 15,
    SBK_QSqlError_IDX                                        = 14,
    SBK_QSqlField_RequiredStatus_IDX                         = 17,
    SBK_QSqlField_IDX                                        = 16,
    SBK_QSqlIndex_IDX                                        = 18,
    SBK_QSqlQuery_BatchExecutionMode_IDX                     = 20,
    SBK_QSqlQuery_IDX                                        = 19,
    SBK_QSqlQueryModel_IDX                                   = 21,
    SBK_QSqlRecord_IDX                                       = 22,
    SBK_QSqlRelation_IDX                                     = 23,
    SBK_QSqlRelationalDelegate_IDX                           = 24,
    SBK_QSqlRelationalTableModel_JoinMode_IDX                = 26,
    SBK_QSqlRelationalTableModel_IDX                         = 25,
    SBK_QSqlResult_BindingSyntax_IDX                         = 28,
    SBK_QSqlResult_VirtualHookOperation_IDX                  = 29,
    SBK_QSqlResult_IDX                                       = 27,
    SBK_QSqlTableModel_EditStrategy_IDX                      = 31,
    SBK_QSqlTableModel_IDX                                   = 30,
    SBK_QtSql_IDX_COUNT                                      = 32,
};

// This variable stores all Python types exported by this module.
extern Shiboken::Module::TypeInitStruct *SbkPySide6_QtSqlTypeStructs;

// This variable stores all Python types exported by this module in a backwards compatible way with identical indexing.
[[deprecated]] extern PyTypeObject **SbkPySide6_QtSqlTypes;

// This variable stores the Python module object exported by this module.
extern PyObject *SbkPySide6_QtSqlModuleObject;

// This variable stores all type converters exported by this module.
extern SbkConverter **SbkPySide6_QtSqlTypeConverters;

// Converter indices
enum [[deprecated]] : int {
    SBK_QTSQL_QLIST_INT_IDX                                  = 0, // QList<int>
    SBK_QTSQL_QLIST_QVARIANT_IDX                             = 2, // QList<QVariant>
    SBK_QTSQL_QMAP_INT_QVARIANT_IDX                          = 4, // QMap<int,QVariant>
    SBK_QTSQL_QLIST_QMODELINDEX_IDX                          = 6, // QList<QModelIndex>
    SBK_QTSQL_QHASH_INT_QBYTEARRAY_IDX                       = 8, // QHash<int,QByteArray>
    SBK_QTSQL_QLIST_QSTRING_IDX                              = 10, // QList<QString>
    SBK_QTSQL_QMAP_QSTRING_QVARIANT_IDX                      = 12, // QMap<QString,QVariant>
    SBK_QTSQL_CONVERTERS_IDX_COUNT                           = 14,
};

// Converter indices
enum : int {
    SBK_QtSql_QList_int_IDX                                  = 0, // QList<int>
    SBK_QtSql_QList_QVariant_IDX                             = 1, // QList<QVariant>
    SBK_QtSql_QMap_int_QVariant_IDX                          = 2, // QMap<int,QVariant>
    SBK_QtSql_QList_QModelIndex_IDX                          = 3, // QList<QModelIndex>
    SBK_QtSql_QHash_int_QByteArray_IDX                       = 4, // QHash<int,QByteArray>
    SBK_QtSql_QList_QString_IDX                              = 5, // QList<QString>
    SBK_QtSql_QMap_QString_QVariant_IDX                      = 6, // QMap<QString,QVariant>
    SBK_QtSql_CONVERTERS_IDX_COUNT                           = 7,
};
// Macros for type check

// Protected enum surrogates
enum PySide6_QtSql_QSqlResult_BindingSyntax_Surrogate : int {};
enum PySide6_QtSql_QSqlResult_VirtualHookOperation_Surrogate : int {};

QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
template<> inline PyTypeObject *SbkType< ::QSql::Location >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QSql_Location_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSql::ParamTypeFlag >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QSql_ParamTypeFlag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QSql::ParamTypeFlag> >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QFlags_QSql_ParamTypeFlag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSql::TableType >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QSql_TableType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSql::NumericalPrecisionPolicy >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QSql_NumericalPrecisionPolicy_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSqlDatabase >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QSqlDatabase_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSqlDriver::DriverFeature >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QSqlDriver_DriverFeature_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSqlDriver::StatementType >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QSqlDriver_StatementType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSqlDriver::IdentifierType >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QSqlDriver_IdentifierType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSqlDriver::NotificationSource >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QSqlDriver_NotificationSource_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSqlDriver::DbmsType >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QSqlDriver_DbmsType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSqlDriver >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QSqlDriver_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSqlDriverCreatorBase >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QSqlDriverCreatorBase_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSqlError::ErrorType >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QSqlError_ErrorType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSqlError >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QSqlError_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSqlField::RequiredStatus >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QSqlField_RequiredStatus_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSqlField >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QSqlField_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSqlIndex >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QSqlIndex_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSqlQuery::BatchExecutionMode >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QSqlQuery_BatchExecutionMode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSqlQuery >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QSqlQuery_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSqlQueryModel >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QSqlQueryModel_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSqlRecord >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QSqlRecord_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSqlRelation >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QSqlRelation_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSqlRelationalDelegate >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QSqlRelationalDelegate_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSqlRelationalTableModel::JoinMode >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QSqlRelationalTableModel_JoinMode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSqlRelationalTableModel >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QSqlRelationalTableModel_IDX]); }
template<> inline PyTypeObject *SbkType< ::PySide6_QtSql_QSqlResult_BindingSyntax_Surrogate >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QSqlResult_BindingSyntax_IDX]); }
template<> inline PyTypeObject *SbkType< ::PySide6_QtSql_QSqlResult_VirtualHookOperation_Surrogate >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QSqlResult_VirtualHookOperation_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSqlResult >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QSqlResult_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSqlTableModel::EditStrategy >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QSqlTableModel_EditStrategy_IDX]); }
template<> inline PyTypeObject *SbkType< ::QSqlTableModel >() { return Shiboken::Module::get(SbkPySide6_QtSqlTypeStructs[SBK_QSqlTableModel_IDX]); }

} // namespace Shiboken

QT_WARNING_POP
#endif // SBK_QTSQL_PYTHON_H

