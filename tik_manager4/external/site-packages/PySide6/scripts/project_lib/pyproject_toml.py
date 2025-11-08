# Copyright (C) 2025 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
from __future__ import annotations

import sys
# TODO: Remove this import when Python 3.11 is the minimum supported version
if sys.version_info >= (3, 11):
    import tomllib
from pathlib import Path

from . import PYPROJECT_JSON_PATTERN
from .pyproject_parse_result import PyProjectParseResult
from .pyproject_json import parse_pyproject_json


def _parse_toml_content(content: str) -> dict:
    """
    Parse TOML content for project name and files list only.
    """
    result = {"project": {}, "tool": {"pyside6-project": {}}}
    current_section = None

    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        if line == '[project]':
            current_section = 'project'
        elif line == '[tool.pyside6-project]':
            current_section = 'tool.pyside6-project'
        elif '=' in line and current_section:
            key, value = [part.strip() for part in line.split('=', 1)]

            # Handle string values - name of the project
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            # Handle array of strings - files names
            elif value.startswith('[') and value.endswith(']'):
                items = value[1:-1].split(',')
                value = [item.strip().strip('"') for item in items if item.strip()]

            if current_section == 'project':
                result['project'][key] = value
            else:  # tool.pyside6-project
                result['tool']['pyside6-project'][key] = value

    return result


def _write_toml_content(data: dict) -> str:
    """
    Write minimal TOML content with project and tool.pyside6-project sections.
    """
    lines = []

    if 'project' in data and data['project']:
        lines.append('[project]')
        for key, value in sorted(data['project'].items()):
            if isinstance(value, str):
                lines.append(f'{key} = "{value}"')

    if 'tool' in data and 'pyside6-project' in data['tool']:
        lines.append('\n[tool.pyside6-project]')
        for key, value in sorted(data['tool']['pyside6-project'].items()):
            if isinstance(value, list):
                items = [f'"{item}"' for item in sorted(value)]
                lines.append(f'{key} = [{", ".join(items)}]')
            else:
                lines.append(f'{key} = "{value}"')

    return '\n'.join(lines)


def parse_pyproject_toml(pyproject_toml_file: Path) -> PyProjectParseResult:
    """
    Parse a pyproject.toml file and return a PyProjectParseResult object.
    """
    result = PyProjectParseResult()

    try:
        content = pyproject_toml_file.read_text(encoding='utf-8')
        # TODO: Remove the manual parsing when Python 3.11 is the minimum supported version
        if sys.version_info >= (3, 11):
            root_table = tomllib.loads(content)  # Use tomllib for Python >= 3.11
            print("Using tomllib for parsing TOML content")
        else:
            root_table = _parse_toml_content(content)  # Fallback to manual parsing
    except Exception as e:
        result.errors.append(str(e))
        return result

    pyside_table = root_table.get("tool", {}).get("pyside6-project", {})
    if not pyside_table:
        result.errors.append("Missing [tool.pyside6-project] table")
        return result

    files = pyside_table.get("files", [])
    if not isinstance(files, list):
        result.errors.append("Missing or invalid files list")
        return result

    # Convert paths
    for file in files:
        if not isinstance(file, str):
            result.errors.append(f"Invalid file: {file}")
            return result
        file_path = Path(file)
        if not file_path.is_absolute():
            file_path = (pyproject_toml_file.parent / file).resolve()
        result.files.append(file_path)

    return result


def write_pyproject_toml(pyproject_file: Path, project_name: str, project_files: list[str]):
    """
    Create or update a pyproject.toml file with the specified content.
    """
    data = {
        "project": {"name": project_name},
        "tool": {
            "pyside6-project": {"files": sorted(project_files)}
        }
    }

    try:
        content = _write_toml_content(data)
        pyproject_file.write_text(content, encoding='utf-8')
    except Exception as e:
        raise ValueError(f"Error writing TOML file: {str(e)}")


def migrate_pyproject(pyproject_file: Path | str = None) -> int:
    """
    Migrate a project *.pyproject JSON file to the new pyproject.toml format.

    The containing subprojects are migrated recursively.

    :return: 0 if successful, 1 if an error occurred.
    """
    project_name = None

    # Transform the user input string into a Path object
    if isinstance(pyproject_file, str):
        pyproject_file = Path(pyproject_file)

    if pyproject_file:
        if not pyproject_file.match(PYPROJECT_JSON_PATTERN):
            print(f"Cannot migrate non \"{PYPROJECT_JSON_PATTERN}\" file:", file=sys.stderr)
            print(f"\"{pyproject_file}\"", file=sys.stderr)
            return 1
        project_files = [pyproject_file]
        project_name = pyproject_file.stem
    else:
        # Get the existing *.pyproject files in the current directory
        project_files = list(Path().glob(PYPROJECT_JSON_PATTERN))
        if not project_files:
            print(f"No project file found in the current directory: {Path()}", file=sys.stderr)
            return 1
        if len(project_files) > 1:
            print("Multiple pyproject files found in the project folder:")
            print('\n'.join(str(project_file) for project_file in project_files))
            response = input("Continue? y/n: ")
            if response.lower().strip() not in {"yes", "y"}:
                return 0
        else:
            # If there is only one *.pyproject file in the current directory,
            # use its file name as the project name
            project_name = project_files[0].stem

    # The project files that will be written to the pyproject.toml file
    output_files = set()
    for project_file in project_files:
        project_data = parse_pyproject_json(project_file)
        if project_data.errors:
            print(f"Invalid project file: {project_file}. Errors found:", file=sys.stderr)
            print('\n'.join(project_data.errors), file=sys.stderr)
            return 1
        output_files.update(project_data.files)

    project_folder = project_files[0].parent.resolve()
    if project_name is None:
        # If a project name has not resolved, use the name of the parent folder
        project_name = project_folder.name

    pyproject_toml_file = project_folder / "pyproject.toml"
    if pyproject_toml_file.exists():
        already_existing_file = True
        try:
            content = pyproject_toml_file.read_text(encoding='utf-8')
            data = _parse_toml_content(content)
        except Exception as e:
            raise ValueError(f"Error parsing TOML: {str(e)}")
    else:
        already_existing_file = False
        data = {"project": {}, "tool": {"pyside6-project": {}}}

    # Update project name if not present
    if "name" not in data["project"]:
        data["project"]["name"] = project_name

    # Update files list
    data["tool"]["pyside6-project"]["files"] = sorted(
        p.relative_to(project_folder).as_posix() for p in output_files
    )

    # Generate TOML content
    toml_content = _write_toml_content(data)

    if already_existing_file:
        print(f"WARNING: A pyproject.toml file already exists at \"{pyproject_toml_file}\"")
        print("The file will be updated with the following content:")
        print(toml_content)
        response = input("Proceed? [Y/n] ")
        if response.lower().strip() not in {"yes", "y"}:
            return 0

    try:
        pyproject_toml_file.write_text(toml_content)
    except Exception as e:
        print(f"Error writing to \"{pyproject_toml_file}\": {str(e)}", file=sys.stderr)
        return 1

    if not already_existing_file:
        print(f"Created \"{pyproject_toml_file}\"")
    else:
        print(f"Updated \"{pyproject_toml_file}\"")

    # Recursively migrate the subprojects
    for sub_project_file in filter(lambda f: f.match(PYPROJECT_JSON_PATTERN), output_files):
        result = migrate_pyproject(sub_project_file)
        if result != 0:
            return result
    return 0
