# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

import ast
import json
import os
import sys
import tokenize
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
from typing import Union


DESCRIPTION = """Parses Python source code to create QObject metatype
information in JSON format for qmltyperegistrar."""


REVISION = 68


CPP_TYPE_MAPPING = {"str": "QString"}


QML_IMPORT_NAME = "QML_IMPORT_NAME"
QML_IMPORT_MAJOR_VERSION = "QML_IMPORT_MAJOR_VERSION"
QML_IMPORT_MINOR_VERSION = "QML_IMPORT_MINOR_VERSION"
QT_MODULES = "QT_MODULES"


ITEM_MODELS = ["QAbstractListModel", "QAbstractProxyModel",
               "QAbstractTableModel", "QConcatenateTablesProxyModel",
               "QFileSystemModel", "QIdentityProxyModel", "QPdfBookmarkModel",
               "QPdfSearchModel", "QSortFilterProxyModel", "QSqlQueryModel",
               "QStandardItemModel", "QStringListModel", "QTransposeProxyModel",
               "QWebEngineHistoryModel"]


QOBJECT_DERIVED = ["QObject", "QQuickItem", "QQuickPaintedItem"] + ITEM_MODELS


# Python 3.9 does not support this syntax, yet
# AstDecorator = ast.Name | ast.Call
# AstPySideTypeSpec = ast.Name | ast.Constant
AstDecorator = Union[ast.Name, ast.Call]
AstPySideTypeSpec = Union[ast.Name, ast.Constant]


ClassList = list[dict]


# PropertyEntry = dict[str, str | int | bool]
PropertyEntry = dict[str, Union[str, int, bool]]

Argument = dict[str, str]
Arguments = list[Argument]
# Signal = dict[str, str | Arguments]
# Slot = dict[str, str | Arguments]
Signal = dict[str, Union[str, Arguments]]
Slot = dict[str, Union[str, Arguments]]


def _decorator(name: str, value: str) -> dict[str, str]:
    """Create a QML decorator JSON entry"""
    return {"name": name, "value": value}


def _attribute(node: ast.Attribute) -> tuple[str, str]:
    """Split an attribute."""
    return node.value.id, node.attr


def _name(node: ast.Name | ast.Attribute | ast.Constant) -> str:
    """Return the name of something that is either an attribute or a name,
       such as base classes or call.func"""
    if isinstance(node, ast.Constant):
        return str(node.value)
    if isinstance(node, ast.Attribute):
        qualifier, name = _attribute(node)
        return f"{qualifier}.{node.attr}"
    return node.id


def _func_name(node: ast.Call) -> str:
    return _name(node.func)


def _python_to_cpp_type(type: str) -> str:
    """Python to C++ type"""
    c = CPP_TYPE_MAPPING.get(type)
    return c if c else type


def _parse_property_kwargs(keywords: list[ast.keyword], prop: PropertyEntry):
    """Parse keyword arguments of @Property"""
    for k in keywords:
        if k.arg == "notify":
            prop["notify"] = _name(k.value)


def _parse_assignment(node: ast.Assign) -> tuple[str | None, ast.AST | None]:
    """Parse an assignment and return a tuple of name, value."""
    if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        var_name = node.targets[0].id
        return (var_name, node.value)
    return (None, None)


def _parse_pyside_type(type_spec: AstPySideTypeSpec) -> str:
    """Parse type specification of a Slot/Property decorator. Usually a type,
       but can also be a string constant with a C++ type name."""
    if isinstance(type_spec, ast.Constant):
        return type_spec.value
    return _python_to_cpp_type(_name(type_spec))


def _parse_call_args(call: ast.Call):
    """Parse arguments of a Signal call/Slot decorator (type list)."""
    result: Arguments = []
    for n, arg in enumerate(call.args):
        par_name = f"a{n + 1}"
        par_type = _parse_pyside_type(arg)
        result.append({"name": par_name, "type": par_type})
    return result


def _parse_slot(func_name: str, call: ast.Call) -> Slot:
    """Parse a 'Slot' decorator."""
    return_type = "void"
    for kwarg in call.keywords:
        if kwarg.arg == "result":
            return_type = _python_to_cpp_type(_name(kwarg.value))
            break
    return {"access": "public", "name": func_name,
            "arguments": _parse_call_args(call),
            "returnType": return_type}


class VisitorContext:
    """Stores a list of QObject-derived classes encountered in order to find
       out which classes inherit QObject."""

    def __init__(self):
        self.qobject_derived = QOBJECT_DERIVED


class MetaObjectDumpVisitor(ast.NodeVisitor):
    """AST visitor for parsing sources and creating the data structure for
       JSON."""

    def __init__(self, context: VisitorContext):
        super().__init__()
        self._context = context
        self._json_class_list: ClassList = []
        # Property by name, which will be turned into the JSON List later
        self._properties: list[PropertyEntry] = []
        self._signals: list[Signal] = []
        self._within_class: bool = False
        self._qt_modules: set[str] = set()
        self._qml_import_name = ""
        self._qml_import_major_version = 0
        self._qml_import_minor_version = 0

    def json_class_list(self) -> ClassList:
        return self._json_class_list

    def qml_import_name(self) -> str:
        return self._qml_import_name

    def qml_import_version(self) -> tuple[int, int]:
        return (self._qml_import_major_version, self._qml_import_minor_version)

    def qt_modules(self):
        return sorted(self._qt_modules)

    @staticmethod
    def create_ast(filename: Path) -> ast.Module:
        """Create an Abstract Syntax Tree on which a visitor can be run"""
        node = None
        with tokenize.open(filename) as file:
            node = ast.parse(file.read(), mode="exec")
        return node

    def visit_Assign(self, node: ast.Assign):
        """Parse the global constants for QML-relevant values"""
        var_name, value_node = _parse_assignment(node)
        if not var_name or not isinstance(value_node, ast.Constant):
            return
        value = value_node.value
        if var_name == QML_IMPORT_NAME:
            self._qml_import_name = value
        elif var_name == QML_IMPORT_MAJOR_VERSION:
            self._qml_import_major_version = value
        elif var_name == QML_IMPORT_MINOR_VERSION:
            self._qml_import_minor_version = value

    def visit_ClassDef(self, node: ast.Module):
        """Visit a class definition"""
        self._properties = []
        self._signals = []
        self._slots = []
        self._within_class = True
        qualified_name = node.name
        last_dot = qualified_name.rfind('.')
        name = (qualified_name[last_dot + 1:] if last_dot != -1
                else qualified_name)

        data = {"className": name,
                "qualifiedClassName": qualified_name}

        q_object = False
        bases = []
        for b in node.bases:
            # PYSIDE-2202: catch weird constructs like "class C(type(Base)):"
            if isinstance(b, ast.Name):
                base_name = _name(b)
                if base_name in self._context.qobject_derived:
                    q_object = True
                    self._context.qobject_derived.append(name)
                base_dict = {"access": "public", "name": base_name}
                bases.append(base_dict)

        data["object"] = q_object
        if bases:
            data["superClasses"] = bases

        class_decorators: list[dict] = []
        for d in node.decorator_list:
            self._parse_class_decorator(d, class_decorators)

        if class_decorators:
            data["classInfos"] = class_decorators

        for b in node.body:
            if isinstance(b, ast.Assign):
                self._parse_class_variable(b)
            else:
                self.visit(b)

        if self._properties:
            data["properties"] = self._properties

        if self._signals:
            data["signals"] = self._signals

        if self._slots:
            data["slots"] = self._slots

        self._json_class_list.append(data)

        self._within_class = False

    def visit_FunctionDef(self, node):
        if self._within_class:
            for d in node.decorator_list:
                self._parse_function_decorator(node.name, d)

    def _parse_class_decorator(self, node: AstDecorator,
                               class_decorators: list[dict]):
        """Parse ClassInfo decorators."""
        if isinstance(node, ast.Call):
            name = _func_name(node)
            if name == "QmlUncreatable":
                class_decorators.append(_decorator("QML.Creatable", "false"))
                if node.args:
                    reason = node.args[0].value
                    if isinstance(reason, str):
                        d = _decorator("QML.UncreatableReason", reason)
                        class_decorators.append(d)
            elif name == "QmlAttached" and len(node.args) == 1:
                d = _decorator("QML.Attached", node.args[0].id)
                class_decorators.append(d)
            elif name == "QmlExtended" and len(node.args) == 1:
                d = _decorator("QML.Extended", node.args[0].id)
                class_decorators.append(d)
            elif name == "ClassInfo" and node.keywords:
                kw = node.keywords[0]
                class_decorators.append(_decorator(kw.arg, kw.value.value))
            elif name == "QmlForeign" and len(node.args) == 1:
                d = _decorator("QML.Foreign", node.args[0].id)
                class_decorators.append(d)
            elif name == "QmlNamedElement" and node.args:
                name = node.args[0].value
                class_decorators.append(_decorator("QML.Element", name))
            elif name.startswith('Q'):
                print('Unknown decorator with parameters:', name,
                      file=sys.stderr)
            return

        if isinstance(node, ast.Name):
            name = node.id
            if name == "QmlElement":
                class_decorators.append(_decorator("QML.Element", "auto"))
            elif name == "QmlSingleton":
                class_decorators.append(_decorator("QML.Singleton", "true"))
            elif name == "QmlAnonymous":
                class_decorators.append(_decorator("QML.Element", "anonymous"))
            elif name.startswith('Q'):
                print('Unknown decorator:', name, file=sys.stderr)
            return

    def _index_of_property(self, name: str) -> int:
        """Search a property by name"""
        for i in range(len(self._properties)):
            if self._properties[i]["name"] == name:
                return i
        return -1

    def _create_property_entry(self, name: str, type: str,
                               getter: str | None = None) -> PropertyEntry:
        """Create a property JSON entry."""
        result: PropertyEntry = {"name": name, "type": type,
                                 "index": len(self._properties)}
        if getter:
            result["read"] = getter
        return result

    def _parse_function_decorator(self, func_name: str, node: AstDecorator):
        """Parse function decorators."""
        if isinstance(node, ast.Attribute):
            name = node.value.id
            value = node.attr
            if value == "setter":  # Property setter
                idx = self._index_of_property(name)
                if idx != -1:
                    self._properties[idx]["write"] = func_name
            return

        if isinstance(node, ast.Call):
            name = _name(node.func)
            if name == "Property":  # Property getter
                if node.args:  # 1st is type/type string
                    type = _parse_pyside_type(node.args[0])
                    prop = self._create_property_entry(func_name, type,
                                                       func_name)
                    _parse_property_kwargs(node.keywords, prop)
                    self._properties.append(prop)
            elif name == "Slot":
                self._slots.append(_parse_slot(func_name, node))
            else:
                print('Unknown decorator with parameters:', name,
                      file=sys.stderr)

    def _parse_class_variable(self, node: ast.Assign):
        """Parse a class variable assignment (Property, Signal, etc.)"""
        (var_name, call) = _parse_assignment(node)
        if not var_name or not isinstance(node.value, ast.Call):
            return
        func_name = _func_name(call)
        if func_name == "Signal" or func_name == "QtCore.Signal":
            signal: Signal = {"access": "public", "name": var_name,
                              "arguments": _parse_call_args(call),
                              "returnType": "void"}
            self._signals.append(signal)
        elif func_name == "Property" or func_name == "QtCore.Property":
            type = _python_to_cpp_type(call.args[0].id)
            prop = self._create_property_entry(var_name, type, call.args[1].id)
            if len(call.args) > 2:
                prop["write"] = call.args[2].id
            _parse_property_kwargs(call.keywords, prop)
            self._properties.append(prop)
        elif func_name == "ListProperty" or func_name == "QtCore.ListProperty":
            type = _python_to_cpp_type(call.args[0].id)
            type = f"QQmlListProperty<{type}>"
            prop = self._create_property_entry(var_name, type)
            self._properties.append(prop)

    def visit_Import(self, node):
        for n in node.names:  # "import PySide6.QtWidgets"
            self._handle_import(n.name)

    def visit_ImportFrom(self, node):
        if "." in node.module:  # "from PySide6.QtWidgets import QWidget"
            self._handle_import(node.module)
        elif node.module == "PySide6":  # "from PySide6 import QtWidgets"
            for n in node.names:
                if n.name.startswith("Qt"):
                    self._qt_modules.add(n.name)

    def _handle_import(self, mod: str):
        if mod.startswith("PySide6."):
            self._qt_modules.add(mod[8:])


def create_arg_parser(desc: str) -> ArgumentParser:
    parser = ArgumentParser(description=desc,
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument('--compact', '-c', action='store_true',
                        help='Use compact format')
    parser.add_argument('--suppress-file', '-s', action='store_true',
                        help='Suppress inputFile entry (for testing)')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Suppress warnings')
    parser.add_argument('files', type=str, nargs="+",
                        help='Python source file')
    parser.add_argument('--out-file', '-o', type=str,
                        help='Write output to file rather than stdout')
    return parser


def parse_file(file: Path, context: VisitorContext,
               suppress_file: bool = False) -> dict | None:
    """Parse a file and return its json data"""
    ast_tree = MetaObjectDumpVisitor.create_ast(file)
    visitor = MetaObjectDumpVisitor(context)
    visitor.visit(ast_tree)

    class_list = visitor.json_class_list()
    if not class_list:
        return None
    result = {"classes": class_list,
              "outputRevision": REVISION}

    # Non-standard QML-related values for pyside6-build usage
    if visitor.qml_import_name():
        result[QML_IMPORT_NAME] = visitor.qml_import_name()
    qml_import_version = visitor.qml_import_version()
    if qml_import_version[0]:
        result[QML_IMPORT_MAJOR_VERSION] = qml_import_version[0]
        result[QML_IMPORT_MINOR_VERSION] = qml_import_version[1]

    qt_modules = visitor.qt_modules()
    if qt_modules:
        result[QT_MODULES] = qt_modules

    if not suppress_file:
        result["inputFile"] = os.fspath(file).replace("\\", "/")
    return result


if __name__ == '__main__':
    arg_parser = create_arg_parser(DESCRIPTION)
    args = arg_parser.parse_args()

    context = VisitorContext()
    json_list = []

    for file_name in args.files:
        file = Path(file_name).resolve()
        if not file.is_file():
            print(f'{file_name} does not exist or is not a file.',
                  file=sys.stderr)
            sys.exit(-1)

        try:
            json_data = parse_file(file, context, args.suppress_file)
            if json_data:
                json_list.append(json_data)
            elif not args.quiet:
                print(f"No classes found in {file_name}", file=sys.stderr)
        except (AttributeError, SyntaxError) as e:
            reason = str(e)
            print(f"Error parsing {file_name}: {reason}", file=sys.stderr)
            raise

    indent = None if args.compact else 4
    if args.out_file:
        with open(args.out_file, 'w') as f:
            json.dump(json_list, f, indent=indent)
    else:
        json.dump(json_list, sys.stdout, indent=indent)
