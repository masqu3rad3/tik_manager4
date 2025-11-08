// Copyright (C) 2018 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

/*********************************************************************
 * INJECT CODE
 ********************************************************************/

// @snippet include-pyside
#include <pysideinit.h>
#include <limits>
#include "glue/core_snippets_p.h"
// @snippet include-pyside

// @snippet core-snippets-p-h
#include "glue/core_snippets_p.h"
// @snippet core-snippets-p-h

// @snippet qarg_helper

// Helper for the Q_ARG/Q_RETURN_ARG functions, creating a meta type
// and instance.
struct QArgData
{
    operator bool() const { return metaType.isValid() && data != nullptr; }

    QMetaType metaType;
    void *data = nullptr;
};

QArgData qArgDataFromPyType(PyObject *t)
{
    QArgData result;
    const char *typeName{};
    if (PyType_Check(t)) {
        auto *pyType = reinterpret_cast<PyTypeObject *>(t);
        typeName = pyType->tp_name;
        result.metaType = PySide::qMetaTypeFromPyType(pyType);
    } else if (PyUnicode_Check(t)) {
        typeName = Shiboken::String::toCString(t);
        result.metaType = QMetaType::fromName(typeName);
    } else {
        PyErr_Format(PyExc_RuntimeError, "%s: Parameter should be a type or type string.",
                     __FUNCTION__);
        return result;
    }

    if (!result.metaType.isValid()) {
        PyErr_Format(PyExc_RuntimeError, "%s: Unable to find a QMetaType for \"%s\".",
                     __FUNCTION__, typeName);
        return result;
    }

    result.data = result.metaType.create();
    if (result.data == nullptr) {
        PyErr_Format(PyExc_RuntimeError, "%s: Unable to create an instance of \"%s\" (%s).",
                     __FUNCTION__, typeName, result.metaType.name());
        return result;
    }
    return result;
}
// @snippet qarg_helper

// @snippet settings-value-helpers
// Convert a QVariant to a desired primitive type
static PyObject *convertToPrimitiveType(const QVariant &out, int metaTypeId)
{
    switch (metaTypeId) {
    case QMetaType::QByteArray:
        return PyBytes_FromString(out.toByteArray().constData());
    case QMetaType::QString:
        return PyUnicode_FromString(out.toByteArray().constData());
    case QMetaType::Short:
    case QMetaType::Long:
    case QMetaType::LongLong:
    case QMetaType::UShort:
    case QMetaType::ULong:
    case QMetaType::ULongLong:
    case QMetaType::Int:
    case QMetaType::UInt:
        return PyLong_FromDouble(out.toFloat());
    case QMetaType::Double:
    case QMetaType::Float:
    case QMetaType::Float16:
        return PyFloat_FromDouble(out.toFloat());
    case QMetaType::Bool:
        if (out.toBool()) {
            Py_RETURN_TRUE;
        }
        Py_RETURN_FALSE;
    default:
        break;
    }
    return nullptr;
}

// Helper for QSettings::value() to convert a value to the desired type
static PyObject *settingsTypeCoercion(const QVariant &out, PyTypeObject *typeObj)
{
    if (typeObj == &PyList_Type) {
        // Convert any string, etc, to a list of 1 element
        if (auto *primitiveValue = convertToPrimitiveType(out, out.typeId())) {
            PyObject *list = PyList_New(1);
            PyList_SetItem(list, 0, primitiveValue);
            return list;
        }

        const QByteArray out_ba = out.toByteArray();
        if (out_ba.isEmpty())
            return PyList_New(0);

        const QByteArrayList valuesList = out_ba.split(',');
        const Py_ssize_t valuesSize = valuesList.size();
        PyObject *list = PyList_New(valuesSize);
        for (Py_ssize_t i = 0; i < valuesSize; ++i) {
            PyObject *item = PyUnicode_FromString(valuesList.at(i).constData());
            PyList_SetItem(list, i, item);
        }
        return list;
    }

    if (typeObj == &PyBytes_Type)
        return convertToPrimitiveType(out, QMetaType::QByteArray);
    if (typeObj == &PyUnicode_Type)
        return convertToPrimitiveType(out, QMetaType::QString);
    if (typeObj == &PyLong_Type)
        return convertToPrimitiveType(out, QMetaType::Int);
    if (typeObj == &PyFloat_Type)
        return convertToPrimitiveType(out, QMetaType::Double);
    if (typeObj == &PyBool_Type)
        return convertToPrimitiveType(out, QMetaType::Bool);

    // TODO: PyDict_Type and PyTuple_Type
    PyErr_SetString(PyExc_TypeError,
                    "Invalid type parameter.\n"
                    "\tUse 'list', 'bytes', 'str', 'int', 'float', 'bool', "
                    "or a Qt-derived type");
    return nullptr;
}

static bool isEquivalentSettingsType(PyTypeObject *typeObj, int metaTypeId)
{
    switch (metaTypeId) {
    case QMetaType::QVariantList:
    case QMetaType::QStringList:
        return typeObj == &PyList_Type;
    case QMetaType::QByteArray:
        return typeObj == &PyBytes_Type;
    case QMetaType::QString:
        return typeObj == &PyUnicode_Type;
    case QMetaType::Short:
    case QMetaType::Long:
    case QMetaType::LongLong:
    case QMetaType::UShort:
    case QMetaType::ULong:
    case QMetaType::ULongLong:
    case QMetaType::Int:
    case QMetaType::UInt:
        return typeObj == &PyLong_Type;
    case QMetaType::Double:
    case QMetaType::Float:
    case QMetaType::Float16:
        return typeObj == &PyFloat_Type;
    case QMetaType::Bool:
        return typeObj == &PyBool_Type;
    default:
        break;
    }
    return false;
}
// @snippet settings-value-helpers

// @snippet qsettings-value
// If we enter the kwds, means that we have a defaultValue or
// at least a type.
// This avoids that we are passing '0' as defaultValue.
// defaultValue can also be passed as positional argument,
// not only as keyword.
// PySide-535: Allow for empty dict instead of nullptr in PyPy
QVariant out;
if ((kwds && PyDict_Size(kwds) > 0) || numArgs > 1) {
    Py_BEGIN_ALLOW_THREADS
    out = %CPPSELF.value(%1, %2);
    Py_END_ALLOW_THREADS
} else {
    Py_BEGIN_ALLOW_THREADS
    out = %CPPSELF.value(%1);
    Py_END_ALLOW_THREADS
}

PyTypeObject *typeObj = reinterpret_cast<PyTypeObject*>(%PYARG_3);

if (typeObj && !Shiboken::ObjectType::checkType(typeObj)
    && !isEquivalentSettingsType(typeObj, out.typeId())) {
    %PYARG_0 = settingsTypeCoercion(out, typeObj);
} else {
    if (out.isValid()) {
        %PYARG_0 = %CONVERTTOPYTHON[QVariant](out);
    } else {
        Py_INCREF(Py_None);
        %PYARG_0 = Py_None;
    }
}

// @snippet qsettings-value

// @snippet metatype-from-type
%0 = new %TYPE(PySide::qMetaTypeFromPyType(reinterpret_cast<PyTypeObject *>(%1)));
// @snippet metatype-from-type

// @snippet metatype-from-metatype-type
Shiboken::AutoDecRef intArg(PyObject_GetAttrString(%PYARG_1, "value"));
%0 = new %TYPE(PyLong_AsLong(intArg));
// @snippet metatype-from-metatype-type

// @snippet conversion-pytypeobject-qmetatype
auto *pyType = reinterpret_cast<PyTypeObject *>(%in);
%out = PySide::qMetaTypeFromPyType(pyType);
// @snippet conversion-pytypeobject-qmetatype

// @snippet conversion-qmetatype-pytypeobject
auto pyType = Shiboken::Conversions::getPythonTypeObject(%in.name());
%out = pyType ? (reinterpret_cast<PyObject *>(pyType)) : Py_None;
Py_INCREF(%out);
return %out;
// @snippet conversion-qmetatype-pytypeobject

// @snippet qvariant-conversion
static QVariant QVariant_convertToVariantMap(PyObject *map)
{
    Py_ssize_t pos = 0;
    Shiboken::AutoDecRef keys(PyDict_Keys(map));
    if (!QVariant_isStringList(keys))
        return {};
    PyObject *key{};
    PyObject *value{};
    QMap<QString,QVariant> ret;
    while (PyDict_Next(map, &pos, &key, &value)) {
        QString cppKey = %CONVERTTOCPP[QString](key);
        QVariant cppValue = %CONVERTTOCPP[QVariant](value);
        ret.insert(cppKey, cppValue);
    }
    return QVariant(ret);
}
static QVariant QVariant_convertToVariantList(PyObject *list)
{
    if (QVariant_isStringList(list)) {
        QList<QString > lst = %CONVERTTOCPP[QList<QString>](list);
        return QVariant(QStringList(lst));
    }
    QVariant valueList = QVariant_convertToValueList(list);
    if (valueList.isValid())
        return valueList;

    if (PySequence_Size(list) < 0) {
        // clear the error if < 0 which means no length at all
        PyErr_Clear();
        return {};
    }

    QList<QVariant> lst;
    Shiboken::AutoDecRef fast(PySequence_Fast(list, "Failed to convert QVariantList"));
    const Py_ssize_t size = PySequence_Size(fast.object());
    for (Py_ssize_t i = 0; i < size; ++i) {
        Shiboken::AutoDecRef pyItem(PySequence_GetItem(fast.object(), i));
        QVariant item = %CONVERTTOCPP[QVariant](pyItem);
        lst.append(item);
    }
    return QVariant(lst);
}

using SpecificConverter = Shiboken::Conversions::SpecificConverter;

static std::optional<SpecificConverter> converterForQtType(const char *typeNameC)
{
    // Fix typedef "QGenericMatrix<3,3,float>" -> QMatrix3x3". The reverse
    // conversion happens automatically in QMetaType::fromName() in
    // QVariant_resolveMetaType().
    QByteArrayView typeNameV(typeNameC);
    if (typeNameV.startsWith("QGenericMatrix<") && typeNameV.endsWith(",float>")) {
        QByteArray typeName = typeNameV.toByteArray();
        typeName.remove(1, 7);
        typeName.remove(7, 1); // '<'
        typeName.chop(7);
        typeName.replace(',', 'x');
        SpecificConverter matrixConverter(typeName.constData());
        if (matrixConverter)
            return matrixConverter;
    }
    SpecificConverter converter(typeNameC);
    if (converter)
        return converter;
    return std::nullopt;
}
// @snippet qvariant-conversion

// @snippet qt-qabs
double _abs = qAbs(%1);
%PYARG_0 = %CONVERTTOPYTHON[double](_abs);
// @snippet qt-qabs

// @snippet qt-addpostroutine
PySide::addPostRoutine(%1);
// @snippet qt-addpostroutine

// @snippet qt-qaddpostroutine
qAddPostRoutine(PySide::globalPostRoutineCallback);
// @snippet qt-qaddpostroutine

// @snippet qcompress-buffer
auto *ptr = reinterpret_cast<uchar*>(Shiboken::Buffer::getPointer(%PYARG_1));
QByteArray compressed = %FUNCTION_NAME(ptr, %2, %3);
%PYARG_0 = %CONVERTTOPYTHON[QByteArray](compressed);
// @snippet qcompress-buffer

// @snippet quncompress-buffer
auto *ptr = reinterpret_cast<uchar*>(Shiboken::Buffer::getPointer(%PYARG_1));
QByteArray uncompressed = %FUNCTION_NAME(ptr, %2);
%PYARG_0 = %CONVERTTOPYTHON[QByteArray](uncompressed);
// @snippet quncompress-buffer

// @snippet qt-version
QList<QByteArray> version = QByteArray(qVersion()).split('.');
PyObject *pyQtVersion = PyTuple_New(3);
for (int i = 0; i < 3; ++i)
    PyTuple_SetItem(pyQtVersion, i, PyLong_FromLong(version[i].toInt()));
PyModule_AddObject(module, "__version_info__", pyQtVersion);
PyModule_AddStringConstant(module, "__version__", qVersion());
// @snippet qt-version

// @snippet qobject-connect
#include <qobjectconnect.h>
// @snippet qobject-connect

// @snippet qobject-connect-1
// %FUNCTION_NAME() - disable generation of function call.
%RETURN_TYPE %0 = PySide::qobjectConnect(%1, %2, %CPPSELF, %3, %4);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qobject-connect-1

// @snippet qobject-connect-2
// %FUNCTION_NAME() - disable generation of function call.
%RETURN_TYPE %0 = PySide::qobjectConnect(%1, %2, %3, %4, %5);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qobject-connect-2

// @snippet qobject-connect-3
// %FUNCTION_NAME() - disable generation of function call.
%RETURN_TYPE %0 = PySide::qobjectConnect(%1, %2, %3, %4, %5);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qobject-connect-3

// @snippet qobject-connect-4
// %FUNCTION_NAME() - disable generation of function call.
%RETURN_TYPE %0 = PySide::qobjectConnectCallback(%1, %2, %PYARG_3, %4);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qobject-connect-4

// @snippet qobject-connect-4-context
// %FUNCTION_NAME() - disable generation of function call.
%RETURN_TYPE %0 = PySide::qobjectConnectCallback(%1, %2, %3, %PYARG_4, %5);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qobject-connect-4-context

// @snippet qobject-connect-5
// %FUNCTION_NAME() - disable generation of function call.
%RETURN_TYPE %0 = PySide::qobjectConnectCallback(%CPPSELF, %1, %PYARG_2, %3);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qobject-connect-5

// @snippet qobject-connect-6
// %FUNCTION_NAME() - disable generation of function call.
%RETURN_TYPE %0 = PySide::qobjectConnect(%CPPSELF, %1, %2, %3, %4);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qobject-connect-6

// @snippet qobject-emit
%RETURN_TYPE %0 = PySide::SignalManager::emitSignal(%CPPSELF, %1, %PYARG_2);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qobject-emit

// @snippet qobject-disconnect-1
// %FUNCTION_NAME() - disable generation of function call.
%RETURN_TYPE %0 = PySide::qobjectDisconnectCallback(%CPPSELF, %1, %2);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qobject-disconnect-1

// @snippet qobject-disconnect-2
// %FUNCTION_NAME() - disable generation of function call.
%RETURN_TYPE %0 = PySide::qobjectDisconnectCallback(%1, %2, %3);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qobject-disconnect-2

// @snippet qfatal
// qFatal doesn't have a stream version, so we do a
// qWarning call followed by a qFatal() call using a
// literal.
Py_BEGIN_ALLOW_THREADS
qWarning() << %1;
qFatal("[A qFatal() call was made from Python code]");
Py_END_ALLOW_THREADS
// @snippet qfatal

// @snippet moduleshutdown
PySide::runCleanupFunctions();
// @snippet moduleshutdown

// @snippet qt-qenum
%PYARG_0 = PySide::QEnum::QEnumMacro(%1, false);
// @snippet qt-qenum

// @snippet qt-qflag
%PYARG_0 = PySide::QEnum::QEnumMacro(%1, true);
// @snippet qt-qflag

// @snippet qt-init-feature
PySide::Feature::init();
// @snippet qt-init-feature

// @snippet qt-pysideinit
Shiboken::Conversions::registerConverterName(SbkPySide6_QtCoreTypeConverters[SBK_QString_IDX], "unicode");
Shiboken::Conversions::registerConverterName(SbkPySide6_QtCoreTypeConverters[SBK_QString_IDX], "str");
Shiboken::Conversions::registerConverterName(SbkPySide6_QtCoreTypeConverters[SBK_QtCore_QList_QVariant_IDX], "QVariantList");
Shiboken::Conversions::registerConverterName(SbkPySide6_QtCoreTypeConverters[SBK_QtCore_QMap_QString_QVariant_IDX], "QVariantMap");

PySide::registerInternalQtConf();
PySide::init(module);
// @snippet qt-pysideinit

// @snippet qt-messagehandler
// Define a global variable to handle qInstallMessageHandler callback
static PyObject *qtmsghandler = nullptr;

static void msgHandlerCallback(QtMsgType type, const QMessageLogContext &ctx, const QString &msg)
{
    Shiboken::GilState state;
    PyObject *excType{};
    PyObject *excValue{};
    PyObject *excTraceback{};
    PyErr_Fetch(&excType, &excValue, &excTraceback);
    Shiboken::AutoDecRef arglist(PyTuple_New(3));
    PyTuple_SetItem(arglist, 0, %CONVERTTOPYTHON[QtMsgType](type));
    PyTuple_SetItem(arglist, 1, %CONVERTTOPYTHON[QMessageLogContext &](ctx));
    QByteArray array = msg.toUtf8();  // Python handler requires UTF-8
    const char *data = array.constData();
    PyTuple_SetItem(arglist, 2, %CONVERTTOPYTHON[const char *](data));
    Shiboken::AutoDecRef ret(PyObject_CallObject(qtmsghandler, arglist));
    PyErr_Restore(excType, excValue, excTraceback);
}
// @snippet qt-messagehandler

// @snippet qt-installmessagehandler
if (%PYARG_1 == Py_None) {
  qInstallMessageHandler(0);
  %PYARG_0 = qtmsghandler ? qtmsghandler : Py_None;
  qtmsghandler = 0;
} else if (!PyCallable_Check(%PYARG_1)) {
  PyErr_SetString(PyExc_TypeError, "parameter must be callable");
} else {
  %PYARG_0 = qtmsghandler ? qtmsghandler : Py_None;
  Py_INCREF(%PYARG_1);
  qtmsghandler = %PYARG_1;
  qInstallMessageHandler(msgHandlerCallback);
}

if (%PYARG_0 == Py_None)
    Py_INCREF(%PYARG_0);
// @snippet qt-installmessagehandler

// @snippet qline-hash
namespace PySide {
    template<> inline Py_ssize_t hash(const QLine &l)
    {
        return qHashMulti(0, l.x1(), l.y1(), l.x2(), l.y2());
    }
};
// @snippet qline-hash

// @snippet qlinef-intersect
QPointF p;
%RETURN_TYPE retval = %CPPSELF.%FUNCTION_NAME(%ARGUMENT_NAMES, &p);
%PYARG_0 = PyTuple_New(2);
PyTuple_SetItem(%PYARG_0, 0, %CONVERTTOPYTHON[%RETURN_TYPE](retval));
PyTuple_SetItem(%PYARG_0, 1, %CONVERTTOPYTHON[QPointF](p));
// @snippet qlinef-intersect

// @snippet qresource-data
const void *d = %CPPSELF.%FUNCTION_NAME();
if (d) {
    %PYARG_0 = Shiboken::Buffer::newObject(d, %CPPSELF.size());
} else {
    Py_INCREF(Py_None);
    %PYARG_0 = Py_None;
}
// @snippet qresource-data

// @snippet qdate-topython
if (!PyDateTimeAPI)
    PyDateTime_IMPORT;
%PYARG_0 = PyDate_FromDate(%CPPSELF.year(), %CPPSELF.month(), %CPPSELF.day());
// @snippet qdate-topython

// @snippet qdate-getdate
int year, month, day;
%CPPSELF.%FUNCTION_NAME(&year, &month, &day);
%PYARG_0 = PyTuple_New(3);
PyTuple_SetItem(%PYARG_0, 0, %CONVERTTOPYTHON[int](year));
PyTuple_SetItem(%PYARG_0, 1, %CONVERTTOPYTHON[int](month));
PyTuple_SetItem(%PYARG_0, 2, %CONVERTTOPYTHON[int](day));
// @snippet qdate-getdate

// @snippet qdate-weeknumber
int yearNumber;
int week = %CPPSELF.%FUNCTION_NAME(&yearNumber);
%PYARG_0 = PyTuple_New(2);
PyTuple_SetItem(%PYARG_0, 0, %CONVERTTOPYTHON[int](week));
PyTuple_SetItem(%PYARG_0, 1, %CONVERTTOPYTHON[int](yearNumber));
// @snippet qdate-weeknumber

// @snippet qdatetime-1
QDate date(%1, %2, %3);
QTime time(%4, %5, %6, %7);
%0 = new %TYPE(date, time,
               Qt::TimeSpec(%8) == Qt::UTC
               ? QTimeZone(QTimeZone::UTC) : QTimeZone(QTimeZone::LocalTime));
Shiboken::Warnings::warnDeprecated("QDateTime", "QDateTime(..., Qt::TimeSpec spec)");
// @snippet qdatetime-1

// @snippet qdatetime-2
QDate date(%1, %2, %3);
QTime time(%4, %5, %6);
%0 = new %TYPE(date, time);
// @snippet qdatetime-2

// @snippet qdatetime-3
QDate date(%1, %2, %3);
QTime time(%4, %5, %6, %7);
%0 = new %TYPE(date, time,
               %8 == Qt::UTC ? QTimeZone(QTimeZone::UTC) : QTimeZone(QTimeZone::LocalTime));
Shiboken::Warnings::warnDeprecated("QDateTime", "QDateTime(..., Qt::TimeSpec spec)");
// @snippet qdatetime-3

// @snippet qdatetime-topython
QDate date = %CPPSELF.date();
QTime time = %CPPSELF.time();
if (!PyDateTimeAPI)
    PyDateTime_IMPORT;
%PYARG_0 = PyDateTime_FromDateAndTime(date.year(), date.month(), date.day(), time.hour(), time.minute(), time.second(), time.msec()*1000);
// @snippet qdatetime-topython

// @snippet qtime-topython
if (!PyDateTimeAPI)
    PyDateTime_IMPORT;
%PYARG_0 = PyTime_FromTime(%CPPSELF.hour(), %CPPSELF.minute(), %CPPSELF.second(), %CPPSELF.msec()*1000);
// @snippet qtime-topython

// @snippet qbitarray-len
return %CPPSELF.size();
// @snippet qbitarray-len

// @snippet qbitarray-getitem
const Py_ssize_t size = %CPPSELF.size();
if (_i < 0 || _i >= size) {
    Shiboken::Errors::setIndexOutOfBounds(_i, 0, size);
    return nullptr;
}
bool ret = %CPPSELF.at(_i);
return %CONVERTTOPYTHON[bool](ret);
// @snippet qbitarray-getitem

// @snippet qbitarray-setitem
PyObject *args = Py_BuildValue("(iiO)", _i, 1, _value);
PyObject *result = Sbk_QBitArrayFunc_setBit(self, args);
Py_DECREF(args);
Py_XDECREF(result);
return !result ? -1 : 0;
// @snippet qbitarray-setitem

// @snippet qmodelroledata-setdata
// Call template <typename T> void QModelRoleData::setData(T &&value)
%CPPSELF.%FUNCTION_NAME(%1);
// @snippet qmodelroledata-setdata

// @snippet qmodelroledataspan-len
return %CPPSELF.size();
// @snippet qmodelroledataspan-len

// @snippet qmodelroledataspan-getitem
const Py_ssize_t size = %CPPSELF.size();
if (_i < 0 || _i >= size) {
    Shiboken::Errors::setIndexOutOfBounds(_i, 0, size);
    return nullptr;
}
// Return a pointer to allow for modification using  QModelRoleData::setData()
QModelRoleData *item = &((*%CPPSELF)[_i]);
return %CONVERTTOPYTHON[QModelRoleData *](item);
// @snippet qmodelroledataspan-getitem

// @snippet default-enter
Py_INCREF(%PYSELF);
pyResult = %PYSELF;
// @snippet default-enter

// @snippet qsignalblocker-unblock
%CPPSELF.unblock();
// @snippet qsignalblocker-unblock

// @snippet unlock
%CPPSELF.unlock();
// @snippet unlock

// @snippet qabstractitemmodel-createindex
%RETURN_TYPE %0 = %CPPSELF.%FUNCTION_NAME(%1, %2, %PYARG_3);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qabstractitemmodel-createindex

// @snippet qabstractitemmodel
qRegisterMetaType<QList<int> >("QList<int>");
// @snippet qabstractitemmodel

// @snippet qobject-metaobject
%RETURN_TYPE %0 = %CPPSELF.%FUNCTION_NAME();
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qobject-metaobject

// @snippet qobject-findchild-2
QObject *child = qObjectFindChild(%CPPSELF, %2, reinterpret_cast<PyTypeObject *>(%PYARG_1), %3);
%PYARG_0 = %CONVERTTOPYTHON[QObject *](child);
// @snippet qobject-findchild-2

// @snippet qobject-findchildren
%PYARG_0 = PyList_New(0);
qObjectFindChildren(%CPPSELF, %2, reinterpret_cast<PyTypeObject *>(%PYARG_1), %3,
                    [%PYARG_0](QObject *child) {
                        Shiboken::AutoDecRef pyChild(%CONVERTTOPYTHON[QObject *](child));
                        PyList_Append(%PYARG_0, pyChild.object());
                    });
// @snippet qobject-findchildren

// @snippet qobject-tr
const QString result = qObjectTr(reinterpret_cast<PyTypeObject *>(%PYSELF), %1, %2, %3);
%PYARG_0 = %CONVERTTOPYTHON[QString](result);
// @snippet qobject-tr

// @snippet qobject-sender
// Retrieve the sender from a dynamic property set by GlobalReceiverV2 in case of a
// non-C++ slot (Python callback).
auto *ret = %CPPSELF.%FUNCTION_NAME();
if (ret == nullptr) {
    auto senderV = %CPPSELF.property("_q_pyside_sender");
    if (senderV.typeId() == QMetaType::QObjectStar)
        ret = senderV.value<QObject *>();
}
%PYARG_0 = %CONVERTTOPYTHON[QObject*](ret);
// @snippet qobject-sender

// @snippet qbytearray-mgetitem
if (PyIndex_Check(_key)) {
    const Py_ssize_t _i = PyNumber_AsSsize_t(_key, PyExc_IndexError);
    const Py_ssize_t size = %CPPSELF.size();
    if (_i < 0 || _i >= size) {
        Shiboken::Errors::setIndexOutOfBounds(_i, 0, size);
        return nullptr;
    }
    char res[2] = {%CPPSELF.at(_i), '\0'};
    return PyBytes_FromStringAndSize(res, 1);
}

if (PySlice_Check(_key) == 0)
    return PyErr_Format(PyExc_TypeError,
                 "list indices must be integers or slices, not %.200s",
                 Py_TYPE(_key)->tp_name);

Py_ssize_t start, stop, step, slicelength;
if (PySlice_GetIndicesEx(_key, %CPPSELF.size(), &start, &stop, &step, &slicelength) < 0)
    return nullptr;

QByteArray ba;
if (slicelength <= 0)
    return %CONVERTTOPYTHON[QByteArray](ba);

if (step == 1) {
    Py_ssize_t max = %CPPSELF.size();
    start = qBound(Py_ssize_t(0), start, max);
    stop = qBound(Py_ssize_t(0), stop, max);
    if (start < stop)
        ba = %CPPSELF.mid(start, stop - start);
    return %CONVERTTOPYTHON[QByteArray](ba);
}

for (Py_ssize_t cur = start; slicelength > 0; cur += step, --slicelength)
    ba.append(%CPPSELF.at(cur));

return %CONVERTTOPYTHON[QByteArray](ba);
// @snippet qbytearray-mgetitem

// @snippet qbytearray-msetitem
// PYSIDE-2404: Usage of the `get()` function not necessary, the type exists.
if (PyIndex_Check(_key)) {
    Py_ssize_t _i = PyNumber_AsSsize_t(_key, PyExc_IndexError);
    if (_i == -1 && PyErr_Occurred())
        return -1;

    if (_i < 0)
        _i += %CPPSELF.size();

    if (_i < 0 || _i >= %CPPSELF.size()) {
        PyErr_SetString(PyExc_IndexError, "QByteArray index out of range");
        return -1;
    }

    // Provide more specific error message for bytes/str, bytearray, QByteArray respectively
    if (PyBytes_Check(_value)) {
        if (Py_SIZE(_value) != 1) {
            PyErr_SetString(PyExc_ValueError, "bytes must be of size 1");
            return -1;
        }
    } else if (PyByteArray_Check(_value)) {
        if (Py_SIZE(_value) != 1) {
            PyErr_SetString(PyExc_ValueError, "bytearray must be of size 1");
            return -1;
        }
    } else if (Py_TYPE(_value) == reinterpret_cast<PyTypeObject *>(
            SbkPySide6_QtCoreTypeStructs[SBK_QByteArray_IDX].type)) {
        if (PyObject_Length(_value) != 1) {
            PyErr_SetString(PyExc_ValueError, "QByteArray must be of size 1");
            return -1;
        }
    } else {
        PyErr_SetString(PyExc_ValueError, "a bytes, bytearray, QByteArray of size 1 is required");
        return -1;
    }

    // Not support int or long.
    %CPPSELF.remove(_i, 1);
    PyObject *args = Py_BuildValue("(nO)", _i, _value);
    PyObject *result = Sbk_QByteArrayFunc_insert(self, args);
    Py_DECREF(args);
    Py_XDECREF(result);
    return result != nullptr ? 0: -1;
}

if (PySlice_Check(_key) == 0) {
    PyErr_Format(PyExc_TypeError, "QBytearray indices must be integers or slices, not %.200s",
                 Py_TYPE(_key)->tp_name);
    return -1;
}

Py_ssize_t start, stop, step, slicelength;
if (PySlice_GetIndicesEx(_key, %CPPSELF.size(), &start, &stop, &step, &slicelength) < 0)
    return -1;

// The parameter candidates are: bytes/str, bytearray, QByteArray itself.
// Not supported are iterables containing ints between 0~255
// case 1: value is nullpre, means delete the items within the range
// case 2: step is 1, means shrink or expand
// case 3: step is not 1, then the number of slots have to equal the number of items in _value
Py_ssize_t value_length = 0;
if (_value != nullptr && _value != Py_None) {
    if (!(PyBytes_Check(_value) || PyByteArray_Check(_value)
          || Py_TYPE(_value) == SbkPySide6_QtCoreTypeStructs[SBK_QByteArray_IDX].type)) {
           PyErr_Format(PyExc_TypeError, "bytes, bytearray or QByteArray is required, not %.200s",
                        Py_TYPE(_value)->tp_name);
           return -1;
    }
    value_length = PyObject_Length(_value);
}

if (step != 1 && value_length != slicelength) {
    PyErr_Format(PyExc_ValueError, "attempt to assign %s of size %d to extended slice of size %d",
                 Py_TYPE(_value)->tp_name, int(value_length), int(slicelength));
    return -1;
}

if (step != 1) {
    Py_ssize_t i = start;
    for (Py_ssize_t j = 0; j < slicelength; ++j) {
        PyObject *item = PyObject_GetItem(_value, PyLong_FromSsize_t(j));
        QByteArray temp;
        if (PyLong_Check(item)) {
            int overflow;
            const long ival = PyLong_AsLongAndOverflow(item, &overflow);
            // Not supposed to be bigger than 255 because only bytes,
            // bytearray, QByteArray were accepted
            temp.append(char(ival));
        } else {
            temp = %CONVERTTOCPP[QByteArray](item);
        }
        %CPPSELF.replace(i, 1, temp);
        i += step;
    }
    return 0;
}

QByteArray ba = %CONVERTTOCPP[QByteArray](_value);
%CPPSELF.replace(start, slicelength, ba);
return 0;
// @snippet qbytearray-msetitem

// @snippet qbytearray-bufferprotocol
extern "C" {
// QByteArray buffer protocol functions
// see: http://www.python.org/dev/peps/pep-3118/

static int SbkQByteArray_getbufferproc(PyObject *obj, Py_buffer *view, int flags)
{
    if (!view || !Shiboken::Object::isValid(obj))
        return -1;

    QByteArray * cppSelf = %CONVERTTOCPP[QByteArray *](obj);
    //XXX      /|\ omitting this space crashes shiboken!
#ifdef Py_LIMITED_API
    view->obj = obj;
    view->buf = reinterpret_cast<void *>(cppSelf->data());
    view->len = cppSelf->size();
    view->readonly = 0;
    view->itemsize = 1;
    view->format = (flags & PyBUF_FORMAT) == PyBUF_FORMAT ? const_cast<char *>("B") : nullptr;
    view->ndim = 1;
    view->shape = (flags & PyBUF_ND) == PyBUF_ND ? &(view->len) : nullptr;
    view->strides = (flags & PyBUF_STRIDES) == PyBUF_STRIDES ? &(view->itemsize) : nullptr;
    view->suboffsets = nullptr;
    view->internal = nullptr;

    Py_XINCREF(obj);
    return 0;
#else // Py_LIMITED_API
    const int result = PyBuffer_FillInfo(view, obj, reinterpret_cast<void *>(cppSelf->data()),
                                         cppSelf->size(), 0, flags);
    if (result == 0)
        Py_XINCREF(obj);
    return result;
#endif
}

static PyBufferProcs SbkQByteArrayBufferProc = {
    /*bf_getbuffer*/  (getbufferproc)SbkQByteArray_getbufferproc,
    /*bf_releasebuffer*/ (releasebufferproc)0,
};

}
// @snippet qbytearray-bufferprotocol

// @snippet qbytearray-operatorplus-1
QByteArray ba = QByteArray(PyBytes_AsString(%PYARG_1), PyBytes_Size(%PYARG_1)) + *%CPPSELF;
%PYARG_0 = %CONVERTTOPYTHON[QByteArray](ba);
// @snippet qbytearray-operatorplus-1

// @snippet qbytearray-operatorplus-2
QByteArray ba = QByteArray(PyByteArray_AsString(%PYARG_1), PyByteArray_Size(%PYARG_1)) + *%CPPSELF;
%PYARG_0 = %CONVERTTOPYTHON[QByteArray](ba);
// @snippet qbytearray-operatorplus-2

// @snippet qbytearray-operatorplus-3
QByteArray ba = *%CPPSELF + QByteArray(PyByteArray_AsString(%PYARG_1), PyByteArray_Size(%PYARG_1));
%PYARG_0 = %CONVERTTOPYTHON[QByteArray](ba);
// @snippet qbytearray-operatorplus-3

// @snippet qbytearray-operatorplusequal
*%CPPSELF += QByteArray(PyByteArray_AsString(%PYARG_1), PyByteArray_Size(%PYARG_1));
// @snippet qbytearray-operatorplusequal

// @snippet qbytearray-operatorequalequal
if (PyUnicode_CheckExact(%PYARG_1)) {
    Shiboken::AutoDecRef data(PyUnicode_AsASCIIString(%PYARG_1));
    QByteArray ba = QByteArray(PyBytes_AsString(data.object()), PyBytes_Size(data.object()));
    bool cppResult = %CPPSELF == ba;
    %PYARG_0 = %CONVERTTOPYTHON[bool](cppResult);
}
// @snippet qbytearray-operatorequalequal

// @snippet qbytearray-operatornotequal
if (PyUnicode_CheckExact(%PYARG_1)) {
    Shiboken::AutoDecRef data(PyUnicode_AsASCIIString(%PYARG_1));
    QByteArray ba = QByteArray(PyBytes_AsString(data.object()), PyBytes_Size(data.object()));
    bool cppResult = %CPPSELF != ba;
    %PYARG_0 = %CONVERTTOPYTHON[bool](cppResult);
}
// @snippet qbytearray-operatornotequal

// @snippet qbytearray-operatorgreater
if (PyUnicode_CheckExact(%PYARG_1)) {
    Shiboken::AutoDecRef data(PyUnicode_AsASCIIString(%PYARG_1));
    QByteArray ba = QByteArray(PyBytes_AsString(data.object()), PyBytes_Size(data.object()));
    bool cppResult = %CPPSELF > ba;
    %PYARG_0 = %CONVERTTOPYTHON[bool](cppResult);
}
// @snippet qbytearray-operatorgreater

// @snippet qbytearray-operatorgreaterequal
if (PyUnicode_CheckExact(%PYARG_1)) {
    Shiboken::AutoDecRef data(PyUnicode_AsASCIIString(%PYARG_1));
    QByteArray ba = QByteArray(PyBytes_AsString(data.object()), PyBytes_Size(data.object()));
    bool cppResult = %CPPSELF >= ba;
    %PYARG_0 = %CONVERTTOPYTHON[bool](cppResult);
}
// @snippet qbytearray-operatorgreaterequal

// @snippet qbytearray-operatorlower
if (PyUnicode_CheckExact(%PYARG_1)) {
    Shiboken::AutoDecRef data(PyUnicode_AsASCIIString(%PYARG_1));
    QByteArray ba = QByteArray(PyBytes_AsString(data.object()), PyBytes_Size(data.object()));
    bool cppResult = %CPPSELF < ba;
    %PYARG_0 = %CONVERTTOPYTHON[bool](cppResult);
}
// @snippet qbytearray-operatorlower

// @snippet qbytearray-operatorlowerequal
if (PyUnicode_CheckExact(%PYARG_1)) {
    Shiboken::AutoDecRef data(PyUnicode_AsASCIIString(%PYARG_1));
    QByteArray ba = QByteArray(PyBytes_AsString(data.object()), PyBytes_Size(data.object()));
    bool cppResult = %CPPSELF <= ba;
    %PYARG_0 = %CONVERTTOPYTHON[bool](cppResult);
}
// @snippet qbytearray-operatorlowerequal

// @snippet qbytearray-repr
PyObject *aux = PyBytes_FromStringAndSize(%CPPSELF.constData(), %CPPSELF.size());
if (aux == nullptr) {
    return nullptr;
}
QByteArray b(Py_TYPE(%PYSELF)->tp_name);
%PYARG_0 = PyUnicode_FromFormat("%s(%R)", b.constData(), aux);
Py_DECREF(aux);
// @snippet qbytearray-repr

// @snippet qbytearray-2
%0 = new QByteArray(PyByteArray_AsString(%PYARG_1), PyByteArray_Size(%PYARG_1));
// @snippet qbytearray-2

// @snippet qbytearray-3
%0 = new QByteArray(PyBytes_AsString(%PYARG_1), PyBytes_Size(%PYARG_1));
// @snippet qbytearray-3

// @snippet qbytearray-py3
PepType_AS_BUFFER(Shiboken::SbkType<QByteArray>()) = &SbkQByteArrayBufferProc;
// @snippet qbytearray-py3

// @snippet qbytearray-data
%PYARG_0 = PyBytes_FromStringAndSize(%CPPSELF.%FUNCTION_NAME(), %CPPSELF.size());
// @snippet qbytearray-data

// @snippet qbytearray-str
PyObject *aux = PyBytes_FromStringAndSize(%CPPSELF.constData(), %CPPSELF.size());
if (aux == nullptr) {
    return nullptr;
}
%PYARG_0 = PyObject_Repr(aux);
Py_DECREF(aux);
// @snippet qbytearray-str

// @snippet qbytearray-len
return %CPPSELF.size();
// @snippet qbytearray-len

// @snippet qbytearray-getitem
const Py_ssize_t size = %CPPSELF.size();
if (_i < 0 || _i >= size) {
    Shiboken::Errors::setIndexOutOfBounds(_i, 0, size);
    return nullptr;
}

char res[2];
res[0] = %CPPSELF.at(_i);
res[1] = 0;
return PyBytes_FromStringAndSize(res, 1);
// @snippet qbytearray-getitem

// @snippet qbytearray-setitem
%CPPSELF.remove(_i, 1);
PyObject *args = Py_BuildValue("(nO)", _i, _value);
PyObject *result = Sbk_QByteArrayFunc_insert(self, args);
Py_DECREF(args);
Py_XDECREF(result);
return !result ? -1 : 0;
// @snippet qbytearray-setitem

// @snippet qfiledevice-unmap
uchar *ptr = reinterpret_cast<uchar *>(Shiboken::Buffer::getPointer(%PYARG_1));
%RETURN_TYPE %0 = %CPPSELF.%FUNCTION_NAME(ptr);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qfiledevice-unmap

// @snippet qfiledevice-map
%PYARG_0 = Shiboken::Buffer::newObject(%CPPSELF.%FUNCTION_NAME(%1, %2, %3), %2, Shiboken::Buffer::ReadWrite);
// @snippet qfiledevice-map

// @snippet qiodevice-bufferedread
Py_ssize_t bufferLen;
auto *data = reinterpret_cast<char*>(Shiboken::Buffer::getPointer(%PYARG_1, &bufferLen));
%RETURN_TYPE %0 = %CPPSELF.%FUNCTION_NAME(data, PyLong_AsLongLong(%PYARG_2));
return PyLong_FromLong(%0);
// @snippet qiodevice-bufferedread

// @snippet qiodevice-readdata
QByteArray ba(1 + qsizetype(%2), char(0));
%CPPSELF.%FUNCTION_NAME(ba.data(), qint64(%2));
%PYARG_0 = Shiboken::String::fromCString(ba.constData());
// @snippet qiodevice-readdata

// @snippet qcryptographichash-adddata
%CPPSELF.%FUNCTION_NAME(Shiboken::String::toCString(%PYARG_1), Shiboken::String::len(%PYARG_1));
// @snippet qcryptographichash-adddata

// @snippet qmetaobject-repr
const QByteArray repr = PySide::MetaObjectBuilder::formatMetaObject(%CPPSELF).toUtf8();
%PYARG_0 = PyUnicode_FromString(repr.constData());
// @snippet qmetaobject-repr

// @snippet qsocketdescriptor
#ifdef WIN32
using DescriptorType = Qt::HANDLE;
#else
using DescriptorType = int;
#endif
// @snippet qsocketdescriptor

// @snippet qsocketnotifier
PyObject *socket = %PYARG_1;
if (socket != nullptr) {
    // We use qintptr as PyLong, but we check for int
    // since it is currently an alias to be Python2 compatible.
    // Internally, ints are qlonglongs.
    if (%CHECKTYPE[int](socket)) {
        int cppSocket = %CONVERTTOCPP[int](socket);
        qintptr socket = (qintptr)cppSocket;
        %0 = new %TYPE(socket, %2, %3);
    } else {
        PyErr_SetString(PyExc_TypeError,
            "QSocketNotifier: first argument (socket) must be an int.");
    }
}
// @snippet qsocketnotifier

// @snippet qtranslator-load
Py_ssize_t size;
auto *ptr = reinterpret_cast<uchar *>(Shiboken::Buffer::getPointer(%PYARG_1, &size));
%RETURN_TYPE %0 = %CPPSELF.%FUNCTION_NAME(const_cast<const uchar *>(ptr), size);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qtranslator-load

// @snippet qtimer-singleshot-functorclass
struct QSingleShotTimerFunctor : public Shiboken::PyObjectHolder
{
public:
    using Shiboken::PyObjectHolder::PyObjectHolder;

    void operator()();
};

void QSingleShotTimerFunctor::operator()()
{
    Shiboken::GilState state;
    Shiboken::AutoDecRef arglist(PyTuple_New(0));
    Shiboken::AutoDecRef ret(PyObject_CallObject(object(), arglist));
    if (Shiboken::Errors::occurred())
        Shiboken::Errors::storeErrorOrPrint();
    release(); // single shot
}
// @snippet qtimer-singleshot-functorclass

// @snippet qtimer-singleshot-direct-mapping
Shiboken::AutoDecRef emptyTuple(PyTuple_New(0));
%CPPSELF.%FUNCTION_NAME(%1, %2, %3);
// @snippet qtimer-singleshot-direct-mapping

// @snippet qtimer-singleshot-functor
auto msec = %1;
if (msec == 0) {
    if (PyObject_TypeCheck(%2, PySideSignalInstance_TypeF())) {
        auto *signal = %PYARG_2;
        auto cppCallback = [signal]()
        {
            Shiboken::GilState state;
            Shiboken::AutoDecRef ret(PyObject_CallMethod(signal, "emit", "()"));
            Py_DECREF(signal);
        };

        Py_INCREF(signal);
        %CPPSELF.%FUNCTION_NAME(msec, cppCallback);
    } else {
        %CPPSELF.%FUNCTION_NAME(msec, QSingleShotTimerFunctor(%PYARG_2));
    }
} else {
    // %FUNCTION_NAME() - disable generation of c++ function call
    Shiboken::AutoDecRef emptyTuple(PyTuple_New(0));
    auto *timerType = Shiboken::SbkType<QTimer>();
    auto newFunc = reinterpret_cast<newfunc>(PepType_GetSlot(timerType, Py_tp_new));
    auto initFunc = reinterpret_cast<initproc>(PepType_GetSlot(timerType, Py_tp_init));
    auto *pyTimer = newFunc(Shiboken::SbkType<QTimer>(), emptyTuple, nullptr);
    initFunc(pyTimer, emptyTuple, nullptr);

    QTimer * timer = %CONVERTTOCPP[QTimer *](pyTimer);
    timer->setSingleShot(true);
    if (!PySide::callConnect(pyTimer, SIGNAL(timeout()), %PYARG_2))
        return nullptr;

    timer->connect(timer, &QTimer::timeout, timer, &QObject::deleteLater, Qt::DirectConnection);
    Shiboken::Object::releaseOwnership(reinterpret_cast<SbkObject *>(pyTimer));
    Py_XDECREF(pyTimer);
    timer->start(msec);
}
// @snippet qtimer-singleshot-functor

// @snippet qtimer-singleshot-functor-context
auto msec = %1;
if (msec == 0) {
    Shiboken::AutoDecRef emptyTuple(PyTuple_New(0));
    auto *callable = %PYARG_3;
    auto cppCallback = [callable]()
    {
        Shiboken::GilState state;
        Shiboken::AutoDecRef arglist(PyTuple_New(0));
        Shiboken::AutoDecRef ret(PyObject_CallObject(callable, arglist));
        Py_DECREF(callable);
    };

    Py_INCREF(callable);
    %CPPSELF.%FUNCTION_NAME(msec, %2, cppCallback);
} else {
    Shiboken::AutoDecRef emptyTuple(PyTuple_New(0));
    auto *timerType = Shiboken::SbkType<QTimer>();
    auto newFunc = reinterpret_cast<newfunc>(PepType_GetSlot(timerType, Py_tp_new));
    auto initFunc = reinterpret_cast<initproc>(PepType_GetSlot(timerType, Py_tp_init));
    auto *pyTimer = newFunc(Shiboken::SbkType<QTimer>(), emptyTuple, nullptr);
    initFunc(pyTimer, emptyTuple, nullptr);

    QTimer * timer = %CONVERTTOCPP[QTimer *](pyTimer);
    timer->setSingleShot(true);

    Shiboken::AutoDecRef result(
        PyObject_CallMethod(pyTimer, "connect", "OsOO",
                            pyTimer,
                            SIGNAL(timeout()),
                            %PYARG_2,
                            %PYARG_3)
    );

    timer->connect(timer, &QTimer::timeout, timer, &QObject::deleteLater, Qt::DirectConnection);
    Shiboken::Object::releaseOwnership(reinterpret_cast<SbkObject *>(pyTimer));
    Py_XDECREF(pyTimer);
    timer->start(msec);
}
// @snippet qtimer-singleshot-functor-context

// @snippet qprocess-startdetached
qint64 pid;
%RETURN_TYPE retval = %TYPE::%FUNCTION_NAME(%1, %2, %3, &pid);
%PYARG_0 = PyTuple_New(2);
PyTuple_SetItem(%PYARG_0, 0, %CONVERTTOPYTHON[%RETURN_TYPE](retval));
PyTuple_SetItem(%PYARG_0, 1, %CONVERTTOPYTHON[qint64](pid));
// @snippet qprocess-startdetached

// @snippet qcoreapplication-init
static void QCoreApplicationConstructor(PyObject *self, PyObject *pyargv, QCoreApplicationWrapper **cptr)
{
    static int argc;
    static char **argv;
    PyObject *stringlist = PyTuple_GetItem(pyargv, 0);
    if (Shiboken::listToArgcArgv(stringlist, &argc, &argv, "PySideApp")) {
        *cptr = new QCoreApplicationWrapper(argc, argv);
        Shiboken::Object::releaseOwnership(reinterpret_cast<SbkObject *>(self));
        PySide::registerCleanupFunction(&PySide::destroyQCoreApplication);
    }
}
// @snippet qcoreapplication-init

// @snippet qcoreapplication-1
QCoreApplicationConstructor(%PYSELF, args, &%0);
// @snippet qcoreapplication-1

// @snippet qcoreapplication-2
PyObject *empty = PyTuple_New(2);
if (!PyTuple_SetItem(empty, 0, PyList_New(0))) {
    QCoreApplicationConstructor(%PYSELF, empty, &%0);
}
// @snippet qcoreapplication-2

// @snippet qcoreapplication-instance
PyObject *pyApp = Py_None;
if (qApp) {
    pyApp = reinterpret_cast<PyObject *>(
        Shiboken::BindingManager::instance().retrieveWrapper(qApp));
    if (!pyApp)
        pyApp = %CONVERTTOPYTHON[QCoreApplication *](qApp);
        // this will keep app live after python exit (extra ref)
}
// PYSIDE-571: make sure that we return the singleton "None"
if (Py_TYPE(pyApp) == Py_TYPE(Py_None))
    Py_DECREF(MakeQAppWrapper(nullptr));
%PYARG_0 = pyApp;
Py_XINCREF(%PYARG_0);
// @snippet qcoreapplication-instance

// @snippet qdatastream-readrawdata
QByteArray data;
data.resize(%2);
int result = 0;
Py_BEGIN_ALLOW_THREADS
result = %CPPSELF.%FUNCTION_NAME(data.data(), data.size());
Py_END_ALLOW_THREADS
if (result == -1) {
    Py_INCREF(Py_None);
    %PYARG_0 = Py_None;
} else {
    %PYARG_0 = PyBytes_FromStringAndSize(data.constData(), result);
}
// @snippet qdatastream-readrawdata

// @snippet qdatastream-writerawdata-pybuffer
int r = 0;
Py_ssize_t bufferLen;
auto *data = reinterpret_cast<const char*>(Shiboken::Buffer::getPointer(%PYARG_1, &bufferLen));
Py_BEGIN_ALLOW_THREADS
r = %CPPSELF.%FUNCTION_NAME(data, bufferLen);
Py_END_ALLOW_THREADS
%PYARG_0 = %CONVERTTOPYTHON[int](r);
// @snippet qdatastream-writerawdata-pybuffer

// @snippet qdatastream-writerawdata
int r = 0;
Py_BEGIN_ALLOW_THREADS
r = %CPPSELF.%FUNCTION_NAME(%1, Shiboken::String::len(%PYARG_1));
Py_END_ALLOW_THREADS
%PYARG_0 = %CONVERTTOPYTHON[int](r);
// @snippet qdatastream-writerawdata

// @snippet releaseownership
Shiboken::Object::releaseOwnership(%PYARG_0);
// @snippet releaseownership

// @snippet qanimationgroup-clear
for (int counter = 0, count = %CPPSELF.animationCount(); counter < count; ++counter ) {
    QAbstractAnimation *animation = %CPPSELF.animationAt(counter);
    PyObject *obj = %CONVERTTOPYTHON[QAbstractAnimation *](animation);
    Shiboken::Object::setParent(nullptr, obj);
    Py_DECREF(obj);
}
%CPPSELF.clear();
// @snippet qanimationgroup-clear

// @snippet qeasingcurve
PySideEasingCurveFunctor::init();
// @snippet qeasingcurve

// @snippet qeasingcurve-setcustomtype
QEasingCurve::EasingFunction func = PySideEasingCurveFunctor::createCustomFunction(%PYSELF, %PYARG_1);
if (func)
    %CPPSELF.%FUNCTION_NAME(func);
// @snippet qeasingcurve-setcustomtype

// @snippet qeasingcurve-customtype
//%FUNCTION_NAME()
%PYARG_0 = PySideEasingCurveFunctor::callable(%PYSELF);
// @snippet qeasingcurve-customtype

// @snippet qt-signal
%PYARG_0 = Shiboken::String::fromFormat("2%s",QMetaObject::normalizedSignature(%1).constData());
// @snippet qt-signal

// @snippet qt-slot
%PYARG_0 = Shiboken::String::fromFormat("1%s",QMetaObject::normalizedSignature(%1).constData());
// @snippet qt-slot

// @snippet qt-registerresourcedata
QT_BEGIN_NAMESPACE
extern bool
qRegisterResourceData(int,
                      const unsigned char *,
                      const unsigned char *,
                      const unsigned char *);

extern bool
qUnregisterResourceData(int,
                        const unsigned char *,
                        const unsigned char *,
                        const unsigned char *);
QT_END_NAMESPACE
// @snippet qt-registerresourcedata

// @snippet qt-qregisterresourcedata
%RETURN_TYPE %0 = %FUNCTION_NAME(%1, reinterpret_cast<uchar *>(PyBytes_AsString(%PYARG_2)),
                                     reinterpret_cast<uchar *>(PyBytes_AsString(%PYARG_3)),
                                     reinterpret_cast<uchar *>(PyBytes_AsString(%PYARG_4)));
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qt-qregisterresourcedata

// @snippet qt-qunregisterresourcedata
%RETURN_TYPE %0 = %FUNCTION_NAME(%1, reinterpret_cast<uchar *>(PyBytes_AsString(%PYARG_2)),
                                     reinterpret_cast<uchar *>(PyBytes_AsString(%PYARG_3)),
                                     reinterpret_cast<uchar *>(PyBytes_AsString(%PYARG_4)));
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qt-qunregisterresourcedata

// @snippet qdebug-format-string
Py_BEGIN_ALLOW_THREADS
%FUNCTION_NAME("%s", %1); // Uses placeholder for security reasons
Py_END_ALLOW_THREADS
// @snippet qdebug-format-string

// @snippet qmessagelogger-format-string
Py_BEGIN_ALLOW_THREADS
%CPPSELF->%FUNCTION_NAME("%s", %1); // Uses placeholder for security reasons
Py_END_ALLOW_THREADS
// @snippet qmessagelogger-format-string

// @snippet qmessagelogger-logcategory-format-string
Py_BEGIN_ALLOW_THREADS
%CPPSELF->%FUNCTION_NAME(%1, "%s", %2); // Uses placeholder for security reasons
Py_END_ALLOW_THREADS
// @snippet qmessagelogger-logcategory-format-string

// @snippet qresource-registerResource
 auto ptr = reinterpret_cast<uchar *>(Shiboken::Buffer::getPointer(%PYARG_1));
 %RETURN_TYPE %0 = %CPPSELF.%FUNCTION_NAME(const_cast<const uchar *>(ptr), %2);
 %PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qresource-registerResource

// @snippet qstring-return
%PYARG_0 = %CONVERTTOPYTHON[QString](%1);
// @snippet qstring-return

// @snippet stream-write-method
Py_BEGIN_ALLOW_THREADS
(*%CPPSELF) << %1;
Py_END_ALLOW_THREADS
// @snippet stream-write-method

// @snippet stream-read-method
%RETURN_TYPE _cpp_result;
Py_BEGIN_ALLOW_THREADS
(*%CPPSELF) >> _cpp_result;
Py_END_ALLOW_THREADS
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](_cpp_result);
// @snippet stream-read-method

// @snippet return-qstring-ref
QString &res = *%0;
%PYARG_0 = %CONVERTTOPYTHON[QString](res);
// @snippet return-qstring-ref

// @snippet return-readData
%RETURN_TYPE %0 = 0;
if (PyBytes_Check(%PYARG_0)) {
    %0 = PyBytes_Size(%PYARG_0.object());
    memcpy(%1, PyBytes_AsString(%PYARG_0.object()), %0);
} else if (Shiboken::String::check(%PYARG_0.object())) {
    %0 = Shiboken::String::len(%PYARG_0.object());
    memcpy(%1, Shiboken::String::toCString(%PYARG_0.object()), %0);
}
// @snippet return-readData

// @snippet qiodevice-readData
QByteArray ba(1 + qsizetype(%2), char(0));
Py_BEGIN_ALLOW_THREADS
%CPPSELF.%FUNCTION_NAME(ba.data(), qint64(%2));
Py_END_ALLOW_THREADS
%PYARG_0 = Shiboken::String::fromCString(ba.constData());
// @snippet qiodevice-readData

// @snippet qt-module-shutdown
{ // Avoid name clash
    Shiboken::AutoDecRef regFunc(static_cast<PyObject *>(nullptr));
    Shiboken::AutoDecRef atexit(Shiboken::Module::import("atexit"));
    if (atexit.isNull()) {
        qWarning("Module atexit not found for registering __moduleShutdown");
        PyErr_Clear();
    } else {
        regFunc.reset(PyObject_GetAttrString(atexit, "register"));
        if (regFunc.isNull()) {
            qWarning("Function atexit.register not found for registering __moduleShutdown");
            PyErr_Clear();
        }
    }
    if (!atexit.isNull() && !regFunc.isNull()){
        PyObject *shutDownFunc = PyObject_GetAttrString(module, "__moduleShutdown");
        Shiboken::AutoDecRef args(PyTuple_New(1));
        PyTuple_SetItem(args, 0, shutDownFunc);
        Shiboken::AutoDecRef retval(PyObject_Call(regFunc, args, nullptr));
        Q_ASSERT(!retval.isNull());
    }
}
// @snippet qt-module-shutdown

// @snippet qthread_init_pypy
#ifdef PYPY_VERSION
// PYSIDE-535: PyPy 7.3.8 needs this call, which is actually a no-op in Python 3.9
//             This function should be replaced by a `Py_Initialize` call, but
//             that is still undefined. So we don't rely yet on any PyPy version.
PyEval_InitThreads();
#endif
// @snippet qthread_init_pypy

// @snippet qthread_exec_
if (PyErr_WarnEx(PyExc_DeprecationWarning,
                 "'exec_' will be removed in the future. "
                 "Use 'exec' instead.",
                 1)) {
    return nullptr;
}
%BEGIN_ALLOW_THREADS
#ifndef AVOID_PROTECTED_HACK
int cppResult = %CPPSELF.exec();
#else
int cppResult = static_cast<::QThreadWrapper *>(cppSelf)->QThreadWrapper::exec_protected();
#endif
%END_ALLOW_THREADS
%PYARG_0 = %CONVERTTOPYTHON[int](cppResult);
// @snippet qthread_exec_

// @snippet exec_
if (PyErr_WarnEx(PyExc_DeprecationWarning,
                 "'exec_' will be removed in the future. "
                 "Use 'exec' instead.",
                 1)) {
    return nullptr;
}
%BEGIN_ALLOW_THREADS
int cppResult = %CPPSELF.exec();
%END_ALLOW_THREADS
%PYARG_0 = %CONVERTTOPYTHON[int](cppResult);
// @snippet exec_

// @snippet exec_arg1
if (PyErr_WarnEx(PyExc_DeprecationWarning,
                 "'exec_' will be removed in the future. "
                 "Use 'exec' instead.",
                 1)) {
    return nullptr;
}
%BEGIN_ALLOW_THREADS
int cppResult;
if (numArgs == 1)
    cppResult = %CPPSELF.exec(%1);
else
    cppResult = %CPPSELF.exec();
%END_ALLOW_THREADS
%PYARG_0 = %CONVERTTOPYTHON[int](cppResult);
// @snippet exec_arg1

// @snippet exec_arg1_noreturn
if (PyErr_WarnEx(PyExc_DeprecationWarning,
                 "'exec_' will be removed in the future. "
                 "Use 'exec' instead.",
                 1)) {
    return nullptr;
}
%BEGIN_ALLOW_THREADS
if (numArgs == 1)
    %CPPSELF.exec(%1);
else
    %CPPSELF.exec();
%END_ALLOW_THREADS
// @snippet exec_arg1_noreturn

// @snippet qtextstreammanipulator-exec
if (PyErr_WarnEx(PyExc_DeprecationWarning,
                 "'exec_' will be removed in the future. "
                 "Use 'exec' instead.",
                 1)) {
    return nullptr;
}
%CPPSELF.exec(%1);
// @snippet qtextstreammanipulator-exec

/*********************************************************************
 * CONVERSIONS
 ********************************************************************/

// @snippet conversion-pybool
%out = %OUTTYPE(%in == Py_True);
// @snippet conversion-pybool

// @snippet conversion-pylong-quintptr
#if QT_POINTER_SIZE == 8
%out = %OUTTYPE(PyLong_AsUnsignedLongLong(%in));
#else
%out = %OUTTYPE(PyLong_AsUnsignedLong(%in));
#endif
// @snippet conversion-pylong-quintptr

// @snippet conversion-pyunicode
%out = PySide::pyUnicodeToQString(%in);
// @snippet conversion-pyunicode

// @snippet conversion-pynone
SBK_UNUSED(%in)
%out = %OUTTYPE();
// @snippet conversion-pynone

// @snippet qfile-path-1
auto cppArg0 = PySide::pyPathToQString(%PYARG_1);
// @snippet qfile-path-1

// @snippet qfile-path-2
auto cppArg1 = PySide::pyPathToQString(%PYARG_2);
// @snippet qfile-path-2

// @snippet qitemselection-add
auto res = (*%CPPSELF) + cppArg0;
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](res);
// @snippet qitemselection-add

// @snippet conversion-pystring-char
char c = %CONVERTTOCPP[char](%in);
%out = %OUTTYPE(static_cast<unsigned short>(c));
// @snippet conversion-pystring-char

// @snippet conversion-pyint
int i = %CONVERTTOCPP[int](%in);
%out = %OUTTYPE(i);
// @snippet conversion-pyint

// @snippet conversion-qlonglong
// PYSIDE-1250: For QVariant, if the type fits into an int; use int preferably.
qlonglong in = %CONVERTTOCPP[qlonglong](%in);
constexpr qlonglong intMax = qint64(std::numeric_limits<int>::max());
constexpr qlonglong intMin = qint64(std::numeric_limits<int>::min());
%out = in >= intMin && in <= intMax ? %OUTTYPE(int(in)) : %OUTTYPE(in);
// @snippet conversion-qlonglong

// @snippet conversion-qstring
QString in = %CONVERTTOCPP[QString](%in);
%out = %OUTTYPE(in);
// @snippet conversion-qstring

// @snippet conversion-qbytearray
QByteArray in = %CONVERTTOCPP[QByteArray](%in);
%out = %OUTTYPE(in);
// @snippet conversion-qbytearray

// @snippet conversion-pyfloat
double in = %CONVERTTOCPP[double](%in);
%out = %OUTTYPE(in);
// @snippet conversion-pyfloat

// @snippet conversion-sbkobject
// a class supported by QVariant?
const QMetaType metaType = QVariant_resolveMetaType(Py_TYPE(%in));
bool ok = false;
if (metaType.isValid()) {
    QVariant var(metaType);
    auto converterO = converterForQtType(metaType.name());
    ok = converterO.has_value();
    if (ok) {
        converterO.value().toCpp(pyIn, var.data());
        %out = var;
    } else {
        qWarning("%s: Cannot find a converter for \"%s\".",
                 __FUNCTION__, metaType.name());
    }
}

// If the type was not encountered, return a default PyObjectWrapper
if (!ok)
    %out = QVariant::fromValue(PySide::PyObjectWrapper(%in));
// @snippet conversion-sbkobject

// @snippet conversion-pydict
QVariant ret = QVariant_convertToVariantMap(%in);
%out = ret.isValid() ? ret : QVariant::fromValue(PySide::PyObjectWrapper(%in));
// @snippet conversion-pydict

// @snippet conversion-pylist
QVariant ret = QVariant_convertToVariantList(%in);
%out = ret.isValid() ? ret : QVariant::fromValue(PySide::PyObjectWrapper(%in));
// @snippet conversion-pylist

// @snippet conversion-pyobject
// Is a shiboken type not known by Qt
%out = QVariant::fromValue(PySide::PyObjectWrapper(%in));
// @snippet conversion-pyobject

// @snippet conversion-qjsonobject-pydict
QVariant dict = QVariant_convertToVariantMap(%in);
QJsonValue val = QJsonValue::fromVariant(dict);
%out = val.toObject();
// @snippet conversion-qjsonobject-pydict

// @snippet conversion-qdate-pydate
int day = PyDateTime_GET_DAY(%in);
int month = PyDateTime_GET_MONTH(%in);
int year = PyDateTime_GET_YEAR(%in);
%out = %OUTTYPE(year, month, day);
// @snippet conversion-qdate-pydate

// @snippet conversion-qdatetime-pydatetime
int day = PyDateTime_GET_DAY(%in);
int month = PyDateTime_GET_MONTH(%in);
int year = PyDateTime_GET_YEAR(%in);
int hour = PyDateTime_DATE_GET_HOUR(%in);
int min = PyDateTime_DATE_GET_MINUTE(%in);
int sec = PyDateTime_DATE_GET_SECOND(%in);
int usec = PyDateTime_DATE_GET_MICROSECOND(%in);
%out = %OUTTYPE(QDate(year, month, day), QTime(hour, min, sec, usec/1000));
// @snippet conversion-qdatetime-pydatetime

// @snippet conversion-qtime-pytime
int hour = PyDateTime_TIME_GET_HOUR(%in);
int min = PyDateTime_TIME_GET_MINUTE(%in);
int sec = PyDateTime_TIME_GET_SECOND(%in);
int usec = PyDateTime_TIME_GET_MICROSECOND(%in);
%out = %OUTTYPE(hour, min, sec, usec/1000);
// @snippet conversion-qtime-pytime

// @snippet conversion-qbytearray-pybytes
%out = %OUTTYPE(PyBytes_AsString(%in), PyBytes_Size(%in));
// @snippet conversion-qbytearray-pybytes

// @snippet conversion-qbytearray-pybytearray
%out = %OUTTYPE(PyByteArray_AsString(%in), PyByteArray_Size(%in));
// @snippet conversion-qbytearray-pybytearray

// @snippet conversion-qbytearray-pystring
%out = %OUTTYPE(Shiboken::String::toCString(%in), Shiboken::String::len(%in));
// @snippet conversion-qbytearray-pystring

/*********************************************************************
 * NATIVE TO TARGET CONVERSIONS
 ********************************************************************/

// @snippet return-pybool
return PyBool_FromLong((bool)%in);
// @snippet return-pybool

// @snippet return-pybytes
return PyBytes_FromStringAndSize(%in.constData(), %in.size());
// @snippet return-pybytes

// @snippet chrono-to-pylong
return PyLong_FromLong(%in.count());
// @snippet chrono-to-pylong

// @snippet pylong-to-chrono
%out = %OUTTYPE(PyLong_AsLongLong(%in));
// @snippet pylong-to-chrono

// @snippet return-pylong
return PyLong_FromLong(%in);
// @snippet return-pylong

// @snippet return-pylong-quintptr
#if QT_POINTER_SIZE == 8
return PyLong_FromUnsignedLongLong(%in);
#else
return PyLong_FromUnsignedLong(%in);
#endif
// @snippet return-pylong-quintptr

// @snippet return-qfunctionpointer-pylong
return PyLong_FromVoidPtr(reinterpret_cast<void *>(%in));
// @snippet return-qfunctionpointer-pylong

// @snippet conversion-pylong-qfunctionpointer
%out = reinterpret_cast<QFunctionPointer>(PyLong_AsVoidPtr(%in));
// @snippet conversion-pylong-qfunctionpointer

// @snippet return-pyunicode
return PySide::qStringToPyUnicode(%in);
// @snippet return-pyunicode

// @snippet return-pyunicode-from-qlatin1string
#ifdef Py_LIMITED_API
return PySide::qStringToPyUnicode(QString::fromLatin1(%in));
#else
return PyUnicode_FromKindAndData(PyUnicode_1BYTE_KIND, %in.constData(), %in.size());
#endif
// @snippet return-pyunicode-from-qlatin1string

// @snippet qlatin1string-check
static bool qLatin1StringCheck(PyObject *o)
{
    return PyUnicode_CheckExact(o) != 0
        && _PepUnicode_KIND(o) == PepUnicode_1BYTE_KIND;
}
// @snippet qlatin1string-check

// @snippet conversion-pystring-qlatin1string
const char *data = reinterpret_cast<const char *>(_PepUnicode_DATA(%in));
const Py_ssize_t len = PyUnicode_GetLength(%in);
%out = QLatin1String(data, len);
// @snippet conversion-pystring-qlatin1string

// @snippet return-pyunicode-from-qanystringview
return PySide::qStringToPyUnicode(%in.toString());
// @snippet return-pyunicode-from-qanystringview

// @snippet return-pyunicode-qchar
auto c = wchar_t(%in.unicode());
return PyUnicode_FromWideChar(&c, 1);
// @snippet return-pyunicode-qchar

// @snippet return-qvariant
if (!%in.isValid())
    Py_RETURN_NONE;

switch (%in.typeId()) {
case QMetaType::UnknownType:
case QMetaType::Nullptr:
    Py_RETURN_NONE;
case QMetaType::VoidStar:
    if (%in.constData() == nullptr)
        Py_RETURN_NONE;
    break;

case QMetaType::QVariantList: {
    const auto var = %in.value<QVariantList>();
    return %CONVERTTOPYTHON[QList<QVariant>](var);
}
case QMetaType::QStringList: {
    const auto var = %in.value<QStringList>();
    return %CONVERTTOPYTHON[QList<QString>](var);
}
case QMetaType::QVariantMap: {
    const auto var = %in.value<QVariantMap>();
    return %CONVERTTOPYTHON[QMap<QString, QVariant>](var);
}
default:
    break;
}

auto converterO = converterForQtType(cppInRef.typeName());
if (converterO.has_value())
    return converterO.value().toPython(cppInRef.data());

PyErr_Format(PyExc_RuntimeError, "Can't find converter for '%s'.", %in.typeName());
return nullptr;
// @snippet return-qvariant

// @snippet return-qjsonobject
// The QVariantMap returned by QJsonObject seems to cause a segfault, so
// using QJsonObject.toVariantMap() won't work.
// Wrapping it in a QJsonValue first allows it to work
QJsonValue val(%in);
QVariant ret = val.toVariant();

return %CONVERTTOPYTHON[QVariant](ret);
// @snippet return-qjsonobject

// @snippet qthread_pthread_cleanup
#ifdef Q_OS_UNIX
#  include <pthread.h>
static void qthread_pthread_cleanup(void *arg)
{
    // PYSIDE 1282: When terminating a thread using QThread::terminate()
    // (pthread_cancel()), QThread::run() is aborted and the lock is released,
    // but ~GilState() is still executed for some reason. Prevent it from
    // releasing.
    auto gil = reinterpret_cast<Shiboken::GilState *>(arg);
    gil->abandon();
}
#endif // Q_OS_UNIX
// @snippet qthread_pthread_cleanup

// @snippet qthread_pthread_cleanup_install
#ifdef Q_OS_UNIX
pthread_cleanup_push(qthread_pthread_cleanup, &gil);
#endif
// @snippet qthread_pthread_cleanup_install

// @snippet qthread_pthread_cleanup_uninstall
#ifdef Q_OS_UNIX
pthread_cleanup_pop(0);
#endif
// @snippet qthread_pthread_cleanup_uninstall

// @snippet qlibraryinfo_python_build

// For versions with one byte per digit.
static QByteArray versionString(long version)
{
    return QByteArray::number((version >> 16) & 0xFF)
           + '.' + QByteArray::number((version >> 8) & 0xFF)
           + '.' + QByteArray::number(version & 0xFF);
}

static QByteArray pythonBuild()
{
    using namespace Qt::StringLiterals;

#ifdef PYPY_VERSION
    QByteArray result = "PyPy " PYPY_VERSION
#else
    QByteArray result = "Python"
#endif
#ifdef Py_LIMITED_API
    " limited API"
#endif
#ifdef Py_GIL_DISABLED
    " free threaded"
#endif
        ;
    result += ' ';

    const auto runTimeVersion = _PepRuntimeVersion();
    const auto runTimeVersionB = versionString(runTimeVersion);
    constexpr long buildVersion = PY_VERSION_HEX >> 8;
    if (runTimeVersion == buildVersion) {
        result += runTimeVersionB;
    } else {
        result += "run time: "_ba + runTimeVersionB + " built: "_ba
                  + versionString(buildVersion);
    }
    return result;
}
// @snippet qlibraryinfo_python_build

// @snippet qlibraryinfo_build
QByteArray %0 = %CPPSELF.%FUNCTION_NAME();
%0 += " [" + pythonBuild() + ']';
%PYARG_0 = PyUnicode_FromString(%0.constData());
// @snippet qlibraryinfo_build

// @snippet qsharedmemory_data_readonly
%PYARG_0 = Shiboken::Buffer::newObject(%CPPSELF.%FUNCTION_NAME(), %CPPSELF.size());
// @snippet qsharedmemory_data_readonly

// @snippet qsharedmemory_data_readwrite
// FIXME: There is no way to tell whether QSharedMemory was attached read/write
%PYARG_0 = Shiboken::Buffer::newObject(%CPPSELF.%FUNCTION_NAME(), %CPPSELF.size(),
                                       Shiboken::Buffer::ReadWrite);
// @snippet qsharedmemory_data_readwrite

// @snippet std-function-void-lambda
auto *callable = %PYARG_1;
auto cppCallback = [callable]()
{
    Shiboken::GilState state;
    Shiboken::AutoDecRef arglist(PyTuple_New(0));
    Shiboken::AutoDecRef ret(PyObject_CallObject(callable, arglist));
    Py_DECREF(callable);
};
// @snippet std-function-void-lambda

// @snippet qthreadpool-start
Py_INCREF(callable);
%CPPSELF.%FUNCTION_NAME(cppCallback, %2);
// @snippet qthreadpool-start

// @snippet qthreadpool-trystart
Py_INCREF(callable);
%RETURN_TYPE %0 = %CPPSELF.%FUNCTION_NAME(cppCallback);
%PYARG_0 = %CONVERTTOPYTHON[int](cppResult);
// @snippet qthreadpool-trystart

// @snippet repr-qevent
QString result;
QDebug(&result).nospace() << "<PySide6.QtCore.QEvent(" << %CPPSELF->type() << ")>";
%PYARG_0 = Shiboken::String::fromCString(qPrintable(result));
// @snippet repr-qevent

// @snippet qmetaproperty_write_enum
if (Shiboken::Enum::check(%PYARG_2))
    cppArg1 = QVariant(int(Shiboken::Enum::getValue(%PYARG_2)));
// @snippet qmetaproperty_write_enum

// @snippet qdatastream-read-bytes
QByteArray data;
data.resize(%2);
auto dataChar = data.data();
cppSelf->readBytes(dataChar, %2);
const char *constDataChar = dataChar;
if (dataChar == nullptr) {
    Py_INCREF(Py_None);
    %PYARG_0 = Py_None;
} else {
    %PYARG_0 = PyBytes_FromStringAndSize(constDataChar, %2);
}
// @snippet qdatastream-read-bytes

// Q_ARG()-equivalent
// @snippet q_arg
const QArgData qArgData = qArgDataFromPyType(%1);
if (!qArgData)
    return nullptr;

switch (qArgData.metaType.id()) {
    case QMetaType::Bool:
        *reinterpret_cast<bool *>(qArgData.data) = %2 == Py_True;
        break;
    case QMetaType::Int:
        *reinterpret_cast<int *>(qArgData.data) = int(PyLong_AsLong(%2));
        break;
    case QMetaType::Double:
        *reinterpret_cast<double *>(qArgData.data) = PyFloat_AsDouble(%2);
        break;
    case QMetaType::QString:
        *reinterpret_cast<QString *>(qArgData.data) = PySide::pyUnicodeToQString(%2);
        break;
    default: {
        Shiboken::Conversions::SpecificConverter converter(qArgData.metaType.name());
        const auto type = converter.conversionType();
        // Copy for values, Pointer for objects
        if (type == Shiboken::Conversions::SpecificConverter::InvalidConversion) {
            PyErr_Format(PyExc_RuntimeError, "%s: Unable to find converter for \"%s\".",
                         __FUNCTION__, qArgData.metaType.name());
            return nullptr;
        }
        converter.toCpp(%2, qArgData.data);
    }
}

QtCoreHelper::QGenericArgumentHolder result(qArgData.metaType, qArgData.data);
%PYARG_0 = %CONVERTTOPYTHON[QtCoreHelper::QGenericArgumentHolder](result);
// @snippet q_arg

// Q_RETURN_ARG()-equivalent
// @snippet q_return_arg
const QArgData qArgData = qArgDataFromPyType(%1);
if (!qArgData)
    return nullptr;

QtCoreHelper::QGenericReturnArgumentHolder result(qArgData.metaType, qArgData.data);
%PYARG_0 = %CONVERTTOPYTHON[QtCoreHelper::QGenericReturnArgumentHolder](result);
// @snippet q_return_arg

// @snippet qmetamethod-invoke-helpers
static InvokeMetaMethodFunc
    createInvokeMetaMethodFunc(const QMetaMethod &method, QObject *object,
                               Qt::ConnectionType type = Qt::AutoConnection)
{
    return [&method, object, type](QGenericArgument a0, QGenericArgument a1,
                                   QGenericArgument a2, QGenericArgument a3,
                                   QGenericArgument a4, QGenericArgument a5,
                                   QGenericArgument a6, QGenericArgument a7,
                                   QGenericArgument a8, QGenericArgument a9) -> bool
    {
        return method.invoke(object, type, a0, a1, a2, a3, a4, a5, a6, a7, a8, a9);
    };
}

static InvokeMetaMethodFuncWithReturn
    createInvokeMetaMethodFuncWithReturn(const QMetaMethod &method, QObject *object,
                                         Qt::ConnectionType type = Qt::AutoConnection)
{
    return [&method, object, type](QGenericReturnArgument r,
                                   QGenericArgument a0, QGenericArgument a1,
                                   QGenericArgument a2, QGenericArgument a3,
                                   QGenericArgument a4, QGenericArgument a5,
                                   QGenericArgument a6, QGenericArgument a7,
                                   QGenericArgument a8, QGenericArgument a9) -> bool
    {
        return method.invoke(object, type, r, a0, a1, a2, a3, a4, a5, a6, a7, a8, a9);
    };
}
// @snippet qmetamethod-invoke-helpers

// @snippet qmetamethod-invoke-conn-type-return-arg
%PYARG_0 = invokeMetaMethodWithReturn(createInvokeMetaMethodFuncWithReturn(*%CPPSELF, %1, %2),
                                      %3, %4, %5, %6, %7, %8, %9, %10, %11, %12, %13);
// @snippet qmetamethod-invoke-conn-type-return-arg

// @snippet qmetamethod-invoke-return-arg
%PYARG_0 = invokeMetaMethodWithReturn(createInvokeMetaMethodFuncWithReturn(*%CPPSELF, %1),
                                      %2, %3, %4, %5, %6, %7, %8, %9, %10, %11, %12);
// @snippet qmetamethod-invoke-return-arg

// @snippet qmetamethod-invoke-conn-type
%PYARG_0 = invokeMetaMethod(createInvokeMetaMethodFunc(*%CPPSELF, %1, %2),
                            %3, %4, %5, %6, %7, %8, %9, %10, %11, %12);
// @snippet qmetamethod-invoke-conn-type

// @snippet qmetamethod-invoke
%PYARG_0 = invokeMetaMethod(createInvokeMetaMethodFunc(*%CPPSELF, %1),
                            %2, %3, %4, %5, %6, %7, %8, %9, %10, %11);
// @snippet qmetamethod-invoke

// @snippet qmetaobject-invokemethod-helpers
static InvokeMetaMethodFunc
    createInvokeMetaMethodFunc(QObject *object, const char *methodName,
                               Qt::ConnectionType type = Qt::AutoConnection)
{
    return [object, methodName, type](QGenericArgument a0, QGenericArgument a1,
                                      QGenericArgument a2, QGenericArgument a3,
                                      QGenericArgument a4, QGenericArgument a5,
                                      QGenericArgument a6, QGenericArgument a7,
                                      QGenericArgument a8, QGenericArgument a9) -> bool
    {
        return QMetaObject::invokeMethod(object, methodName, type,
                                         a0, a1, a2, a3, a4, a5, a6, a7, a8, a9);
    };
}

static InvokeMetaMethodFuncWithReturn
    createInvokeMetaMethodFuncWithReturn(QObject *object, const char *methodName,
                                         Qt::ConnectionType type = Qt::AutoConnection)
{
    return [object, methodName, type](QGenericReturnArgument r,
                                      QGenericArgument a0, QGenericArgument a1,
                                      QGenericArgument a2, QGenericArgument a3,
                                      QGenericArgument a4, QGenericArgument a5,
                                      QGenericArgument a6, QGenericArgument a7,
                                      QGenericArgument a8, QGenericArgument a9) -> bool
    {
        return QMetaObject::invokeMethod(object, methodName, type,
                                         r, a0, a1, a2, a3, a4, a5, a6, a7, a8, a9);
    };
}
// @snippet qmetaobject-invokemethod-helpers

// invokeMethod(QObject *,const char *, QGenericArgument a0, a1, a2 )
// @snippet qmetaobject-invokemethod-arg
%PYARG_0 = invokeMetaMethod(createInvokeMetaMethodFunc(%1, %2),
                            %3, %4, %5, %6, %7, %8, %9, %10, %11, %12);
// @snippet qmetaobject-invokemethod-arg

// invokeMethod(QObject *,const char *,Qt::ConnectionType, QGenericArgument a0, a1, a2 )
// @snippet qmetaobject-invokemethod-conn-type-arg
%PYARG_0 = invokeMetaMethod(createInvokeMetaMethodFunc(%1, %2, %3),
                             %4, %5, %6, %7, %8, %9, %10, %11, %12, %13);
// @snippet qmetaobject-invokemethod-conn-type-arg

// invokeMethod(QObject *,const char *, Qt::ConnectionType, QGenericReturnArgument,QGenericArgument a0, a1, a2 )
// @snippet qmetaobject-invokemethod-conn-type-return-arg
%PYARG_0 = invokeMetaMethodWithReturn(createInvokeMetaMethodFuncWithReturn(%1, %2, %3),
                                      %4, %5, %6, %7, %8, %9, %10, %11, %12, %13, %14);
// @snippet qmetaobject-invokemethod-conn-type-return-arg

// invokeMethod(QObject *,const char *, QGenericReturnArgument,QGenericArgument a0, a1, a2 )
// @snippet qmetaobject-invokemethod-return-arg
%PYARG_0 = invokeMetaMethodWithReturn(createInvokeMetaMethodFuncWithReturn(%1, %2),
                                      %3, %4, %5, %6, %7, %8, %9, %10, %11, %12, %13);
// @snippet qmetaobject-invokemethod-return-arg

// @snippet keycombination-from-keycombination
cptr = new ::%TYPE(%1);
// @snippet keycombination-from-keycombination

// @snippet keycombination-from-modifier
cptr = new ::%TYPE(%1, %2);
// @snippet keycombination-from-modifier

// @snippet qmetamethod-from-signal
auto *signalInst = reinterpret_cast<PySideSignalInstance *>(%PYARG_1);
const auto data = PySide::Signal::getEmitterData(signalInst);
const auto result = data.methodIndex != -1
    ? data.emitter->metaObject()->method(data.methodIndex)
    : QMetaMethod{};
%PYARG_0 = %CONVERTTOPYTHON[QMetaMethod](result);
// @snippet qmetamethod-from-signal

// @snippet qrunnable_create
auto callable = %PYARG_1;
auto callback = [callable]() -> void
{
    if (!PyCallable_Check(callable)) {
        qWarning("Argument 1 of %FUNCTION_NAME must be a callable.");
        return;
    }
    Shiboken::GilState state;
    Shiboken::AutoDecRef ret(PyObject_CallObject(callable, nullptr));
    Py_DECREF(callable);
};
Py_INCREF(callable);
%RETURN_TYPE %0 = %CPPSELF.%FUNCTION_NAME(callback);
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qrunnable_create

// @snippet qlocale_system
// For darwin systems, QLocale::system() involves looking at the Info.plist of the application
// bundle to detect the system localization. In the case of Qt for Python, the application bundle
// is the used Python framework. To enable retreival of localized string, the property list key
// CFBunldeAllowMixedLocalizations should be set to True inside the Info.plist file. Otherwise,
// CFBundleDevelopmentRegion will be used to find the language preference of the user, which in the
// case of Python is always english.
// This is a hack until CFBunldeAllowMixedLocalizations will be set in the Python framework
// installation in darwin systems.
// Upstream issue in CPython: https://github.com/python/cpython/issues/108269
#ifdef Q_OS_DARWIN
    Shiboken::AutoDecRef locale(PyImport_ImportModule("locale"));
    Shiboken::AutoDecRef getLocale(PyObject_GetAttrString(locale, "getlocale"));
    Shiboken::AutoDecRef systemLocale(PyObject_CallObject(getLocale, nullptr));
    PyObject* localeCode = PyTuple_GetItem(systemLocale, 0);
    %RETURN_TYPE %0;
    if (localeCode != Py_None) {
        QString localeCodeStr = PySide::pyStringToQString(localeCode);
        %0 = QLocale(localeCodeStr);
    } else {
       // The default locale is 'C' locale as mentioned in
       // https://docs.python.org/3/library/locale.html
        %0 = ::QLocale::c();
    }
#else
    %RETURN_TYPE %0 = %CPPSELF.%FUNCTION_NAME();
#endif
%PYARG_0 = %CONVERTTOPYTHON[%RETURN_TYPE](%0);
// @snippet qlocale_system

// @snippet qcoreapplication-requestpermission
auto permission = %1;
auto callable = %PYARG_3;

// check if callable
if (!PyCallable_Check(callable)) {
    qWarning("Functor of %FUNCTION_NAME is not a callable");
    return {};
}

// find the number of arguments of callable. It should either be empy or accept a QPermission
// object
int count = 0;
PyObject* fc = nullptr;
bool classMethod = false;
Shiboken::AutoDecRef func_ob(PyObject_GetAttr(callable, Shiboken::PyMagicName::func()));

if (func_ob.isNull() && PyObject_HasAttr(callable, Shiboken::PyMagicName::code())) {
    // variable `callable` is a function
    fc = PyObject_GetAttr(callable, Shiboken::PyMagicName::code());
} else {
    // variable `callable` is a class method
    fc = PyObject_GetAttr(func_ob, Shiboken::PyMagicName::code());
    classMethod = true;
}

if (fc) {
    PyObject* ac = PyObject_GetAttrString(fc, "co_argcount");
    if (ac) {
        count = PyLong_AsLong(ac);
        Py_DECREF(ac);
    }
    Py_DECREF(fc);
}

if ((classMethod && (count > 2)) || (!classMethod && (count > 1))) {
    qWarning("Functor of %FUNCTION_NAME must either have QPermission object as argument or none."
             "The QPermission object store the result of requestPermission()");
    return {};
}

bool arg_qpermission = (classMethod && (count == 2)) || (!classMethod && (count == 1));

auto callback = [callable, arg_qpermission](const QPermission &permission) -> void
{
    Shiboken::GilState state;
    if (arg_qpermission) {
        Shiboken::AutoDecRef arglist(PyTuple_New(1));
        PyTuple_SetItem(arglist.object(), 0, %CONVERTTOPYTHON[QPermission](permission));
        Shiboken::AutoDecRef ret(PyObject_CallObject(callable, arglist));
    } else {
        Shiboken::AutoDecRef ret(PyObject_CallObject(callable, nullptr));
    }
    Py_DECREF(callable);
};
Py_INCREF(callable);

Py_BEGIN_ALLOW_THREADS
%CPPSELF.%FUNCTION_NAME(permission, %2, callback);
Py_END_ALLOW_THREADS
// @snippet qcoreapplication-requestpermission

// @snippet qlockfile-getlockinfo
qint64 pid{};
QString hostname, appname;
%CPPSELF.%FUNCTION_NAME(&pid, &hostname, &appname);
%PYARG_0 = PyTuple_New(3);
PyTuple_SetItem(%PYARG_0, 0, %CONVERTTOPYTHON[qint64](pid));
PyTuple_SetItem(%PYARG_0, 1, %CONVERTTOPYTHON[QString](hostname));
PyTuple_SetItem(%PYARG_0, 2, %CONVERTTOPYTHON[QString](appname));
// @snippet qlockfile-getlockinfo

// @snippet darwin_permission_plugin
#ifdef Q_OS_DARWIN
#include<QtCore/qplugin.h>
// register the static plugin and setup its metadata
Q_IMPORT_PLUGIN(QDarwinCameraPermissionPlugin)
Q_IMPORT_PLUGIN(QDarwinMicrophonePermissionPlugin)
Q_IMPORT_PLUGIN(QDarwinBluetoothPermissionPlugin)
Q_IMPORT_PLUGIN(QDarwinContactsPermissionPlugin)
Q_IMPORT_PLUGIN(QDarwinCalendarPermissionPlugin)
#endif
// @snippet darwin_permission_plugin

// @snippet qt-modifier
PyObject *_inputDict = PyDict_New();
// Note: The builtins line is no longer needed since Python 3.10. Undocumented!
PyDict_SetItemString(_inputDict, "__builtins__", PyEval_GetBuiltins());
PyDict_SetItemString(_inputDict, "QtCore", module);
PyDict_SetItemString(_inputDict, "Qt", reinterpret_cast<PyObject *>(pyType));
// Explicitly not dereferencing the result.
PyRun_String(R"PY(if True:
    from enum import Flag
    from textwrap import dedent
    from warnings import warn
    # QtCore and Qt come as globals.

    def func_or(self, other):
        if isinstance(self, Flag) and isinstance(other, Flag):
            # this is normal or-ing flags together
            return Qt.KeyboardModifier(self.value | other.value)
        return QtCore.QKeyCombination(self, other)

    def func_add(self, other):
        warn(dedent(f"""
            The "+" operator is deprecated in Qt For Python 6.0 .
            Please use "|" instead."""), stacklevel=2)
        return func_or(self, other)

    Qt.KeyboardModifier.__or__ = func_or
    Qt.KeyboardModifier.__ror__ = func_or
    Qt.Modifier.__or__ = func_or
    Qt.Modifier.__ror__ = func_or
    Qt.KeyboardModifier.__add__ = func_add
    Qt.KeyboardModifier.__radd__ = func_add
    Qt.Modifier.__add__ = func_add
    Qt.Modifier.__radd__ = func_add

)PY", Py_file_input, _inputDict, _inputDict);
// @snippet qt-modifier

// @snippet qdirlisting-iter
auto result = QtCoreHelper::QDirListingIterator(*%CPPSELF);
%PYARG_0 = %CONVERTTOPYTHON[QtCoreHelper::QDirListingIterator](result);
// @snippet qdirlisting-iter

// @snippet qdirlistingiterator-next
if (%CPPSELF.next()) {
    Py_INCREF(%PYSELF);
    %PYARG_0 = %PYSELF;
}
// @snippet qdirlistingiterator-next

// @snippet qdirlisting-direntry-repr
QByteArray result = '<' + QByteArray(Py_TYPE(%PYSELF)->tp_name)
                    + " object at 0x"
                    + QByteArray::number(quintptr(%PYSELF), 16) + " (\""
                    + %CPPSELF.absoluteFilePath().toUtf8() + "\")>";
%PYARG_0 = Shiboken::String::fromCString(result.constData());
// @snippet qdirlisting-direntry-repr

// @snippet return-native-eventfilter-conversion
%RETURN_TYPE %out = false;
if (PySequence_Check(%PYARG_0) != 0 && PySequence_Size(%PYARG_0) == 2) {
    Shiboken::AutoDecRef pyItem(PySequence_GetItem(%PYARG_0, 0));
    %out = %CONVERTTOCPP[bool](pyItem);
    if (result) {
        Shiboken::AutoDecRef pyResultItem(PySequence_GetItem(pyResult, 1));
        *result = %CONVERTTOCPP[qintptr](pyResultItem);
    }
}
// @snippet return-native-eventfilter-conversion

// @snippet return-native-eventfilter
%PYARG_0 = PyTuple_New(2);
PyTuple_SetItem(%PYARG_0, 0, %CONVERTTOPYTHON[%RETURN_TYPE](%0));
PyTuple_SetItem(%PYARG_0, 1, %CONVERTTOPYTHON[qintptr](*result_out));
// @snippet return-native-eventfilter
