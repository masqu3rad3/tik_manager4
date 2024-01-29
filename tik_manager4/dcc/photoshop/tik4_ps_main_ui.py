"""Launch Tik Manager for Photoshop."""

import sys
from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.ui import main

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main.launch(dcc="Photoshop")
    sys.exit(app.exec_())