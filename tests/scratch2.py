import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from tik_manager4.ui.widgets import new_subproject


app = QtWidgets.QApplication(sys.argv)
dialog = new_subproject.NewSubproject()

dialog.show()

sys.exit(app.exec_())