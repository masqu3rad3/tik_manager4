# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

"""C++ formatting helper functions and formatter class"""


import ast

from .qt import ClassFlag, qt_class_flags

CLOSING = {"{": "}", "(": ")", "[": "]"}  # Closing parenthesis for C++


def _fix_function_argument_type(type, for_return):
    """Fix function argument/return qualifiers using some heuristics for Qt."""
    if type == "float":
        return "double"
    if type == "str":
        type = "QString"
    if not type.startswith("Q"):
        return type
    flags = qt_class_flags(type)
    if flags & ClassFlag.PASS_BY_VALUE:
        return type
    if flags & ClassFlag.PASS_BY_CONSTREF:
        return type if for_return else f"const {type} &"
    if flags & ClassFlag.PASS_BY_REF:
        return type if for_return else f"{type} &"
    return type + " *"  # Assume pointer by default


def to_string(node):
    """Helper to retrieve a string from the (Lists of)Name/Attribute
       aggregated into some nodes"""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ''


def format_inheritance(class_def_node):
    """Returns inheritance specification of a class"""
    result = ''
    for base in class_def_node.bases:
        name = to_string(base)
        if name != 'object':
            result += ', public ' if result else ' : public '
            result += name
    return result


def format_for_target(target_node):
    if isinstance(target_node, ast.Tuple):  # for i,e in enumerate()
        result = ''
        for i, el in enumerate(target_node.elts):
            if i > 0:
                result += ', '
            result += format_reference(el)
        return result
    return format_reference(target_node)


def format_for_loop(f_node):
    """Format a for loop
       This applies some heuristics to detect:
       1) "for a in [1,2])" -> "for (f: {1, 2}) {"
       2) "for i in range(5)" -> "for (i = 0; i < 5; ++i) {"
       3) "for i in range(2,5)" -> "for (i = 2; i < 5; ++i) {"

       TODO: Detect other cases, maybe including enumerate().
    """
    loop_vars = format_for_target(f_node.target)
    result = 'for (' + loop_vars
    if isinstance(f_node.iter, ast.Call):
        f = format_reference(f_node.iter.func)
        if f == 'range':
            start = 0
            end = -1
            if len(f_node.iter.args) == 2:
                start = format_literal(f_node.iter.args[0])
                end = format_literal(f_node.iter.args[1])
            elif len(f_node.iter.args) == 1:
                end = format_literal(f_node.iter.args[0])
            result += f' = {start}; {loop_vars} < {end}; ++{loop_vars}'
    elif isinstance(f_node.iter, ast.List):
        # Range based for over list
        result += ': ' + format_literal_list(f_node.iter)
    elif isinstance(f_node.iter, ast.Name):
        # Range based for over variable
        result += ': ' + f_node.iter.id
    result += ') {'
    return result


def format_name_constant(node):
    """Format a ast.NameConstant."""
    if node.value is None:
        return "nullptr"
    return "true" if node.value else "false"


def format_literal(node):
    """Returns the value of number/string literals"""
    if isinstance(node, ast.NameConstant):
        return format_name_constant(node)
    if isinstance(node, ast.Num):
        return str(node.n)
    if isinstance(node, ast.Str):
        # Fixme: escaping
        return f'"{node.s}"'
    return ''


def format_literal_list(l_node, enclosing='{'):
    """Formats a list/tuple of number/string literals as C++ initializer list"""
    result = enclosing
    for i, el in enumerate(l_node.elts):
        if i > 0:
            result += ', '
        result += format_literal(el)
    result += CLOSING[enclosing]
    return result


def format_member(attrib_node, qualifier_in='auto'):
    """Member access foo->member() is expressed as an attribute with
       further nested Attributes/Names as value"""
    n = attrib_node
    result = ''
    # Black magic: Guess '::' if name appears to be a class name
    qualifier = qualifier_in
    if qualifier_in == 'auto':
        qualifier = '::' if n.attr[0:1].isupper() else '->'
    while isinstance(n, ast.Attribute):
        result = n.attr if not result else n.attr + qualifier + result
        n = n.value
    if isinstance(n, ast.Name) and n.id != 'self':
        if qualifier_in == 'auto' and n.id == "Qt":  # Qt namespace
            qualifier = "::"
        result = n.id + qualifier + result
    return result


def format_reference(node, qualifier='auto'):
    """Format member reference or free item"""
    return node.id if isinstance(node, ast.Name) else format_member(node, qualifier)


def format_function_def_arguments(function_def_node):
    """Formats arguments of a function definition"""
    # Default values is a list of the last default values, expand
    # so that indexes match
    argument_count = len(function_def_node.args.args)
    default_values = function_def_node.args.defaults
    while len(default_values) < argument_count:
        default_values.insert(0, None)
    result = ''
    for i, a in enumerate(function_def_node.args.args):
        if result:
            result += ', '
        if a.arg != 'self':
            if a.annotation and isinstance(a.annotation, ast.Name):
                result += _fix_function_argument_type(a.annotation.id, False) + ' '
            result += a.arg
            if default_values[i]:
                result += ' = '
                default_value = default_values[i]
                if isinstance(default_value, ast.Attribute):
                    result += format_reference(default_value)
                else:
                    result += format_literal(default_value)
    return result


def format_start_function_call(call_node):
    """Format a call of a free or member function"""
    return format_reference(call_node.func) + '('


def write_import(file, i_node):
    """Print an import of a Qt class as #include"""
    for alias in i_node.names:
        if alias.name.startswith('Q'):
            file.write(f'#include <{alias.name}>\n')


def write_import_from(file, i_node):
    """Print an import from Qt classes as #include sequence"""
    # "from PySide6.QtGui import QGuiApplication" or
    # "from PySide6 import QtGui"
    mod = i_node.module
    if not mod.startswith('PySide') and not mod.startswith('PyQt'):
        return
    dot = mod.find('.')
    qt_module = mod[dot + 1:] + '/' if dot >= 0 else ''
    for i in i_node.names:
        if i.name.startswith('Q'):
            file.write(f'#include <{qt_module}{i.name}>\n')


class Indenter:
    """Helper for Indentation"""

    def __init__(self, output_file):
        self._indent_level = 0
        self._indentation = ''
        self._output_file = output_file

    def indent_string(self, string):
        """Start a new line by a string"""
        self._output_file.write(self._indentation)
        self._output_file.write(string)

    def indent_line(self, line):
        """Write an indented line"""
        self._output_file.write(self._indentation)
        self._output_file.write(line)
        self._output_file.write('\n')

    def INDENT(self):
        """Write indentation"""
        self._output_file.write(self._indentation)

    def indent(self):
        """Increase indentation level"""
        self._indent_level = self._indent_level + 1
        self._indentation = '    ' * self._indent_level

    def dedent(self):
        """Decrease indentation level"""
        self._indent_level = self._indent_level - 1
        self._indentation = '    ' * self._indent_level


class CppFormatter(Indenter):
    """Provides helpers for formatting multi-line C++ constructs"""

    def __init__(self, output_file):
        Indenter.__init__(self, output_file)

    def write_class_def(self, class_node):
        """Print a class definition with inheritance"""
        self._output_file.write('\n')
        inherits = format_inheritance(class_node)
        self.indent_line(f'class {class_node.name}{inherits}')
        self.indent_line('{')
        self.indent_line('public:')

    def write_function_def(self, f_node, class_context):
        """Print a function definition with arguments"""
        self._output_file.write('\n')
        arguments = format_function_def_arguments(f_node)
        if f_node.name == '__init__' and class_context:  # Constructor
            name = class_context
        elif f_node.name == '__del__' and class_context:  # Destructor
            name = '~' + class_context
        else:
            return_type = "void"
            if f_node.returns and isinstance(f_node.returns, ast.Name):
                return_type = _fix_function_argument_type(f_node.returns.id, True)
            name = return_type + " " + f_node.name
        self.indent_string(f'{name}({arguments})')
        self._output_file.write('\n')
        self.indent_line('{')
