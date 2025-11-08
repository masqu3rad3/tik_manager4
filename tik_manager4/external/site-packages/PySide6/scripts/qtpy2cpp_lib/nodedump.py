# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

"""Helper to dump AST nodes for debugging"""


import ast


def to_string(node):
    """Helper to retrieve a string from the (Lists of )Name/Attribute
       aggregated into some nodes"""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ''


def debug_format_node(node):
    """Format AST node for debugging"""
    if isinstance(node, ast.alias):
        return f'alias("{node.name}")'
    if isinstance(node, ast.arg):
        return f'arg({node.arg})'
    if isinstance(node, ast.Attribute):
        if isinstance(node.value, ast.Name):
            nested_name = debug_format_node(node.value)
            return f'Attribute("{node.attr}", {nested_name})'
        return f'Attribute("{node.attr}")'
    if isinstance(node, ast.Call):
        return 'Call({}({}))'.format(to_string(node.func), len(node.args))
    if isinstance(node, ast.ClassDef):
        base_names = [to_string(base) for base in node.bases]
        bases = ': ' + ','.join(base_names) if base_names else ''
        return f'ClassDef({node.name}{bases})'
    if isinstance(node, ast.ImportFrom):
        return f'ImportFrom("{node.module}")'
    if isinstance(node, ast.FunctionDef):
        arg_names = [a.arg for a in node.args.args]
        return 'FunctionDef({}({}))'.format(node.name, ', '.join(arg_names))
    if isinstance(node, ast.Name):
        return 'Name("{}", Ctx={})'.format(node.id, type(node.ctx).__name__)
    if isinstance(node, ast.NameConstant):
        return f'NameConstant({node.value})'
    if isinstance(node, ast.Num):
        return f'Num({node.n})'
    if isinstance(node, ast.Str):
        return f'Str("{node.s}")'
    return type(node).__name__
