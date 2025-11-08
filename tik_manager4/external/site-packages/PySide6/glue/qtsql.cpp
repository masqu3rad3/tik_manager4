// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only


// @snippet simple-exec
if (PyErr_WarnEx(PyExc_DeprecationWarning,
                 "'exec_' will be removed in the future. "
                 "Use 'exec' instead.",
                 1)) {
    return nullptr;
}
%BEGIN_ALLOW_THREADS
bool cppResult = %CPPSELF.exec();
%END_ALLOW_THREADS
%PYARG_0 = %CONVERTTOPYTHON[bool](cppResult);
// @snippet simple-exec


// @snippet qsqldatabase-exec
if (PyErr_WarnEx(PyExc_DeprecationWarning,
                 "'exec_' will be removed in the future. "
                 "Use 'exec' instead.",
                 1)) {
    return nullptr;
}
%BEGIN_ALLOW_THREADS
QSqlQuery cppResult = %CPPSELF.exec(%1);
%END_ALLOW_THREADS
%PYARG_0 = %CONVERTTOPYTHON[QSqlQuery](cppResult);
// @snippet qsqldatabase-exec

// @snippet qsqlquery-exec
if (PyErr_WarnEx(PyExc_DeprecationWarning,
                 "'exec_' will be removed in the future. "
                 "Use 'exec' instead.",
                 1)) {
    return nullptr;
}
%BEGIN_ALLOW_THREADS
bool cppResult = %CPPSELF.exec(%1);
%END_ALLOW_THREADS
%PYARG_0 = %CONVERTTOPYTHON[bool](cppResult);
// @snippet qsqlquery-exec

// @snippet qsqlresult-exec
if (PyErr_WarnEx(PyExc_DeprecationWarning,
                 "'exec_' will be removed in the future. "
                 "Use 'exec' instead.",
                 1)) {
    return nullptr;
}
%BEGIN_ALLOW_THREADS
#ifndef AVOID_PROTECTED_HACK
bool cppResult = %CPPSELF.exec();
#else
bool cppResult = static_cast<::QSqlResultWrapper *>(cppSelf)->QSqlResultWrapper::exec_protected();
#endif
%END_ALLOW_THREADS
%PYARG_0 = %CONVERTTOPYTHON[bool](cppResult);
// @snippet qsqlresult-exec
