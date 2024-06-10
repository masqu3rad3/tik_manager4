from tik_manager4.ui.widgets.validated_string import ValidatedString
from tik_manager4.ui.widgets.common import TikButton, TikIconButton

from tik_manager4.ui.Qt import QtWidgets, QtCore


class PathBrowser(QtWidgets.QWidget):
    """Customize QLineEdit widget purposed for browsing paths."""

    def __init__(self, name, object_name=None, value=None, disables=None, **kwargs):
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
            self.widget.setText(dialog.selectedFiles()[0])
            self.com.valueChangeEvent(self.widget.text())

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
