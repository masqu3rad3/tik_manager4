from tik_manager4.ui.Qt import QtWidgets, QtGui, QtCore


class CollapsibleLayout(QtWidgets.QVBoxLayout):
    """A Layout which can expand and collapse its children."""
    def __init__(self, title="", expanded=False, parent=None):
        super(CollapsibleLayout, self).__init__()
        if parent:
            self.setLayout(parent)

        # create a button to expand and collapse the layout
        self._title = title
        self._button = QtWidgets.QPushButton()
        self.addWidget(self._button)
        self._button.setText("+ {}".format(self._title))
        # set button color to slightly lighter, size to 15pt, and text alignment to left
        # self._button.setStyleSheet("QPushButton {color: #d9d9d9; font-size: 13pt; text-align: left;}")
        # increase the button height to 30px
        self._button.setMinimumHeight(25)
        # set the button to flat with borders
        # self._button.setFlat(True)
        # make button look like a label with borders
        self._button.setFlat(True)
        self._button.setStyleSheet("QPushButton {border: 1px solid #d9d9d9; border-radius: 5px;}")

        self.contents_widget = QtWidgets.QWidget()
        # set margins to 0
        # self.contents_widget.setContentsMargins(0, 0, 0, 0)
        self.contents_layout = QtWidgets.QVBoxLayout()
        # set margins to 0
        # self.contents_layout.setContentsMargins(0, 0, 0, 0)
        self.addWidget(self.contents_widget)
        self.contents_widget.setLayout(self.contents_layout)
        # self.addStretch()
        self._expanded = expanded
        if self._expanded:
            self.expand()
        else:
            self.collapse()
        self._button.clicked.connect(self.toggle)
    def toggle(self):
        """Toggle the layout."""
        if self._expanded:
            self.collapse()
        else:
            self.expand()

    def expand(self):
        """Expand the layout."""
        self._button.setText("- {}".format(self._title))
        self.contents_widget.setVisible(True)
        self._expanded = True

    def collapse(self):
        """Collapse the layout."""
        self._button.setText("+ {}".format(self._title))
        self.contents_widget.setVisible(False)
        self._expanded = False