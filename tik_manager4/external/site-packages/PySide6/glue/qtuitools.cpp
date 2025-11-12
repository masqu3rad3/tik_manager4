// Copyright (C) 2018 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
// @snippet uitools-loadui
/*
 * Based on code provided by:
 *          Antonio Valentino <antonio.valentino at tiscali.it>
 *          Frédéric <frederic.mantegazza at gbiloba.org>
 */

#include <shiboken.h>

#include <QtUiTools/QUiLoader>
#include <QtWidgets/QWidget>
#include <QtCore/QFile>

static void createChildrenNameAttributes(PyObject *root, QObject *object)
{
    for (auto *child : object->children()) {
        const QByteArray name = child->objectName().toLocal8Bit();

        if (!name.isEmpty() && !name.startsWith("_") && !name.startsWith("qt_")) {
            Shiboken::AutoDecRef attrName(Py_BuildValue("s", name.constData()));
            if (!PyObject_HasAttr(root, attrName)) {
                Shiboken::AutoDecRef pyChild(%CONVERTTOPYTHON[QObject *](child));
                PyObject_SetAttr(root, attrName, pyChild);
            }
            createChildrenNameAttributes(root, child);
        }
        createChildrenNameAttributes(root, child);
    }
}

static PyObject *QUiLoadedLoadUiFromDevice(QUiLoader *self, QIODevice *dev, QWidget *parent)
{
    QWidget *wdg = self->load(dev, parent);

    if (wdg) {
        PyObject *pyWdg = %CONVERTTOPYTHON[QWidget *](wdg);
        createChildrenNameAttributes(pyWdg, wdg);
        if (parent) {
            Shiboken::AutoDecRef pyParent(%CONVERTTOPYTHON[QWidget *](parent));
            Shiboken::Object::setParent(pyParent, pyWdg);
        }
        return pyWdg;
    }

    if (!PyErr_Occurred())
        PyErr_Format(PyExc_RuntimeError, "Unable to open/read ui device");
    return nullptr;
}

static PyObject *QUiLoaderLoadUiFromFileName(QUiLoader *self, const QString &uiFile, QWidget *parent)
{
    QFile fd(uiFile);
    return QUiLoadedLoadUiFromDevice(self, &fd, parent);
}
// @snippet uitools-loadui

// @snippet quiloader
Q_IMPORT_PLUGIN(PyCustomWidgets);
// @snippet quiloader

// @snippet quiloader-registercustomwidget
registerCustomWidget(%PYARG_1);
%CPPSELF.addPluginPath(QString{}); // force reload widgets
// @snippet quiloader-registercustomwidget

// @snippet quiloader-load-1
// Avoid calling the original function: %CPPSELF.%FUNCTION_NAME()
%PYARG_0 = QUiLoadedLoadUiFromDevice(%CPPSELF, %1, %2);
// @snippet quiloader-load-1

// @snippet quiloader-load-2
// Avoid calling the original function: %CPPSELF.%FUNCTION_NAME()
auto str = PySide::pyPathToQString(%1);
%PYARG_0 = QUiLoaderLoadUiFromFileName(%CPPSELF, str, %2);
// @snippet quiloader-load-2

// @snippet loaduitype
/*
Arguments:
    %PYARG_1 (uifile)
*/
// 1. Generate the Python code from the UI file
PyObject *strObj = PyUnicode_AsUTF8String(%PYARG_1);
char *arg1 = PyBytes_AsString(strObj);
QByteArray uiFileName(arg1);
Py_DECREF(strObj);

if (uiFileName.isEmpty()) {
    qCritical() << "Error converting the UI filename to QByteArray";
    Py_RETURN_NONE;
}

QFile uiFile(QString::fromUtf8(uiFileName));

if (!uiFile.exists()) {
    qCritical().noquote() << "File" << uiFileName << "does not exist";
    Py_RETURN_NONE;
}

// Use the 'pyside6-uic' wrapper instead of 'uic'
// This approach is better than rely on 'uic' since installing
// the wheels cover this case.
QString uicBin(QStringLiteral("pyside6-uic"));
QStringList uicArgs = {QString::fromUtf8(uiFileName)};

QProcess uicProcess;
uicProcess.start(uicBin, uicArgs);
if (!uicProcess.waitForStarted()) {
    qCritical().noquote() << "Cannot run '" << uicBin << "': "
        << uicProcess.errorString() << " - Check if 'pyside6-uic' is in PATH";
    Py_RETURN_NONE;
}

if (!uicProcess.waitForFinished()
    || uicProcess.exitStatus() != QProcess::NormalExit
    || uicProcess.exitCode() != 0) {
    qCritical().noquote() << '\'' << uicBin << "' failed: "
        << uicProcess.errorString() << " - Exit status " << uicProcess.exitStatus()
        << " (" << uicProcess.exitCode() << ")\n";
    Py_RETURN_NONE;
}

QByteArray uiFileContent = uicProcess.readAllStandardOutput();
QByteArray errorOutput = uicProcess.readAllStandardError();

if (!errorOutput.isEmpty()) {
    qCritical().noquote() << '\'' << uicBin << "' failed: " << errorOutput;
    Py_RETURN_NONE;
}

// 2. Obtain the 'classname' and the Qt base class.
QByteArray className;
QByteArray baseClassName;

// Problem
// The generated Python file doesn't have the Qt Base class information.

// Solution
// Use the XML file
if (!uiFile.open(QIODevice::ReadOnly))
    Py_RETURN_NONE;

// This will look for the first <widget> tag, e.g.:
//      <widget class="QWidget" name="ThemeWidgetForm">
// and then extract the information from "class", and "name",
// to get the baseClassName and className respectively
QXmlStreamReader reader(&uiFile);
while (!reader.atEnd() && baseClassName.isEmpty() && className.isEmpty()) {
    auto token = reader.readNext();
    if (token == QXmlStreamReader::StartElement && reader.name() == u"widget") {
        baseClassName = reader.attributes().value(QLatin1StringView("class")).toUtf8();
        className = reader.attributes().value(QLatin1StringView("name")).toUtf8();
    }
}

uiFile.close();

if (className.isEmpty() || baseClassName.isEmpty() || reader.hasError()) {
    qCritical() << "An error occurred when parsing the UI file while looking for the class info "
                << reader.errorString();
    Py_RETURN_NONE;
}

QByteArray pyClassName("Ui_"+className);

PyObject *module = PyImport_ImportModule("__main__");
PyObject *loc = PyModule_GetDict(module);

// 3. exec() the code so the class exists in the context: exec(uiFileContent)
// The context of PyRun_SimpleString is __main__.
// 'Py_file_input' is the equivalent to using exec(), since it will execute
// the code, without returning anything.
Shiboken::AutoDecRef codeUi(Py_CompileString(uiFileContent.constData(), "<stdin>", Py_file_input));
if (codeUi.isNull()) {
    qCritical() << "Error while compiling the generated Python file";
    Py_RETURN_NONE;
}
PyObject *uiObj = PyEval_EvalCode(codeUi, loc, loc);

if (uiObj == nullptr) {
    qCritical() << "Error while running exec() on the generated code";
    Py_RETURN_NONE;
}

// 4. eval() the name of the class on a variable to return
// 'Py_eval_input' is the equivalent to using eval(), since it will just
// evaluate an expression.
Shiboken::AutoDecRef codeClass(Py_CompileString(pyClassName.constData(),"<stdin>", Py_eval_input));
if (codeClass.isNull()) {
    qCritical() << "Error while compiling the Python class";
    Py_RETURN_NONE;
}

Shiboken::AutoDecRef codeBaseClass(Py_CompileString(baseClassName.constData(), "<stdin>", Py_eval_input));
if (codeBaseClass.isNull()) {
    qCritical() << "Error while compiling the base class";
    Py_RETURN_NONE;
}

PyObject *classObj = PyEval_EvalCode(codeClass, loc, loc);
PyObject *baseClassObj = PyEval_EvalCode(codeBaseClass, loc, loc);

%PYARG_0  = PyTuple_New(2);
if (%PYARG_0 == nullptr) {
    qCritical() << "Error while creating the return Tuple";
    Py_RETURN_NONE;
}
PyTuple_SetItem(%PYARG_0, 0, classObj);
PyTuple_SetItem(%PYARG_0, 1, baseClassObj);
// @snippet loaduitype
