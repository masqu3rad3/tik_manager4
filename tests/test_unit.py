import pytest
from pathlib import Path
import platform
import os
import subprocess

# ENTITY LEVEL


@pytest.mark.parametrize(
    "is_file, system, expected_cmd",
    [
        (True, "Windows", None),  # Windows, path is a file
        (False, "Windows", None),  # Windows, path is a directory
        (True, "Linux", ["xdg-open", "sample"]),  # Linux, path is a file
        (False, "Linux", ["xdg-open", "sample"]),  # Linux, path is a directory
        (True, "Darwin", ["open", "sample"]),  # macOS, path is a file
        (False, "Darwin", ["open", "sample"]),  # macOS, path is a directory
    ],
)
def test_opening_a_folder(tik, is_file, system, expected_cmd, monkeypatch):
    """Tests opening a folder."""
    tik.project.__init__()
    tik.user.__init__()

    target = "sample" if not is_file else "sample.txt"

    # Monkeypatching Path.is_file to return is_file
    monkeypatch.setattr(Path, "is_file", lambda x: is_file)

    # Monkeypatching platform.system to return the specific OS
    monkeypatch.setattr(platform, "system", lambda: system)

    # Tracking calls to os.startfile and subprocess.Popen
    startfile_called = []
    popen_called = []

    def mock_startfile(target):
        startfile_called.append(target)

    def mock_popen(cmd):
        popen_called.append(cmd)

    monkeypatch.setattr(os, "startfile", mock_startfile)
    monkeypatch.setattr(subprocess, "Popen", mock_popen)

    tik.project._open_folder(target)

    if system == "Windows":
        assert startfile_called == ["sample"]
        assert popen_called == []
    else:
        assert startfile_called == []
        assert popen_called == [expected_cmd]
