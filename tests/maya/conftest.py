"""Pytest configuration for Maya tests."""

import os
import shutil
from pathlib import Path
import pytest

# IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"

@pytest.fixture(scope='session', autouse=True)
def initialize():
    """Initialize Maya standalone session before running tests."""
    import maya.standalone
    try:
        maya.standalone.initialize()
    except RuntimeError:
        # Maya is already initialized
        pass
    yield
    maya.standalone.uninitialize()

# Override the default tik_manager4 initialization for Maya


@pytest.fixture(scope='function')
def tik(tmp_path):
    """Initialize tik_manager4 for testing."""
    print("\n")
    print("----------------------------")
    print("Preparing Mockup Common and User Folders...")
    print("----------------------------")
    mockup_commons_path = Path(tmp_path / "mockup_common")
    mockup_commons_path.mkdir(parents=True, exist_ok=True)
    # user_home = Path(utils.get_home_dir())
    user_path = Path().home() / "TikManager4"
    user_path.mkdir(parents=True, exist_ok=True)
    # backup the user to the tmp_path
    shutil.copytree(str(user_path), str(tmp_path / "user_backup"))
    # clear the user folder
    shutil.rmtree(str(user_path))
    user_path.mkdir(parents=True, exist_ok=True)
    import tik_manager4
    yield tik_manager4.initialize("Maya", common_folder=str(mockup_commons_path))
    # restore the original user directory
    shutil.rmtree(str(user_path))
    shutil.copytree(str(tmp_path / "user_backup"), str(user_path))


# @pytest.fixture(autouse=True)
# def skip_github():
#     if IN_GITHUB_ACTIONS:
#         pytest.skip('Skipping Maya tests in GitHub Actions.')