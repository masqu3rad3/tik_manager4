import sys
from PyQt5 import QtWidgets
from tik_manager4.ui.dialog import subproject_dialog

app = QtWidgets.QApplication(sys.argv)
dialog = new_subproject.NewSubprojectDialog()

dialog.show()

sys.exit(app.exec_())