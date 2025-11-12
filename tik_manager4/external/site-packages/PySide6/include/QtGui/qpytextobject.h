// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef QPYTEXTOBJECT
#define QPYTEXTOBJECT

#include <QtCore/QObject>
#include <QtGui/QTextObjectInterface>

// Qt5: no idea why this definition is not found automatically! It should come
// from <QTextObjectInterface> which resolves to qabstracttextdocumentlayout.h
#ifdef Q_MOC_RUN
Q_DECLARE_INTERFACE(QTextObjectInterface, "org.qt-project.Qt.QTextObjectInterface")
#endif

QT_BEGIN_NAMESPACE
class QPyTextObject : public QObject, public QTextObjectInterface
{
    Q_OBJECT
    Q_INTERFACES(QTextObjectInterface)
public:
    QPyTextObject(QObject *parent = nullptr) : QObject(parent) {}
};
QT_END_NAMESPACE

#endif
