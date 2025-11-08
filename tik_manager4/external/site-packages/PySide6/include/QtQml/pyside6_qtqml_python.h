// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only


#ifndef SBK_QTQML_PYTHON_H
#define SBK_QTQML_PYTHON_H

#include <sbkpython.h>
#include <sbkmodule.h>
#include <sbkconverter.h>
// Module Includes
#include <pyside6_qtcore_python.h>
#include <pyside6_qtnetwork_python.h>

// Bound library includes
#include <QtQml/qjsengine.h>
#include <QtQml/qjsmanagedvalue.h>
#include <QtQml/qjsprimitivevalue.h>
#include <QtQml/qjsvalue.h>
#include <QtQml/qqml.h>
#include <QtQml/qqmlabstracturlinterceptor.h>
#include <QtQml/qqmlcomponent.h>
#include <QtQml/qqmlcontext.h>
#include <QtQml/qqmldebug.h>
#include <QtQml/qqmlengine.h>
#include <QtQml/qqmlfile.h>
#include <QtQml/qqmlincubator.h>
#include <QtQml/qqmlproperty.h>

QT_BEGIN_NAMESPACE
class QJSValueIterator;
class QPyQmlParserStatus;
class QPyQmlPropertyValueSource;
class QQmlApplicationEngine;
class QQmlEngine;
class QQmlError;
class QQmlExpression;
class QQmlExtensionInterface;
class QQmlExtensionPlugin;
class QQmlFileSelector;
class QQmlIncubationController;
class QQmlListReference;
class QQmlNetworkAccessManagerFactory;
class QQmlParserStatus;
class QQmlPropertyMap;
class QQmlPropertyValueSource;
class QQmlScriptString;
class QQmlTypesExtensionInterface;
QT_END_NAMESPACE
// Begin code injection
// Volatile Bool Ptr type definition for QQmlIncubationController::incubateWhile(std::atomic<bool> *, int)
#include <atomic>

using AtomicBool = std::atomic<bool>;

struct QtQml_VolatileBoolObject {
    PyObject_HEAD
    AtomicBool *flag;
};
// End of code injection


// Type indices
enum [[deprecated]] : int {
    SBK_QJSENGINE_OBJECTOWNERSHIP_IDX                        = 8,
    SBK_QJSENGINE_EXTENSION_IDX                              = 6,
    SBK_QFLAGS_QJSENGINE_EXTENSION_IDX                       = 0,
    SBK_QJSENGINE_IDX                                        = 4,
    SBK_QJSMANAGEDVALUE_TYPE_IDX                             = 12,
    SBK_QJSMANAGEDVALUE_IDX                                  = 10,
    SBK_QJSPRIMITIVEVALUE_TYPE_IDX                           = 16,
    SBK_QJSPRIMITIVEVALUE_IDX                                = 14,
    SBK_QJSVALUE_SPECIALVALUE_IDX                            = 24,
    SBK_QJSVALUE_ERRORTYPE_IDX                               = 20,
    SBK_QJSVALUE_OBJECTCONVERSIONBEHAVIOR_IDX                = 22,
    SBK_QJSVALUE_IDX                                         = 18,
    SBK_QJSVALUEITERATOR_IDX                                 = 26,
    SBK_QPYQMLPARSERSTATUS_IDX                               = 30,
    SBK_QPYQMLPROPERTYVALUESOURCE_IDX                        = 32,
    SBK_QQMLABSTRACTURLINTERCEPTOR_DATATYPE_IDX              = 36,
    SBK_QQMLABSTRACTURLINTERCEPTOR_IDX                       = 34,
    SBK_QQMLAPPLICATIONENGINE_IDX                            = 38,
    SBK_QQMLCOMPONENT_COMPILATIONMODE_IDX                    = 42,
    SBK_QQMLCOMPONENT_STATUS_IDX                             = 44,
    SBK_QQMLCOMPONENT_IDX                                    = 40,
    SBK_QQMLCONTEXT_IDX                                      = 46,
    SBK_QQMLCONTEXT_PROPERTYPAIR_IDX                         = 48,
    SBK_QQMLDEBUGGINGENABLER_STARTMODE_IDX                   = 52,
    SBK_QQMLDEBUGGINGENABLER_IDX                             = 50,
    SBK_QQMLENGINE_IDX                                       = 54,
    SBK_QQMLERROR_IDX                                        = 56,
    SBK_QQMLEXPRESSION_IDX                                   = 58,
    SBK_QQMLEXTENSIONINTERFACE_IDX                           = 60,
    SBK_QQMLEXTENSIONPLUGIN_IDX                              = 62,
    SBK_QQMLFILE_STATUS_IDX                                  = 66,
    SBK_QQMLFILE_IDX                                         = 64,
    SBK_QQMLFILESELECTOR_IDX                                 = 68,
    SBK_QQMLIMAGEPROVIDERBASE_IMAGETYPE_IDX                  = 74,
    SBK_QQMLIMAGEPROVIDERBASE_FLAG_IDX                       = 72,
    SBK_QFLAGS_QQMLIMAGEPROVIDERBASE_FLAG_IDX                = 2,
    SBK_QQMLIMAGEPROVIDERBASE_IDX                            = 70,
    SBK_QQMLINCUBATIONCONTROLLER_IDX                         = 76,
    SBK_QQMLINCUBATOR_INCUBATIONMODE_IDX                     = 80,
    SBK_QQMLINCUBATOR_STATUS_IDX                             = 82,
    SBK_QQMLINCUBATOR_IDX                                    = 78,
    SBK_QQMLLISTREFERENCE_IDX                                = 84,
    SBK_QQMLNETWORKACCESSMANAGERFACTORY_IDX                  = 88,
    SBK_QQMLPARSERSTATUS_IDX                                 = 90,
    SBK_QQMLPROPERTY_PROPERTYTYPECATEGORY_IDX                = 94,
    SBK_QQMLPROPERTY_TYPE_IDX                                = 96,
    SBK_QQMLPROPERTY_IDX                                     = 92,
    SBK_QQMLPROPERTYMAP_IDX                                  = 98,
    SBK_QQMLPROPERTYVALUESOURCE_IDX                          = 100,
    SBK_QQMLSCRIPTSTRING_IDX                                 = 102,
    SBK_QQMLTYPESEXTENSIONINTERFACE_IDX                      = 104,
    // SBK_QML_HAS_ATTACHED_PROPERTIES_IDX                   = 28,
    SBK_QQMLMODULEIMPORTSPECIALVERSIONS_IDX                  = 86,
    SBK_QTQML_IDX_COUNT                                      = 108,
};

// Type indices
enum : int {
    SBK_QJSEngine_ObjectOwnership_IDX                        = 4,
    SBK_QJSEngine_Extension_IDX                              = 3,
    SBK_QFlags_QJSEngine_Extension_IDX                       = 0,
    SBK_QJSEngine_IDX                                        = 2,
    SBK_QJSManagedValue_Type_IDX                             = 6,
    SBK_QJSManagedValue_IDX                                  = 5,
    SBK_QJSPrimitiveValue_Type_IDX                           = 8,
    SBK_QJSPrimitiveValue_IDX                                = 7,
    SBK_QJSValue_SpecialValue_IDX                            = 12,
    SBK_QJSValue_ErrorType_IDX                               = 10,
    SBK_QJSValue_ObjectConversionBehavior_IDX                = 11,
    SBK_QJSValue_IDX                                         = 9,
    SBK_QJSValueIterator_IDX                                 = 13,
    SBK_QPyQmlParserStatus_IDX                               = 15,
    SBK_QPyQmlPropertyValueSource_IDX                        = 16,
    SBK_QQmlAbstractUrlInterceptor_DataType_IDX              = 18,
    SBK_QQmlAbstractUrlInterceptor_IDX                       = 17,
    SBK_QQmlApplicationEngine_IDX                            = 19,
    SBK_QQmlComponent_CompilationMode_IDX                    = 21,
    SBK_QQmlComponent_Status_IDX                             = 22,
    SBK_QQmlComponent_IDX                                    = 20,
    SBK_QQmlContext_IDX                                      = 23,
    SBK_QQmlContext_PropertyPair_IDX                         = 24,
    SBK_QQmlDebuggingEnabler_StartMode_IDX                   = 26,
    SBK_QQmlDebuggingEnabler_IDX                             = 25,
    SBK_QQmlEngine_IDX                                       = 27,
    SBK_QQmlError_IDX                                        = 28,
    SBK_QQmlExpression_IDX                                   = 29,
    SBK_QQmlExtensionInterface_IDX                           = 30,
    SBK_QQmlExtensionPlugin_IDX                              = 31,
    SBK_QQmlFile_Status_IDX                                  = 33,
    SBK_QQmlFile_IDX                                         = 32,
    SBK_QQmlFileSelector_IDX                                 = 34,
    SBK_QQmlImageProviderBase_ImageType_IDX                  = 37,
    SBK_QQmlImageProviderBase_Flag_IDX                       = 36,
    SBK_QFlags_QQmlImageProviderBase_Flag_IDX                = 1,
    SBK_QQmlImageProviderBase_IDX                            = 35,
    SBK_QQmlIncubationController_IDX                         = 38,
    SBK_QQmlIncubator_IncubationMode_IDX                     = 40,
    SBK_QQmlIncubator_Status_IDX                             = 41,
    SBK_QQmlIncubator_IDX                                    = 39,
    SBK_QQmlListReference_IDX                                = 42,
    SBK_QQmlNetworkAccessManagerFactory_IDX                  = 44,
    SBK_QQmlParserStatus_IDX                                 = 45,
    SBK_QQmlProperty_PropertyTypeCategory_IDX                = 47,
    SBK_QQmlProperty_Type_IDX                                = 48,
    SBK_QQmlProperty_IDX                                     = 46,
    SBK_QQmlPropertyMap_IDX                                  = 49,
    SBK_QQmlPropertyValueSource_IDX                          = 50,
    SBK_QQmlScriptString_IDX                                 = 51,
    SBK_QQmlTypesExtensionInterface_IDX                      = 52,
    SBK_QML_HAS_ATTACHED_PROPERTIES_IDX                      = 14,
    SBK_QQmlModuleImportSpecialVersions_IDX                  = 43,
    SBK_QtQml_IDX_COUNT                                      = 54,
};

// This variable stores all Python types exported by this module.
extern Shiboken::Module::TypeInitStruct *SbkPySide6_QtQmlTypeStructs;

// This variable stores all Python types exported by this module in a backwards compatible way with identical indexing.
[[deprecated]] extern PyTypeObject **SbkPySide6_QtQmlTypes;

// This variable stores the Python module object exported by this module.
extern PyObject *SbkPySide6_QtQmlModuleObject;

// This variable stores all type converters exported by this module.
extern SbkConverter **SbkPySide6_QtQmlTypeConverters;

// Converter indices
enum [[deprecated]] : int {
    SBK_QTQML_QLIST_INT_IDX                                  = 0, // QList<int>
    SBK_QTQML_QLIST_QQMLERROR_IDX                            = 2, // QList<QQmlError>
    SBK_QTQML_QMAP_QSTRING_QVARIANT_IDX                      = 4, // QMap<QString,QVariant>
    SBK_QTQML_QHASH_QSTRING_QVARIANT_IDX                     = 6, // QHash<QString,QVariant>
    SBK_QTQML_QLIST_QJSVALUE_IDX                             = 8, // QList<QJSValue>
    SBK_QTQML_QLIST_QQMLCONTEXT_PROPERTYPAIR_IDX             = 10, // QList<QQmlContext::PropertyPair>
    SBK_QTQML_QLIST_QQMLABSTRACTURLINTERCEPTORPTR_IDX        = 12, // QList<QQmlAbstractUrlInterceptor*>
    SBK_QTQML_QLIST_QOBJECTPTR_IDX                           = 14, // QList<QObject*>
    SBK_QTQML_QLIST_QVARIANT_IDX                             = 16, // QList<QVariant>
    SBK_QTQML_QLIST_QSTRING_IDX                              = 18, // QList<QString>
    SBK_QTQML_CONVERTERS_IDX_COUNT                           = 20,
};

// Converter indices
enum : int {
    SBK_QtQml_QList_int_IDX                                  = 0, // QList<int>
    SBK_QtQml_QList_QQmlError_IDX                            = 1, // QList<QQmlError>
    SBK_QtQml_QMap_QString_QVariant_IDX                      = 2, // QMap<QString,QVariant>
    SBK_QtQml_QHash_QString_QVariant_IDX                     = 3, // QHash<QString,QVariant>
    SBK_QtQml_QList_QJSValue_IDX                             = 4, // QList<QJSValue>
    SBK_QtQml_QList_QQmlContext_PropertyPair_IDX             = 5, // QList<QQmlContext::PropertyPair>
    SBK_QtQml_QList_QQmlAbstractUrlInterceptorPTR_IDX        = 6, // QList<QQmlAbstractUrlInterceptor*>
    SBK_QtQml_QList_QObjectPTR_IDX                           = 7, // QList<QObject*>
    SBK_QtQml_QList_QVariant_IDX                             = 8, // QList<QVariant>
    SBK_QtQml_QList_QString_IDX                              = 9, // QList<QString>
    SBK_QtQml_CONVERTERS_IDX_COUNT                           = 10,
};
// Macros for type check

QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
template<> inline PyTypeObject *SbkType< ::QQmlModuleImportSpecialVersions >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlModuleImportSpecialVersions_IDX]); }
template<> inline PyTypeObject *SbkType< ::QJSEngine::ObjectOwnership >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QJSEngine_ObjectOwnership_IDX]); }
template<> inline PyTypeObject *SbkType< ::QJSEngine::Extension >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QJSEngine_Extension_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QJSEngine::Extension> >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QFlags_QJSEngine_Extension_IDX]); }
template<> inline PyTypeObject *SbkType< ::QJSEngine >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QJSEngine_IDX]); }
template<> inline PyTypeObject *SbkType< ::QJSManagedValue::Type >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QJSManagedValue_Type_IDX]); }
template<> inline PyTypeObject *SbkType< ::QJSManagedValue >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QJSManagedValue_IDX]); }
template<> inline PyTypeObject *SbkType< ::QJSPrimitiveValue::Type >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QJSPrimitiveValue_Type_IDX]); }
template<> inline PyTypeObject *SbkType< ::QJSPrimitiveValue >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QJSPrimitiveValue_IDX]); }
template<> inline PyTypeObject *SbkType< ::QJSValue::SpecialValue >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QJSValue_SpecialValue_IDX]); }
template<> inline PyTypeObject *SbkType< ::QJSValue::ErrorType >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QJSValue_ErrorType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QJSValue::ObjectConversionBehavior >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QJSValue_ObjectConversionBehavior_IDX]); }
template<> inline PyTypeObject *SbkType< ::QJSValue >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QJSValue_IDX]); }
template<> inline PyTypeObject *SbkType< ::QJSValueIterator >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QJSValueIterator_IDX]); }
template<> inline PyTypeObject *SbkType< ::QPyQmlParserStatus >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QPyQmlParserStatus_IDX]); }
template<> inline PyTypeObject *SbkType< ::QPyQmlPropertyValueSource >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QPyQmlPropertyValueSource_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlAbstractUrlInterceptor::DataType >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlAbstractUrlInterceptor_DataType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlAbstractUrlInterceptor >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlAbstractUrlInterceptor_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlApplicationEngine >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlApplicationEngine_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlComponent::CompilationMode >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlComponent_CompilationMode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlComponent::Status >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlComponent_Status_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlComponent >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlComponent_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlContext >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlContext_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlContext::PropertyPair >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlContext_PropertyPair_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlDebuggingEnabler::StartMode >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlDebuggingEnabler_StartMode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlDebuggingEnabler >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlDebuggingEnabler_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlEngine >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlEngine_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlError >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlError_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlExpression >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlExpression_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlExtensionInterface >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlExtensionInterface_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlExtensionPlugin >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlExtensionPlugin_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlFile::Status >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlFile_Status_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlFile >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlFile_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlFileSelector >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlFileSelector_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlImageProviderBase::ImageType >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlImageProviderBase_ImageType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlImageProviderBase::Flag >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlImageProviderBase_Flag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QQmlImageProviderBase::Flag> >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QFlags_QQmlImageProviderBase_Flag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlImageProviderBase >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlImageProviderBase_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlIncubationController >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlIncubationController_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlIncubator::IncubationMode >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlIncubator_IncubationMode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlIncubator::Status >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlIncubator_Status_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlIncubator >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlIncubator_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlListReference >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlListReference_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlNetworkAccessManagerFactory >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlNetworkAccessManagerFactory_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlParserStatus >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlParserStatus_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlProperty::PropertyTypeCategory >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlProperty_PropertyTypeCategory_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlProperty::Type >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlProperty_Type_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlProperty >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlProperty_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlPropertyMap >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlPropertyMap_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlPropertyValueSource >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlPropertyValueSource_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlScriptString >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlScriptString_IDX]); }
template<> inline PyTypeObject *SbkType< ::QQmlTypesExtensionInterface >() { return Shiboken::Module::get(SbkPySide6_QtQmlTypeStructs[SBK_QQmlTypesExtensionInterface_IDX]); }

} // namespace Shiboken

QT_WARNING_POP
#endif // SBK_QTQML_PYTHON_H

