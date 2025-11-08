# Copyright (C) 2025 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only
import json
from pathlib import Path

from .pyproject_parse_result import PyProjectParseResult


def write_pyproject_json(pyproject_file: Path, project_files: list[str]):
    """
    Create or update a *.pyproject file with the specified content.

    :param pyproject_file: The *.pyproject file path to create or update.
    :param project_files: The relative paths of the files to include in the project.
    """
    # The content of the file is fully replaced, so it is not necessary to read and merge any
    # existing content
    content = {
        "files": sorted(project_files),
    }
    pyproject_file.write_text(json.dumps(content), encoding="utf-8")


def parse_pyproject_json(pyproject_json_file: Path) -> PyProjectParseResult:
    """
    Parse a pyproject.json file and return a PyProjectParseResult object.
    """
    result = PyProjectParseResult()
    try:
        with pyproject_json_file.open("r") as pyf:
            project_file_data = json.load(pyf)
    except json.JSONDecodeError as e:
        result.errors.append(str(e))
        return result
    except Exception as e:
        result.errors.append(str(e))
        return result

    if not isinstance(project_file_data, dict):
        result.errors.append("The root element of pyproject.json must be a JSON object")
        return result

    found_files = project_file_data.get("files")
    if found_files and not isinstance(found_files, list):
        result.errors.append("The files element must be a list")
        return result

    for file in project_file_data.get("files", []):
        if not isinstance(file, str):
            result.errors.append(f"Invalid file: {file}")
            return result

        file_path = Path(file)
        if not file_path.is_absolute():
            file_path = (pyproject_json_file.parent / file).resolve()
        result.files.append(file_path)

    return result
