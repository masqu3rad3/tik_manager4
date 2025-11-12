// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

/*********************************************************************
 * INJECT CODE
 ********************************************************************/

// @snippet qsignalspy-signal
auto *signalInst = reinterpret_cast<PySideSignalInstance *>(%PYARG_1);
PyObject *emitterPyObject = PySide::Signal::getObject(signalInst);
QObject* emitter = %CONVERTTOCPP[QObject *](emitterPyObject);
QByteArray signature = PySide::Signal::getSignature(signalInst);
if (!signature.isEmpty())
    signature.prepend('2'); // SIGNAL() macro

if (emitter == nullptr || signature.isEmpty()) {
    QByteArray error = QByteArrayLiteral("Wrong parameter (")
        + (%PYARG_1)->ob_type->tp_name
        + QByteArrayLiteral(") passed, QSignalSpy requires a signal.");
    PyErr_SetString(PyExc_ValueError, error.constData());
    return -1;
}

// PySide::Signal::getObject() increments the refcount for emitterPyObject,
// but there is nothing that decrements the count when the spy goes out of
// scope.  It doesn't seem like QSignalSpy should prevent the target object
// from being garbage collected.  So we need to decrement the refcount here.
Py_DECREF(emitterPyObject);
%0 = new QSignalSpy(emitter, signature.constData());
// @snippet qsignalspy-signal
