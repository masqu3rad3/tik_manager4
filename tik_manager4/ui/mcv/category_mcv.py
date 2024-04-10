# pylint: disable=consider-using-f-string
# pylint: disable=super-with-arguments

from datetime import datetime

from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
from tik_manager4.ui.dialog.feedback import Feedback
from tik_manager4.ui.dialog.work_dialog import NewVersionDialog
from tik_manager4.ui.widgets.common import VerticalSeparator


class TikWorkItem(QtGui.QStandardItem):
    state_color_dict = {
        "working": (255, 255, 0),
        "published": (0, 255, 0),
        "omitted": (255, 255, 0),
        "promoted": (0, 255, 0),
    }

    def __init__(self, work_obj):
        super(TikWorkItem, self).__init__()

        self.tik_obj = work_obj
        #
        self.fnt = QtGui.QFont("Open Sans", 10)
        self.fnt.setBold(False)

        self.setEditable(False)

        self.setFont(self.fnt)
        self.setText(work_obj.name)
        self.state = None
        self.refresh()

    def refresh(self):
        self.set_state(self.tik_obj.state)

    def set_state(self, state):
        self.state = state
        _state_color = self.state_color_dict[state]
        # cross out omitted items
        self.fnt.setStrikeOut(state == "omitted")
        self.setFont(self.fnt)
        # if the work not saved with the same dcc of the current dcc, make it italic
        if not self.dcc_check():
            self.fnt.setItalic(True)
            self.setFont(self.fnt)
            _state_color = tuple([int(x * 0.5) for x in _state_color])
        self.setForeground(QtGui.QColor(*_state_color))

    def dcc_check(self):
        """Checks if the dcc of the work matches the dcc of the current session"""
        return self.tik_obj.dcc.lower() == self.tik_obj.guard.dcc.lower()


class TikPublishItem(QtGui.QStandardItem):
    state_color_dict = {
        "working": (0, 255, 255),
        "published": (0, 255, 255),
        "omitted": (0, 255, 255),
        "promoted": (0, 255, 0),
    }

    def __init__(self, publish_obj):
        super(TikPublishItem, self).__init__()

        self.tik_obj = publish_obj

        self.fnt = QtGui.QFont("Open Sans", 10)
        self.fnt.setBold(False)
        self.setEditable(False)

        self.setFont(self.fnt)
        self.setText(str(publish_obj.name))
        self.state = None
        # self.setForeground(QtGui.QColor(*self.state_color_dict["publish"]))
        self.refresh()

    def refresh(self):
        self.set_state(self.tik_obj.state)

    def set_state(self, state):
        self.state = state
        _state_color = self.state_color_dict[state]
        # cross out omitted items
        self.fnt.setStrikeOut(state == "omitted")
        self.setFont(self.fnt)
        # if the work not saved with the same dcc of the current dcc, make it italic
        if not self.dcc_check():
            self.fnt.setItalic(True)
            self.setFont(self.fnt)
            _state_color = tuple([int(x * 0.5) for x in _state_color])
        self.setForeground(QtGui.QColor(*_state_color))

    def dcc_check(self):
        """Checks if the dcc of the work matches the dcc of the current session"""
        return self.tik_obj.dcc == self.tik_obj.guard.dcc


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

    def set_publishes(self, publishes_list):
        self._publishes = publishes_list
        self.populate(publishes=True)

    def populate(self, publishes=False):
        self.clear()
        if not publishes:
            for work in self._works:
                self.append_work(work)
        else:
            for publish in self._publishes:
                self.append_publish(publish)

    def append_publish(self, publish):
        """Append a publish to the model."""
        _item = TikPublishItem(publish)
        pid = QtGui.QStandardItem(str(publish.publish_id))
        path = QtGui.QStandardItem(publish.path)
        creator = QtGui.QStandardItem("NA")
        dcc = QtGui.QStandardItem(publish.dcc)
        date = QtGui.QStandardItem("NA")
        version_count = QtGui.QStandardItem(str(publish.version_count))

        self.appendRow([_item, pid, path, creator, dcc, date, version_count])

        # test
        # test = TikPublishItem(publish)
        # _item.appendRow([test, pid, path, creator, dcc, date, version_count])
        # test [END]

        return _item

    def append_work(self, work):
        """Append a work to the model."""
        _item = TikWorkItem(work)
        pid = QtGui.QStandardItem(str(work.id))
        path = QtGui.QStandardItem(work.path)
        creator = QtGui.QStandardItem(work.creator)
        dcc = QtGui.QStandardItem(work.dcc)
        date = QtGui.QStandardItem(
            datetime.fromtimestamp(work.date_modified).strftime("%Y/%m/%d %H:%M:%S")
        )
        version_count = QtGui.QStandardItem(str(work.version_count))

        self.appendRow([_item, pid, path, creator, dcc, date, version_count])

        return _item

    @staticmethod
    def check_data(structure_object):
        """checks if this is a proper structural data"""
        return structure_object


class TikCategoryView(QtWidgets.QTreeView):
    item_selected = QtCore.Signal(object)
    version_created = QtCore.Signal()
    file_dropped = QtCore.Signal(str)
    load_event = (
        QtCore.Signal()
    )  # the signal for main UI importing the selected version of the selected work
    import_event = (
        QtCore.Signal()
    )  # the signal for main UI importing the selected version of the selected work

    def __init__(self, parent=None):
        super(TikCategoryView, self).__init__(parent)
        self.feedback = Feedback(parent=self)
        self.setUniformRowHeights(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        # do not show branches
        self.setRootIsDecorated(False)
        # self.setRootIsDecorated(True)

        # make it expandable
        self.setExpandsOnDoubleClick(True)

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

        self.setAcceptDrops(True)

        self.expandAll()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
            # Extract file path from dropped URLs
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                self.file_dropped.emit(file_path)
        else:
            event.ignore()

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
            self.item_selected.emit(_item.tik_obj)
        else:
            self.item_selected.emit(None)

    def expandAll(self):
        """Expand all the items in the view"""
        super(TikCategoryView, self).expandAll()
        self.resizeColumnToContents(0)

    def hide_columns(self, columns):
        """If the given column exists in the model, hides it"""
        if not isinstance(columns, list):
            columns = [columns]

        for column in columns:
            if column in self.model.columns:
                self.setColumnHidden(self.model.columns.index(column), True)

    def unhide_columns(self, columns):
        """If the given column exists in the model, unhides it"""
        if not isinstance(columns, list):
            columns = [columns]

        for column in columns:
            if column in self.model.columns:
                self.setColumnHidden(self.model.columns.index(column), False)

    def toggle_column(self, column, state):
        """If the given column exists in the model, unhides it"""
        if state:
            self.unhide_columns(column)
        else:
            self.hide_columns(column)

    def show_columns(self, list_of_columns):
        """Shows the given columns."""
        for column in list_of_columns:
            self.unhide_columns(column)

    def get_visible_columns(self):
        """Returns the visible columns."""
        return [
            self.model.columns[x]
            for x in range(self.model.columnCount())
            if not self.isColumnHidden(x)
        ]

    def get_column_sizes(self):
        """Return all column sizes in a dictionary."""
        return {x: int(self.columnWidth(x)) for x in range(self.model.columnCount())}

    def set_column_sizes(self, column_sizes):
        """Set the column sizes from the given dictionary."""
        for column, size in column_sizes.items():
            self.setColumnWidth(int(column), size)

    def filter(self, text):
        """Filter the model"""
        self.proxy_model.setFilterRegExp(
            QtCore.QRegExp(text, QtCore.Qt.CaseInsensitive, QtCore.QRegExp.RegExp)
        )

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

        # if the item is a work, add the ingest action
        if item.tik_obj.object_type == "work":
            ingest_act = right_click_menu.addAction(self.tr("Ingest Here"))
            ingest_act.triggered.connect(lambda _=None, x=item: self.ingest_here(item))
            right_click_menu.addSeparator()

        load_act = right_click_menu.addAction(self.tr("Load"))
        load_act.triggered.connect(self.load_event.emit)
        import_act = right_click_menu.addAction(self.tr("Import To the Scene"))
        import_act.triggered.connect(self.import_event.emit)
        right_click_menu.addSeparator()
        open_database_folder_act = right_click_menu.addAction(
            self.tr("Open Database Folder")
        )
        open_database_folder_act.triggered.connect(
            lambda _=None, x=item: self.open_database_folder(item)
        )
        open_scene_folder_act = right_click_menu.addAction(self.tr("Open Scene Folder"))
        open_scene_folder_act.triggered.connect(
            lambda _=None, x=item: self.open_scene_folder(item)
        )
        # separator
        right_click_menu.addSeparator()
        copy_scene_path_act = right_click_menu.addAction(
            self.tr("Copy Scene Directory to Clipboard")
        )
        copy_scene_path_act.triggered.connect(
            lambda _=None, x=item: self.copy_scene_path(item)
        )

        right_click_menu.addSeparator()

        delete_item_act = right_click_menu.addAction(self.tr("Revive Work/Publish"))
        delete_item_act.triggered.connect(lambda _=None, x=item: self.revive_item(item))
        delete_item_act = right_click_menu.addAction(self.tr("Omit Work/Publish"))
        delete_item_act.triggered.connect(lambda _=None, x=item: self.omit_item(item))
        delete_item_act = right_click_menu.addAction(self.tr("Delete Work/Publish"))
        delete_item_act.triggered.connect(lambda _=None, x=item: self.delete_item(item))

        right_click_menu.exec_(self.sender().viewport().mapToGlobal(position))

    def refresh(self):
        """Re-populates the model keeping the expanded state"""
        self.model.populate()

    @staticmethod
    def metadata_pre_checks(dcc_handler, metadata):
        """Collection of pre-checks for the metadata method."""
        metadata_fps = metadata.get_value("fps", None)
        current_fps = dcc_handler.get_scene_fps()
        if metadata_fps and current_fps:  # if the dcc supports fps and metadata has a value
            if current_fps != metadata_fps:
                msg = f"The current fps ({current_fps}) does not match with the defined fps ({metadata_fps})."
                yield msg
        metadata_start_frame = metadata.get_value("start_frame", None)
        metadata_end_frame = metadata.get_value("end_frame", None)
        raw_frame_range = dcc_handler.get_ranges()
        start_mismatch = False
        end_mismatch = False
        if any([metadata_start_frame,
                metadata_end_frame]) and raw_frame_range:  # if the dcc supports range and metadata has a value
            if metadata_start_frame:
                if float(metadata_start_frame) != float(raw_frame_range[0]):
                    start_mismatch = True
            if metadata_end_frame:
                if float(metadata_end_frame) != float(raw_frame_range[-1]):
                    end_mismatch = True
            if start_mismatch or end_mismatch:
                msg = f"The current frame range ({raw_frame_range[0], raw_frame_range[-1]}) does not match with the defined frame range ({[metadata_start_frame, metadata_end_frame]})."
                yield msg

    def new_version_pre_checks(self, work_obj, metadata):
        """Collection of pre-checks for the new version method."""
        dcc_version_mismatch = work_obj.check_dcc_version_mismatch()
        if dcc_version_mismatch:
            msg = ("The current DCC version does not match the version of the work or metadata definition.\n\n"
                f"Current DCC version: {dcc_version_mismatch[1]}\n"
                f"Defined DCC version: {dcc_version_mismatch[0]}\n\n")
            yield msg

        for msg in self.metadata_pre_checks(work_obj._dcc_handler, metadata):
            yield msg

    def ingest_here(self, item):
        """Send the ingest signal with the given item"""
        # first check for permissions
        if item.tik_obj.check_permissions(level=1) == -1:
            msg = "This user does not have permissions for this action."
            self.feedback.pop_info(title="Permission Error", text=msg)
            return

        # get the metadata for the checks.
        parent_task = item.tik_obj.parent_task
        metadata = parent_task.parent_sub.metadata

        # check the dcc for any issues that may prevent saving.
        dcc_issues = item.tik_obj.guard.dcc_handler.pre_save_issues()
        if dcc_issues:
            self.feedback.pop_info(title="DCC Error", text=dcc_issues, critical=True)
            return
        pre_checks = self.new_version_pre_checks(item.tik_obj, metadata)

        if not item.dcc_check():
            self.feedback.pop_info(
                title="DCC Mismatch",
                text="The current DCC does not match the DCC of the work.",
                critical=True,
            )
            return

        for check_msg in pre_checks:
            question = self.feedback.pop_question(
                title="Metadata Mismatch",
                text=f"{check_msg}\n\nDo you want to continue?",
                buttons=["continue", "cancel"]
            )
            if question == "cancel":
                return

        dialog = NewVersionDialog(work_object=item.tik_obj, parent=self, ingest=True)
        state = dialog.exec_()
        if state:
            # emit a version_created signal to update the main window
            self.version_created.emit()

    def open_database_folder(self, item):
        """Opens the database folder for the given item"""
        item.tik_obj.show_database_folder()

    def open_scene_folder(self, item):
        """Opens the scene folder for the given item"""
        item.tik_obj.show_project_folder()

    def copy_scene_path(self, item):
        """Copy the absolute path of the scene file to the clipboard"""
        item.tik_obj.copy_path_to_clipboard(item.tik_obj.get_abs_project_path())

    def omit_item(self, item):
        """Omits the given item"""
        item.tik_obj.omit()
        item.refresh()

    def revive_item(self, item):
        """Revives the given item"""
        item.tik_obj.revive()
        item.refresh()

    def delete_item(self, item):
        """Deletes the given item"""

        # lets make pre-check for permissions:
        state, msg = item.tik_obj.check_destroy_permissions()
        if not state:
            self.feedback.pop_info(title="Permission error", text=msg, critical=True)
            return

        if item.tik_obj.object_type == "work":
            are_you_sure = self.feedback.pop_question(
                title="Are you sure?",
                text=f"You are about to delete '{item.tik_obj.name}' completely.\n\n"
                     "This will delete ALL VERSIONS and ALL PUBLISHES of this work.\n\n"
                     "This action cannot be undone.\n"
                     "Are you sure you want to continue?",
                buttons=["yes", "cancel"]
            )
            if are_you_sure == "cancel":
                return
            # double check if there is a publish under this work
            if item.tik_obj.publish.versions:
                are_you_sure = self.feedback.pop_question(
                    title="Are you REALLY sure?",
                    text="There are published versions under this work.\n\n"
                         "ALL PUBLISHES and ALL WORK VERSIONS will be deleted.\n\n"
                         "This action cannot be undone.\n"
                         "Are you REALLY sure you want to continue?",
                    buttons=["yes", "cancel"]
                )
                if are_you_sure == "cancel":
                    return
        elif item.tik_obj.object_type == "publish":
            are_you_sure = self.feedback.pop_question(
                title="Are you sure?",
                text=f"You are about to delete '{item.tik_obj.name}' completely.\n\n"
                     "This will delete ALL VERSIONS of this publish.\n\n"
                     "This action cannot be undone.\n"
                     "Are you sure you want to continue?",
                buttons=["yes", "cancel"]
            )
            if are_you_sure == "cancel":
                return

        item.tik_obj.destroy()
        # remove the item from the model
        self.model.removeRow(item.row())



class TikCategoryLayout(QtWidgets.QVBoxLayout):
    mode_changed = QtCore.Signal(int)

    def __init__(self, *args, **kwargs):
        super(TikCategoryLayout, self).__init__(*args, **kwargs)

        self.setContentsMargins(0, 0, 0, 0)

        self.label = QtWidgets.QLabel("Works")
        self.label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.addWidget(self.label)
        self.addWidget(VerticalSeparator(color=(174, 215, 91)))

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
        self.work_radio_button.clicked.connect(self.on_mode_change)
        self.publish_radio_button.clicked.connect(self.on_mode_change)

        # TODO: get this from the last state of the user
        self._last_category = None
        self.mode = 0  # 0 = work, 1 = publish

        for idx in range(1, self.work_tree_view.header().count()):
            self.work_tree_view.hideColumn(idx)

    def get_active_category(self):
        """Get the active category object and return it."""
        if self.task and self.category_tab_widget.currentWidget():
            return self.task.categories[
                self.category_tab_widget.currentWidget().objectName()
            ]
        return None

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
            category.scan_works()
            self.pre_tab = QtWidgets.QWidget()
            self.pre_tab.setObjectName(key)
            self.category_tab_widget.addTab(self.pre_tab, key)
        self.category_tab_widget.blockSignals(False)

    def on_mode_change(self, _event):
        """Change the mode."""
        if self.work_radio_button.isChecked():
            self.mode = 0
            self.mode_changed.emit(0)
        else:
            self.mode = 1
            self.mode_changed.emit(1)
        self.category_tab_widget.currentChanged.emit(
            self.category_tab_widget.currentIndex()
        )

    def on_category_change(self, index):
        """Do this when the category tab changes."""
        if not self.task:
            return
        # get the current tab name
        self._last_category = self.category_tab_widget.tabText(index)
        if not self._last_category:
            return
        works = self.task.categories[self._last_category].works
        if self.mode == 0 and self._last_category:
            self.work_tree_view.model.set_works(works.values())
        else:
            _publishes = [
                work_obj.publish
                for work_obj in works.values()
                if work_obj.publish.versions
            ]
            self.work_tree_view.model.set_publishes(_publishes)

    def clear(self):
        """Refresh the layout"""
        self.category_tab_widget.blockSignals(True)
        self.category_tab_widget.clear()
        self.work_tree_view.model.clear()
        self.category_tab_widget.blockSignals(False)


# test the TikCategoryLayout
if __name__ == "__main__":
    import sys
    import os
    import tik_manager4

    app = QtWidgets.QApplication(sys.argv)

    test_project_path = os.path.join(
        os.path.expanduser("~"), "t4_test_manual_DO_NOT_USE"
    )
    tik = tik_manager4.initialize("Standalone")
    tik.user.set("Admin", "1234")
    tik.set_project(test_project_path)

    # get an example task
    tasks = tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].scan_tasks()
    example_task_a = (
        tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["superman"]
    )
    example_task_b = (
        tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["batman"]
    )

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
