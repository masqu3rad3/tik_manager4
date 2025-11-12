# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

"""Tool to dump Python Tokens"""


import sys
import tokenize


def format_token(t):
    r = repr(t)
    if r.startswith('TokenInfo('):
        r = r[10:]
    pos = r.find("), line='")
    if pos < 0:
        pos = r.find('), line="')
    if pos > 0:
        r = r[:pos + 1]
    return r


def first_non_space(s):
    for i, c in enumerate(s):
        if c != ' ':
            return i
    return 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Specify file Name")
        sys.exit(1)
    filename = sys.argv[1]
    indent_level = 0
    indent = ''
    last_line_number = -1
    with tokenize.open(filename) as f:
        generator = tokenize.generate_tokens(f.readline)
        for t in generator:
            line_number = t.start[0]
            if line_number != last_line_number:
                code_line = t.line.rstrip()
                non_space = first_non_space(code_line)
                print('{:04d} {}{}'.format(line_number, '_' * non_space,
                                           code_line[non_space:]))
                last_line_number = line_number
            if t.type == tokenize.INDENT:
                indent_level = indent_level + 1
                indent = '    ' * indent_level
            elif t.type == tokenize.DEDENT:
                indent_level = indent_level - 1
                indent = '    ' * indent_level
            else:
                print('       ', indent, format_token(t))
