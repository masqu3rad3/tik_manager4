# pylint: disable=consider-using-f-string
# pylint: disable=super-with-arguments

from datetime import datetime

from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
from tik_manager4.ui.dialog.feedback import Feedback


class TikWorkItem(QtGui.QStandardItem):
    color_dict = {
        "working": (255, 255, 0),
        "has_publish": (0, 255, 0),
        "omit": (255, 0, 0)
    }

    def __init__(self, work_obj):
        super(TikWorkItem, self).__init__()

        self.work = work_obj
        #
        fnt = QtGui.QFont('Open Sans', 10)
        fnt.setBold(False)
        self.setEditable(False)

        self.setFont(fnt)
        self.setText(work_obj.name)
        self.state = None
        self.set_state("working")

    def set_state(self, state):
        self.state = state
        self.setForeground(QtGui.QColor(*self.color_dict[state]))


class TikCategoryModel(QtGui.QStandardItemModel):
    columns = ["name", "id", "path", "creator", "dcc", "date", "version count"]

    def __init__(self):
        super(TikCategoryModel, self).__init__()

        self.setHorizontalHeaderLabels(self.columns)

        self._works = []
        self._publishes = []

    def clear(self):
        self.setRowCount(0)

    def set_works(self, works_list):
        # TODO: validate
        self._works = works_list
        self.populate()

    def populate(self):
        self.clear()
        for work in self._works:
            self.append_work(work)

    def append_work(self, work):
        """Append a work to the model."""
        _item = TikWorkItem(work)
        pid = QtGui.QStandardItem(str(work.id))
        path = QtGui.QStandardItem(work.path)
        creator = QtGui.QStandardItem(work.creator)
        dcc = QtGui.QStandardItem(work.dcc)
        date = QtGui.QStandardItem(datetime.fromtimestamp(work.date_modified).strftime('%Y/%m/%d %H:%M:%S'))
        version_count = QtGui.QStandardItem(str(work.version_count))

        self.appendRow([_item, pid, path, creator, dcc, date, version_count])

        return _item

    @staticmethod
    def check_data(structure_object):
        """checks if this is a proper structural data"""
        return structure_object


class TikCategoryView(QtWidgets.QTreeView):
    item_selected = QtCore.Signal(object)

    def __init__(self, parent=None):
        super(TikCategoryView, self).__init__(parent)
        self._feedback = Feedback(parent=self)
        self.setUniformRowHeights(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        # do not show branches
        self.setRootIsDecorated(False)

        self.model = TikCategoryModel()
        self.proxy_model = QtCore.QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setRecursiveFilteringEnabled(True)
        self.setSortingEnabled(True)

        self.setModel(self.proxy_model)

        # SIGNALS

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.right_click_menu)

        # create another context menu for columns
        self.header().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.header().customContextMenuRequested.connect(self.header_right_click_menu)

        # self.clicked.connect(self.item_clicked)

        self.expandAll()

    def select_by_id(self, unique_id):
        """Selects the item with the given id"""
        for row in range(self.model.rowCount()):
            idx = self.model.index(row, 1)
            if idx.data() == str(unique_id):
                idx = idx.sibling(idx.row(), 0)
                index = self.proxy_model.mapFromSource(idx)
                self.setCurrentIndex(index)
                return True
        return False

    def currentChanged(self, *args, **kwargs):
        super(TikCategoryView, self).currentChanged(*args, **kwargs)
        self.item_clicked(self.currentIndex())

    def get_selected_item(self):
        """Return the current item"""
        idx = self.currentIndex()
        if not idx.isValid():
            return None
        idx = idx.sibling(idx.row(), 0)

        # the id needs to mapped from proxy to source
        index = self.proxy_model.mapToSource(idx)
        _item = self.model.itemFromIndex(index)
        return _item

    def item_clicked(self, idx):
        """Emit the item_selected signal when an item is clicked"""
        # block signals to prevent infinite loop
        self.blockSignals(True)
        # make sure the index is pointing to the first column
        idx = idx.sibling(idx.row(), 0)

        # the id needs to mapped from proxy to source
        index = self.proxy_model.mapToSource(idx)
        _item = self.model.itemFromIndex(index)

        self.blockSignals(False)
        if _item:
            self.item_selected.emit(_item.work)
        else:
            self.item_selected.emit(None)

    def expandAll(self):
        """Expand all the items in the view"""
        super(TikCategoryView, self).expandAll()
        self.resizeColumnToContents(0)

    def hide_columns(self, columns):
        """ If the given column exists in the model, hides it"""
        if not isinstance(columns, list):
            columns = [columns]

        for column in columns:
            if column in self.model.columns:
                self.setColumnHidden(self.model.columns.index(column), True)

    def unhide_columns(self, columns):
        """ If the given column exists in the model, unhides it"""
        if not isinstance(columns, list):
            columns = [columns]

        for column in columns:
            if column in self.model.columns:
                self.setColumnHidden(self.model.columns.index(column), False)

    def toggle_column(self, column, state):
        """ If the given column exists in the model, unhides it"""
        if state:
            self.unhide_columns(column)
        else:
            self.hide_columns(column)

    def filter(self, text):
        """Filter the model"""
        self.proxy_model.setFilterRegExp(QtCore.QRegExp(text, QtCore.Qt.CaseInsensitive, QtCore.QRegExp.RegExp))

    def header_right_click_menu(self, position):
        menu = QtWidgets.QMenu(self)

        # add checkable actions for each column
        for column in self.model.columns:
            action = QtWidgets.QAction(column, self)
            action.setCheckable(True)
            action.setChecked(not self.isColumnHidden(self.model.columns.index(column)))
            # connect the action to the column's visibility
            action.toggled.connect(lambda state, c=column: self.toggle_column(c, state))

            menu.addAction(action)

        menu.exec_(self.mapToGlobal(position))

    def right_click_menu(self, position):
        indexes = self.sender().selectedIndexes()
        index_under_pointer = self.indexAt(position)
        right_click_menu = QtWidgets.QMenu(self)
        if not index_under_pointer.isValid():
            return
        # make sure the idx is pointing to the first column
        index_under_pointer = index_under_pointer.sibling(index_under_pointer.row(), 0)
        mapped_index = self.proxy_model.mapToSource(index_under_pointer)
        item = self.model.itemFromIndex(mapped_index)
        if len(indexes) > 0:
            level = 0
            index = indexes[0]
            while index.parent().isValid():
                index = index.parent()
                level += 1
        else:
            level = 0
        act_edit_sub = right_click_menu.addAction(self.tr("Edit Task"))
        act_edit_sub.triggered.connect(lambda _, x=item: self.edit_sub_project(item))
        act_delete_sub = right_click_menu.addAction(self.tr("Delete Task"))
        act_delete_sub.triggered.connect(lambda _, x=item: self.delete_task(item))
        right_click_menu.exec_(self.sender().viewport().mapToGlobal(position))

    def refresh(self):
        """Re-populates the model keeping the expanded state"""
        self.model.populate()

class TikCategoryLayout(QtWidgets.QVBoxLayout):
    def __init__(self, *args, **kwargs):
        super(TikCategoryLayout, self).__init__(*args, **kwargs)

        self.setContentsMargins(0, 0, 0, 0)

        self.label = QtWidgets.QLabel("Works")
        self.label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.addWidget(self.label)
        # create a separator label
        self.separator = QtWidgets.QLabel()
        self.separator.setFrameShape(QtWidgets.QFrame.HLine)
        self.separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.separator.setStyleSheet("background-color: rgb(174, 215, 91);")
        self.separator.setFixedHeight(1)
        self.addWidget(self.separator)


        # create two radio buttons one for work and one for publish
        self.work_radio_button = QtWidgets.QRadioButton("Work")
        # make the radio button label larger
        self.work_radio_button.setFont(QtGui.QFont("Arial", 10))
        self.publish_radio_button = QtWidgets.QRadioButton("Publish")
        self.publish_radio_button.setFont(QtGui.QFont("Arial", 10))

        # TODO: this needs to come from the last state of the user
        self.work_radio_button.setChecked(True)

        # create a horizontal layout for the radio buttons
        self.radio_button_layout = QtWidgets.QHBoxLayout()
        self.radio_button_layout.setSpacing(6)
        self.radio_button_layout.addWidget(self.work_radio_button)
        self.radio_button_layout.addWidget(self.publish_radio_button)

        # add a spacer to the layout
        self.radio_button_layout.addStretch()

        # add the radio button layout to the main layout
        self.addLayout(self.radio_button_layout)


        self.category_tab_widget = QtWidgets.QTabWidget()
        self.category_tab_widget.setMaximumSize(QtCore.QSize(16777215, 23))
        self.category_tab_widget.setTabPosition(QtWidgets.QTabWidget.North)
        self.category_tab_widget.setElideMode(QtCore.Qt.ElideNone)
        self.category_tab_widget.setUsesScrollButtons(True)
        self.category_tab_widget.setObjectName("category_tab_widget")
        self.addWidget(self.category_tab_widget)

        self.work_tree_view = TikCategoryView()
        self.addWidget(self.work_tree_view)

        self.filter_le = QtWidgets.QLineEdit()
        self.addWidget(self.filter_le)
        self.filter_le.textChanged.connect(self.work_tree_view.filter)
        self.filter_le.setPlaceholderText("Filter")
        self.filter_le.setClearButtonEnabled(True)
        self.filter_le.setFocus()
        self.filter_le.returnPressed.connect(self.work_tree_view.setFocus)


        self.task = None

        # SIGNALS

        self.category_tab_widget.currentChanged.connect(self.on_category_change)

        # TODO: get this from the last state of the user
        self._last_category = None

    def get_category_index(self):
        """Get the index of the category."""
        if self._last_category:
            for idx, category in enumerate(self.task.categories.keys()):
                if category == self._last_category:
                    return idx
        return 0

    def set_category_by_index(self, category_index):
        """Set the category by index"""
        self.category_tab_widget.setCurrentIndex(category_index)
        self.on_category_change(category_index)

    def set_task(self, task):
        """Set the task"""
        if not task:
            self.clear()
            return
        self.task = task
        self.populate_categories(self.task.categories)

        # set the current tab to the first tab
        idx = self.get_category_index()
        self.category_tab_widget.setCurrentIndex(idx)
        self.on_category_change(idx)
        self.work_tree_view.expandAll()

    def populate_categories(self, categories):
        """Populate the layout with categories"""
        # clear the layout
        self.category_tab_widget.blockSignals(True)
        self.category_tab_widget.clear()
        for key, category in categories.items():
            self.pre_tab = QtWidgets.QWidget()
            self.pre_tab.setObjectName(key)
            self.category_tab_widget.addTab(self.pre_tab, key)
            # self.append_category(category)
        self.category_tab_widget.blockSignals(False)


    def on_category_change(self, index):
        """When the category tab changes"""
        # get the current tab name
        self._last_category = self.category_tab_widget.tabText(index)
        if self.work_radio_button.isChecked():
            works = self.task.categories[self._last_category].works
            self.work_tree_view.model.set_works(works.values())
        else:
            pass

    def clear(self):
        """Refresh the layout"""
        self.category_tab_widget.blockSignals(True)
        self.category_tab_widget.clear()
        self.work_tree_view.model.clear()
        self.category_tab_widget.blockSignals(False)

# test the TikCategoryLayout
if __name__ == "__main__":
    import sys
    from time import sleep
    import os
    import tik_manager4

    app = QtWidgets.QApplication(sys.argv)

    test_project_path = os.path.join(os.path.expanduser("~"), "t4_test_manual_DO_NOT_USE")
    tik = tik_manager4.initialize("Standalone")
    tik.user.set("Admin", "1234")
    tik.set_project(test_project_path)

    # get an example task
    # tasks = tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks
    tasks = tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].scan_tasks()
    example_task_a = tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["superman"]
    example_task_b = tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["batman"]

    # create a test dialog and add the layout
    test_dialog = QtWidgets.QDialog()
    category_layout = TikCategoryLayout()
    category_layout.set_task(example_task_a)
    # show the category layout
    test_dialog.setWindowTitle("TikCategoryLayout Test")
    test_dialog.setLayout(category_layout)
    # resize the dialog
    test_dialog.resize(800, 600)
    test_dialog.show()


    app.exec_()

    sys.exit(app.exec_())
