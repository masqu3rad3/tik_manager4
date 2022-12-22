import sys
from PyQt5 import QtWidgets
from tik_manager4.ui.dialog import new_subproject

app = QtWidgets.QApplication(sys.argv)
dialog = new_subproject.NewSubproject()

dialog.show()

sys.exit(app.exec_())