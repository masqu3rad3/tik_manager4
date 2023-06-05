"""Dialog for setting project."""

from tik_manager4.ui.Qt import QtWidgets, QtCore
from tik_manager4.ui.widgets import path_browser
from tik_manager4.ui.dialog.feedback import Feedback
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

        self.build_ui()

    def build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        header_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(header_layout)
        split_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(split_layout)
        splitter = QtWidgets.QSplitter()
        splitter.setHandleWidth(10)
        split_layout.addWidget(splitter)
        folders_tree_widget = QtWidgets.QWidget(splitter)
        folders_tree_layout = QtWidgets.QVBoxLayout(folders_tree_widget)
        folders_tree_layout.setContentsMargins(0, 0, 0, 0)
        bookmarks_widget = QtWidgets.QWidget(splitter)
        bookmarks_layout = QtWidgets.QVBoxLayout(bookmarks_widget)
        bookmarks_layout.setContentsMargins(0, 0, 0, 0)


        look_in_lbl = QtWidgets.QLabel(text="Look in:")
        browser_wgt = path_browser.PathBrowser("lookIn")
        # look_in_lbl = QtWidgets.QLabel(text="Look in:")
        # self.look_in_le = QtWidgets.QLineEdit(self)
        # header_layout.addWidget(look_in_lbl)
        # header_layout.addWidget(self.look_in_le)
        header_layout.addWidget(look_in_lbl)
        header_layout.addWidget(browser_wgt)

        # back_pb = QtWidgets.QPushButton()
        # back_pb.setIcon(pick.icon("arrow_left.png"))
        # back_pb.setToolTip("Go back")
        # header_layout.addWidget(back_pb)

        recent_pb = QtWidgets.QPushButton(text="Recent")
        recent_pb.setToolTip("Recent projects")
        header_layout.addWidget(recent_pb)

        folders_tree = QtWidgets.QTreeView(splitter, minimumSize=QtCore.QSize(0, 0), dragEnabled=True,
                                                    dragDropMode=QtWidgets.QAbstractItemView.DragOnly,
                                                    selectionMode=QtWidgets.QAbstractItemView.SingleSelection,
                                                    itemsExpandable=False, rootIsDecorated=False,
                                                    sortingEnabled=True, frameShape=QtWidgets.QFrame.NoFrame)
        folders_tree_layout.addWidget(folders_tree)



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

