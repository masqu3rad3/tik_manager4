// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef __QEASINGCURVE_GLUE__
#define __QEASINGCURVE_GLUE__

#include <sbkpython.h>
#include <QtCore/QEasingCurve>

class PySideEasingCurveFunctor
{
    public:
        static void init();
        static QEasingCurve::EasingFunction createCustomFunction(PyObject *parent, PyObject *pyFunc);

        qreal operator()(qreal progress);

        PyObject *callable(); //Return New reference
        static PyObject *callable(PyObject *parent); //Return New reference

        ~PySideEasingCurveFunctor();
    private:
        PyObject *m_parent;
        PyObject *m_func;
        int m_index;

        PySideEasingCurveFunctor(int index, PyObject *parent, PyObject *pyFunc);
};

#endif
