import sys
import os
from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
from tik_manager4.ui.dialog.new_subproject import NewSubproject
from tik_manager4.ui.dialog.new_task import NewTask
from tik_manager4.ui.dialog.feedback import Feedback
# from tik_manager4.objects import main
from tik_manager4.objects import guard
import tik_manager4

class TikSubItem(QtGui.QStandardItem):
    color_dict = {
        "subproject": (255, 255, 255)
    }
    def __init__(self, sub_obj):
        super(TikSubItem, self).__init__()
        self.subproject = sub_obj
        #
        fnt = QtGui.QFont('Open Sans', 12)
        fnt.setBold(False)
        self.setEditable(False)
        # raise

        self.setForeground(QtGui.QColor(255, 255, 255))
        self.setFont(fnt)
        self.setText(sub_obj.name)

class TikColumnItem(QtGui.QStandardItem):
    def __init__(self, name, overridden=False):
        super(TikColumnItem, self).__init__()
        self.setEditable(False)
        self.setText(name)
        if overridden:
            self.tag_overridden()
        else:
            self.tag_normal()
    def tag_overridden(self):
        fnt = QtGui.QFont('Open Sans', 10)
        fnt.setBold(False)
        # make it yellow
        self.setForeground(QtGui.QColor(255, 255, 0))
        self.setFont(fnt)

    def tag_normal(self):
        fnt = QtGui.QFont('Open Sans', 10)
        fnt.setBold(False)
        self.setFont(fnt)

class TikSubModel(QtGui.QStandardItemModel):
    # columns = list(guard.Guard.commons.metadata.keys())
    # columns = ["name", "id", "path", "resolution", "fps", "mode"]
    filter_key = ""
    def __init__(self, structure_object):
        super(TikSubModel, self).__init__()
        self.columns = ["name", "id", "path"] + list(guard.Guard.commons.metadata.properties.keys())

        self.setHorizontalHeaderLabels(self.columns)

        self.project = None
        self.set_data(structure_object)





    def set_data(self, structure_object):
        self.project = structure_object

    def populate(self):
        self.setRowCount(0)
        visited = []
        queue = []

        # start with the initial dictionary with self subproject
        all_data = {
            "id": self.project.id,
            "name": self.project.name,
            "path": self.project.path,
            # "resolution": self.project.resolution,
            # "fps": self.project.fps,
            # "mode": self.project.mode,
            "tasks": self.project.tasks,
            # "categories": [category.name for category in self.project.categories],
            "subs": [],  # this will be filled with the while loop
        }

        # add the initial dictionary and self into the queue
        # Each queue item is a list.
        # first element is the dictionary point and second is the subproject object
        parent_row = self
        queue.append([all_data, self.project, parent_row])

        while queue:
            current = queue.pop(0)
            parent = current[0]
            sub = current[1]
            sub.scan_tasks()
            parent_row = current[2]

            for neighbour in list(sub.subs.values()):
                if neighbour not in visited:
                    sub_data = {
                        "id": neighbour.id,
                        "name": neighbour.name,
                        "path": neighbour.path,
                        "tasks": neighbour.tasks,
                        "subs": [],  # this will be filled with the while loop
                    }
                    parent["subs"].append(sub_data)
                    _item = self.append_sub(neighbour, parent_row)

                    # add tasks
                    neighbour.scan_tasks()
                    visited.append(neighbour)
                    queue.append([sub_data, neighbour, _item])

        return all_data

    def append_sub(self, sub_obj, parent):
        _sub_item = TikSubItem(sub_obj)
        _row = [_sub_item]
        # generate the column texts
        # id and path are mandatory, start with them
        _row.append(TikColumnItem(str(sub_obj.id)))
        _row.append(TikColumnItem(sub_obj.path))
        for column in self.columns[3:]: # skip the first 3 columns which are mandatory
            # get the override status
            _column_value = sub_obj.metadata.get_value(column, "")
            _overridden = sub_obj.metadata.is_overridden(column)
            _column_item = TikColumnItem(str(_column_value), _overridden)
            _row.append(_column_item)

        parent.appendRow(_row)
        return _sub_item

    # search all model tree for a given id
    # def find_sub(self, sub_id):
    #     for row in range(self.rowCount()):
    #         _item = self.item(row)
    #         if _item.subproject.id == sub_id:
    #             return _item
    #         else:
    #             _sub_item = self.find_sub_recursive(_item, sub_id)
    #             if _sub_item:
    #                 return _sub_item
    def find_sub_recursive(self, item, sub_id):
        for row in range(item.rowCount()):
            _item = item.child(row)
            if _item.subproject.id == sub_id:
                return _item
            else:
                _sub_item = self.find_sub_recursive(_item, sub_id)
                if _sub_item:
                    return _sub_item



class TikSubView(QtWidgets.QTreeView):
    item_selected = QtCore.Signal(object)
    add_item = QtCore.Signal(object)
    def __init__(self, project_obj=None, right_click_enabled=True):
        super(TikSubView, self).__init__()

        self._feedback = Feedback(parent=self)
        self.setUniformRowHeights(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.model = None
        if project_obj:
            self.set_project(project_obj)

        # SIGNALS

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        if right_click_enabled:
            self.customContextMenuRequested.connect(self.right_click_menu)
        self.clicked.connect(self.get_tasks)

        # create another context menu for columns
        self.header().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.header().customContextMenuRequested.connect(self.header_right_click_menu)

        self.expandAll()
        self._recursive_task_scan = False

    def get_selected_item(self):
        idx = self.currentIndex()
        if not idx.isValid():
            return None
        idx = idx.sibling(idx.row(), 0)

        # the id needs to mapped from proxy to source
        index = self.proxy_model.mapToSource(idx)
        _item = self.model.itemFromIndex(index)
        print(_item)
        return _item


    def set_recursive_task_scan(self, value):
        self._recursive_task_scan = value

    def expandAll(self):
        super(TikSubView, self).expandAll()
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)
        self.resizeColumnToContents(2)
        self.resizeColumnToContents(3)
        self.resizeColumnToContents(4)

    def collect_tasks(self, sub_item, recursive=True):
        if not isinstance(sub_item, tik_manager4.objects.subproject.Subproject):
            # just to prevent crashes if something goes wrong
            return
        for key, value in sub_item.scan_tasks().items():
            yield value

        if recursive:
            queue = list(sub_item.subs.values())
            while queue:
                sub = queue.pop(0)
                for key, value in sub.scan_tasks().items():
                    yield value
                queue.extend(list(sub.subs.values()))


    def get_tasks(self, idx):
        # self.get_selected_item()
        # make sure the idx is pointing to the first column
        idx = idx.sibling(idx.row(), 0)

        # the id needs to mapped from proxy to source
        index = self.proxy_model.mapToSource(idx)
        _item = self.model.itemFromIndex(index)

        _tasks = self.collect_tasks(_item.subproject, recursive=self._recursive_task_scan)
        self.item_selected.emit(_tasks)

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


    def set_project(self, project_obj):
        self.model = TikSubModel(project_obj)
        # self.model.setFilterRegExp(QtCore.QRegExp("Ass*", QtCore.Qt.CaseInsensitive, QtCore.QRegExp.RegExp))
        # self.proxy_model = QtCore.QSortFilterProxyModel()

        self.proxy_model = ProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setRecursiveFilteringEnabled(True)
        self.setSortingEnabled(True)
        # set sort indicator to ascending
        self.sortByColumn(0, QtCore.Qt.AscendingOrder)
        # self.proxy_model.sort(2, QtCore.Qt.AscendingOrder)
        # self.proxy_model.setFilterRegExp(QtCore.QRegExp("Sup*", QtCore.Qt.CaseInsensitive, QtCore.QRegExp.RegExp))
        # self.setModel(self.model)
        self.setModel(self.proxy_model)

        self.model.populate()


    def filter(self, text):
        # pass
        self.proxy_model.setFilterRegExp(QtCore.QRegExp(text, QtCore.Qt.CaseInsensitive, QtCore.QRegExp.RegExp))
        # exclude TikTaskItems from the filter
        # self.proxy_model.setFilterKeyColumn(0)

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
        right_click_menu = QtWidgets.QMenu(self)
        act_new_sub = right_click_menu.addAction(self.tr("New Sub-Project"))
        act_new_sub.triggered.connect(lambda _, x=item: self.new_sub_project(item))
        act_edit_sub = right_click_menu.addAction(self.tr("Edit Sub-Project"))
        act_edit_sub.triggered.connect(lambda _, x=item: self.edit_sub_project(item))
        act_delete_sub = right_click_menu.addAction(self.tr("Delete Sub-Project"))
        act_delete_sub.triggered.connect(lambda _, x=item: self.delete_sub_project(item))

        right_click_menu.addSeparator()

        act_new_task = right_click_menu.addAction(self.tr("New Task"))
        act_new_task.triggered.connect(lambda _, x=item: self.new_task(item))

        right_click_menu.addSeparator()

        act_open_project_folder = right_click_menu.addAction(self.tr("Open Project Folder In Explorer"))
        act_open_database_folder = right_click_menu.addAction(self.tr("Open Database Folder In Explorer"))
        act_open_project_folder.triggered.connect(lambda _, x=item: item.subproject.show_project_folder())
        act_open_database_folder.triggered.connect(lambda _, x=item: item.subproject.show_database_folder())

        right_click_menu.exec_(self.sender().viewport().mapToGlobal(position))


    def new_sub_project(self, item):
        # first check for the user permission:
        if self.model.project._check_permissions(level=2) != -1:
            _dialog = NewSubproject(self.model.project, parent_sub=item.subproject, parent=self)
            state = _dialog.exec_()
            if state:
                # TODO: is this overcomplicated?
                _new_sub = _dialog.get_created_subproject()
                # Find the parent item _new_sub id
                _item_at_id_column = self.model.findItems(str(_new_sub.parent.id), QtCore.Qt.MatchRecursive, 1)[0]
                # find the index of the item
                _index = self.model.indexFromItem(_item_at_id_column)
                # make sure the index is pointing to the first column
                first_column_index = _index.sibling(_index.row(), 0)
                # get the item from index
                _item = self.model.itemFromIndex(first_column_index)

                # The reason we are doing this is that we may change the parent of the item on new subproject UI

                # self.model.append_sub(_dialog.get_created_subproject(), item)
                self.model.append_sub(_new_sub, _item)
        else:
            message, title = self.model.project.log.get_last_message()
            self._feedback.pop_info(title.capitalize(), message)

    def edit_sub_project(self, item):
        # first check for the user permission:
        if self.model.project._check_permissions(level=2) != -1:
            pass
            # TODO implement the edit subproject dialog
            # _dialog = EditSubproject(item.subproject, parent=self)
            # state = _dialog.exec_()
            # if state:
            #     self.model.update_sub(item)
        else:
            message, title = self.model.project.log.get_last_message()
            self._feedback.pop_info(title.capitalize(), message)

    def new_task(self, item):
        # first check for the user permission:
        # if self.model.project._check_permissions(level=2) != -1:
        _dialog = NewTask(self.model.project, parent_sub=item.subproject, parent=self)
        state = _dialog.exec_()
        if state:
                # emit clicked signal
                # self.item_selected.emit([_dialog.get_created_task()])
                self.add_item.emit(_dialog.get_created_task())
                # self.model.append_task(_dialog.get_created_task(), item)
        else:
            message, title = self.model.project.log.get_last_message()
            self._feedback.pop_info(title.capitalize(), message)

    def delete_sub_project(self, item):
        # Prompt the user to confirm the deletion
        message = "Are you sure you want to delete the sub-project: {}?".format(item.subproject.name)
        title = "Delete Sub-Project"
        sure = self._feedback.pop_question(title, message, buttons=["ok", "cancel"])
        if sure == "ok":
            # double check if the sub-project is not empty
            if not item.subproject.is_subproject_empty(item.subproject):
                message = "The sub-project is not empty.\n\nALL TASKS AND SUB-PROJECTS WILL BE DELETED!\n\nARE YOU " \
                          "SURE YOU WANT TO CONTINUE? "
                title = "NON EMPTY SUB-PROJECT"
                really_sure = self._feedback.pop_question(title, message, buttons=["ok", "cancel"])
                if really_sure != "ok":
                    return
            state = self.model.project.delete_sub_project(uid=item.subproject.id)
            if state != -1:
                self.model.removeRow(item.row(), item.parent().index())

                # after removing the row, find the current selected one and emit the clicked signal
                self.get_tasks(self.currentIndex())

            else:
                message, title = self.model.project.log.get_last_message()
                self._feedback.pop_info(title.capitalize(), message)
        else:
            return


class ProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(ProxyModel, self).__init__(parent)
        pass
    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        index = model.index(source_row, 0, QtCore.QModelIndex())

        item = model.itemFromIndex(index)
        if isinstance(item, TikSubItem):
            pass
            # print(item.subproject.scan_tasks())
            # return False
        # for role, value in self.excludes.iteritems():
        #     data = model.data(index, role)
        #     if data == value:
        #         return False

        return super(ProxyModel, self).filterAcceptsRow(source_row, source_parent)


class TikProjectLayout(QtWidgets.QVBoxLayout):
    def __init__(self, project_obj, recursive_enabled=True, right_click_enabled=True):
        super(TikProjectLayout, self).__init__()
        self.project_obj = project_obj
        # add a checkbox for recursive search
        if recursive_enabled:
            self.recursive_search_cb = QtWidgets.QCheckBox("Get Tasks Recursively")
            self.recursive_search_cb.setChecked(True)
            self.addWidget(self.recursive_search_cb)
        # add a search bar

        self.sub_view = TikSubView(project_obj, right_click_enabled=right_click_enabled)
        self.addWidget(self.sub_view)
        self.filter_le = QtWidgets.QLineEdit()
        self.addWidget(self.filter_le)
        self.filter_le.textChanged.connect(self.sub_view.filter)
        self.filter_le.setPlaceholderText("🔍")
        self.filter_le.setClearButtonEnabled(True)
        self.filter_le.setFocus()

        if recursive_enabled:
            self.sub_view.set_recursive_task_scan(self.recursive_search_cb.isChecked())
            self.recursive_search_cb.stateChanged.connect(self.sub_view.set_recursive_task_scan)
        self.filter_le.returnPressed.connect(self.sub_view.setFocus)


# if __name__ == '__main__':
#     test_project_path = os.path.join(os.path.expanduser("~"), "t4_test_manual_DO_NOT_USE")
#     tik = tik_manager4.initialize("Standalone")
#     tik.user._set("Admin", "1234")
#     tik.project._set(test_project_path)
#
#
#     app = QtWidgets.QApplication(sys.argv)
#     test_dialog = QtWidgets.QDialog()
#
#     dirname = os.path.dirname(os.path.abspath(__file__))
#     tik_manager_dir = os.path.abspath(os.path.join(dirname, os.pardir))
#     QtCore.QDir.addSearchPath("css", os.path.join(tik_manager_dir, "theme"))
#     QtCore.QDir.addSearchPath("rc", os.path.join(tik_manager_dir, "theme/rc"))
#
#     style_file = QtCore.QFile("css:tikManager.qss")
#     style_file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
#     test_dialog.setStyleSheet(str(style_file.readAll(), 'utf-8'))
#
#     # view = TikSubView()
#     # view.set_project(tik.project)
#     # view.hide_columns(["id", "path", "resolution", "fps"])
#     view = TikProjectLayout(tik.project)
#     test_dialog.setLayout(view)
#
#     test_dialog.show()
#     # view.show()
#     sys.exit(app.exec_())
