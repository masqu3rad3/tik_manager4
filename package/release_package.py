"""Module to handle the releases."""
import sys
import os

# set the TIK_DCC environment variable
os.environ["TIK_DCC"] = "standalone"

import subprocess

from pathlib import Path
from tik_manager4 import _version
from tik_manager4.dcc.dcc_install import Injector

INNO_SETUP_EXE = Path("C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe")
INNO_SCRIPT = Path(__file__).parent / "tik_manager4_innosetup.iss"

class ReleaseUtility:
    """Class to handle the releases."""
    def __init__(self):
        """Initialize the release utility."""
        self.release_version = _version.__version__
        self.tik_root = Path(__file__).parent.parent / "tik_manager4"
    def freeze(self):
        """Freeze the application using pyinstaller."""
        subprocess.call(["pyinstaller", "tik4.spec", "--clean", "--noconfirm"], cwd=self.tik_root, shell=True)

    def inno_setup(self):
        """Compile the installer using inno setup."""
        if not INNO_SETUP_EXE.exists():
            raise FileNotFoundError("Inno Setup not found at the specified location.")
        sys.stdout.write("Starting Inno Setup.")

        injector = Injector(INNO_SCRIPT)
        injector.match_mode = "contains"
        app_line = f'#define appVersion "{self.release_version}"'
        injector.replace_single_line(app_line, "#define appVersion")

        subprocess.call([str(INNO_SETUP_EXE), str(INNO_SCRIPT)], shell=True)


if __name__ == "__main__":
    release_utility = ReleaseUtility()
    release_utility.freeze()
    release_utility.inno_setup()
