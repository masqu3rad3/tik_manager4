"""Run Tik Manager Standalone edition."""

# PyInstaller "tik_manager.py" -w -y --clean
# Move the executable and _internal folder to the root folder for the CSS to work

from pathlib import Path
import os
import sys
from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.ui import main

def terminate_zbrush():
    """Create a file in the documents folder to terminate the loop."""
    file_path = Path.home() / "Documents" / ".tik_zbrush_terminate.txt"
    with open(file_path, "w") as f:
        f.write("Terminating Zbrush Loop")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    # get the first argument and put it as an environment variable to ZCOMM_LINK
    os.environ["ZCOMM_LINK"] = sys.argv[1:]
    print("DEBUGGGG")
    print(sys.argv[1:])

    tik = main.launch(dcc="Zbrush")
    # Connect terminate_zbrush() to the aboutToQuit signal
    app.aboutToQuit.connect(terminate_zbrush)
    sys.exit(app.exec_())
