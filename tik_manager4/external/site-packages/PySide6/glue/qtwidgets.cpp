// Copyright (C) 2018 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

/*********************************************************************
 * INJECT CODE
 ********************************************************************/

// @snippet qtreewidgetitemiterator-next
if (**%CPPSELF) {
    QTreeWidgetItemIterator *%0 = new QTreeWidgetItemIterator((*%CPPSELF)++);
    %PYARG_0 = %CONVERTTOPYTHON[QTreeWidgetItemIterator *](%0);
}
// @snippet qtreewidgetitemiterator-next

// @snippet qtreewidgetitemiterator-value
QTreeWidgetItem *%0 = %CPPSELF.operator *();
%PYARG_0 = %CONVERTTOPYTHON[QTreeWidgetItem *](%0);
Shiboken::Object::releaseOwnership(%PYARG_0);
// @snippet qtreewidgetitemiterator-value

// @snippet qgraphicsitem
PyObject *userTypeConstant =  PyLong_FromLong(QGraphicsItem::UserType);
tpDict.reset(PepType_GetDict(Sbk_QGraphicsItem_TypeF()));
PyDict_SetItemString(tpDict.object(), "UserType", userTypeConstant);
// @snippet qgraphicsitem

// @snippet qgraphicsitem-scene-return-parenting
if (%0) {
    QObject *parent = %0->parent();
    Shiboken::AutoDecRef pyParent(%CONVERTTOPYTHON[QObject *](parent));
    Shiboken::Object::setParent(pyParent, %PYARG_0);
}
// @snippet qgraphicsitem-scene-return-parenting

// @snippet qgraphicsitem-isblockedbymodalpanel
QGraphicsItem *item_ = nullptr;
%RETURN_TYPE retval_ = %CPPSELF.%FUNCTION_NAME(&item_);
%PYARG_0 = PyTuple_New(2);
PyTuple_SetItem(%PYARG_0, 0, %CONVERTTOPYTHON[%RETURN_TYPE](retval_));
PyTuple_SetItem(%PYARG_0, 1, %CONVERTTOPYTHON[QGraphicsItem *](item_));
// @snippet qgraphicsitem-isblockedbymodalpanel

// @snippet qitemeditorfactory-registereditor
Shiboken::Object::releaseOwnership(%PYARG_2);
// @snippet qitemeditorfactory-registereditor

// @snippet qitemeditorfactory-setdefaultfactory
//this function is static we need keep ref to default value, to be able to call python virtual functions
static PyObject *_defaultValue = nullptr;
%CPPSELF.%FUNCTION_NAME(%1);
Py_INCREF(%PYARG_1);
if (_defaultValue)
    Py_DECREF(_defaultValue);

_defaultValue = %PYARG_1;
// @snippet qitemeditorfactory-setdefaultfactory

// @snippet qformlayout-fix-args
int _row;
QFormLayout::ItemRole _role;
%CPPSELF->%FUNCTION_NAME(%ARGUMENT_NAMES, &_row, &_role);
%PYARG_0 = PyTuple_New(2);
PyTuple_SetItem(%PYARG_0, 0, %CONVERTTOPYTHON[int](_row));
// On the C++ side, *rolePtr is not set if row == -1, in which case on
// the Python side this gets converted to a random value outside the
// enum range. Fix this by setting _role to a default value here.
if (_row == -1)
    _role = QFormLayout::LabelRole;
PyTuple_SetItem(%PYARG_0, 1, %CONVERTTOPYTHON[QFormLayout::ItemRole](_role));
// @snippet qformlayout-fix-args

// @snippet qfiledialog-return
%BEGIN_ALLOW_THREADS
%RETURN_TYPE retval_ = %CPPSELF.%FUNCTION_NAME(%1, %2, %3, %4, &%5, %6);
%END_ALLOW_THREADS
%PYARG_0 = PyTuple_New(2);
PyTuple_SetItem(%PYARG_0, 0, %CONVERTTOPYTHON[%RETURN_TYPE](retval_));
PyTuple_SetItem(%PYARG_0, 1, %CONVERTTOPYTHON[QString](%5));
// @snippet qfiledialog-return

// @snippet qwidget-addaction-glue
static PyObject *connectAction(QAction *action, PyObject *callback)
{
    PyObject *pyAct = %CONVERTTOPYTHON[QAction *](action);
    Shiboken::AutoDecRef result(PyObject_CallMethod(pyAct, "connect", "OsO",
                                                    pyAct,
                                                    SIGNAL(triggered()), callback));
    if (result.isNull()) {
        Py_DECREF(pyAct);
        return nullptr;
    }
    return pyAct;
}

static inline PyObject *addActionWithPyObject(QWidget *self, const QString &text,
                                              PyObject *callback)
{
    QAction *act = self->addAction(text);
    return connectAction(act, callback);
}

static inline PyObject *addActionWithPyObject(QWidget *self, const QIcon &icon, const QString &text,
                                              PyObject *callback)
{
    auto *act = self->addAction(icon, text);
    return connectAction(act, callback);
}

static inline PyObject *addActionWithPyObject(QWidget *self, const QString &text,
                                              const QKeySequence &shortcut,
                                              PyObject *callback)
{
    QAction *act = self->addAction(text, shortcut);
    return connectAction(act, callback);
}

static inline PyObject *addActionWithPyObject(QWidget *self, const QIcon &icon,
                                              const QString &text,
                                              const QKeySequence &shortcut,
                                              PyObject *callback)
{
    QAction *act = self->addAction(icon, text, shortcut);
    return connectAction(act, callback);
}
// @snippet qwidget-addaction-glue

// FIXME PYSIDE7: Remove in favor of widgets methods
// @snippet qmenu-glue
inline PyObject *addMenuActionWithPyObject(QMenu *self, const QIcon &icon,
                                           const QString &text, PyObject *callback,
                                           const QKeySequence &shortcut)
{
    QAction *act = self->addAction(text);

    if (!icon.isNull())
        act->setIcon(icon);

    if (!shortcut.isEmpty())
        act->setShortcut(shortcut);

    self->addAction(act);

    PyObject *pyAct = %CONVERTTOPYTHON[QAction *](act);
    Shiboken::AutoDecRef result(PyObject_CallMethod(pyAct, "connect", "OsO",
                                                    pyAct,
                                                    SIGNAL(triggered()), callback));
    if (result.isNull()) {
        Py_DECREF(pyAct);
        return nullptr;
    }

    return pyAct;
}
// @snippet qmenu-glue

// addAction(QString,PyObject*,QKeySequence) FIXME PYSIDE7 deprecated
// @snippet qmenu-addaction-1
%PYARG_0 = addMenuActionWithPyObject(%CPPSELF, QIcon(), %1, %2, %3);
// @snippet qmenu-addaction-1

// addAction(QIcon,QString,PyObject*,QKeySequence) FIXME PYSIDE7 deprecated
// @snippet qmenu-addaction-2
%PYARG_0 = addMenuActionWithPyObject(%CPPSELF, %1, %2, %3, %4);
// @snippet qmenu-addaction-2

// @snippet qmenu-addaction-3
%CPPSELF.addAction(%1);
// @snippet qmenu-addaction-3

// addAction(QString,PyObject*)
// @snippet qwidget-addaction-2
%PYARG_0 = addActionWithPyObject(%CPPSELF, %1, %2);
// @snippet qwidget-addaction-2

// addAction(QString,QKeySequence,PyObject*) or addAction(QIcon,QString,PyObject*)
// @snippet qwidget-addaction-3
%PYARG_0 = addActionWithPyObject(%CPPSELF, %1, %2, %3);
// @snippet qwidget-addaction-3

// addAction(QIcon,QString,QKeySequence,PyObject*)
// @snippet qwidget-addaction-4
%PYARG_0 = addActionWithPyObject(%CPPSELF, %1, %2, %3, %4);
// @snippet qwidget-addaction-4

// @snippet qmenu-clear
Shiboken::BindingManager &bm = Shiboken::BindingManager::instance();
const auto &actions = %CPPSELF.actions();
for (auto *act : actions) {
    if (auto wrapper = bm.retrieveWrapper(act)) {
        auto pyObj = reinterpret_cast<PyObject *>(wrapper);
        Py_INCREF(pyObj);
        Shiboken::Object::setParent(nullptr, pyObj);
        Shiboken::Object::invalidate(pyObj);
        Py_DECREF(pyObj);
    }
}
// @snippet qmenu-clear

// @snippet qmenubar-clear
const auto &actions = %CPPSELF.actions();
for (auto *act : actions) {
  Shiboken::AutoDecRef pyAct(%CONVERTTOPYTHON[QAction *](act));
  Shiboken::Object::setParent(nullptr, pyAct);
  Shiboken::Object::invalidate(pyAct);
}
// @snippet qmenubar-clear

// @snippet qtoolbox-removeitem
QWidget *_widget = %CPPSELF.widget(%1);
if (_widget) {
    Shiboken::AutoDecRef pyWidget(%CONVERTTOPYTHON[QWidget *](_widget));
    Shiboken::Object::setParent(0, pyWidget);
}
// @snippet qtoolbox-removeitem

// @snippet qlayout-help-functions
#ifndef _QLAYOUT_HELP_FUNCTIONS_
#define _QLAYOUT_HELP_FUNCTIONS_ // Guard for jumbo builds

static const char msgInvalidParameterAdd[] =
    "Invalid parameter None passed to addLayoutOwnership().";
static const char msgInvalidParameterRemoval[] =
    "Invalid parameter None passed to removeLayoutOwnership().";

void addLayoutOwnership(QLayout *layout, QLayoutItem *item);
void removeLayoutOwnership(QLayout *layout, QWidget *widget);

inline void addLayoutOwnership(QLayout *layout, QWidget *widget)
{
    if (layout == nullptr || widget == nullptr) {
        PyErr_SetString(PyExc_RuntimeError, msgInvalidParameterAdd);
        return;
    }

    //transfer ownership to parent widget
    QWidget *lw = layout->parentWidget();
    QWidget *pw = widget->parentWidget();

   Shiboken::AutoDecRef pyChild(%CONVERTTOPYTHON[QWidget *](widget));

    //Transfer parent to layout widget
    if (pw && lw && pw != lw)
        Shiboken::Object::setParent(nullptr, pyChild);

    if (!lw && !pw) {
        //keep the reference while the layout is orphan
        Shiboken::AutoDecRef pyParent(%CONVERTTOPYTHON[QWidget *](layout));
        Shiboken::Object::keepReference(reinterpret_cast<SbkObject *>(pyParent.object()),
                                        retrieveObjectName(pyParent).constData(),
                                        pyChild, true);
    } else {
        if (!lw)
            lw = pw;
        Shiboken::AutoDecRef pyParent(%CONVERTTOPYTHON[QWidget *](lw));
        Shiboken::Object::setParent(pyParent, pyChild);
    }
}

inline void addLayoutOwnership(QLayout *layout, QLayout *other)
{
    if (layout == nullptr || other == nullptr) {
        PyErr_SetString(PyExc_RuntimeError, msgInvalidParameterAdd);
        return;
    }

    //transfer all children widgets from other to layout parent widget
    QWidget *parent = layout->parentWidget();
    if (!parent) {
        //keep the reference while the layout is orphan
        Shiboken::AutoDecRef pyParent(%CONVERTTOPYTHON[QLayout *](layout));
        Shiboken::AutoDecRef pyChild(%CONVERTTOPYTHON[QLayout *](other));
        Shiboken::Object::keepReference(reinterpret_cast<SbkObject *>(pyParent.object()),
                                        retrieveObjectName(pyParent).constData(),
                                        pyChild, true);
        return;
    }

    for (int i = 0, i_max = other->count(); i < i_max; ++i) {
        QLayoutItem *item = other->itemAt(i);
        if (PyErr_Occurred() || !item)
            return;
        addLayoutOwnership(layout, item);
    }

    Shiboken::AutoDecRef pyParent(%CONVERTTOPYTHON[QLayout *](layout));
    Shiboken::AutoDecRef pyChild(%CONVERTTOPYTHON[QLayout *](other));
    Shiboken::Object::setParent(pyParent, pyChild);
}

inline void addLayoutOwnership(QLayout *layout, QLayoutItem *item)
{

    if (layout == nullptr || item == nullptr) {
        PyErr_SetString(PyExc_RuntimeError, msgInvalidParameterAdd);
        return;
    }

    if (QWidget *w = item->widget()) {
        addLayoutOwnership(layout, w);
    } else {
        if (QLayout *l = item->layout())
            addLayoutOwnership(layout, l);
    }

    Shiboken::AutoDecRef pyParent(%CONVERTTOPYTHON[QLayout *](layout));
    Shiboken::AutoDecRef pyChild(%CONVERTTOPYTHON[QLayoutItem *](item));
    Shiboken::Object::setParent(pyParent, pyChild);
}

static void removeWidgetFromLayout(QLayout *layout, QWidget *widget)
{
    if (layout == nullptr || widget == nullptr) {
        PyErr_SetString(PyExc_RuntimeError, msgInvalidParameterRemoval);
        return;
    }

    if (QWidget *parent = widget->parentWidget()) {
        //give the ownership to parent
        Shiboken::AutoDecRef pyParent(%CONVERTTOPYTHON[QWidget *](parent));
        Shiboken::AutoDecRef pyChild(%CONVERTTOPYTHON[QWidget *](widget));
        Shiboken::Object::setParent(pyParent, pyChild);
    } else {
        //remove reference on layout
        Shiboken::AutoDecRef pyParent(%CONVERTTOPYTHON[QWidget *](layout));
        Shiboken::AutoDecRef pyChild(%CONVERTTOPYTHON[QWidget *](widget));
        Shiboken::Object::removeReference(reinterpret_cast<SbkObject *>(pyParent.object()),
                                          retrieveObjectName(pyParent).constData(),
                                          pyChild);
    }
}

inline void removeLayoutOwnership(QLayout *layout, QLayoutItem *item)
{
    if (layout == nullptr || item == nullptr) {
        PyErr_SetString(PyExc_RuntimeError, msgInvalidParameterRemoval);
        return;
    }

    if (QWidget *w = item->widget()) {
        removeWidgetFromLayout(layout, w);
    } else {
        QLayout *l = item->layout();
        if (l && item != l)
            removeLayoutOwnership(layout, l);
    }

    Shiboken::AutoDecRef pyChild(%CONVERTTOPYTHON[QLayoutItem *](item));
    Shiboken::Object::invalidate(pyChild);
    Shiboken::Object::setParent(0, pyChild);
}

inline void removeLayoutOwnership(QLayout *layout, QWidget *widget)
{
    if (layout == nullptr || widget == nullptr) {
        PyErr_SetString(PyExc_RuntimeError, msgInvalidParameterRemoval);
        return;
    }

    for (int i = 0, i_max = layout->count(); i < i_max; ++i) {
        QLayoutItem *item = layout->itemAt(i);
        if (PyErr_Occurred() || !item)
            return;
        if (item->widget() == widget)
            removeLayoutOwnership(layout, item);
    }
}
#endif // _QLAYOUT_HELP_FUNCTIONS_
// @snippet qlayout-help-functions

// @snippet qlayout-setalignment
%CPPSELF.setAlignment(%1);
// @snippet qlayout-setalignment

// @snippet addownership-item-at
if (%0 != nullptr)
    addLayoutOwnership(%CPPSELF, %0);
// @snippet addownership-item-at

// @snippet addownership-1
addLayoutOwnership(%CPPSELF, %1);
// @snippet addownership-1

// @snippet addownership-2
addLayoutOwnership(%CPPSELF, %2);
// @snippet addownership-2

// @snippet removeownership-1
removeLayoutOwnership(%CPPSELF, %1);
// @snippet removeownership-1

// @snippet qgridlayout-getitemposition
int a, b, c, d;
%CPPSELF.%FUNCTION_NAME(%1, &a, &b, &c, &d);
%PYARG_0 = PyTuple_New(4);
PyTuple_SetItem(%PYARG_0, 0, %CONVERTTOPYTHON[int](a));
PyTuple_SetItem(%PYARG_0, 1, %CONVERTTOPYTHON[int](b));
PyTuple_SetItem(%PYARG_0, 2, %CONVERTTOPYTHON[int](c));
PyTuple_SetItem(%PYARG_0, 3, %CONVERTTOPYTHON[int](d));
// @snippet qgridlayout-getitemposition

// @snippet qgraphicsscene-destroyitemgroup
QGraphicsItem *parentItem = %1->parentItem();
Shiboken::AutoDecRef parent(%CONVERTTOPYTHON[QGraphicsItem *](parentItem));
const auto &childItems = %1->childItems();
for (auto *item : childItems)
    Shiboken::Object::setParent(parent, %CONVERTTOPYTHON[QGraphicsItem *](item));
%CPPSELF.%FUNCTION_NAME(%1);
// the arg was destroyed by Qt.
Shiboken::Object::invalidate(%PYARG_1);
// @snippet qgraphicsscene-destroyitemgroup

// @snippet qgraphicsscene-addwidget
%RETURN_TYPE %0 = %CPPSELF.%FUNCTION_NAME(%1, %2);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
Shiboken::Object::keepReference(reinterpret_cast<SbkObject *>(%PYARG_0), "setWidget(QWidget*)1", %PYARG_1);
// @snippet qgraphicsscene-addwidget

// @snippet qgraphicsscene-clear
const QList<QGraphicsItem *> items = %CPPSELF.items();
Shiboken::BindingManager &bm = Shiboken::BindingManager::instance();
for (auto *item : items) {
    SbkObject *obj = bm.retrieveWrapper(item);
    if (obj) {
        if (Py_REFCNT(reinterpret_cast<PyObject *>(obj)) > 1) // If the refcnt is 1 the object will vannish anyway.
            Shiboken::Object::invalidate(obj);
        Shiboken::Object::removeParent(obj);
    }
}
%CPPSELF.%FUNCTION_NAME();
// @snippet qgraphicsscene-clear

// @snippet qtreewidget-clear
QTreeWidgetItem *rootItem = %CPPSELF.invisibleRootItem();
Shiboken::BindingManager &bm = Shiboken::BindingManager::instance();

// PYSIDE-1251:
// Since some objects can be created with a parent and without
// being saved on a local variable (refcount = 1), they will be
// deleted when setting the parent to nullptr, so we change the loop
// to do this from the last child to the first, to avoid the case
// when the child(1) points to the original child(2) in case the
// first one was removed.
for (int i = rootItem->childCount() - 1; i >= 0; --i) {
    QTreeWidgetItem *item = rootItem->child(i);
    if (SbkObject *wrapper = bm.retrieveWrapper(item))
        Shiboken::Object::setParent(nullptr, reinterpret_cast<PyObject *>(wrapper));
}
// @snippet qtreewidget-clear

// @snippet qtreewidgetitem
// Only call the parent function if this return some value
// the parent can be the TreeWidget
if (%0)
  Shiboken::Object::setParent(%PYARG_0, %PYSELF);
// @snippet qtreewidgetitem

// @snippet qlistwidget-clear
Shiboken::BindingManager &bm = Shiboken::BindingManager::instance();
for (int i = 0, count = %CPPSELF.count(); i < count; ++i) {
    QListWidgetItem *item = %CPPSELF.item(i);
    if (auto wrapper = bm.retrieveWrapper(item)) {
        auto pyObj = reinterpret_cast<PyObject *>(wrapper);
        Py_INCREF(pyObj);
        Shiboken::Object::setParent(nullptr, pyObj);
        Shiboken::Object::invalidate(pyObj);
        Py_DECREF(pyObj);
    }
}
%CPPSELF.%FUNCTION_NAME();
// @snippet qlistwidget-clear

// @snippet qwidget-retrieveobjectname
#ifndef _RETRIEVEOBJECTNAME_
#define _RETRIEVEOBJECTNAME_ // Guard for jumbo builds
static QByteArray retrieveObjectName(PyObject *obj)
{
    Shiboken::AutoDecRef objName(PyObject_Str(obj));
    return Shiboken::String::toCString(objName);
}
#endif
// @snippet qwidget-retrieveobjectname

// @snippet qwidget-glue

// Transfer objects ownership from layout to widget
static inline void qwidgetReparentLayout(QWidget *parent, QLayout *layout)
{
    Shiboken::AutoDecRef pyParent(%CONVERTTOPYTHON[QWidget *](parent));

    for (int i=0, i_count = layout->count(); i < i_count; i++) {
        QLayoutItem *item = layout->itemAt(i);
        if (PyErr_Occurred() || !item)
            return;

        if (QWidget *w = item->widget()) {
            QWidget *pw = w->parentWidget();
            if (pw != parent) {
                Shiboken::AutoDecRef pyChild(%CONVERTTOPYTHON[QWidget *](w));
                Shiboken::Object::setParent(pyParent, pyChild);
            }
        } else {
            if (QLayout *l = item->layout())
                qwidgetReparentLayout(parent, l);
        }
    }

    Shiboken::AutoDecRef pyChild(%CONVERTTOPYTHON[QLayout *](layout));
    Shiboken::Object::setParent(pyParent, pyChild);
    //remove previous references
    Shiboken::Object::keepReference(reinterpret_cast<SbkObject *>(pyChild.object()),
                                    retrieveObjectName(pyChild).constData(),
                                    Py_None);
}

static inline void qwidgetSetLayout(QWidget *self, QLayout *layout)
{
    if (!layout || self->layout())
        return;

    QObject *oldParent = layout->parent();
    if (oldParent && oldParent != self) {
        if (oldParent->isWidgetType()) {
            // remove old parent policy
            Shiboken::AutoDecRef pyLayout(%CONVERTTOPYTHON[QLayout *](layout));
            Shiboken::Object::setParent(Py_None, pyLayout);
        } else {
            PyErr_Format(PyExc_RuntimeError, "QWidget::setLayout: Attempting to set QLayout \"%s\" on %s \"%s\", when the QLayout already has a parent",
                          qPrintable(layout->objectName()), self->metaObject()->className(), qPrintable(self->objectName()));
            return;
        }
    }

    if (oldParent != self) {
        qwidgetReparentLayout(self, layout);
        if (PyErr_Occurred())
            return;

        self->setLayout(layout);
    }
}
// @snippet qwidget-glue

// @snippet qwidget-setstyle
Shiboken::Object::keepReference(reinterpret_cast<SbkObject *>(%PYSELF), "__style__",  %PYARG_1);
// @snippet qwidget-setstyle

// @snippet qwidget-style
QStyle *myStyle = %CPPSELF->style();
if (myStyle && qApp) {
    bool keepReference = true;
    %PYARG_0 = %CONVERTTOPYTHON[QStyle *](myStyle);
    QStyle *appStyle = qApp->style();
    if (appStyle == myStyle) {
        Shiboken::AutoDecRef pyApp(%CONVERTTOPYTHON[QApplication *](qApp));
        // Do not set parentship when qApp is embedded
        if (Shiboken::Object::wasCreatedByPython(reinterpret_cast<SbkObject *>(pyApp.object()))) {
            Shiboken::Object::setParent(pyApp, %PYARG_0);
            Shiboken::Object::releaseOwnership(%PYARG_0);
            keepReference = false;
        }
    }
    if (keepReference)
        Shiboken::Object::keepReference(reinterpret_cast<SbkObject *>(%PYSELF), "__style__",  %PYARG_0);
}
// @snippet qwidget-style

// @snippet qapplication-init
static void QApplicationConstructor(PyObject *self, PyObject *pyargv, QApplicationWrapper **cptr)
{
    static int argc;
    static char **argv;
    PyObject *stringlist = PyTuple_GetItem(pyargv, 0);
    if (Shiboken::listToArgcArgv(stringlist, &argc, &argv, "PySideApp")) {
        *cptr = new QApplicationWrapper(argc, argv, 0);
        Shiboken::Object::releaseOwnership(reinterpret_cast<SbkObject *>(self));
        PySide::registerCleanupFunction(&PySide::destroyQCoreApplication);
    }
}
// @snippet qapplication-init

// @snippet qapplication-setStyle
if (qApp) {
    Shiboken::AutoDecRef pyApp(%CONVERTTOPYTHON[QApplication *](qApp));
    Shiboken::Object::setParent(pyApp, %PYARG_1);
    Shiboken::Object::releaseOwnership(%PYARG_1);
}
// @snippet qapplication-setStyle

// @snippet qwidget-setlayout
qwidgetSetLayout(%CPPSELF, %1);
// %FUNCTION_NAME() - disable generation of function call.
// @snippet qwidget-setlayout

// @snippet qtabwidget-removetab
QWidget *tab = %CPPSELF.widget(%1);
if (tab) {
    Shiboken::AutoDecRef pyWidget(%CONVERTTOPYTHON[QWidget *](tab));
    %CPPSELF.%FUNCTION_NAME(%1);
}
// @snippet qtabwidget-removetab

// @snippet qtabwidget-clear
Shiboken::BindingManager &bm = Shiboken::BindingManager::instance();
for (int i = 0, count = %CPPSELF.count(); i < count; ++i) {
    QWidget *widget = %CPPSELF.widget(i);
    if (bm.hasWrapper(widget)) {
        Shiboken::AutoDecRef pyWidget(%CONVERTTOPYTHON[QWidget *](widget));
        Shiboken::Object::releaseOwnership(pyWidget);
    }
}
%CPPSELF.%FUNCTION_NAME();
// @snippet qtabwidget-clear

// @snippet qlineedit-addaction
%CPPSELF.addAction(%1);
// @snippet qlineedit-addaction

// addAction(QIcon,QString,const QObject*,const char*,Qt::ConnectionType)
// @snippet qwidget-addaction-1
QAction *action = %CPPSELF.addAction(%1, %2);
%PYARG_0 = %CONVERTTOPYTHON[QAction *](action);
Shiboken::AutoDecRef result(PyObject_CallMethod(%PYARG_0,
    "connect", "OsO",
    %PYARG_0, SIGNAL(triggered()), %PYARG_3)
);
// @snippet qwidget-addaction-1

// addAction(QString,const QObject*,const char*,Qt::ConnectionType)
// @snippet qwidget-addaction-2
QAction *action = %CPPSELF.addAction(%1);
%PYARG_0 = %CONVERTTOPYTHON[QAction *](action);
Shiboken::AutoDecRef result(PyObject_CallMethod(%PYARG_0,
    "connect", "OsO",
    %PYARG_0, SIGNAL(triggered()), %PYARG_2)
);
// @snippet qwidget-addaction-2

// @snippet qtoolbar-clear
QList<PyObject *> lst;
Shiboken::BindingManager &bm = Shiboken::BindingManager::instance();
const auto &toolButtonChildren = %CPPSELF.findChildren<QToolButton *>();
for (auto *child : toolButtonChildren) {
    if (bm.hasWrapper(child)) {
        PyObject *pyChild = %CONVERTTOPYTHON[QToolButton *](child);
        Shiboken::Object::setParent(nullptr, pyChild);
        lst << pyChild;
    }
}

//Remove actions
const auto &actions = %CPPSELF.actions();
for (auto *act : actions) {
    Shiboken::AutoDecRef pyAct(%CONVERTTOPYTHON[QAction *](act));
    Shiboken::Object::setParent(nullptr, pyAct);
    Shiboken::Object::invalidate(pyAct);
}

%CPPSELF.clear();
for (auto *obj : std::as_const(lst)) {
    Shiboken::Object::invalidate(reinterpret_cast<SbkObject *>(obj));
    Py_XDECREF(obj);
}
// @snippet qtoolbar-clear

// @snippet qapplication-1
QApplicationConstructor(%PYSELF, args, &%0);
// @snippet qapplication-1

// @snippet qapplication-2
PyObject *empty = PyTuple_New(2);
if (!PyTuple_SetItem(empty, 0, PyList_New(0)))
    QApplicationConstructor(%PYSELF, empty, &%0);
// @snippet qapplication-2

// @snippet qgraphicsproxywidget-setwidget
QWidget *_old = %CPPSELF.widget();
if (_old)
   Shiboken::Object::setParent(nullptr, %CONVERTTOPYTHON[QWidget *](_old));
%CPPSELF.%FUNCTION_NAME(%1);
Shiboken::Object::setParent(%PYSELF, %PYARG_1);
// @snippet qgraphicsproxywidget-setwidget

// @snippet qapplication-exec
if (PyErr_WarnEx(PyExc_DeprecationWarning,
                 "'exec_' will be removed in the future. "
                 "Use 'exec' instead.",
                 1)) {
    return nullptr;
}
%BEGIN_ALLOW_THREADS
int cppResult = %CPPSELF.exec();
%END_ALLOW_THREADS
%PYARG_0 = %CONVERTTOPYTHON[int](cppResult);
// @snippet qapplication-exec

// @snippet qmenu-exec-1
if (PyErr_WarnEx(PyExc_DeprecationWarning,
                 "'exec_' will be removed in the future. "
                 "Use 'exec' instead.",
                 1)) {
    return nullptr;
}
%BEGIN_ALLOW_THREADS
QAction *cppResult = %CPPSELF.exec();
%END_ALLOW_THREADS
%PYARG_0 = %CONVERTTOPYTHON[QAction*](cppResult);
// @snippet qmenu-exec-1

// @snippet qmenu-exec-2
if (PyErr_WarnEx(PyExc_DeprecationWarning,
                 "'exec_' will be removed in the future. "
                 "Use 'exec' instead.",
                 1)) {
    return nullptr;
}
%BEGIN_ALLOW_THREADS
QAction *cppResult = %CPPSELF.exec(%1, %2);
%END_ALLOW_THREADS
%PYARG_0 = %CONVERTTOPYTHON[QAction*](cppResult);
// @snippet qmenu-exec-2

// @snippet qmenu-exec-3
if (PyErr_WarnEx(PyExc_DeprecationWarning,
                 "'exec_' will be removed in the future. "
                 "Use 'exec' instead.",
                 1)) {
    return nullptr;
}
%BEGIN_ALLOW_THREADS
QAction *cppResult = %CPPSELF.exec(%1, %2, %3, %4);
%END_ALLOW_THREADS
%PYARG_0 = %CONVERTTOPYTHON[QAction*](cppResult);
// @snippet qmenu-exec-3

// @snippet qstyleoption-typename
const char *styleOptionType(const QStyleOption *o)
{
    switch (o->type) {
    case QStyleOption::SO_Default:
        break;
    case QStyleOption::SO_FocusRect:
        return "QStyleOptionFocusRect";
    case QStyleOption::SO_Button:
        return "QStyleOptionButton";
    case QStyleOption::SO_Tab:
        return "QStyleOptionTab";
    case QStyleOption::SO_MenuItem:
        return "QStyleOptionMenuItem";
    case QStyleOption::SO_Frame:
        return "QStyleOptionFrame";
    case QStyleOption::SO_ProgressBar:
        return "QStyleOptionProgressBar";
    case QStyleOption::SO_ToolBox:
        return "QStyleOptionToolBox";
    case QStyleOption::SO_Header:
        return "QStyleOptionHeader";
    case QStyleOption::SO_DockWidget:
        return "QStyleOptionDockWidget";
    case QStyleOption::SO_ViewItem:
        return "QStyleOptionViewItem";
    case QStyleOption::SO_TabWidgetFrame:
        return "QStyleOptionTabWidgetFrame";
    case QStyleOption::SO_TabBarBase:
        return "QStyleOptionTabBarBase";
    case QStyleOption::SO_RubberBand:
        return "QStyleOptionRubberBand";
    case QStyleOption::SO_ToolBar:
        return "QStyleOptionToolBar";
    case QStyleOption::SO_GraphicsItem:
        return "QStyleOptionGraphicsItem";
    case QStyleOption::SO_Slider:
        return "QStyleOptionSlider";
    case QStyleOption::SO_SpinBox:
        return "QStyleOptionSpinBox";
    case QStyleOption::SO_ToolButton:
        return "QStyleOptionToolButton";
    case QStyleOption::SO_ComboBox:
        return "QStyleOptionComboBox";
    case QStyleOption::SO_TitleBar:
        return "QStyleOptionTitleBar";
    case QStyleOption::SO_GroupBox:
        return "QStyleOptionGroupBox";
    case QStyleOption::SO_SizeGrip:
        return "QStyleOptionSizeGrip";
    default:
        break;
    }
    return "QStyleOption";
}
// @snippet qstyleoption-typename

// @snippet qwizardpage-registerfield
auto *signalInst = reinterpret_cast<PySideSignalInstance *>(%PYARG_4);
const auto data = PySide::Signal::getEmitterData(signalInst);
if (data.methodIndex == -1)
    return PyErr_Format(PyExc_RuntimeError, "QWizardPage::registerField(): Unable to retrieve signal emitter.");
const auto method = data.emitter->metaObject()->method(data.methodIndex);
const QByteArray signature = QByteArrayLiteral("2") + method.methodSignature();
%BEGIN_ALLOW_THREADS
%CPPSELF.%FUNCTION_NAME(%1, %2, %3, signature.constData());
%END_ALLOW_THREADS
// @snippet qwizardpage-registerfield

// The constructor heuristics generate setting a parent-child relationship
// when creating a QDialog with parent. This causes the dialog to leak
// when it synchronous exec() is used instead of asynchronous show().
// In that case, remove the parent-child relationship.
// @snippet qdialog-exec-remove-parent-relation
Shiboken::Object::removeParent(reinterpret_cast<SbkObject *>(%PYSELF));
// @snippet qdialog-exec-remove-parent-relation

// @snippet qmessagebox-open-connect-accept
if (!PySide::callConnect(%PYSELF, SIGNAL(accepted()), %PYARG_1))
    return nullptr;
%CPPSELF.%FUNCTION_NAME();
// @snippet qmessagebox-open-connect-accept

// @snippet replace-widget-child
$CHILD_TYPE* oldChild = %CPPSELF.$FUNCTION_GET_OLD();
if (oldChild != nullptr && oldChild != $CPPARG) {
    Shiboken::AutoDecRef pyChild(%CONVERTTOPYTHON[$CHILD_TYPE*](oldChild));
    Shiboken::Object::setParent(nullptr, pyChild);
    Shiboken::Object::releaseOwnership(pyChild);
}
Shiboken::Object::setParent(%PYSELF, $PYARG);
// @snippet replace-widget-child

/*********************************************************************
 * CONVERSIONS
 ********************************************************************/

/*********************************************************************
 * NATIVE TO TARGET CONVERSIONS
 ********************************************************************/
