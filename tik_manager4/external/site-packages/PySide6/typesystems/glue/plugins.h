// Copyright (C) 2020 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only

#ifndef _PLUGIN_H_
#define _PLUGIN_H_

#include "customwidgets.h"

#include <QtCore/qpluginloader.h>

static inline PyCustomWidgets *findPlugin()
{
    const auto &instances = QPluginLoader::staticInstances();
    for (QObject *o : instances) {
        if (auto plugin = qobject_cast<PyCustomWidgets *>(o))
            return plugin;
    }
    return nullptr;
}

static void registerCustomWidget(PyObject *obj)
{
    static PyCustomWidgets *const plugin = findPlugin();

    if (plugin)
        plugin->registerWidgetType(obj);
    else
        qWarning("Qt for Python: Failed to find the static QUiLoader plugin.");
}

#endif
