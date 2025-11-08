# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

"""Tool to dump a Python AST"""


import ast
import tokenize
from argparse import ArgumentParser, RawTextHelpFormatter
from enum import Enum

from nodedump import debug_format_node

DESCRIPTION = "Tool to dump a Python AST"


_source_lines = []
_opt_verbose = False


def first_non_space(s):
    for i, c in enumerate(s):
        if c != ' ':
            return i
    return 0


class NodeType(Enum):
    IGNORE = 1
    PRINT_ONE_LINE = 2  # Print as a one liner, do not visit children
    PRINT = 3  # Print with opening closing tag, visit children
    PRINT_WITH_SOURCE = 4   # Like PRINT, but print source line above


def get_node_type(node):
    if isinstance(node, (ast.Load, ast.Store, ast.Delete)):
        return NodeType.IGNORE
    if isinstance(node, (ast.Add, ast.alias, ast.arg, ast.Eq, ast.Gt, ast.Lt,
                         ast.Mult, ast.Name, ast.NotEq, ast.NameConstant, ast.Not,
                         ast.Num, ast.Str)):
        return NodeType.PRINT_ONE_LINE
    if not hasattr(node, 'lineno'):
        return NodeType.PRINT
    if isinstance(node, (ast.Attribute)):
        return NodeType.PRINT_ONE_LINE if isinstance(node.value, ast.Name) else NodeType.PRINT
    return NodeType.PRINT_WITH_SOURCE


class DumpVisitor(ast.NodeVisitor):
    def __init__(self):
        ast.NodeVisitor.__init__(self)
        self._indent = 0
        self._printed_source_lines = {-1}

    def generic_visit(self, node):
        node_type = get_node_type(node)
        if _opt_verbose and node_type in (NodeType.IGNORE, NodeType.PRINT_ONE_LINE):
            node_type = NodeType.PRINT
        if node_type == NodeType.IGNORE:
            return
        self._indent = self._indent + 1
        indent = '    ' * self._indent

        if node_type == NodeType.PRINT_WITH_SOURCE:
            line_number = node.lineno - 1
            if line_number not in self._printed_source_lines:
                self._printed_source_lines.add(line_number)
                line = _source_lines[line_number]
                non_space = first_non_space(line)
                print('{:04d} {}{}'.format(line_number, '_' * non_space,
                                           line[non_space:]))

        if node_type == NodeType.PRINT_ONE_LINE:
            print(indent, debug_format_node(node))
        else:
            print(indent, '>', debug_format_node(node))
            ast.NodeVisitor.generic_visit(self, node)
            print(indent, '<', type(node).__name__)

        self._indent = self._indent - 1


def parse_ast(filename):
    node = None
    with tokenize.open(filename) as f:
        global _source_lines
        source = f.read()
        _source_lines = source.split('\n')
        node = ast.parse(source, mode="exec")
    return node


def create_arg_parser(desc):
    parser = ArgumentParser(description=desc,
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose')
    parser.add_argument('source', type=str, help='Python source')
    return parser


if __name__ == '__main__':
    arg_parser = create_arg_parser(DESCRIPTION)
    options = arg_parser.parse_args()
    _opt_verbose = options.verbose
    title = f'AST tree for {options.source}'
    print('=' * len(title))
    print(title)
    print('=' * len(title))
    tree = parse_ast(options.source)
    DumpVisitor().visit(tree)
