# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

"""
deprecated.py

This module contains deprecated things that are removed from the interface.
They are implemented in Python again, together with a deprecation warning.

Functions that are to be called for
    PySide6.<module> must be named
    fix_for_<module> .

Note that this fixing code is run after all initializations, but before the
import is finished. But that is no problem since the module is passed in.
"""

# eof
