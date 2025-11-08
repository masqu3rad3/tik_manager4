// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

/*********************************************************************
 * INJECT CODE
 ********************************************************************/

// @snippet qopenglshaderprogram_setuniformvalue_float
float value = %2;
%CPPSELF.setUniformValue(%1, value);
// @snippet qopenglshaderprogram_setuniformvalue_float

// @snippet qopenglshaderprogram_setuniformvalue_int
int value = %2;
%CPPSELF.setUniformValue(%1, value);
// @snippet qopenglshaderprogram_setuniformvalue_int

// @snippet qopenglversionfunctionsfactory-get
QAbstractOpenGLFunctions *af = %CPPSELF.%FUNCTION_NAME(%1, %2);
if (auto *f = dynamic_cast<QOpenGLFunctions_4_5_Core *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_4_5_Core *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_4_5_Compatibility *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_4_5_Compatibility *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_4_4_Core *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_4_4_Core *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_4_4_Compatibility *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_4_4_Compatibility *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_4_3_Core *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_4_3_Core *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_4_2_Core *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_4_2_Core *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_4_1_Core *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_4_1_Core *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_4_0_Core *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_4_0_Core *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_4_0_Compatibility *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_4_0_Compatibility *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_3_3_Core *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_3_3_Core *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_3_3_Compatibility *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_3_3_Compatibility *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_3_2_Core *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_3_2_Core *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_3_2_Compatibility *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_3_2_Compatibility *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_3_1 *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_3_1 *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_3_0 *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_3_0 *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_2_1 *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_2_1 *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_2_0 *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_2_0 *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_1_5 *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_1_5 *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_1_4 *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_1_4 *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_1_3 *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_1_3 *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_1_2 *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_1_2 *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_1_1 *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_1_1 *](f);
} else if (auto *f = dynamic_cast<QOpenGLFunctions_1_0 *>(af)) {
    %PYARG_0 = %CONVERTTOPYTHON[QOpenGLFunctions_1_0 *](f);
} else {
    QString message;
    QDebug(&message) << "No OpenGL functions could be obtained for" << %1;
    PyErr_SetString(PyExc_RuntimeError, message.toUtf8().constData());
    %PYARG_0 = Py_None;
}
// @snippet qopenglversionfunctionsfactory-get

// @snippet glgetvreturnsize_declaration
int glGetVReturnSize(GLenum pname);
// @snippet glgetvreturnsize_declaration

// @snippet glgeti-vreturnsize_declaration
int glGetI_VReturnSize(GLenum pname);
// @snippet glgeti-vreturnsize_declaration

// @snippet vao-binder-enter
Py_INCREF(%PYSELF);
pyResult = %PYSELF;
// @snippet vao-binder-enter

// @snippet vao-binder-exit
%CPPSELF.release();
// @snippet vao-binder-exit
