from tik_manager4.ui.widgets.signals import ValueChangeStr
from tik_manager4.ui.widgets import path_browser
# from tik_manager4.ui.widgets.validated_string import ValidatedString
from tik_manager4.ui.Qt import QtWidgets, QtCore

# from tik_manager4.ui.mcv import subproject_tree
import tik_manager4.ui.mcv.subproject_tree


# class PathBrowser(QtWidgets.QWidget):
#     """A custom QLineEdit widget purposed for browsing paths"""
#
#     def __init__(self, name, object_name=None, value=None, disables=None, **kwargs):
#         super(PathBrowser, self).__init__()
#         # self.com = ValueChangeStr()
#         self.value = value or ""
#         self.disables = disables or []
#         self.setObjectName(object_name or name)
#         self.layout = QtWidgets.QHBoxLayout(self)
#         self.widget = ValidatedString(name, object_name, value=self.value, allow_spaces=False, allow_directory=True, allow_empty=True)
#         self.com = self.widget.com
#         self.layout.addWidget(self.widget)
#         self.layout.setContentsMargins(0, 0, 0, 0)
#         self.button = QtWidgets.QPushButton("Browse")
#         self.button.clicked.connect(self.browse)
#         self.layout.addWidget(self.button)
#
#     def browse(self):
#         """Open a file dialog to browse for paths"""
#         # create a dialog to browse for paths
#         dialog = QtWidgets.QFileDialog(self)
#         dialog.setFileMode(QtWidgets.QFileDialog.Directory)
#         dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly, True)
#         dialog.setOption(QtWidgets.QFileDialog.DontUseNativeDialog, True)
#         dialog.setOption(QtWidgets.QFileDialog.DontResolveSymlinks, True)
#         # show only the directories
#         dialog.setFilter(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot)
#         if dialog.exec_():
#             self.widget.setText(dialog.selectedFiles()[0])
#             self.com.valueChangeEvent(self.widget.text())

class SubprojectBrowser(path_browser.PathBrowser):
    """A custom QLineEdit widget purposed for browsing subprojects"""
    sub = QtCore.Signal(object)

    def __init__(self, name, object_name=None, value=None, disables=None, project_object=None, **kwargs):
        super(SubprojectBrowser, self).__init__(name, object_name=object_name, value=value, disables=disables, project_object=None, **kwargs)
        if not project_object:
            raise ValueError("A project object must be provided to the SubprojectBrowser")
        self.project_object = project_object
        self.dialog = None

    def browse(self):
        """Create a TikSubProject tree inside a OK - Cancel dialog to select the subproject"""

        # create a dialog
        self.dialog = QtWidgets.QDialog(self)
        self.dialog.setWindowTitle("Select Subproject")
        self.dialog.setModal(True)

        # create a layout
        layout = QtWidgets.QVBoxLayout(self.dialog)
        self.dialog.setLayout(layout)

        # create a subproject tree layout
        sub_projects = tik_manager4.ui.mcv.subproject_tree.TikSubProjectLayout(self.project_object, recursive_enabled=False, right_click_enabled=False)

        # get all the columns from the model and hide all of them except the first one
        columns = sub_projects.sub_view.model.columns
        sub_projects.sub_view.hide_columns(columns[1:])
        layout.addLayout(sub_projects)

        # create a button box
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        layout.addWidget(button_box)
        button_box.accepted.connect(self.dialog.accept)
        button_box.rejected.connect(self.dialog.reject)
        self.adjustSize()




        self.dialog.show()
        # make the dialog vertically longer but no longer than the desktop height
        self.dialog.resize(self.dialog.width(), min(self.dialog.height() * 2, QtWidgets.QApplication.desktop().height() - 100))

        # move the dialog next to its parent dialog but only horizontally

        self.dialog.move(self.mapToGlobal(QtCore.QPoint(0, 0)) + QtCore.QPoint(self.width(), 0))

        # show the dialog

        if self.dialog.exec_():
            # get the model data from the selected item of TikProjectLayout
            _tikSubItem = sub_projects.sub_view.get_selected_item()
            if _tikSubItem:
                self.widget.setText(_tikSubItem.subproject.path)
                self.value = _tikSubItem.subproject.path
                self.com.valueChangeEvent(self.value)
                self.sub.emit(_tikSubItem.subproject)
