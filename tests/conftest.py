"""Configuration for pytest."""
import os
import stat
import shutil
from pathlib import Path
import pytest

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
    # user_path = user_home / "TikManager4"
    user_path.mkdir(parents=True, exist_ok=True)
    # backup the user to the tmp_path
    shutil.copytree(str(user_path), str(tmp_path / "user_backup"))
    # clear the user folder
    shutil.rmtree(str(user_path))
    user_path.mkdir(parents=True, exist_ok=True)
    import tik_manager4
    yield tik_manager4.initialize("Standalone", common_folder=str(mockup_commons_path))
    # restore the original user directory
    shutil.rmtree(str(user_path))
    shutil.copytree(str(tmp_path / "user_backup"), str(user_path))


@pytest.fixture(scope='session', autouse=True)
def files():
    """Fixture to handle files."""
    return Files()


class Files:
    def _onerror_handler(self, func, path, exc_info):
        """
        Error handler for shutil.rmtree to handle read-only files.
        """

        # If the error is due to a permission error and the file is read-only
        if issubclass(exc_info[0], PermissionError):
            os.chmod(path, stat.S_IWRITE)  # Give write permission
            func(path)  # Retry the original function
        else:
            raise  # Re-raise the original exception if it's not a permission error

    def force_remove_directory(self, directory_path):
        """
        Forcefully remove a directory along with read-only files.
        """
        try:
            shutil.rmtree(str(directory_path), onerror=self._onerror_handler)
            print(f"Successfully removed {directory_path}.")
        except Exception as e:
            print(f"Error removing {directory_path}: {e}")