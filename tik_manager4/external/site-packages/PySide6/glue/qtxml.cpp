// Copyright (C) 2018 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

// @snippet qdomdocument-setcontent
QString _errorMsg_;
int _errorLine_ = 0;
int _errorColumn_ = 0;
%BEGIN_ALLOW_THREADS
bool _ret_ = %CPPSELF.%FUNCTION_NAME(%ARGUMENT_NAMES, &_errorMsg_, &_errorLine_,
    &_errorColumn_);
%END_ALLOW_THREADS
%PYARG_0 = PyTuple_New(4);
PyTuple_SetItem(%PYARG_0, 0, %CONVERTTOPYTHON[bool](_ret_));
PyTuple_SetItem(%PYARG_0, 1, %CONVERTTOPYTHON[QString](_errorMsg_));
PyTuple_SetItem(%PYARG_0, 2, %CONVERTTOPYTHON[int](_errorLine_));
PyTuple_SetItem(%PYARG_0, 3, %CONVERTTOPYTHON[int](_errorColumn_));
// @snippet qdomdocument-setcontent
