"""Module to handle the releases."""

import sys
import getopt
import os

# set the TIK_DCC environment variable
os.environ["TIK_DCC"] = "null"

import subprocess

from pathlib import Path
from tik_manager4 import _version
from tik_manager4.dcc.dcc_install import Injector

os.environ["TIK_VERSION"] = _version.__version__

INNO_SETUP_EXE = Path("C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe")
PACKAGE_ROOT = Path(__file__).parent
# INNO_SCRIPT = Path(__file__).parent / "tik_manager4_innosetup_debug.iss"


class ReleaseUtility:
    """Class to handle the releases."""

    def __init__(self, debug_mode=False):
        """Initialize the release utility."""
        self.release_version = _version.__version__
        self.tik_root = Path(__file__).parent.parent / "tik_manager4"
        self.spec_file_name = "tik4_debug.spec" if debug_mode else "tik4.spec"
        self.inno_script_path = PACKAGE_ROOT / "tik_manager4_innosetup_debug.iss" if debug_mode else PACKAGE_ROOT / "tik_manager4_innosetup.iss"

    def freeze(self):
        """Freeze the application using pyinstaller."""
        subprocess.call(
            ["pyinstaller", self.spec_file_name, "--clean", "--noconfirm"],
            cwd=self.tik_root,
            shell=True,
        )

    def inno_setup(self):
        """Compile the installer using inno setup."""
        if not INNO_SETUP_EXE.exists():
            raise FileNotFoundError("Inno Setup not found at the specified location.")
        sys.stdout.write("Starting Inno Setup.")

        injector = Injector(self.inno_script_path)
        injector.match_mode = "contains"
        app_line = f'#define appVersion "{self.release_version}"'
        injector.replace_single_line(app_line, "#define appVersion")

        subprocess.call([str(INNO_SETUP_EXE), str(self.inno_script_path)], shell=True)


if __name__ == "__main__":
    # get the arguments from sys
    opts, args = getopt.getopt(sys.argv[1:], "d", ["debug"])
    # if there is a debug flag, set the debug mode to True
    _debug_mode = any([opt in ("-d", "--debug") for opt, _ in opts])
    release_utility = ReleaseUtility(debug_mode=_debug_mode)
    release_utility.freeze()
    if not _debug_mode:
        release_utility.inno_setup()
