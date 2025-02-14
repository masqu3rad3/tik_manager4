import sys
from typing import Optional, List, Callable


class FeedbackCLI:
    def __init__(self, **kwargs):
        self.result = None

    def style_button(
        self, button, height: int = 30, width: int = 100, label: Optional[str] = None
    ):
        """CLI version does not require button styling."""
        pass

    def pop_info(
        self,
        title: str = "Info",
        text: str = "",
        details: str = "",
        critical: bool = False,
        button_label: Optional[str] = None,
        modal: bool = True,
        on_close: Optional[Callable[[int], None]] = None,
    ) -> int:
        """Shows an informational message in the terminal."""
        print(f"\n[ {title.upper()} ]")
        print(text)
        if details:
            print(f"Details: {details}")
        input(f"Press Enter to continue...")  # Simulates "Ok" button

        if critical:
            print("Critical error encountered. Exiting.")
            sys.exit(1)

        result = 1  # Simulate QtWidgets.QMessageBox.Ok
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
        """Asks a question via CLI with configurable buttons."""
        if buttons is None:
            buttons = ["save", "no", "cancel"]

        print(f"\n[ {title.upper()} ]")
        print(text)
        if details:
            print(f"Details: {details}")

        valid_buttons = {btn.lower(): btn for btn in buttons}

        while True:
            user_input = (
                input(f"Options {list(valid_buttons.keys())}: ").strip().lower()
            )
            if user_input in valid_buttons:
                self.result = valid_buttons[user_input]
                return self.result
            print("Invalid option. Please try again.")


# Example usage
if __name__ == "__main__":
    feedback = FeedbackCLI()
    feedback.pop_info(
        "Notice", "This is an informational message.", "Additional details here."
    )
    response = feedback.pop_question(
        "Confirmation", "Do you want to proceed?", buttons=["yes", "no"]
    )
    print(f"User selected: {response}")
