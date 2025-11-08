// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef QPYDESIGNEREXTENSIONS_H
#define QPYDESIGNEREXTENSIONS_H

#include <QtDesigner/QDesignerContainerExtension>
#include <QtDesigner/QDesignerMemberSheetExtension>
#include <QtDesigner/QDesignerPropertySheetExtension>
#include <QtDesigner/QDesignerTaskMenuExtension>
#include <QtUiPlugin/QDesignerCustomWidgetCollectionInterface>
#include <QtUiPlugin/QDesignerCustomWidgetInterface>

// Not automatically found since "find_package(Qt6 COMPONENTS Designer)" is not used

#ifdef Q_MOC_RUN
Q_DECLARE_INTERFACE(QDesignerContainerExtension, "org.qt-project.Qt.Designer.Container")
Q_DECLARE_INTERFACE(QDesignerMemberSheetExtension, "org.qt-project.Qt.Designer.MemberSheet")
Q_DECLARE_EXTENSION_INTERFACE(QDesignerPropertySheetExtension, "org.qt-project.Qt.Designer.PropertySheet")
Q_DECLARE_INTERFACE(QDesignerTaskMenuExtension, "org.qt-project.Qt.Designer.TaskMenu")
Q_DECLARE_INTERFACE(QDesignerCustomWidgetCollectionInterface, "org.qt-project.Qt.QDesignerCustomWidgetCollectionInterface")
#endif

struct _object; // PyObject

QT_BEGIN_NAMESPACE

// Extension implementations need to inherit QObject which cannot be done in Python.
// Provide a base class (cf QPyTextObject).

class QPyDesignerContainerExtension : public QObject, public QDesignerContainerExtension
{
    Q_OBJECT
    Q_INTERFACES(QDesignerContainerExtension)
public:
    explicit QPyDesignerContainerExtension(QObject *parent = nullptr) : QObject(parent) {}
};

class QPyDesignerMemberSheetExtension : public QObject, public QDesignerMemberSheetExtension
{
    Q_OBJECT
    Q_INTERFACES(QDesignerMemberSheetExtension)
public:
    explicit QPyDesignerMemberSheetExtension(QObject *parent = nullptr) : QObject(parent) {}
};

class QPyDesignerPropertySheetExtension : public QObject, public QDesignerPropertySheetExtension
{
    Q_OBJECT
    Q_INTERFACES(QDesignerPropertySheetExtension)
public:
    explicit QPyDesignerPropertySheetExtension(QObject *parent = nullptr) : QObject(parent) {}
};

class QPyDesignerTaskMenuExtension : public QObject, public QDesignerTaskMenuExtension
{
    Q_OBJECT
    Q_INTERFACES(QDesignerTaskMenuExtension)
public:
    explicit QPyDesignerTaskMenuExtension(QObject *parent = nullptr) : QObject(parent) {}
};

class QPyDesignerCustomWidgetCollection : public QDesignerCustomWidgetCollectionInterface
{
public:
    ~QPyDesignerCustomWidgetCollection();

    static QPyDesignerCustomWidgetCollection *instance();

    QList<QDesignerCustomWidgetInterface *> customWidgets() const override;

    static void addCustomWidget(QDesignerCustomWidgetInterface *c);

    static bool _registerCustomWidgetHelper(_object *typeArg, _object *kwds);

private:
    QPyDesignerCustomWidgetCollection();

    QList<QDesignerCustomWidgetInterface *> m_customWidgets;
};

QT_END_NAMESPACE

#endif // QPYDESIGNEREXTENSIONS_H
