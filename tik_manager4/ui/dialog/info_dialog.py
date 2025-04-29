"""Generic dialog to display information from a dictionary.

Example usage:
    from tik_manager4.ui.dialog.info_dialog import InfoDialog
    InfoDialog.show_info(data=example_data, title="Asset Details")
"""

from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui


class InfoDialog(QtWidgets.QDialog):
    """A generic dialog to display key-value information from a dictionary."""

    def __init__(self, data=None, title="Information", parent=None):
        """
        Initialize the InfoDialog.

        Args:
            data (dict, optional): A flat dictionary containing the data to display.
                                   Defaults to None.
            title (str, optional): The title for the dialog window.
                                   Defaults to "Information".
            parent (QtWidgets.QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent=parent)

        self.setWindowTitle(title)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(400)

        self._form_layout = QtWidgets.QFormLayout()
        self._form_layout.setContentsMargins(0, 0, 0, 0)
        self._form_layout.setSpacing(5) # Restore spacing
        self._form_layout.setLabelAlignment(QtCore.Qt.AlignRight)

        # Widget and layout to hold the form layout within a scroll area
        scroll_content = QtWidgets.QWidget()
        scroll_content.setLayout(self._form_layout)

        # Scroll Area setup
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_content)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame) # Optional: remove border
        # Removed scroll area stylesheet

        # Button Box
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject) # Connect Close button to reject/close

        # Main Layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(scroll_area) # Add scroll area instead of form layout directly
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

        if data:
            self.set_data(data)

    def set_data(self, data):
        """
        Populates the dialog with data from a dictionary.

        Args:
            data (dict): A flat dictionary containing the data to display.
        """
        # Clear previous data
        while self._form_layout.count():
            child = self._form_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Populate with new data
        if not isinstance(data, dict):
            # Handle non-dict input gracefully (e.g., show a message)
            label = QtWidgets.QLabel("Invalid data format. Expected a dictionary.")
            label.setStyleSheet("font-style: italic; color: grey;") # Keep simple styling
            self._form_layout.addRow(label)
            return

        for key, value in data.items():
            key_label = QtWidgets.QLabel(f"{str(key).replace('_', ' ').title()}:")
            # Removed style sheet and auto fill background
            value_label = QtWidgets.QLabel(str(value))
            value_label.setWordWrap(True) # Allow text wrapping for long values
            value_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse) # Allow copying text
            # Removed style sheet and auto fill background
            self._form_layout.addRow(key_label, value_label)
            # Removed row_index logic

    @staticmethod
    def show_info(data, title="Information", parent=None):
        """Static method to quickly show an info dialog."""
        dialog = InfoDialog(data=data, title=title, parent=parent)
        dialog.exec_() # Use exec_ for modal dialog
