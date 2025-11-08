// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only


#ifndef SBK_QTDESIGNER_PYTHON_H
#define SBK_QTDESIGNER_PYTHON_H

#include <sbkpython.h>
#include <sbkmodule.h>
#include <sbkconverter.h>
// Module Includes
#include <pyside6_qtwidgets_python.h>
#include <pyside6_qtgui_python.h>
#include <pyside6_qtcore_python.h>

// Bound library includes
#include <QtDesigner/abstractdnditem.h>
#include <QtDesigner/abstractformwindow.h>
#include <QtDesigner/abstractformwindowcursor.h>
#include <QtDesigner/abstractformwindowmanager.h>
#include <QtDesigner/abstractwidgetbox.h>

QT_BEGIN_NAMESPACE
class QAbstractExtensionFactory;
class QAbstractExtensionManager;
class QAbstractFormBuilder;
class QDesignerActionEditorInterface;
class QDesignerContainerExtension;
class QDesignerCustomWidgetCollectionInterface;
class QDesignerCustomWidgetInterface;
class QDesignerDynamicPropertySheetExtension;
class QDesignerFormEditorInterface;
class QDesignerFormWindowToolInterface;
class QDesignerMemberSheetExtension;
class QDesignerObjectInspectorInterface;
class QDesignerPropertyEditorInterface;
class QDesignerPropertySheetExtension;
class QDesignerTaskMenuExtension;
class QExtensionFactory;
class QExtensionManager;
class QFormBuilder;
class QPyDesignerContainerExtension;
class QPyDesignerCustomWidgetCollection;
class QPyDesignerMemberSheetExtension;
class QPyDesignerPropertySheetExtension;
class QPyDesignerTaskMenuExtension;
QT_END_NAMESPACE

// Type indices
enum [[deprecated]] : int {
    SBK_QABSTRACTEXTENSIONFACTORY_IDX                        = 0,
    SBK_QABSTRACTEXTENSIONMANAGER_IDX                        = 2,
    SBK_QABSTRACTFORMBUILDER_IDX                             = 4,
    SBK_QDESIGNERACTIONEDITORINTERFACE_IDX                   = 6,
    SBK_QDESIGNERCONTAINEREXTENSION_IDX                      = 8,
    SBK_QDESIGNERCUSTOMWIDGETCOLLECTIONINTERFACE_IDX         = 10,
    SBK_QDESIGNERCUSTOMWIDGETINTERFACE_IDX                   = 12,
    SBK_QDESIGNERDNDITEMINTERFACE_DROPTYPE_IDX               = 16,
    SBK_QDESIGNERDNDITEMINTERFACE_IDX                        = 14,
    SBK_QDESIGNERDYNAMICPROPERTYSHEETEXTENSION_IDX           = 18,
    SBK_QDESIGNERFORMEDITORINTERFACE_IDX                     = 20,
    SBK_QDESIGNERFORMWINDOWCURSORINTERFACE_MOVEOPERATION_IDX = 26,
    SBK_QDESIGNERFORMWINDOWCURSORINTERFACE_MOVEMODE_IDX      = 24,
    SBK_QDESIGNERFORMWINDOWCURSORINTERFACE_IDX               = 22,
    SBK_QDESIGNERFORMWINDOWINTERFACE_FEATUREFLAG_IDX         = 30,
    SBK_QFLAGS_QDESIGNERFORMWINDOWINTERFACE_FEATUREFLAG_IDX  = 66,
    SBK_QDESIGNERFORMWINDOWINTERFACE_RESOURCEFILESAVEMODE_IDX = 32,
    SBK_QDESIGNERFORMWINDOWINTERFACE_IDX                     = 28,
    SBK_QDESIGNERFORMWINDOWMANAGERINTERFACE_ACTION_IDX       = 36,
    SBK_QDESIGNERFORMWINDOWMANAGERINTERFACE_ACTIONGROUP_IDX  = 38,
    SBK_QDESIGNERFORMWINDOWMANAGERINTERFACE_IDX              = 34,
    SBK_QDESIGNERFORMWINDOWTOOLINTERFACE_IDX                 = 40,
    SBK_QDESIGNERMEMBERSHEETEXTENSION_IDX                    = 42,
    SBK_QDESIGNEROBJECTINSPECTORINTERFACE_IDX                = 44,
    SBK_QDESIGNERPROPERTYEDITORINTERFACE_IDX                 = 46,
    SBK_QDESIGNERPROPERTYSHEETEXTENSION_IDX                  = 48,
    SBK_QDESIGNERTASKMENUEXTENSION_IDX                       = 50,
    SBK_QDESIGNERWIDGETBOXINTERFACE_IDX                      = 52,
    SBK_QDESIGNERWIDGETBOXINTERFACE_CATEGORY_TYPE_IDX        = 56,
    SBK_QDESIGNERWIDGETBOXINTERFACE_CATEGORY_IDX             = 54,
    SBK_QDESIGNERWIDGETBOXINTERFACE_WIDGET_TYPE_IDX          = 60,
    SBK_QDESIGNERWIDGETBOXINTERFACE_WIDGET_IDX               = 58,
    SBK_QEXTENSIONFACTORY_IDX                                = 62,
    SBK_QEXTENSIONMANAGER_IDX                                = 64,
    SBK_QFORMBUILDER_IDX                                     = 68,
    SBK_QPYDESIGNERCONTAINEREXTENSION_IDX                    = 70,
    SBK_QPYDESIGNERCUSTOMWIDGETCOLLECTION_IDX                = 72,
    SBK_QPYDESIGNERMEMBERSHEETEXTENSION_IDX                  = 74,
    SBK_QPYDESIGNERPROPERTYSHEETEXTENSION_IDX                = 76,
    SBK_QPYDESIGNERTASKMENUEXTENSION_IDX                     = 78,
    SBK_QTDESIGNER_IDX_COUNT                                 = 80,
};

// Type indices
enum : int {
    SBK_QAbstractExtensionFactory_IDX                        = 0,
    SBK_QAbstractExtensionManager_IDX                        = 1,
    SBK_QAbstractFormBuilder_IDX                             = 2,
    SBK_QDesignerActionEditorInterface_IDX                   = 3,
    SBK_QDesignerContainerExtension_IDX                      = 4,
    SBK_QDesignerCustomWidgetCollectionInterface_IDX         = 5,
    SBK_QDesignerCustomWidgetInterface_IDX                   = 6,
    SBK_QDesignerDnDItemInterface_DropType_IDX               = 8,
    SBK_QDesignerDnDItemInterface_IDX                        = 7,
    SBK_QDesignerDynamicPropertySheetExtension_IDX           = 9,
    SBK_QDesignerFormEditorInterface_IDX                     = 10,
    SBK_QDesignerFormWindowCursorInterface_MoveOperation_IDX = 13,
    SBK_QDesignerFormWindowCursorInterface_MoveMode_IDX      = 12,
    SBK_QDesignerFormWindowCursorInterface_IDX               = 11,
    SBK_QDesignerFormWindowInterface_FeatureFlag_IDX         = 15,
    SBK_QFlags_QDesignerFormWindowInterface_FeatureFlag_IDX  = 33,
    SBK_QDesignerFormWindowInterface_ResourceFileSaveMode_IDX = 16,
    SBK_QDesignerFormWindowInterface_IDX                     = 14,
    SBK_QDesignerFormWindowManagerInterface_Action_IDX       = 18,
    SBK_QDesignerFormWindowManagerInterface_ActionGroup_IDX  = 19,
    SBK_QDesignerFormWindowManagerInterface_IDX              = 17,
    SBK_QDesignerFormWindowToolInterface_IDX                 = 20,
    SBK_QDesignerMemberSheetExtension_IDX                    = 21,
    SBK_QDesignerObjectInspectorInterface_IDX                = 22,
    SBK_QDesignerPropertyEditorInterface_IDX                 = 23,
    SBK_QDesignerPropertySheetExtension_IDX                  = 24,
    SBK_QDesignerTaskMenuExtension_IDX                       = 25,
    SBK_QDesignerWidgetBoxInterface_IDX                      = 26,
    SBK_QDesignerWidgetBoxInterface_Category_Type_IDX        = 28,
    SBK_QDesignerWidgetBoxInterface_Category_IDX             = 27,
    SBK_QDesignerWidgetBoxInterface_Widget_Type_IDX          = 30,
    SBK_QDesignerWidgetBoxInterface_Widget_IDX               = 29,
    SBK_QExtensionFactory_IDX                                = 31,
    SBK_QExtensionManager_IDX                                = 32,
    SBK_QFormBuilder_IDX                                     = 34,
    SBK_QPyDesignerContainerExtension_IDX                    = 35,
    SBK_QPyDesignerCustomWidgetCollection_IDX                = 36,
    SBK_QPyDesignerMemberSheetExtension_IDX                  = 37,
    SBK_QPyDesignerPropertySheetExtension_IDX                = 38,
    SBK_QPyDesignerTaskMenuExtension_IDX                     = 39,
    SBK_QtDesigner_IDX_COUNT                                 = 40,
};

// This variable stores all Python types exported by this module.
extern Shiboken::Module::TypeInitStruct *SbkPySide6_QtDesignerTypeStructs;

// This variable stores all Python types exported by this module in a backwards compatible way with identical indexing.
[[deprecated]] extern PyTypeObject **SbkPySide6_QtDesignerTypes;

// This variable stores the Python module object exported by this module.
extern PyObject *SbkPySide6_QtDesignerModuleObject;

// This variable stores all type converters exported by this module.
extern SbkConverter **SbkPySide6_QtDesignerTypeConverters;

// Converter indices
enum [[deprecated]] : int {
    SBK_QTDESIGNER_QLIST_INT_IDX                             = 0, // QList<int>
    SBK_QTDESIGNER_QLIST_QACTIONPTR_IDX                      = 2, // QList<QAction*>
    SBK_QTDESIGNER_QLIST_QBYTEARRAY_IDX                      = 4, // QList<QByteArray>
    SBK_QTDESIGNER_QLIST_QDESIGNERCUSTOMWIDGETINTERFACEPTR_IDX = 6, // QList<QDesignerCustomWidgetInterface*>
    SBK_QTDESIGNER_QLIST_QDESIGNERDNDITEMINTERFACEPTR_IDX    = 8, // QList<QDesignerDnDItemInterface*>
    SBK_QTDESIGNER_QLIST_QWIDGETPTR_IDX                      = 10, // QList<QWidget*>
    SBK_QTDESIGNER_QLIST_QOBJECTPTR_IDX                      = 12, // QList<QObject*>
    SBK_QTDESIGNER_QLIST_QVARIANT_IDX                        = 14, // QList<QVariant>
    SBK_QTDESIGNER_QLIST_QSTRING_IDX                         = 16, // QList<QString>
    SBK_QTDESIGNER_QMAP_QSTRING_QVARIANT_IDX                 = 18, // QMap<QString,QVariant>
    SBK_QTDESIGNER_CONVERTERS_IDX_COUNT                      = 20,
};

// Converter indices
enum : int {
    SBK_QtDesigner_QList_int_IDX                             = 0, // QList<int>
    SBK_QtDesigner_QList_QActionPTR_IDX                      = 1, // QList<QAction*>
    SBK_QtDesigner_QList_QByteArray_IDX                      = 2, // QList<QByteArray>
    SBK_QtDesigner_QList_QDesignerCustomWidgetInterfacePTR_IDX = 3, // QList<QDesignerCustomWidgetInterface*>
    SBK_QtDesigner_QList_QDesignerDnDItemInterfacePTR_IDX    = 4, // QList<QDesignerDnDItemInterface*>
    SBK_QtDesigner_QList_QWidgetPTR_IDX                      = 5, // QList<QWidget*>
    SBK_QtDesigner_QList_QObjectPTR_IDX                      = 6, // QList<QObject*>
    SBK_QtDesigner_QList_QVariant_IDX                        = 7, // QList<QVariant>
    SBK_QtDesigner_QList_QString_IDX                         = 8, // QList<QString>
    SBK_QtDesigner_QMap_QString_QVariant_IDX                 = 9, // QMap<QString,QVariant>
    SBK_QtDesigner_CONVERTERS_IDX_COUNT                      = 10,
};
// Macros for type check

QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
template<> inline PyTypeObject *SbkType< ::QAbstractExtensionFactory >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QAbstractExtensionFactory_IDX]); }
template<> inline PyTypeObject *SbkType< ::QAbstractExtensionManager >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QAbstractExtensionManager_IDX]); }
template<> inline PyTypeObject *SbkType< ::QAbstractFormBuilder >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QAbstractFormBuilder_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDesignerActionEditorInterface >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QDesignerActionEditorInterface_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDesignerContainerExtension >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QDesignerContainerExtension_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDesignerCustomWidgetCollectionInterface >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QDesignerCustomWidgetCollectionInterface_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDesignerCustomWidgetInterface >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QDesignerCustomWidgetInterface_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDesignerDnDItemInterface::DropType >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QDesignerDnDItemInterface_DropType_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDesignerDnDItemInterface >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QDesignerDnDItemInterface_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDesignerDynamicPropertySheetExtension >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QDesignerDynamicPropertySheetExtension_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDesignerFormEditorInterface >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QDesignerFormEditorInterface_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDesignerFormWindowCursorInterface::MoveOperation >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QDesignerFormWindowCursorInterface_MoveOperation_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDesignerFormWindowCursorInterface::MoveMode >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QDesignerFormWindowCursorInterface_MoveMode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDesignerFormWindowCursorInterface >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QDesignerFormWindowCursorInterface_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDesignerFormWindowInterface::FeatureFlag >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QDesignerFormWindowInterface_FeatureFlag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFlags<QDesignerFormWindowInterface::FeatureFlag> >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QFlags_QDesignerFormWindowInterface_FeatureFlag_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDesignerFormWindowInterface::ResourceFileSaveMode >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QDesignerFormWindowInterface_ResourceFileSaveMode_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDesignerFormWindowInterface >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QDesignerFormWindowInterface_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDesignerFormWindowManagerInterface::Action >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QDesignerFormWindowManagerInterface_Action_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDesignerFormWindowManagerInterface::ActionGroup >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QDesignerFormWindowManagerInterface_ActionGroup_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDesignerFormWindowManagerInterface >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QDesignerFormWindowManagerInterface_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDesignerFormWindowToolInterface >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QDesignerFormWindowToolInterface_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDesignerMemberSheetExtension >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QDesignerMemberSheetExtension_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDesignerObjectInspectorInterface >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QDesignerObjectInspectorInterface_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDesignerPropertyEditorInterface >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QDesignerPropertyEditorInterface_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDesignerPropertySheetExtension >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QDesignerPropertySheetExtension_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDesignerTaskMenuExtension >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QDesignerTaskMenuExtension_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDesignerWidgetBoxInterface >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QDesignerWidgetBoxInterface_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDesignerWidgetBoxInterface::Category::Type >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QDesignerWidgetBoxInterface_Category_Type_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDesignerWidgetBoxInterface::Category >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QDesignerWidgetBoxInterface_Category_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDesignerWidgetBoxInterface::Widget::Type >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QDesignerWidgetBoxInterface_Widget_Type_IDX]); }
template<> inline PyTypeObject *SbkType< ::QDesignerWidgetBoxInterface::Widget >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QDesignerWidgetBoxInterface_Widget_IDX]); }
template<> inline PyTypeObject *SbkType< ::QExtensionFactory >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QExtensionFactory_IDX]); }
template<> inline PyTypeObject *SbkType< ::QExtensionManager >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QExtensionManager_IDX]); }
template<> inline PyTypeObject *SbkType< ::QFormBuilder >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QFormBuilder_IDX]); }
template<> inline PyTypeObject *SbkType< ::QPyDesignerContainerExtension >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QPyDesignerContainerExtension_IDX]); }
template<> inline PyTypeObject *SbkType< ::QPyDesignerCustomWidgetCollection >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QPyDesignerCustomWidgetCollection_IDX]); }
template<> inline PyTypeObject *SbkType< ::QPyDesignerMemberSheetExtension >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QPyDesignerMemberSheetExtension_IDX]); }
template<> inline PyTypeObject *SbkType< ::QPyDesignerPropertySheetExtension >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QPyDesignerPropertySheetExtension_IDX]); }
template<> inline PyTypeObject *SbkType< ::QPyDesignerTaskMenuExtension >() { return Shiboken::Module::get(SbkPySide6_QtDesignerTypeStructs[SBK_QPyDesignerTaskMenuExtension_IDX]); }

} // namespace Shiboken

QT_WARNING_POP
#endif // SBK_QTDESIGNER_PYTHON_H

