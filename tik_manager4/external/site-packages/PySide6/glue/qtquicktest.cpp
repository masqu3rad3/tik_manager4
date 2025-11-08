// Copyright (C) 2023 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

/*********************************************************************
 * INJECT CODE
 ********************************************************************/

// @snippet call-quick-test-main
static int callQuickTestMain(const QString &name, QObject *setup,
                             QStringList argv, QString dir)
{
    if (dir.isEmpty())
        dir = QDir::currentPath();
    if (argv.isEmpty())
        argv.append(name);

    std::vector<QByteArray> argvB;
    std::vector<char *> argvC;
    const auto argc = argv.size();
    argvB.reserve(argc);
    argvC.reserve(argc);
    for (const auto &arg : argv) {
        argvB.emplace_back(arg.toUtf8());
        argvC.push_back(argvB.back().data());
    }

    return quick_test_main_with_setup(int(argc), argvC.data(),
                                      name.toUtf8().constData(),
                                      dir.toUtf8().constData(), setup);
}
// @snippet call-quick-test-main

// @snippet quick-test-main
const int exitCode = callQuickTestMain(%1, nullptr, %2, %3);
%PYARG_0 = %CONVERTTOPYTHON[int](exitCode);
// @snippet quick-test-main

// @snippet quick-test-main_with_setup
Shiboken::AutoDecRef pySetupObject(PyObject_CallObject(reinterpret_cast<PyObject *>(%2), nullptr));
if (pySetupObject.isNull() || PyErr_Occurred() != nullptr)
    return nullptr;

/// Convenience to convert a PyObject to QObject
QObject *setupObject = PySide::convertToQObject(pySetupObject.object(), true /* raiseError */);
if (setupObject == nullptr)
    return nullptr;

const int exitCode = callQuickTestMain(%1, setupObject, %3, %4);
%PYARG_0 = %CONVERTTOPYTHON[int](exitCode);
// @snippet quick-test-main_with_setup
