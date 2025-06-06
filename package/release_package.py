"""Module to handle the releases."""

import sys
import getopt
import os

# set the TIK_DCC environment variable
os.environ["TIK_DCC"] = "null"

import logging
import re
import subprocess

from pathlib import Path
from tik_manager4 import _version
from tik_manager4.dcc.dcc_install import Injector

os.environ["TIK_VERSION"] = _version.__version__

INNO_SETUP_EXE = Path("C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe")
PACKAGE_ROOT = Path(__file__).parent

LOG = logging.getLogger(__name__)

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
        LOG.info("\nStarting Freeze Process.\n")
        subprocess.call(
            ["pyinstaller", self.spec_file_name, "--clean", "--noconfirm"],
            cwd=self.tik_root,
            shell=True,
        )
        LOG.info("Freeze Process Completed.")
        LOG.info("-------------------------")

    def inno_setup(self):
        """Compile the installer using inno setup."""
        LOG.info("\nStarting Inno Setup.\n")
        if not INNO_SETUP_EXE.exists():
            raise FileNotFoundError("Inno Setup not found at the specified location.")
        sys.stdout.write("Starting Inno Setup.")

        injector = Injector(self.inno_script_path)
        injector.match_mode = "contains"
        app_line = f'#define appVersion "{self.release_version}"'
        injector.replace_single_line(app_line, "#define appVersion")

        subprocess.call([str(INNO_SETUP_EXE), str(self.inno_script_path)], shell=True)
        LOG.info("Inno Setup completed.")
        LOG.info("---------------------")

    def extract_and_sanitize_release_notes(self):
        """Extract and sanitize the release notes."""
        LOG.info("\nExtracting and sanitizing release notes.\n")
        relase_notes = PACKAGE_ROOT.parent / "RELEASE_NOTES.md"
        content = relase_notes.read_text()

        # Match the target version section and capture its notes
        version_pattern = re.compile(
            rf"##\s+v{re.escape(self.release_version)}\n(.*?)(?:\n##|$)",
            re.DOTALL
        )

        match = version_pattern.search(content)
        if not match:
            sanitized_notes = "No release notes found."
            LOG.warning(f"Version v%s not found in release notes.", self.release_version)
        else:
            notes = match.group(1).strip()
            # Remove brackets and their content
            sanitized_notes = re.sub(r"\[.*?\]\s*", "", notes)

        (PACKAGE_ROOT / "build").mkdir(exist_ok=True)

        output_file = PACKAGE_ROOT / "build" / f"ReleaseNotes_v{self.release_version}.md"
        output_file.write_text(sanitized_notes)

        LOG.info("Release notes extracted and saved to %s", output_file)
        return output_file



if __name__ == "__main__":
    # get the arguments from sys
    opts, args = getopt.getopt(
        sys.argv[1:], "dt", ["debug", "testrelease", "build", "package"]
    )

    _debug_mode = any(opt in ("-d", "--debug") for opt, _ in opts)
    _testrelease_mode = any(opt in ("-t", "--testrelease") for opt, _ in opts)
    _build_only = any(opt == "--build" for opt, _ in opts)
    _package_only = any(opt == "--package" for opt, _ in opts)

    release_utility = ReleaseUtility(debug_mode=_debug_mode)

    if _debug_mode:
        release_utility.release_version = f"{_version.__version__}-debug"
    if _testrelease_mode:
        release_utility.release_version = f"{_version.__version__}-alpha"

    if _build_only:
        release_utility.freeze()
        release_utility.extract_and_sanitize_release_notes()
        sys.exit(0)

    if _package_only:
        release_utility.inno_setup()
        sys.exit(0)

    # Default full release flow (if no --build or --package specified)
    release_utility.freeze()
    if not _testrelease_mode or _debug_mode:
        release_utility.extract_and_sanitize_release_notes()
    if not _debug_mode:
        release_utility.inno_setup()
