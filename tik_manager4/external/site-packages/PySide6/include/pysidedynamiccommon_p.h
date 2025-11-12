// Copyright (C) 2025 Ford Motor Company
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDE_DYNAMIC_COMMON_P_H
#define PYSIDE_DYNAMIC_COMMON_P_H

#include <sbkconverter.h>

#include <QtCore/qlist.h>
#include <QtCore/qvariant.h>
#include <QtCore/qmetatype.h>

PyObject *toPython(const QVariant &variant);
int create_managed_py_enums(PyObject *self, QMetaObject *meta);
PyObject *DynamicType_get_enum(PyObject *self, PyObject *name);

// Data for dynamically created property handlers
struct PropertyCapsule
{
    QByteArray name;
    int propertyIndex;   // meta->indexOfProperty() - including offset
    int indexInObject;   // Index minus offset for indexing into QVariantList
};

// Data for dynamically created method handlers
struct MethodCapsule
{
    QByteArray name;
    int methodIndex;
    QList<QMetaType> argumentTypes;
    QMetaType returnType; // meta->indexOfMethod() - including offset
};

// These functions are used to create a PyCapsule holding a pointer to a C++
// object, which is set as an attribute on a Python type. When the Python
// type is garbage collected, the type's attributes are as well, resulting in
// the capsule's cleanup running to delete the pointer. This won't be as
// efficient as a custom tp_free on the type, but it's easier to manage.
// And it only runs when as all references to the type (and all instances) are
// released, so it won't be used frequently.

extern int capsule_count;

template <typename T>
void Capsule_destructor(PyObject *capsule)
{
    capsule_count--;
    T pointer = static_cast<T>(PyCapsule_GetPointer(capsule, nullptr));
    delete pointer;
    pointer = nullptr;
}

template <>
inline void Capsule_destructor<SbkConverter *>(PyObject *capsule)
{
    capsule_count--;
    SbkConverter *pointer = static_cast<SbkConverter *>(PyCapsule_GetPointer(capsule, nullptr));
    Shiboken::Conversions::deleteConverter(pointer);
    pointer = nullptr;
}

template <typename T>
int set_cleanup_capsule_attr_for_pointer(PyTypeObject *type, const char *name, T pointer)
{
    static_assert(std::is_pointer<T>::value, "T must be a pointer type");

    if (!pointer) {
        PyErr_SetString(PyExc_RuntimeError, "Pointer is null");
        return -1;
    }
    auto capsule = PyCapsule_New(pointer, nullptr, Capsule_destructor<T>);
    if (!capsule)
        return -1;  // Propagate the error

    if (PyObject_SetAttrString(reinterpret_cast<PyObject *>(type), name, capsule) < 0)
        return -1;  // Propagate the error

    Py_DECREF(capsule);
    capsule_count++;

    return 0;
}

#endif // PYSIDE_DYNAMIC_COMMON_P_H
