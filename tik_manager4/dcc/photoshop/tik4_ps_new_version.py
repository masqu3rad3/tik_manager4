"""Launch Tik Manager for Photoshop."""

import sys
from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.ui import main

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    tik4 = main.launch(dcc="Photoshop", dont_show=True)
    tik4.on_new_version()
    sys.exit(app.exec_())