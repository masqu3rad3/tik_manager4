// Copyright (C) 2018 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

// @snippet qmlerrror-repr
const QByteArray message = %CPPSELF.toString().toUtf8();
%PYARG_0 = Shiboken::String::fromCString(message.constData());
// @snippet qmlerrror-repr

// @snippet qmlattachedpropertiesobject
auto *%0 = PySide::Qml::qmlAttachedPropertiesObject(%ARGUMENT_NAMES);
%PYARG_0 = %CONVERTTOPYTHON[QObject*](%0);
// @snippet qmlattachedpropertiesobject

// @snippet qmlregistertype
int %0 = PySide::Qml::qmlRegisterType(%ARGUMENT_NAMES);
%PYARG_0 = %CONVERTTOPYTHON[int](%0);
// @snippet qmlregistertype

// @snippet qmlregistersingletontype_qobject_callback
int %0 = PySide::Qml::qmlRegisterSingletonType(%ARGUMENT_NAMES, true, true);
%PYARG_0 = %CONVERTTOPYTHON[int](%0);
// @snippet qmlregistersingletontype_qobject_callback

// @snippet qmlregistersingletontype_qobject_nocallback
int %0 = PySide::Qml::qmlRegisterSingletonType(%ARGUMENT_NAMES, nullptr, true, false);
%PYARG_0 = %CONVERTTOPYTHON[int](%0);
// @snippet qmlregistersingletontype_qobject_nocallback

// @snippet qmlregistersingletontype_qjsvalue
int %0 = PySide::Qml::qmlRegisterSingletonType(nullptr, %ARGUMENT_NAMES, false, true);
%PYARG_0 = %CONVERTTOPYTHON[int](%0);
// @snippet qmlregistersingletontype_qjsvalue

// @snippet qmlregistersingletoninstance
int %0 = PySide::Qml::qmlRegisterSingletonInstance(%ARGUMENT_NAMES);
%PYARG_0 = %CONVERTTOPYTHON[int](%0);
// @snippet qmlregistersingletoninstance

// @snippet qmlregisteruncreatabletype
int %0 = PySide::Qml::qmlRegisterType(%ARGUMENT_NAMES, false);
%PYARG_0 = %CONVERTTOPYTHON[int](%0);
// @snippet qmlregisteruncreatabletype

// @snippet init
PySide::Qml::init(module);
initQtQmlVolatileBool(module);
// @snippet init

// @snippet qjsengine-toscriptvalue
%RETURN_TYPE retval = %CPPSELF.%FUNCTION_NAME(%1);
return %CONVERTTOPYTHON[%RETURN_TYPE](retval);
// @snippet qjsengine-toscriptvalue

// @snippet qmlelement
%PYARG_0 = PySide::Qml::qmlElementMacro(%ARGUMENT_NAMES);
// @snippet qmlelement

// @snippet qmlanonymous
%PYARG_0 = PySide::Qml::qmlAnonymousMacro(%ARGUMENT_NAMES);
// @snippet qmlanonymous

// @snippet qmlsingleton
%PYARG_0 = PySide::Qml::qmlSingletonMacro(%ARGUMENT_NAMES);
// @snippet qmlsingleton

// @snippet qqmlengine-singletoninstance-qmltypeid
QJSValue instance = %CPPSELF.singletonInstance<QJSValue>(%1);
if (instance.isNull()) {
    Py_INCREF(Py_None);
    %PYARG_0 = Py_None;
} else if (instance.isQObject()) {
    QObject *result = instance.toQObject();
    %PYARG_0 = %CONVERTTOPYTHON[QObject *](result);
} else  {
    %PYARG_0 = %CONVERTTOPYTHON[QJSValue](instance);
}
// @snippet qqmlengine-singletoninstance-qmltypeid

// @snippet qqmlengine-singletoninstance-typename
QJSValue instance = %CPPSELF.singletonInstance<QJSValue>(%1, %2);
if (instance.isNull()) {
    Py_INCREF(Py_None);
    %PYARG_0 = Py_None;
} else if (instance.isQObject()) {
    QObject *result = instance.toQObject();
    %PYARG_0 = %CONVERTTOPYTHON[QObject *](result);
} else  {
    %PYARG_0 = %CONVERTTOPYTHON[QJSValue](instance);
}
// @snippet qqmlengine-singletoninstance-typename
