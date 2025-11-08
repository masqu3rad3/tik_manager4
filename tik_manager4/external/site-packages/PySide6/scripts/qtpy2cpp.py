# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

import logging
import os
import sys
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path

from qtpy2cpp_lib.visitor import ConvertVisitor

DESCRIPTION = "Tool to convert Python to C++"


def create_arg_parser(desc):
    parser = ArgumentParser(description=desc,
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument("--debug", "-d", action="store_true",
                        help="Debug")
    parser.add_argument("--stdout", "-s", action="store_true",
                        help="Write to stdout")
    parser.add_argument("--force", "-f", action="store_true",
                        help="Force overwrite of existing files")
    parser.add_argument("files", type=str, nargs="+", help="Python source file(s)")
    return parser


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    arg_parser = create_arg_parser(DESCRIPTION)
    args = arg_parser.parse_args()
    ConvertVisitor.debug = args.debug

    for input_file_str in args.files:
        input_file = Path(input_file_str)
        if not input_file.is_file():
            logger.error(f"{input_file_str} does not exist or is not a file.")
            sys.exit(-1)
        file_root, ext = os.path.splitext(input_file)
        if input_file.suffix != ".py":
            logger.error(f"{input_file_str} does not appear to be a Python file.")
            sys.exit(-1)

        ast_tree = ConvertVisitor.create_ast(input_file_str)
        if args.stdout:
            sys.stdout.write(f"// Converted from {input_file.name}\n")
            ConvertVisitor(input_file, sys.stdout).visit(ast_tree)
        else:
            target_file = input_file.parent / (input_file.stem + ".cpp")
            if target_file.exists():
                if not target_file.is_file():
                    logger.error(f"{target_file} exists and is not a file.")
                    sys.exit(-1)
                if not args.force:
                    logger.error(f"{target_file} exists. Use -f to overwrite.")
                    sys.exit(-1)

            with target_file.open("w") as file:
                file.write(f"// Converted from {input_file.name}\n")
                ConvertVisitor(input_file, file).visit(ast_tree)
                logger.info(f"Wrote {target_file}.")
