from pathlib import Path
from typing import Optional, List
import sys

from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.ui import pick
from tik_manager4.ui.widgets.common import TikMessageBox, TikButtonBox

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

FONT = "Roboto"

BUTTON_STYLE = """
QPushButton
{
    color: #b1b1b1;
    background-color: #404040;
    border-width: 1px;
    border-color: #1e1e1e;
    border-style: solid;
    padding: 5px;
    font-size: 12x;
    border-radius: 4px;
}

QPushButton:hover
{
    background-color: #505050;
    border: 1px solid #ff8d1c;
}

QPushButton:hover[circle=true]
{
    background-color: #505050;
    border: 2px solid #ff8d1c;
}

QPushButton:disabled {
    color: #505050;
    background-color: #303030;
    border: 1px solid #404040;
    border-width: 1px;
    border-color: #1e1e1e;
    border-style: solid;
    padding: 5px;
    font-size: 12x;
}

QPushButton:pressed {
  background-color: #ff8d1c;
  border: 1px solid #ff8d1c;
}
"""

def style_button(button, height: int = 30, width: int = 100,
                 label: Optional[str] = None):
    """Applies consistent styling to a button."""
    button.setFixedHeight(height)
    button.setFixedWidth(width)
    button.setStyleSheet(BUTTON_STYLE)
    if label:
        button.setText(label)

class Feedback:
    def __init__(self, parent=None):
        self.parent = parent
        self.result = None

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
        if not self.parent:
            _style_file = pick.style_file(file_name="tikManager.qss")
            msg.setStyleSheet(str(_style_file.readAll(), "utf-8"))
        msg.setIcon(QtWidgets.QMessageBox.Critical if critical else QtWidgets.QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setModal(modal)
        msg.setText(text)
        msg.setInformativeText(details)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)

        ok_button = msg.button(QtWidgets.QMessageBox.Ok)
        style_button(ok_button, label=button_label)

        result = msg.exec_()
        if on_close:
            on_close(result)
        return result

    def pop_error(self, *args, **kwargs) -> int:
        """Shows an error dialog box."""
        return self.pop_info(*args, critical=True, **kwargs)

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
            "continue": QtWidgets.QMessageBox.Yes,
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
        if not self.parent:
            _style_file = pick.style_file(file_name="tikManager.qss")
            q.setStyleSheet(str(_style_file.readAll(), "utf-8"))
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

        # go over all buttons and style them
        for button in q.buttons():
            style_button(button)

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


class Confirmation(QtWidgets.QDialog):
    """A user interaction class to prevent accidental actions.

    The user will be asked to confirm a word (such as the name of a project or task)
    before proceeding. This prevents accidental actions.
    """

    def __init__(self, parent=None, confirmation_word=None):
        super().__init__(parent)
        if not parent:
            _style_file = pick.style_file(file_name="tikManager.qss")
            self.setStyleSheet(str(_style_file.readAll(), "utf-8"))
        self.setModal(True)  # Make it a modal dialog
        self.setWindowTitle("Confirmation")

        self.result = None
        self._confirmation_word = confirmation_word

        # Create layout and widgets
        self.layout = QtWidgets.QVBoxLayout(self)
        self.label = QtWidgets.QLabel("Type the confirmation word to proceed:", self)
        self.input_field = QtWidgets.QLineEdit(self)
        self.input_field.setPlaceholderText("Type confirmation word here")
        self.input_field.setFocus()
        button_box = TikButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.input_field)
        self.layout.addWidget(button_box)

        # SIGNALS
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

    def set_confirmation_word(self, word):
        """Set the confirmation word that the user must type correctly."""
        self._confirmation_word = word

    def ask_confirmation(self, title="Question", text="Type the confirmation word to proceed"):
        """Pop up the confirmation dialog and check the user input."""
        self.setWindowTitle(title)
        self.label.setText(text)

        if self.exec_() == QtWidgets.QDialog.Accepted:
            user_input = self.input_field.text()
            if user_input == self._confirmation_word:
                self.result = True
                return True

        self.result = False
        return False

# test the module
if __name__ == "__main__":
    confirmation = Confirmation(confirmation_word="test")
    confirmation.ask_confirmation()
    print(confirmation.result)
    sys.exit(app.exec_())
