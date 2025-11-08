// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only


#ifndef SBK_QTHELP_PYTHON_H
#define SBK_QTHELP_PYTHON_H

#include <sbkpython.h>
#include <sbkmodule.h>
#include <sbkconverter.h>
// Module Includes
#include <pyside6_qtwidgets_python.h>
#include <pyside6_qtgui_python.h>
#include <pyside6_qtcore_python.h>

// Bound library includes
#include <QtHelp/qhelpsearchengine.h>

QT_BEGIN_NAMESPACE
class QCompressedHelpInfo;
class QHelpContentItem;
class QHelpContentModel;
class QHelpContentWidget;
class QHelpEngine;
class QHelpEngineCore;
class QHelpFilterData;
class QHelpFilterEngine;
class QHelpFilterSettingsWidget;
class QHelpGlobal;
class QHelpIndexModel;
class QHelpIndexWidget;
struct QHelpLink;
class QHelpSearchEngine;
class QHelpSearchEngineCore;
class QHelpSearchQueryWidget;
class QHelpSearchResult;
class QHelpSearchResultWidget;
QT_END_NAMESPACE

// Type indices
enum [[deprecated]] : int {
    SBK_QCOMPRESSEDHELPINFO_IDX                              = 0,
    SBK_QHELPCONTENTITEM_IDX                                 = 2,
    SBK_QHELPCONTENTMODEL_IDX                                = 4,
    SBK_QHELPCONTENTWIDGET_IDX                               = 6,
    SBK_QHELPENGINE_IDX                                      = 8,
    SBK_QHELPENGINECORE_IDX                                  = 10,
    SBK_QHELPFILTERDATA_IDX                                  = 12,
    SBK_QHELPFILTERENGINE_IDX                                = 14,
    SBK_QHELPFILTERSETTINGSWIDGET_IDX                        = 16,
    SBK_QHELPGLOBAL_IDX                                      = 18,
    SBK_QHELPINDEXMODEL_IDX                                  = 20,
    SBK_QHELPINDEXWIDGET_IDX                                 = 22,
    SBK_QHELPLINK_IDX                                        = 24,
    SBK_QHELPSEARCHENGINE_IDX                                = 26,
    SBK_QHELPSEARCHENGINECORE_IDX                            = 28,
    SBK_QHELPSEARCHQUERY_FIELDNAME_IDX                       = 32,
    SBK_QHELPSEARCHQUERY_IDX                                 = 30,
    SBK_QHELPSEARCHQUERYWIDGET_IDX                           = 34,
    SBK_QHELPSEARCHRESULT_IDX                                = 36,
    SBK_QHELPSEARCHRESULTWIDGET_IDX                          = 38,
    SBK_QTHELP_IDX_COUNT                                     = 40,
};

// Type indices
enum : int {
    SBK_QCompressedHelpInfo_IDX                              = 0,
    SBK_QHelpContentItem_IDX                                 = 1,
    SBK_QHelpContentModel_IDX                                = 2,
    SBK_QHelpContentWidget_IDX                               = 3,
    SBK_QHelpEngine_IDX                                      = 4,
    SBK_QHelpEngineCore_IDX                                  = 5,
    SBK_QHelpFilterData_IDX                                  = 6,
    SBK_QHelpFilterEngine_IDX                                = 7,
    SBK_QHelpFilterSettingsWidget_IDX                        = 8,
    SBK_QHelpGlobal_IDX                                      = 9,
    SBK_QHelpIndexModel_IDX                                  = 10,
    SBK_QHelpIndexWidget_IDX                                 = 11,
    SBK_QHelpLink_IDX                                        = 12,
    SBK_QHelpSearchEngine_IDX                                = 13,
    SBK_QHelpSearchEngineCore_IDX                            = 14,
    SBK_QHelpSearchQuery_FieldName_IDX                       = 16,
    SBK_QHelpSearchQuery_IDX                                 = 15,
    SBK_QHelpSearchQueryWidget_IDX                           = 17,
    SBK_QHelpSearchResult_IDX                                = 18,
    SBK_QHelpSearchResultWidget_IDX                          = 19,
    SBK_QtHelp_IDX_COUNT                                     = 20,
};

// This variable stores all Python types exported by this module.
extern Shiboken::Module::TypeInitStruct *SbkPySide6_QtHelpTypeStructs;

// This variable stores all Python types exported by this module in a backwards compatible way with identical indexing.
[[deprecated]] extern PyTypeObject **SbkPySide6_QtHelpTypes;

// This variable stores the Python module object exported by this module.
extern PyObject *SbkPySide6_QtHelpModuleObject;

// This variable stores all type converters exported by this module.
extern SbkConverter **SbkPySide6_QtHelpTypeConverters;

// Converter indices
enum [[deprecated]] : int {
    SBK_QTHELP_QLIST_INT_IDX                                 = 0, // QList<int>
    SBK_QTHELP_QLIST_QVERSIONNUMBER_IDX                      = 2, // QList<QVersionNumber>
    SBK_QTHELP_QLIST_QMODELINDEX_IDX                         = 4, // QList<QModelIndex>
    SBK_QTHELP_QLIST_QHELPLINK_IDX                           = 6, // QList<QHelpLink>
    SBK_QTHELP_QMULTIMAP_QSTRING_QURL_IDX                    = 8, // QMultiMap<QString,QUrl>
    SBK_QTHELP_QLIST_QHELPSEARCHQUERY_IDX                    = 10, // QList<QHelpSearchQuery>
    SBK_QTHELP_QLIST_QHELPSEARCHRESULT_IDX                   = 12, // QList<QHelpSearchResult>
    SBK_QTHELP_STD_PAIR_QSTRING_QSTRING_IDX                  = 14, // std::pair<QString,QString>
    SBK_QTHELP_QLIST_STD_PAIR_QSTRING_QSTRING_IDX            = 16, // QList<std::pair<QString,QString>>
    SBK_QTHELP_QMAP_QSTRING_QSTRING_IDX                      = 18, // QMap<QString,QString>
    SBK_QTHELP_QMAP_QSTRING_QVERSIONNUMBER_IDX               = 20, // QMap<QString,QVersionNumber>
    SBK_QTHELP_QLIST_QURL_IDX                                = 22, // QList<QUrl>
    SBK_QTHELP_QLIST_QSTRINGLIST_IDX                         = 24, // QList<QStringList>
    SBK_QTHELP_QMAP_INT_QVARIANT_IDX                         = 26, // QMap<int,QVariant>
    SBK_QTHELP_QHASH_INT_QBYTEARRAY_IDX                      = 28, // QHash<int,QByteArray>
    SBK_QTHELP_QLIST_QVARIANT_IDX                            = 30, // QList<QVariant>
    SBK_QTHELP_QLIST_QSTRING_IDX                             = 32, // QList<QString>
    SBK_QTHELP_QMAP_QSTRING_QVARIANT_IDX                     = 34, // QMap<QString,QVariant>
    SBK_QTHELP_CONVERTERS_IDX_COUNT                          = 36,
};

// Converter indices
enum : int {
    SBK_QtHelp_QList_int_IDX                                 = 0, // QList<int>
    SBK_QtHelp_QList_QVersionNumber_IDX                      = 1, // QList<QVersionNumber>
    SBK_QtHelp_QList_QModelIndex_IDX                         = 2, // QList<QModelIndex>
    SBK_QtHelp_QList_QHelpLink_IDX                           = 3, // QList<QHelpLink>
    SBK_QtHelp_QMultiMap_QString_QUrl_IDX                    = 4, // QMultiMap<QString,QUrl>
    SBK_QtHelp_QList_QHelpSearchQuery_IDX                    = 5, // QList<QHelpSearchQuery>
    SBK_QtHelp_QList_QHelpSearchResult_IDX                   = 6, // QList<QHelpSearchResult>
    SBK_QtHelp_std_pair_QString_QString_IDX                  = 7, // std::pair<QString,QString>
    SBK_QtHelp_QList_std_pair_QString_QString_IDX            = 8, // QList<std::pair<QString,QString>>
    SBK_QtHelp_QMap_QString_QString_IDX                      = 9, // QMap<QString,QString>
    SBK_QtHelp_QMap_QString_QVersionNumber_IDX               = 10, // QMap<QString,QVersionNumber>
    SBK_QtHelp_QList_QUrl_IDX                                = 11, // QList<QUrl>
    SBK_QtHelp_QList_QStringList_IDX                         = 12, // QList<QStringList>
    SBK_QtHelp_QMap_int_QVariant_IDX                         = 13, // QMap<int,QVariant>
    SBK_QtHelp_QHash_int_QByteArray_IDX                      = 14, // QHash<int,QByteArray>
    SBK_QtHelp_QList_QVariant_IDX                            = 15, // QList<QVariant>
    SBK_QtHelp_QList_QString_IDX                             = 16, // QList<QString>
    SBK_QtHelp_QMap_QString_QVariant_IDX                     = 17, // QMap<QString,QVariant>
    SBK_QtHelp_CONVERTERS_IDX_COUNT                          = 18,
};
// Macros for type check

QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
template<> inline PyTypeObject *SbkType< ::QCompressedHelpInfo >() { return Shiboken::Module::get(SbkPySide6_QtHelpTypeStructs[SBK_QCompressedHelpInfo_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHelpContentItem >() { return Shiboken::Module::get(SbkPySide6_QtHelpTypeStructs[SBK_QHelpContentItem_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHelpContentModel >() { return Shiboken::Module::get(SbkPySide6_QtHelpTypeStructs[SBK_QHelpContentModel_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHelpContentWidget >() { return Shiboken::Module::get(SbkPySide6_QtHelpTypeStructs[SBK_QHelpContentWidget_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHelpEngine >() { return Shiboken::Module::get(SbkPySide6_QtHelpTypeStructs[SBK_QHelpEngine_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHelpEngineCore >() { return Shiboken::Module::get(SbkPySide6_QtHelpTypeStructs[SBK_QHelpEngineCore_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHelpFilterData >() { return Shiboken::Module::get(SbkPySide6_QtHelpTypeStructs[SBK_QHelpFilterData_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHelpFilterEngine >() { return Shiboken::Module::get(SbkPySide6_QtHelpTypeStructs[SBK_QHelpFilterEngine_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHelpFilterSettingsWidget >() { return Shiboken::Module::get(SbkPySide6_QtHelpTypeStructs[SBK_QHelpFilterSettingsWidget_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHelpGlobal >() { return Shiboken::Module::get(SbkPySide6_QtHelpTypeStructs[SBK_QHelpGlobal_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHelpIndexModel >() { return Shiboken::Module::get(SbkPySide6_QtHelpTypeStructs[SBK_QHelpIndexModel_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHelpIndexWidget >() { return Shiboken::Module::get(SbkPySide6_QtHelpTypeStructs[SBK_QHelpIndexWidget_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHelpLink >() { return Shiboken::Module::get(SbkPySide6_QtHelpTypeStructs[SBK_QHelpLink_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHelpSearchEngine >() { return Shiboken::Module::get(SbkPySide6_QtHelpTypeStructs[SBK_QHelpSearchEngine_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHelpSearchEngineCore >() { return Shiboken::Module::get(SbkPySide6_QtHelpTypeStructs[SBK_QHelpSearchEngineCore_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHelpSearchQuery::FieldName >() { return Shiboken::Module::get(SbkPySide6_QtHelpTypeStructs[SBK_QHelpSearchQuery_FieldName_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHelpSearchQuery >() { return Shiboken::Module::get(SbkPySide6_QtHelpTypeStructs[SBK_QHelpSearchQuery_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHelpSearchQueryWidget >() { return Shiboken::Module::get(SbkPySide6_QtHelpTypeStructs[SBK_QHelpSearchQueryWidget_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHelpSearchResult >() { return Shiboken::Module::get(SbkPySide6_QtHelpTypeStructs[SBK_QHelpSearchResult_IDX]); }
template<> inline PyTypeObject *SbkType< ::QHelpSearchResultWidget >() { return Shiboken::Module::get(SbkPySide6_QtHelpTypeStructs[SBK_QHelpSearchResultWidget_IDX]); }

} // namespace Shiboken

QT_WARNING_POP
#endif // SBK_QTHELP_PYTHON_H

