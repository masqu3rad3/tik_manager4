// Copyright (C) 2025 Ford Motor Company
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef PYSIDE_CAPSULEMETHOD_P_H
#define PYSIDE_CAPSULEMETHOD_P_H

#include <sbkpython.h>

extern "C"
{

/**
 * This code is needed to solve, in C++ and adhering to the stable API,
 * creating what are in effect lambda functions as instance methods on custom
 * types. The goal is to be able to add methods to a dynamic type. If the .rep
 * file defines a slot `mySlot`, it need to be added to the dynamic type. For
 * Source types, this should be an abstract method that raises a
 * NotImplementedError unless defined in the Python subclass. For Replica
 * types, this should include an implementation that forwards the request
 * through the underlying QRemoteObjectReplica instance.
 *
 * The stable API doesn't currently provide a way define a method that can
 * receive both the `self`, `args`, and runtime (but constant per method, i.e.,
 * lambda like) data using Py_tp_methods. Possibly post 3.13 when METH_METHOD is
 * part of the stable API. But for now, it is not.
 *
 * The solution is to create a custom descriptor
 * (https://docs.python.org/3/howto/descriptor.html) that can hold the runtime
 * data and then when called, will return a PyCFunction_New generated PyObject
 * that is passed both class instance `self` and the runtime data (a PyCapsule)
 * together as a tuple as a new `self` for the method. The static method
 * definition needs to expect and handle this, but when combined in C++, we can
 * define a single handler that receives both the original `self` of the instance
 * and the runtime capsule with data for handling.
 */

/**
  * The CapsuleDescriptorData struct is what will be passed as the pseudo `self`
  * from a CapsuleMethod or CapsuleProperty to the associated handler method. The
  * handler method (which should look like a standard PyMethodDef method) should
  * parse it into the payload (the "lambda variables") and the actual instance
  * (the "self").
  */
struct CapsuleDescriptorData
{
    PyObject *self;
    PyObject *payload;
};

/**
 * The new type defining a descriptor that stores a PyCapsule.  This is used to
 * store the runtime data, with the __get__ method returning a new Callable.
 */
PyTypeObject *CapsuleMethod_TypeF(void);

/**
 * The new type defining a descriptor that stores a PyCapsule.  This is used to
 * store the runtime data, with the __get__ (and __set__ if isWritable) providing
 * property behavior.
 */
PyTypeObject *CapsuleProperty_TypeF(bool isWritable);

/**
 * Add a capsule method (a descriptor) to a type.  This will create a new capsule
 * method descriptor and add it as an attribute to the type, using the given name.
 *
 * A single handle can then respond to what appear to be distinct methods on the
 * type, but using the runtime data (from the capsule) when handling each call.
 *
 * @param type The type to attach the created descriptor to.
 * @param method The method definition to associate with the descriptor.
 *               The name of the method will be used as the attribute name.
 * @param capsule The capsule to store in the descriptor.
 * @return True if the descriptor was added successfully, false otherwise.
 */
bool add_capsule_method_to_type(PyTypeObject *type, PyMethodDef *method,
                                PyObject *capsule);

/**
 * Make a new CapsuleProperty type.
 */
PyObject *make_capsule_property(PyMethodDef *method, PyObject *capsule,
                                bool isWritable = false);

} // extern "C"

#endif // PYSIDE_CAPSULEMETHOD_P_H
