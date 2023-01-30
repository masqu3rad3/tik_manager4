from tik_manager4.ui.Qt import QtWidgets, QtGui, QtCore


class CollapsibleLayout(QtWidgets.QVBoxLayout):
    """A Layout which can expand and collapse its children."""
    def __init__(self, title="", expanded=False, parent=None):
        super(CollapsibleLayout, self).__init__()
        # if parent:
        #     parent.setLayout(self)

        # create a button to expand and collapse the layout
        self._title = title
        self._button = QtWidgets.QPushButton()
        self.addWidget(self._button)
        self._button.setText("+ {}".format(self._title))
        # align the text to the left
        self._button.setStyleSheet("text-align: left")
        self.contents_widget = QtWidgets.QWidget()
        # set margins to 0
        self.contents_widget.setContentsMargins(0, 0, 0, 0)
        self.contents_layout = QtWidgets.QVBoxLayout()
        # set margins to 0
        self.contents_layout.setContentsMargins(0, 0, 0, 0)
        # self.contents
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