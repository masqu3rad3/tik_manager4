// Copyright (C) 2022 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef CLASSDECORATOR_P_H
#define CLASSDECORATOR_P_H

#include <pysidemacros.h>

#include <sbkpython.h>
#include <pep384ext.h>

#include <QtCore/qbytearray.h>

#include <array>
#include <string>

/// Helpers for class decorators with parameters
namespace PySide::ClassDecorator {

/// Base class for private objects of class decorators with parameters
class PYSIDE_API DecoratorPrivate
{
public:
     Q_DISABLE_COPY_MOVE(DecoratorPrivate)

    virtual ~DecoratorPrivate();

    /// Virtual function which is passed the decorated class type
    /// \param args Decorated class type argument
    /// \return class with reference count increased if the call was successful,
    ///         else nullptr
    virtual PyObject *tp_call(PyObject *self, PyObject *args, PyObject * /* kw */) = 0;

    /// Virtual function which is passed the decorator parameters
    /// \param args Decorator arguments
    /// \return 0 if the parameters are correct
    virtual int tp_init(PyObject *self, PyObject *args, PyObject *kwds) = 0;
    virtual const char *name() const = 0;

    /// Helper that returns DecoratorPrivate instance from a PyObject
    template <class DerivedPrivate>
    static DerivedPrivate *get(PyObject *o)
    { return static_cast<DerivedPrivate *>(DecoratorPrivate::getPrivate(o)); }

protected:
    /// Check mode for the arguments of the call operator
    enum class CheckMode { None, WrappedType, QObjectType };

    DecoratorPrivate() noexcept;
    static DecoratorPrivate *getPrivate(PyObject *o);

    /// Helper for checking the arguments of the call operator
    /// \param args Arguments
    /// \param checkMode Type check mode
    /// \return The type object extracted from args tuple (borrowed reference)
    ///         if the argument is a matching type
    PyObject *tp_call_check(PyObject *args,
                            CheckMode checkMode = CheckMode::QObjectType) const;
};

/// Base class for private objects of class decorator with a string parameter
class PYSIDE_API StringDecoratorPrivate : public DecoratorPrivate
{
public:
    /// Init function that retrieves the string parameter using convertToString()
    int tp_init(PyObject *self, PyObject *args, PyObject *kwds) override;

    QByteArray string() const { return m_string; }

protected:
    /// Helper function that retrieves the string parameter
    /// \param self self
    /// \param args Arguments
    /// \return 0 if the parameter is correct, else -1 (for tp_init())
    static int convertToString(PyObject *self, PyObject *args);

private:
    QByteArray m_string;
};

/// Base class for private objects of class decorator with a type parameter
class PYSIDE_API TypeDecoratorPrivate : public DecoratorPrivate
{
public:
    /// Init function that retrieves the type parameter using convertToType()
    int tp_init(PyObject *self, PyObject *args, PyObject *kwds) override;

    PyTypeObject *type() const { return m_type; }

protected:
    /// Helper function that retrieves the type parameter
    /// \param self self
    /// \param args Arguments
    /// \return 0 if the parameter is correct, else -1 (for tp_init())
    static int convertToType(PyObject *self, PyObject *args);

private:
    PyTypeObject *m_type = nullptr;
};

} // namespace PySide::ClassDecorator

extern "C"
{
LIBSHIBOKEN_API void Sbk_object_dealloc(PyObject *self);

/// Python type for class decorators with DecoratorPrivate
struct PYSIDE_API PySideClassDecorator
{
    PyObject_HEAD
    PySide::ClassDecorator::DecoratorPrivate *d;
};
};

namespace PySide::ClassDecorator {

/// Helper template providing the methods (slots) for class decorators
template <class DecoratorPrivate>
struct Methods
{
    static PyObject *tp_new(PyTypeObject *subtype)
    {
        auto *result = PepExt_TypeCallAlloc<PySideClassDecorator>(subtype, 0);
        result->d = new DecoratorPrivate;
        return reinterpret_cast<PyObject *>(result);
    }

    static void tp_free(void *self)
    {
        auto *pySelf = reinterpret_cast<PyObject *>(self);
        auto *decorator = reinterpret_cast<PySideClassDecorator *>(self);
        delete decorator->d;
        PepExt_TypeCallFree(Py_TYPE(pySelf)->tp_base, self);
    }

    static PyObject *tp_call(PyObject *self, PyObject *args, PyObject *kwds)
    {
        auto *decorator = reinterpret_cast<PySideClassDecorator *>(self);
        return decorator->d->tp_call(self, args, kwds);
    }

    static int tp_init(PyObject *self, PyObject *args, PyObject *kwds)
    {
        auto *decorator = reinterpret_cast<PySideClassDecorator *>(self);
        return decorator->d->tp_init(self, args, kwds);
    }

    using TypeSlots = std::array<PyType_Slot, 6>;

    static TypeSlots typeSlots()
    {
        return { {{Py_tp_call, reinterpret_cast<void *>(tp_call)},
                  {Py_tp_init, reinterpret_cast<void *>(tp_init)},
                  {Py_tp_new, reinterpret_cast<void *>(tp_new)},
                  {Py_tp_free, reinterpret_cast<void *>(tp_free)},
                  {Py_tp_dealloc, reinterpret_cast<void *>(Sbk_object_dealloc)},
                  {0, nullptr}}
               };
    }
};

} // namespace PySide::ClassDecorator

#endif // CLASSDECORATOR_P_H
