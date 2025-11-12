// Copyright (C) 2016 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#include <sbkpython.h>
#include <shiboken.h>
#include <pysideweakref.h>

#include <QtCore/QEasingCurve>

#include "glue/qeasingcurve_glue.h"

#define MAX_CUSTOM_FUNCTIONS    10

static void deleteData(void *data);

struct CustomFunctionsData
{
    static CustomFunctionsData m_list[MAX_CUSTOM_FUNCTIONS];

    PySideEasingCurveFunctor *m_obj;
    QEasingCurve::EasingFunction m_func;
};

CustomFunctionsData CustomFunctionsData::m_list[MAX_CUSTOM_FUNCTIONS];

template<int N>
struct CustomFunctions
{
    static void init()
    {
        CustomFunctionsData data;
        data.m_obj = 0;
        data.m_func = &CustomFunctions<N>::callback;
        CustomFunctionsData::m_list[N] = data;

        CustomFunctions<N-1>::init();
    }

    static qreal callback(qreal v)
    {
        return (*CustomFunctionsData::m_list[N].m_obj)(v);
    }
};

template<>
struct CustomFunctions<0>
{
    static void init()
    {
        CustomFunctionsData data;
        data.m_obj = 0;
        data.m_func = &CustomFunctions<0>::callback;
        CustomFunctionsData::m_list[0] = data;
    }

    static qreal callback(qreal v)
    {
        return (*CustomFunctionsData::m_list[0].m_obj)(v);
    }
};

void deleteData(void *data)
{
    delete (PySideEasingCurveFunctor *)(data);
}

void PySideEasingCurveFunctor::init()
{
    CustomFunctions<MAX_CUSTOM_FUNCTIONS-1>::init();
}

QEasingCurve::EasingFunction PySideEasingCurveFunctor::createCustomFunction(PyObject *parent, PyObject *pyFunc)
{
    for(int i=0; i < MAX_CUSTOM_FUNCTIONS; i++) {
        CustomFunctionsData &data = CustomFunctionsData::m_list[i];
        if (data.m_obj == 0) {
            data.m_obj = new PySideEasingCurveFunctor(i, parent, pyFunc);
            return data.m_func;
        }
    }
    //PyErr_Format(PyExc_RuntimeError, "PySide only supports %d custom functions simultaneously.", MAX_CUSTOM_FUNCTIONS);
    return 0;
}

PySideEasingCurveFunctor::~PySideEasingCurveFunctor()
{

    CustomFunctionsData::m_list[m_index].m_obj = 0;
    PyObject_SetAttr(m_parent, Shiboken::PyMagicName::ecf(), Py_None);
}

qreal PySideEasingCurveFunctor::operator()(qreal progress)
{
    Shiboken::GilState state;
    PyObject *args = Py_BuildValue("(f)", progress);
    PyObject *result = PyObject_CallObject(m_func, args);
    qreal cppResult = 0.0;
    if (result) {
        Shiboken::Conversions::pythonToCppCopy(Shiboken::Conversions::PrimitiveTypeConverter<qreal>(), result, &cppResult);
        Py_DECREF(result);
    }
    Py_DECREF(args);
    return cppResult;
}

PyObject *PySideEasingCurveFunctor::callable()
{
    Py_INCREF(m_func);
    return m_func;
}

PyObject *PySideEasingCurveFunctor::callable(PyObject *parent)
{
    return PyObject_GetAttr(parent, Shiboken::PyMagicName::ecf());
}

PySideEasingCurveFunctor::PySideEasingCurveFunctor(int index, PyObject *parent, PyObject *pyFunc)
    : m_parent(parent), m_func(pyFunc), m_index(index)
{
    PyObject_SetAttr(m_parent, Shiboken::PyMagicName::ecf(), m_func);
    PySide::WeakRef::create(m_parent, deleteData, this);
}
