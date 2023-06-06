"""Dialog for setting project."""
import os

from tik_manager4.ui.Qt import QtWidgets, QtCore
from tik_manager4.ui.widgets import path_browser
from tik_manager4.ui.dialog.feedback import Feedback
from tik_manager4.ui.widgets.value_widgets import DropList
from tik_manager4.ui import pick


class SetProjectDialog(QtWidgets.QDialog):
    def __init__(self, main_object, *args, **kwargs):
        self.main_object = main_object
        super(SetProjectDialog, self).__init__(*args, **kwargs)
        self.feedback = Feedback(parent=self)
        self.setWindowTitle("Set Project")
        self.setModal(True)

        self.setMinimumSize(982, 450)
        self.setFocus()

        self.active_project = None
        self.build_ui()

        self.populate_bookmarks()

    def build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        header_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(header_layout)
        split_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(split_layout)
        splitter = QtWidgets.QSplitter()
        # splitter.setHandleWidth(20)
        split_layout.addWidget(splitter)
        folders_tree_widget = QtWidgets.QWidget(splitter)
        folders_tree_layout = QtWidgets.QVBoxLayout(folders_tree_widget)
        folders_tree_layout.setContentsMargins(0, 0, 0, 0)
        bookmarks_widget = QtWidgets.QWidget(splitter)
        bookmarks_layout = QtWidgets.QVBoxLayout(bookmarks_widget)
        bookmarks_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(buttons_layout)

        look_in_lbl = QtWidgets.QLabel(text="Look in:")
        browser_wgt = path_browser.PathBrowser("lookIn")
        browser_wgt.widget.setText(self.main_object.project.root)
        header_layout.addWidget(look_in_lbl)
        header_layout.addWidget(browser_wgt)

        recent_pb = QtWidgets.QPushButton(text="Recent")
        recent_pb.setToolTip("Recent projects")
        header_layout.addWidget(recent_pb)

        # projects side
        self.folders_tree = QtWidgets.QTreeView(splitter, minimumSize=QtCore.QSize(0, 0), dragEnabled=True,
                                                    dragDropMode=QtWidgets.QAbstractItemView.DragOnly,
                                                    selectionMode=QtWidgets.QAbstractItemView.SingleSelection,
                                                    itemsExpandable=False, rootIsDecorated=False,
                                                    sortingEnabled=True, frameShape=QtWidgets.QFrame.NoFrame)
        folders_tree_layout.addWidget(self.folders_tree)
        directory_filter = QtWidgets.QLineEdit()
        directory_filter.setPlaceholderText("Filter")
        folders_tree_layout.addWidget(directory_filter)

        source_model = QtWidgets.QFileSystemModel()
        source_model.setNameFilterDisables(False)
        source_model.setNameFilters(["*"])
        source_model.setRootPath(self.main_object.project.root)
        source_model.setFilter(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot | QtCore.QDir.Time)
        self.folders_tree.setModel(source_model)
        self.folders_tree.setRootIndex(source_model.index(self.main_object.project.root))
        self.folders_tree.setColumnWidth(0, 400)
        self.folders_tree.setColumnWidth(1, 0)
        self.folders_tree.setColumnWidth(2, 0)
        selection_model = self.folders_tree.selectionModel()


        self.bookmarks_droplist = DropList(name="Bookmarks", buttons_position="down", buttons=["+", "-"])
        plus_btn = self.bookmarks_droplist.buttons[0]
        minus_btn = self.bookmarks_droplist.buttons[1]
        bookmarks_layout.addWidget(self.bookmarks_droplist)

        # make the right side of the splitter stretchable
        splitter.setStretchFactor(0, 1)

        # buttons
        # create a button box as "set" and "cancel"
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons_layout.addWidget(button_box)


        # SIGNALS
        self.bookmarks_droplist.dropped.connect(self.on_drag_and_drop)
        plus_btn.clicked.connect(self.on_add_bookmark)
        minus_btn.clicked.connect(self.on_remove_bookmark)

        button_box.accepted.connect(self.set_and_close)
        self.bookmarks_droplist.list.doubleClicked.connect(self.set_and_close)
        selection_model.selectionChanged.connect(self.activate_folders)
        self.bookmarks_droplist.list.currentRowChanged.connect(self.activate_bookmarks)
    def activate_folders(self):
        """Get the active project from folders tree and clear the bookmarks area selection."""
        index = self.folders_tree.currentIndex()
        self.active_project = os.path.normpath(self.folders_tree.model().filePath(index))
        self.bookmarks_droplist.list.clearSelection()

    def activate_bookmarks(self, row):
        """Get the active project from bookmarks and clear the folders tree area selection."""
        # row = self.bookmarks_droplist.list.currentRow()
        if row != -1:
            self.active_project = self.main_object.user.get_project_bookmarks()[row]
            self.folders_tree.clearSelection()

    def set_and_close(self):
        """Set the active project and close the dialog."""

        if not self.active_project:
            self.feedback.pop_info(title="Cannot set project", text="No project selected.\nPlease select a project from the folders or bookmarks and press 'Set'")
            return
        self.main_object.set_project(self.active_project)
        self.close()

    def on_add_bookmark(self):
        """Called when the add bookmark button is clicked."""
        idx = self.folders_tree.currentIndex()
        if idx.isValid():
            path = self.folders_tree.model().filePath(idx)
            self.main_object.user.add_project_bookmark(path)
            self.populate_bookmarks()

    def on_remove_bookmark(self):
        """Called when the remove bookmark button is clicked."""
        row = self.bookmarks_droplist.list.currentRow()
        if row != -1:
            p_path = self.main_object.user.get_project_bookmarks()[row]
            self.main_object.user.delete_project_bookmark(p_path)
            self.populate_bookmarks()

    def on_drag_and_drop(self, p_path):
        """Called when a path is dropped to the dialog."""
        norm_path = os.path.normpath(p_path)
        self.main_object.user.add_project_bookmark(norm_path)
        self.populate_bookmarks()

    def populate_bookmarks(self):
        self.bookmarks_droplist.list.clear()
        self.bookmarks_droplist.list.addItems(self.main_object.user.bookmark_names)

# Test the dialog
if __name__ == "__main__":
    import sys
    import tik_manager4
    from tik_manager4.ui import pick
    app = QtWidgets.QApplication(sys.argv)
    tik = tik_manager4.initialize("Standalone")
    dialog = SetProjectDialog(tik)
    _style_file = pick.style_file()
    dialog.setStyleSheet(str(_style_file.readAll(), 'utf-8'))
    dialog.show()
    sys.exit(app.exec_())

