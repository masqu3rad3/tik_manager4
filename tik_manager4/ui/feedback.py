import os
import sys

from tik_manager4.core import compatibility as compat
# from tik_manager4.core import filelog

from tik_manager4.ui.Qt import QtWidgets

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

class Feedback():
    def __init__(self, *args, **kwargs):
        self.parent=None

    def pop_info(self, title="Info", text="", details="", critical=False, button_label=None, modal=True):
        msg = QtWidgets.QMessageBox(parent=self.parent)
        if critical:
            msg.setIcon(QtWidgets.QMessageBox.Critical)
        else:
            msg.setIcon(QtWidgets.QMessageBox.Information)

        msg.setWindowTitle(title)
        msg.setModal(modal)
        msg.setText(text)
        msg.setInformativeText(details)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.button(QtWidgets.QMessageBox.Ok).setFixedHeight(30)
        msg.button(QtWidgets.QMessageBox.Ok).setFixedWidth(100)
        if button_label:
            msg.button(QtWidgets.QMessageBox.Ok).setText(button_label)
        return msg.exec_()
        # return msg.show()

    def pop_question(self, title="Question", text="", details="", buttons=None, modal=True):
        if buttons is None:
            buttons = ["save", "no", "cancel"]
        button_dict = {
            "yes": "QtWidgets.QMessageBox.Yes",
            "save": "QtWidgets.QMessageBox.Save",
            "ok": "QtWidgets.QMessageBox.Ok",
            "no": "QtWidgets.QMessageBox.No",
            "cancel": "QtWidgets.QMessageBox.Cancel"
        }
        widgets = []
        for button in buttons:
            widget = button_dict.get(button)
            if not widget:
                raise RuntimeError("Non-valid button defined. Valid buttons are: %s" % button_dict.keys())
            widgets.append(widget)

        q = QtWidgets.QMessageBox(parent=self.parent)
        q.setIcon(QtWidgets.QMessageBox.Question)
        q.setWindowTitle(title)
        q.setModal(modal)
        q.setText(text)
        q.setInformativeText(details)
        eval('q.setStandardButtons(%s)' %(" | ".join(widgets)))
        ret = q.exec_()
        for key, value in button_dict.items():
            if ret == eval(value):
                return key

    def browse_directory(self, modal=True):
        dlg = QtWidgets.QFileDialog(parent=self.parent)
        dlg.setModal(modal)
        dlg.setFileMode(QtWidgets.QFileDialog.Directory)
        if dlg.exec_():
        # if dlg.exec():
            return os.path.normpath(compat.encode(dlg.selectedFiles()[0]))



