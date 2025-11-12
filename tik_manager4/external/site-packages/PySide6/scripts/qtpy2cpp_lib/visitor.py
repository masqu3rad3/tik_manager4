# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

"""AST visitor printing out C++"""

import ast
import sys
import tokenize
import warnings

from .formatter import (CppFormatter, format_for_loop, format_literal,
                        format_name_constant,
                        format_reference, write_import, write_import_from)
from .nodedump import debug_format_node
from .qt import ClassFlag, qt_class_flags


def _is_qt_constructor(assign_node):
    """Is this assignment node a plain construction of a Qt class?
       'f = QFile(name)'. Returns the class_name."""
    call = assign_node.value
    if (isinstance(call, ast.Call) and isinstance(call.func, ast.Name)):
        func = call.func.id
        if func.startswith("Q"):
            return func
    return None


def _is_if_main(if_node):
    """Return whether an if statement is: if __name__ == '__main__' """
    test = if_node.test
    return (isinstance(test, ast.Compare)
            and len(test.ops) == 1
            and isinstance(test.ops[0], ast.Eq)
            and isinstance(test.left, ast.Name)
            and test.left.id == "__name__"
            and len(test.comparators) == 1
            and isinstance(test.comparators[0], ast.Constant)
            and test.comparators[0].value == "__main__")


class ConvertVisitor(ast.NodeVisitor, CppFormatter):
    """AST visitor printing out C++
    Note on implementation:
    - Any visit_XXX() overridden function should call self.generic_visit(node)
      to continue visiting
    - When controlling the visiting manually (cf visit_Call()),
      self.visit(child) needs to be called since that dispatches to
      visit_XXX(). This is usually done to prevent undesired output
      for example from references of calls, etc.
    """

    debug = False

    def __init__(self, file_name, output_file):
        ast.NodeVisitor.__init__(self)
        CppFormatter.__init__(self, output_file)
        self._file_name = file_name
        self._class_scope = []  # List of class names
        self._stack = []  # nodes
        self._stack_variables = []  # variables instantiated on stack
        self._debug_indent = 0

    @staticmethod
    def create_ast(filename):
        """Create an Abstract Syntax Tree on which a visitor can be run"""
        node = None
        with tokenize.open(filename) as file:
            node = ast.parse(file.read(), mode="exec")
        return node

    def generic_visit(self, node):
        parent = self._stack[-1] if self._stack else None
        if self.debug:
            self._debug_enter(node, parent)
        self._stack.append(node)
        try:
            super().generic_visit(node)
        except Exception as e:
            line_no = node.lineno if hasattr(node, 'lineno') else -1
            error_message = str(e)
            message = f'{self._file_name}:{line_no}: Error "{error_message}"'
            warnings.warn(message)
            self._output_file.write(f'\n// {error_message}\n')
        del self._stack[-1]
        if self.debug:
            self._debug_leave(node)

    def visit_Add(self, node):
        self._handle_bin_op(node, "+")

    def _is_augmented_assign(self):
        """Is it 'Augmented_assign' (operators +=/-=, etc)?"""
        return self._stack and isinstance(self._stack[-1], ast.AugAssign)

    def visit_AugAssign(self, node):
        """'Augmented_assign', Operators +=/-=, etc."""
        self.INDENT()
        self.generic_visit(node)
        self._output_file.write("\n")

    def visit_Assign(self, node):
        self.INDENT()

        qt_class = _is_qt_constructor(node)
        on_stack = qt_class and qt_class_flags(qt_class) & ClassFlag.INSTANTIATE_ON_STACK

        # Is this a free variable and not a member assignment? Instantiate
        # on stack or give a type
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if qt_class:
                if on_stack:
                    # "QFile f(args)"
                    var = node.targets[0].id
                    self._stack_variables.append(var)
                    self._output_file.write(f"{qt_class} {var}(")
                    self._write_function_args(node.value.args)
                    self._output_file.write(");\n")
                    return
                self._output_file.write("auto *")

        line_no = node.lineno if hasattr(node, 'lineno') else -1
        for target in node.targets:
            if isinstance(target, ast.Tuple):
                w = f"{self._file_name}:{line_no}: List assignment not handled."
                warnings.warn(w)
            elif isinstance(target, ast.Subscript):
                w = f"{self._file_name}:{line_no}: Subscript assignment not handled."
                warnings.warn(w)
            else:
                self._output_file.write(format_reference(target))
                self._output_file.write(' = ')
        if qt_class and not on_stack:
            self._output_file.write("new ")
        self.visit(node.value)
        self._output_file.write(';\n')

    def visit_Attribute(self, node):
        """Format a variable reference (cf visit_Name)"""
        # Default parameter (like Qt::black)?
        if self._ignore_function_def_node(node):
            return
        self._output_file.write(format_reference(node))

    def visit_BinOp(self, node):
        # Parentheses are not exposed, so, every binary operation needs to
        # be enclosed by ().
        self._output_file.write('(')
        self.generic_visit(node)
        self._output_file.write(')')

    def _handle_bin_op(self, node, op):
        """Handle a binary operator which can appear as 'Augmented Assign'."""
        self.generic_visit(node)
        full_op = f" {op}= " if self._is_augmented_assign() else f" {op} "
        self._output_file.write(full_op)

    def visit_BitAnd(self, node):
        self._handle_bin_op(node, "&")

    def visit_BitOr(self, node):
        self._handle_bin_op(node, "|")

    def _format_call(self, node):
        # Decorator list?
        if self._ignore_function_def_node(node):
            return
        f = node.func
        if isinstance(f, ast.Name):
            self._output_file.write(f.id)
        else:
            # Attributes denoting chained calls "a->b()->c()".  Walk along in
            # reverse order, recursing for other calls.
            names = []
            n = f
            while isinstance(n, ast.Attribute):
                names.insert(0, n.attr)
                n = n.value

            if isinstance(n, ast.Name):  # Member or variable reference
                if n.id != "self":
                    sep = "->"
                    if n.id in self._stack_variables:
                        sep = "."
                    elif n.id[0:1].isupper():  # Heuristics for static
                        sep = "::"
                    self._output_file.write(n.id)
                    self._output_file.write(sep)
            elif isinstance(n, ast.Call):  # A preceding call
                self._format_call(n)
                self._output_file.write("->")

            self._output_file.write("->".join(names))

        self._output_file.write('(')
        self._write_function_args(node.args)
        self._output_file.write(')')

    def visit_Call(self, node):
        self._format_call(node)
        # Context manager expression?
        if self._within_context_manager():
            self._output_file.write(";\n")

    def _write_function_args(self, args_node):
        # Manually do visit(), skip the children of func
        for i, arg in enumerate(args_node):
            if i > 0:
                self._output_file.write(', ')
            self.visit(arg)

    def visit_ClassDef(self, node):
        # Manually do visit() to skip over base classes
        # and annotations
        self._class_scope.append(node.name)
        self.write_class_def(node)
        self.indent()
        for b in node.body:
            self.visit(b)
        self.dedent()
        self.indent_line('};')
        del self._class_scope[-1]

    def visit_Div(self, node):
        self._handle_bin_op(node, "/")

    def visit_Eq(self, node):
        self.generic_visit(node)
        self._output_file.write(" == ")

    def visit_Expr(self, node):
        self.INDENT()
        self.generic_visit(node)
        self._output_file.write(';\n')

    def visit_Gt(self, node):
        self.generic_visit(node)
        self._output_file.write(" > ")

    def visit_GtE(self, node):
        self.generic_visit(node)
        self._output_file.write(" >= ")

    def visit_For(self, node):
        # Manually do visit() to get the indentation right.
        # TODO: what about orelse?
        self.indent_line(format_for_loop(node))
        self.indent()
        for b in node.body:
            self.visit(b)
        self.dedent()
        self.indent_line('}')

    def visit_FunctionDef(self, node):
        class_context = self._class_scope[-1] if self._class_scope else None
        for decorator in node.decorator_list:
            func = decorator.func  # (Call)
            if isinstance(func, ast.Name) and func.id == "Slot":
                self._output_file.write("\npublic slots:")
        self.write_function_def(node, class_context)
        # Find stack variables
        for arg in node.args.args:
            if arg.annotation and isinstance(arg.annotation, ast.Name):
                type_name = arg.annotation.id
                flags = qt_class_flags(type_name)
                if flags & ClassFlag.PASS_ON_STACK_MASK:
                    self._stack_variables.append(arg.arg)
        self.indent()
        self.generic_visit(node)
        self.dedent()
        self.indent_line('}')
        self._stack_variables.clear()

    def visit_If(self, node):
        # Manually do visit() to get the indentation right. Note:
        # elsif() is modelled as nested if.

        # Check for the main function
        if _is_if_main(node):
            self._output_file.write("\nint main(int argc, char *argv[])\n{\n")
            self.indent()
            for b in node.body:
                self.visit(b)
            self.indent_string("return 0;\n")
            self.dedent()
            self._output_file.write("}\n")
            return

        self.indent_string('if (')
        self.visit(node.test)
        self._output_file.write(') {\n')
        self.indent()
        for b in node.body:
            self.visit(b)
        self.dedent()
        self.indent_string('}')
        if node.orelse:
            self._output_file.write(' else {\n')
            self.indent()
            for b in node.orelse:
                self.visit(b)
            self.dedent()
            self.indent_string('}')
        self._output_file.write('\n')

    def visit_Import(self, node):
        write_import(self._output_file, node)

    def visit_ImportFrom(self, node):
        write_import_from(self._output_file, node)

    def visit_List(self, node):
        # Manually do visit() to get separators right
        self._output_file.write('{')
        for i, el in enumerate(node.elts):
            if i > 0:
                self._output_file.write(', ')
            self.visit(el)
        self._output_file.write('}')

    def visit_LShift(self, node):
        self.generic_visit(node)
        self._output_file.write(" << ")

    def visit_Lt(self, node):
        self.generic_visit(node)
        self._output_file.write(" < ")

    def visit_LtE(self, node):
        self.generic_visit(node)
        self._output_file.write(" <= ")

    def visit_Mult(self, node):
        self._handle_bin_op(node, "*")

    def _within_context_manager(self):
        """Return whether we are within a context manager (with)."""
        parent = self._stack[-1] if self._stack else None
        return parent and isinstance(parent, ast.withitem)

    def _ignore_function_def_node(self, node):
        """Should this node be ignored within a FunctionDef."""
        if not self._stack:
            return False
        parent = self._stack[-1]
        # A type annotation or default value of an argument?
        if isinstance(parent, (ast.arguments, ast.arg)):
            return True
        if not isinstance(parent, ast.FunctionDef):
            return False
        # Return type annotation or decorator call
        return node == parent.returns or node in parent.decorator_list

    def visit_Index(self, node):
        self._output_file.write("[")
        self.generic_visit(node)
        self._output_file.write("]")

    def visit_Name(self, node):
        """Format a variable reference (cf visit_Attribute)"""
        # Skip Context manager variables, return or argument type annotation
        if self._within_context_manager() or self._ignore_function_def_node(node):
            return
        self._output_file.write(format_reference(node))

    def visit_NameConstant(self, node):
        # Default parameter?
        if self._ignore_function_def_node(node):
            return
        self.generic_visit(node)
        self._output_file.write(format_name_constant(node))

    def visit_Not(self, node):
        self.generic_visit(node)
        self._output_file.write("!")

    def visit_NotEq(self, node):
        self.generic_visit(node)
        self._output_file.write(" != ")

    def visit_Num(self, node):
        self.generic_visit(node)
        self._output_file.write(format_literal(node))

    def visit_RShift(self, node):
        self.generic_visit(node)
        self._output_file.write(" >> ")

    def visit_Return(self, node):
        self.indent_string("return")
        if node.value:
            self._output_file.write(" ")
            self.generic_visit(node)
        self._output_file.write(";\n")

    def visit_Slice(self, node):
        self._output_file.write("[")
        if node.lower:
            self.visit(node.lower)
        self._output_file.write(":")
        if node.upper:
            self.visit(node.upper)
        self._output_file.write("]")

    def visit_Str(self, node):
        self.generic_visit(node)
        self._output_file.write(format_literal(node))

    def visit_Sub(self, node):
        self._handle_bin_op(node, "-")

    def visit_UnOp(self, node):
        self.generic_visit(node)

    def visit_With(self, node):
        self.INDENT()
        self._output_file.write("{ // Converted from context manager\n")
        self.indent()
        for item in node.items:
            self.INDENT()
            if item.optional_vars:
                self._output_file.write(format_reference(item.optional_vars))
                self._output_file.write(" = ")
        self.generic_visit(node)
        self.dedent()
        self.INDENT()
        self._output_file.write("}\n")

    def _debug_enter(self, node, parent=None):
        message = '{}>generic_visit({})'.format('  ' * self ._debug_indent,
                                                debug_format_node(node))
        if parent:
            message += ', parent={}'.format(debug_format_node(parent))
        message += '\n'
        sys.stderr.write(message)
        self._debug_indent += 1

    def _debug_leave(self, node):
        self._debug_indent -= 1
        message = '{}<generic_visit({})\n'.format('  ' * self ._debug_indent,
                                                  type(node).__name__)
        sys.stderr.write(message)
