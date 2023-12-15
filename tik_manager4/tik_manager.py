"""Run Tik Manager Standalone edition."""

# PyInstaller "tik_manager.py" -w -y --clean
# Move the executable and _internal folder to the root folder for the CSS to work

import sys
from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.ui import main

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main.launch()
    sys.exit(app.exec_())
