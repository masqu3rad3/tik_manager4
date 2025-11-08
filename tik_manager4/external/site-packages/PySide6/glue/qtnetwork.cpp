// Copyright (C) 2018 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

// @snippet qudpsocket-readdatagram
Shiboken::ArrayPointer<char> data(%ARGUMENT_NAMES);
QHostAddress ha;
quint16 port;
%BEGIN_ALLOW_THREADS
%RETURN_TYPE retval = %CPPSELF.%FUNCTION_NAME(data, %ARGUMENT_NAMES, &ha, &port);
%END_ALLOW_THREADS
QByteArray ba(data, retval);
%PYARG_0 = PyTuple_New(3);
PyTuple_SetItem(%PYARG_0, 0, %CONVERTTOPYTHON[QByteArray](ba));
PyTuple_SetItem(%PYARG_0, 1, %CONVERTTOPYTHON[QHostAddress](ha));
PyTuple_SetItem(%PYARG_0, 2, %CONVERTTOPYTHON[quint16](port));
// @snippet qudpsocket-readdatagram

// @snippet qhostinfo-lookuphost-functor
struct QHostInfoFunctor : public Shiboken::PyObjectHolder
{
public:
    using Shiboken::PyObjectHolder::PyObjectHolder;

    void operator()(const QHostInfo &hostInfo);
};

void QHostInfoFunctor::operator()(const QHostInfo &hostInfo)
{
    Shiboken::GilState state;
    Shiboken::AutoDecRef arglist(PyTuple_New(1));
    auto *pyHostInfo = %CONVERTTOPYTHON[QHostInfo](hostInfo);
    PyTuple_SetItem(arglist.object(), 0, pyHostInfo);
    Shiboken::AutoDecRef ret(PyObject_CallObject(object(), arglist));
    release(); // single shot
}
// @snippet qhostinfo-lookuphost-functor

// @snippet qhostinfo-lookuphost-callable
%CPPSELF.%FUNCTION_NAME(%1, QHostInfoFunctor(%PYARG_2));
// @snippet qhostinfo-lookuphost-callable

// @snippet qipv6address-len
return 16;
// @snippet qipv6address-len

// @snippet qipv6address-getitem
if (_i >= 16) {
    PyErr_SetString(PyExc_IndexError, "index out of bounds");
    return nullptr;
}
if (_i < 0)
    _i = 16 - qAbs(_i);

uint item = %CPPSELF.c[_i];
return %CONVERTTOPYTHON[uint](item);
// @snippet qipv6address-getitem

// @snippet qipv6address-setitem
if (_i >= 16) {
    PyErr_SetString(PyExc_IndexError, "index out of bounds");
    return -1;
}
if (_i < 0)
    _i = 16 - qAbs(_i);
quint8 item = %CONVERTTOCPP[quint8](_value);
%CPPSELF.c[_i] = item;
return 0;
// @snippet qipv6address-setitem

// @snippet qrestaccessmanager-functor
class QRestFunctor
{
public:
    explicit QRestFunctor(PyObject *callable) noexcept : m_callable(callable)
    {
        Py_INCREF(callable);
    }

    void operator()(QRestReply &restReply);

private:
    PyObject *m_callable;
};

void QRestFunctor::operator()(QRestReply &restReply)
{
    Q_ASSERT(m_callable);
    Shiboken::GilState state;
    Shiboken::AutoDecRef arglist(PyTuple_New(1));
    auto *restReplyPtr = &restReply;
    auto *pyRestReply = %CONVERTTOPYTHON[QRestReply*](restReplyPtr);
    PyTuple_SetItem(arglist.object(), 0, pyRestReply);
    Shiboken::AutoDecRef ret(PyObject_CallObject(m_callable, arglist));
    Py_DECREF(m_callable);
    m_callable = nullptr;
}
// @snippet qrestaccessmanager-functor

// @snippet qrestaccessmanager-callback
auto *networkReply = %CPPSELF.%FUNCTION_NAME(%1, %2, QRestFunctor(%PYARG_3));
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](networkReply);
// @snippet qrestaccessmanager-callback

// @snippet qrestaccessmanager-data-callback
auto *networkReply = %CPPSELF.%FUNCTION_NAME(%1, %2, %3, QRestFunctor(%PYARG_4));
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](networkReply);
// @snippet qrestaccessmanager-data-callback

// @snippet qrestaccessmanager-method-data-callback
auto *networkReply = %CPPSELF.%FUNCTION_NAME(%1, %2, %3, %4, QRestFunctor(%PYARG_5));
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](networkReply);
// @snippet qrestaccessmanager-method-data-callback

// @snippet qrestreply-readjson
QJsonParseError jsonParseError;
std::optional<QJsonDocument> documentOptional = %CPPSELF.%FUNCTION_NAME(&jsonParseError);

PyObject *pyDocument{};
if (documentOptional.has_value()) {
    const auto &document = documentOptional.value();
    pyDocument = %CONVERTTOPYTHON[QJsonDocument](document);
} else {
    pyDocument = Py_None;
    Py_INCREF(Py_None);
}

%PYARG_0 = PyTuple_New(2);
PyTuple_SetItem(%PYARG_0, 0, pyDocument);
PyTuple_SetItem(%PYARG_0, 1, %CONVERTTOPYTHON[QJsonParseError](jsonParseError));
// @snippet qrestreply-readjson
