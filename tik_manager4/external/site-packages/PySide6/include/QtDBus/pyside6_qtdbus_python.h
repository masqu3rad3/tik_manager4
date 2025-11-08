// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only


#ifndef SBK_QTDBUS_PYTHON_H
#define SBK_QTDBUS_PYTHON_H

#include <sbkpython.h>
#include <sbkmodule.h>
#include <sbkconverter.h>
// Module Includes
#include <pyside6_qtcore_python.h>

// Bound library includes
#include <QtDBus/qdbusargument.h>
#include <QtDBus/qdbusconnection.h>
#include <QtDBus/qdbusconnectioninterface.h>
#include <QtDBus/qdbuserror.h>
#include <QtDBus/qdbusmessage.h>
#include <QtDBus/qdbusservicewatcher.h>

QT_BEGIN_NAMESPACE
class QDBusAbstractAdaptor;
class QDBusAbstractInterface;
class QDBusAbstractInterfaceBase;
class QDBusContext;
class QDBusInterface;
class QDBusObjectPath;
class QDBusPendingCall;
class QDBusPendingCallWatcher;
class QDBusServer;
class QDBusSignature;
class QDBusUnixFileDescriptor;
class QDBusVariant;
class QDBusVirtualObject;

namespace QtDBusHelper {
    class QDBusReply;
}
QT_END_NAMESPACE

// Type indices
enum [[deprecated]] : int {
    SBK_QDBUS_CALLMODE_IDX                                   = 2,
    SBK_QTDBUSQDBUS_IDX                                      = 0,
    SBK_QDBUSABSTRACTADAPTOR_IDX                             = 4,
    SBK_QDBUSABSTRACTINTERFACE_IDX                           = 6,
    SBK_QDBUSABSTRACTINTERFACEBASE_IDX                       = 8,
    SBK_QDBUSARGUMENT_ELEMENTTYPE_IDX                        = 12,
    SBK_QDBUSARGUMENT_IDX                                    = 10,
    SBK_QDBUSCONNECTION_BUSTYPE_IDX                          = 16,
    SBK_QDBUSCONNECTION_REGISTEROPTION_IDX                   = 20,
    SBK_QFLAGS_QDBUSCONNECTION_REGISTEROPTION_IDX            = 68,
    SBK_QDBUSCONNECTION_UNREGISTERMODE_IDX                   = 22,
    SBK_QDBUSCONNECTION_VIRTUALOBJECTREGISTEROPTION_IDX      = 24,
    SBK_QFLAGS_QDBUSCONNECTION_VIRTUALOBJECTREGISTEROPTION_IDX = 70,
    SBK_QDBUSCONNECTION_CONNECTIONCAPABILITY_IDX             = 18,
    SBK_QFLAGS_QDBUSCONNECTION_CONNECTIONCAPABILITY_IDX      = 66,
    SBK_QDBUSCONNECTION_IDX                                  = 14,
    SBK_QDBUSCONNECTIONINTERFACE_SERVICEQUEUEOPTIONS_IDX     = 30,
    SBK_QDBUSCONNECTIONINTERFACE_SERVICEREPLACEMENTOPTIONS_IDX = 32,
    SBK_QDBUSCONNECTIONINTERFACE_REGISTERSERVICEREPLY_IDX    = 28,
    SBK_QDBUSCONNECTIONINTERFACE_IDX                         = 26,
    SBK_QDBUSCONTEXT_IDX                                     = 34,
    SBK_QDBUSERROR_ERRORTYPE_IDX                             = 38,
    SBK_QDBUSERROR_IDX                                       = 36,
    SBK_QDBUSINTERFACE_IDX                                   = 40,
    SBK_QDBUSMESSAGE_MESSAGETYPE_IDX                         = 44,
    SBK_QDBUSMESSAGE_IDX                                     = 42,
    SBK_QDBUSOBJECTPATH_IDX                                  = 46,
    SBK_QDBUSPENDINGCALL_IDX                                 = 48,
    SBK_QDBUSPENDINGCALLWATCHER_IDX                          = 50,
    SBK_QDBUSSERVER_IDX                                      = 52,
    SBK_QDBUSSERVICEWATCHER_WATCHMODEFLAG_IDX                = 56,
    SBK_QFLAGS_QDBUSSERVICEWATCHER_WATCHMODEFLAG_IDX         = 72,
    SBK_QDBUSSERVICEWATCHER_IDX                              = 54,
    SBK_QDBUSSIGNATURE_IDX                                   = 58,
    SBK_QDBUSUNIXFILEDESCRIPTOR_IDX                          = 60,
    SBK_QDBUSVARIANT_IDX                                     = 62,
    SBK_QDBUSVIRTUALOBJECT_IDX                               = 64,
    SBK_QTDBUSHELPER_QDBUSREPLY_IDX                          = 76,
    SBK_QTDBUS_IDX_COUNT                                     = 78,
};

// Type indices
enum : int {
    SBK_QDBus_CallMode_IDX                                   = 1,
    SBK_QtDBusQDBus_IDX                                      = 0,
    SBK_QDBusAbstractAdaptor_IDX                             = 2,
    SBK_QDBusAbstractInterface_IDX                           = 3,
    SBK_QDBusAbstractInterfaceBase_IDX                       = 4,
    SBK_QDBusArgument_ElementType_IDX                        = 6,
    SBK_QDBusArgument_IDX                                    = 5,
    SBK_QDBusConnection_BusType_IDX                          = 8,
    SBK_QDBusConnection_RegisterOption_IDX                   = 10,
    SBK_QFlags_QDBusConnection_RegisterOption_IDX            = 34,
    SBK_QDBusConnection_UnregisterMode_IDX                   = 11,
    SBK_QDBusConnection_VirtualObjectRegisterOption_IDX      = 12,
    SBK_QFlags_QDBusConnection_VirtualObjectRegisterOption_IDX = 35,
    SBK_QDBusConnection_ConnectionCapability_IDX             = 9,
    SBK_QFlags_QDBusConnection_ConnectionCapability_IDX      = 33,
    SBK_QDBusConnection_IDX                                  = 7,
    SBK_QDBusConnectionInterface_ServiceQueueOptions_IDX     = 15,
    SBK_QDBusConnectionInterface_ServiceReplacementOptions_IDX = 16,
    SBK_QDBusConnectionInterface_RegisterServiceReply_IDX    = 14,
    SBK_QDBusConnectionInterface_IDX                         = 13,
    SBK_QDBusContext_IDX                                     = 17,
    SBK_QDBusError_ErrorType_IDX                             = 19,
    SBK_QDBusError_IDX                                       = 18,
    SBK_QDBusInterface_IDX                                   = 20,
    SBK_QDBusMessage_MessageType_IDX                         = 22,
    SBK_QDBusMessage_IDX                                     = 21,
    SBK_QDBusObjectPath_IDX                                  = 23,
    SBK_QDBusPendingCall_IDX                                 = 24,
    SBK_QDBusPendingCallWatcher_IDX                          = 25,
    SBK_QDBusServer_IDX                                      = 26,
    SBK_QDBusServiceWatcher_WatchModeFlag_IDX                = 28,
    SBK_QFlags_QDBusServiceWatcher_WatchModeFlag_IDX         = 36,
    SBK_QDBusServiceWatcher_IDX                              = 27,
    SBK_QDBusSignature_IDX                                   = 29,
    SBK_QDBusUnixFileDescriptor_IDX                          = 30,
    SBK_QDBusVariant_IDX                                     = 31,
    SBK_QDBusVirtualObject_IDX                               = 32,
    SBK_QtDBusHelper_QDBusReply_IDX                          = 38,
    SBK_QtDBus_IDX_COUNT                                     = 39,
};

// This variable stores all Python types exported by this module.
extern Shiboken::Module::TypeInitStruct *SbkPySide6_QtDBusTypeStructs;

// This variable stores all Python types exported by this module in a backwards compatible way with identical indexing.
[[deprecated]] extern PyTypeObject **SbkPySide6_QtDBusTypes;

// This variable stores the Python module object exported by this module.
extern PyObject *SbkPySide6_QtDBusModuleObject;

// This variable stores all type converters exported by this module.
extern SbkConverter **SbkPySide6_QtDBusTypeConverters;

// Converter indices
enum [[deprecated]] : int {
    SBK_QTDBUS_QLIST_INT_IDX                                 = 0, // QList<int>
    SBK_QTDBUS_QLIST_QVARIANT_IDX                            = 2, // QList<QVariant>
    SBK_QTDBUS_QHASH_QSTRING_QVARIANT_IDX                    = 4, // QHash<QString,QVariant>
    SBK_QTDBUS_QMAP_QSTRING_QVARIANT_IDX                     = 6, // QMap<QString,QVariant>
    SBK_QTDBUS_QLIST_QSTRING_IDX                             = 8, // QList<QString>
    SBK_QTDBUS_CONVERTERS_IDX_COUNT                          = 10,
};

// Converter indices
enum : int {
    SBK_QtDBus_QList_int_IDX                                 = 0, // QList<int>
    SBK_QtDBus_QList_QVariant_IDX                            = 1, // QList<QVariant>
    SBK_QtDBus_QHash_QString_QVariant_IDX                    = 2, // QHash<QString,QVariant>
    SBK_QtDBus_QMap_QString_QVariant_IDX                     = 3, // QMap<QString,QVariant>
    SBK_QtDBus_QList_QString_IDX                             = 4, // QList<QString>
    SBK_QtDBus_CONVERTERS_IDX_COUNT                          = 5,
};
// Macros for type check

QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
template<> inline PyTypeObject *SbkType< ::QDBus::CallMode >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBus_CallMode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusAbstractAdaptor >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusAbstractAdaptor_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusAbstractInterface >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusAbstractInterface_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusAbstractInterfaceBase >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusAbstractInterfaceBase_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusArgument::ElementType >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusArgument_ElementType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusArgument >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusArgument_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusConnection::BusType >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusConnection_BusType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusConnection::RegisterOption >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusConnection_RegisterOption_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QDBusConnection::RegisterOption> >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QFlags_QDBusConnection_RegisterOption_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusConnection::UnregisterMode >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusConnection_UnregisterMode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusConnection::VirtualObjectRegisterOption >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusConnection_VirtualObjectRegisterOption_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QDBusConnection::VirtualObjectRegisterOption> >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QFlags_QDBusConnection_VirtualObjectRegisterOption_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusConnection::ConnectionCapability >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusConnection_ConnectionCapability_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QDBusConnection::ConnectionCapability> >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QFlags_QDBusConnection_ConnectionCapability_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusConnection >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusConnection_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusConnectionInterface::ServiceQueueOptions >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusConnectionInterface_ServiceQueueOptions_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusConnectionInterface::ServiceReplacementOptions >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusConnectionInterface_ServiceReplacementOptions_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusConnectionInterface::RegisterServiceReply >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusConnectionInterface_RegisterServiceReply_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusConnectionInterface >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusConnectionInterface_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusContext >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusContext_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusError::ErrorType >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusError_ErrorType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusError >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusError_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusInterface >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusInterface_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusMessage::MessageType >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusMessage_MessageType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusMessage >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusMessage_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusObjectPath >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusObjectPath_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusPendingCall >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusPendingCall_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusPendingCallWatcher >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusPendingCallWatcher_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusServer >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusServer_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusServiceWatcher::WatchModeFlag >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusServiceWatcher_WatchModeFlag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QDBusServiceWatcher::WatchModeFlag> >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QFlags_QDBusServiceWatcher_WatchModeFlag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusServiceWatcher >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusServiceWatcher_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusSignature >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusSignature_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusUnixFileDescriptor >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusUnixFileDescriptor_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusVariant >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusVariant_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDBusVirtualObject >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QDBusVirtualObject_IDX]); }
template<> inline PyTypeObject *SbkType< ::QtDBusHelper::QDBusReply >() { return Shiboken::Module::get(SbkPySide6_QtDBusTypeStructs[SBK_QtDBusHelper_QDBusReply_IDX]); }

} // namespace Shiboken

QT_WARNING_POP
#endif // SBK_QTDBUS_PYTHON_H

