"""Configuration for pytest."""

import shutil
from pathlib import Path
import pytest
from tik_manager4.core import utils
import tik_manager4

@pytest.fixture(scope='function')
def tik(tmp_path):
    """Initialize tik_manager4 for testing."""
    print("\n")
    print("----------------------------")
    print("Preparing Mockup Common and User Folders...")
    print("----------------------------")
    mockup_commons_path = Path(tmp_path / "mockup_common")
    mockup_commons_path.mkdir(parents=True, exist_ok=True)
    user_home = Path(utils.get_home_dir())
    user_path = user_home / "TikManager4"
    user_path.mkdir(parents=True, exist_ok=True)
    # backup the user to the tmp_path
    shutil.copytree(str(user_path), str(tmp_path / "user_backup"))
    # clear the user folder
    shutil.rmtree(str(user_path))
    user_path.mkdir(parents=True, exist_ok=True)

    yield tik_manager4.initialize("Standalone", common_folder=str(mockup_commons_path))
    # restore the original user directory
    shutil.rmtree(str(user_path))
    shutil.copytree(str(tmp_path / "user_backup"), str(user_path))
