from tik_manager4.ui.widgets.validated_string import ValidatedString
from tik_manager4.ui.widgets.common import TikButton, TikIconButton

from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui


class PathBrowser(QtWidgets.QWidget):
    """Customize QLineEdit widget purposed for browsing paths."""

    def __init__(self, name, object_name=None, value=None, disables=None, items=None, **kwargs):
        super(PathBrowser, self).__init__()
        self.value = value or ""
        self.disables = disables or []
        self.setObjectName(object_name or name)
        self.layout = QtWidgets.QHBoxLayout(self)
        self.widget = ValidatedString(
            name,
            object_name,
            value=self.value,
            allow_spaces=True,
            allow_directory=True,
            allow_empty=True,
        )

        self.com = self.widget.com
        self.layout.addWidget(self.widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.button = TikIconButton(icon_name="folder", circle=False)
        self.button.clicked.connect(self.browse)
        self.layout.addWidget(self.button)

        self._items = items
        if items:
            # if items are defined, make a zort menu button popup.
            self.items_button = TikIconButton(icon_name="menu", circle=False)
            self.layout.addWidget(self.items_button)
            self.items_button.clicked.connect(self.items_pop_menu)
        else:
            self.items_button = None

    @property
    def items(self):
        """Return the items in the path browser"""
        return self._items or []

    @items.setter
    def items(self, value_list):
        """Set the items in the path browser"""
        self._items = value_list

    def zort_menu(self, items):
        """Create a zort menu for the items"""
        if self.items_button:
            self.items_button.setMenu(items)
            self.items_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
            self.layout.addWidget(self.items_button)

    def items_pop_menu(self):
        """Pop menu for recent projects."""

        zort_menu = QtWidgets.QMenu(self)
        for z_item in self._items:
            _temp_action = QtWidgets.QAction(z_item, self)
            zort_menu.addAction(_temp_action)
            _temp_action.triggered.connect(
                lambda _ignore=z_item, item=z_item: self._set_end_emit(item)
            )

        return bool(zort_menu.exec_((QtGui.QCursor.pos())))

    def _set_end_emit(self, value):
        """Set the value and emit the value change event"""
        self.widget.setText(value)
        self.com.valueChangeEvent(self.widget.text())

    def browse(self):
        """Open a file dialog to browse for paths"""
        # create a dialog to browse for paths
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly, True)
        dialog.setOption(QtWidgets.QFileDialog.DontUseNativeDialog, True)
        dialog.setOption(QtWidgets.QFileDialog.DontResolveSymlinks, True)
        # show only the directories
        dialog.setFilter(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot)
        if dialog.exec_():
            self._set_end_emit(dialog.selectedFiles()[0])
            # self.widget.setText(dialog.selectedFiles()[0])
            # self.com.valueChangeEvent(self.widget.text())

class FileBrowser(PathBrowser):
    """Customize QLineEdit widget purposed for browsing files."""
    def browse(self):
        """Open a file dialog to browse for files"""
        # create a dialog to browse for files
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        dialog.setOption(QtWidgets.QFileDialog.DontUseNativeDialog, True)
        dialog.setOption(QtWidgets.QFileDialog.DontResolveSymlinks, True)
        if dialog.exec_():
            self.widget.setText(dialog.selectedFiles()[0])
            self.com.valueChangeEvent(self.widget.text())
