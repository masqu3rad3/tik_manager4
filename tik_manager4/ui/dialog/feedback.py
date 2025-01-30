from pathlib import Path
from typing import Optional, List
import sys

from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.ui.widgets.common import TikMessageBox

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)


class Feedback:
    def __init__(self, parent=None):
        self.parent = parent
        self.result = None

    def style_button(self, button, height: int = 30, width: int = 100, label: Optional[str] = None):
        """Applies consistent styling to a button."""
        button.setFixedHeight(height)
        button.setFixedWidth(width)
        if label:
            button.setText(label)

    def pop_info(
        self,
        title: str = "Info",
        text: str = "",
        details: str = "",
        critical: bool = False,
        button_label: Optional[str] = None,
        modal: bool = True,
        on_close: Optional[callable] = None,
    ) -> int:
        """Shows an informational dialog box."""
        msg = TikMessageBox(parent=self.parent)
        msg.setIcon(QtWidgets.QMessageBox.Critical if critical else QtWidgets.QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setModal(modal)
        msg.setText(text)
        msg.setInformativeText(details)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)

        ok_button = msg.button(QtWidgets.QMessageBox.Ok)
        self.style_button(ok_button, label=button_label)

        result = msg.exec_()
        if on_close:
            on_close(result)
        return result

    def pop_question(
            self,
            title: str = "Question",
            text: str = "",
            details: str = "",
            buttons: Optional[List[str]] = None,
            modal: bool = True,
    ) -> Optional[str]:
        """Shows a question dialog box with configurable buttons."""
        if buttons is None:
            buttons = ["save", "no", "cancel"]

        button_dict = {
            "yes": QtWidgets.QMessageBox.Yes,
            "yes_to_all": QtWidgets.QMessageBox.YesToAll,
            "save": QtWidgets.QMessageBox.Save,
            "ok": QtWidgets.QMessageBox.Ok,
            "open": QtWidgets.QMessageBox.Open,
            "close": QtWidgets.QMessageBox.Close,
            "discard": QtWidgets.QMessageBox.Discard,
            "apply": QtWidgets.QMessageBox.Apply,
            "reset": QtWidgets.QMessageBox.Reset,
            "restore_defaults": QtWidgets.QMessageBox.RestoreDefaults,
            "help": QtWidgets.QMessageBox.Help,
            "save_all": QtWidgets.QMessageBox.SaveAll,
            "no": QtWidgets.QMessageBox.No,
            "no_to_all": QtWidgets.QMessageBox.NoToAll,
            "cancel": QtWidgets.QMessageBox.Cancel,
            "ignore": QtWidgets.QMessageBox.Ignore,
            "abort": QtWidgets.QMessageBox.Abort,
            "retry": QtWidgets.QMessageBox.Retry,
        }

        widgets = []
        for button in buttons:
            widget = button_dict.get(button)
            if not widget:
                raise RuntimeError(
                    f"Invalid button: {button}. Valid buttons are: {list(button_dict.keys())}"
                )
            widgets.append(widget)

        q = TikMessageBox(parent=self.parent)
        q.setIcon(QtWidgets.QMessageBox.Question)
        q.setWindowTitle(title)
        q.setModal(modal)
        q.setText(text)
        q.setInformativeText(details)

        # Combine buttons using bitwise OR operator
        combined_buttons = widgets[0]
        for widget in widgets[1:]:
            combined_buttons |= widget

        q.setStandardButtons(combined_buttons)

        ret = q.exec_()
        for key, value in button_dict.items():
            if ret == value:
                self.result = key
                return key

    def browse_directory(self, modal: bool = True) -> Optional[str]:
        """Browse for a directory. Deprecated: Consider moving to a utility function."""
        dlg = QtWidgets.QFileDialog(parent=self.parent)
        dlg.setModal(modal)
        dlg.setFileMode(QtWidgets.QFileDialog.Directory)
        if dlg.exec_():
            return str(Path(dlg.selectedFiles()[0]))
