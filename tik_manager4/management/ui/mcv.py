"""Model View Controller for Platform management."""

# import functools

import os
import tempfile
import urllib.request
import urllib.error
# import requests

from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui
# we need to import the QtNetwork module from Qt like this to make sure it's
# available with pyinstaller
# from tik_manager4.ui import Qt
from tik_manager4.ui.widgets.pop import WaitDialog
from tik_manager4.ui.widgets.common import TikIconButton
from tik_manager4.ui import pick

class ProjectItem(QtGui.QStandardItem):
    """Item for the project model."""

    def __init__(self, definition_dict):
        """Initialize the item."""
        super().__init__()
        self.project_definition = definition_dict
        self.setText(definition_dict.get("name", "No Name"))

        # Show the thumbnail from URL
        self._empty_thumbnail = pick.icon("empty_thumbnail")
        url = definition_dict.get("image", None)
        headers = definition_dict.get("image_authorization_headers", {})
        self._load_icon_from_url(url, authorization_headers=headers)

    def _load_icon_from_url(self, url, authorization_headers=None):
        """Load the icon from the URL using urllib."""
        authorization_headers = authorization_headers or {}
        if not url:
            self.setIcon(self._empty_thumbnail)
            return

        try:
            request = urllib.request.Request(url, headers=authorization_headers)
            with urllib.request.urlopen(request) as response:
                content = response.read()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name

            pixmap = QtGui.QPixmap(temp_file_path)
            self.setIcon(QtGui.QIcon(pixmap))
            os.remove(temp_file_path)
        except (urllib.error.URLError, urllib.error.HTTPError):
            self.setIcon(self._empty_thumbnail)

# class ProjectItem(QtGui.QStandardItem):
#     """Item for the project model."""
#
#     def __init__(self, definition_dict):
#         """Initialize the item."""
#         super().__init__()
#         self.project_definition = definition_dict
#         self.setText(definition_dict.get("name", "No Name"))
#
#         # show the thumbnail from url
#         self._empty_thumbnail = pick.icon("empty_thumbnail")
#         url = definition_dict.get("image", None)
#         headers = definition_dict.get("image_authorization_headers", {})
#         self._load_icon_from_url(url, authorization_headers=headers)
#
#     def _load_icon_from_url(self, url, authorization_headers=None):
#         """Load the icon from the url."""
#         authorization_headers = authorization_headers or {}
#         if not url:
#             self.setIcon(self._empty_thumbnail)
#             return
#         try:
#             response = requests.get(url, headers=authorization_headers)
#             response.raise_for_status()
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
#                 temp_file.write(response.content)
#                 temp_file_path = temp_file.name
#
#             pixmap = QtGui.QPixmap(temp_file_path)
#             self.setIcon(QtGui.QIcon(pixmap))
#             os.remove(temp_file_path)
#         except requests.RequestException:
#             self.setIcon(self._empty_thumbnail)

class ProjectColumnItem(QtGui.QStandardItem):
    """Item for the columns of the project model."""

    # pylint: disable=too-few-public-methods
    def __init__(self, text):
        """Initialize the item."""
        super().__init__(text)
        self.setEditable(False)


class ProjectModel(QtGui.QStandardItemModel):
    """Model for the Shotgrid projects."""

    columns = ["Name", "Id", "Status", "Start Date", "End Date"]
    filter_key = "super"

    def __init__(self, project_data=None):
        """Initialize the model."""
        super().__init__()
        self._project_data = project_data or []

        self.setHorizontalHeaderLabels(self.columns)
        if project_data:
            self.populate_model()

    @property
    def project_data(self):
        """Return the project data."""
        return self._project_data

    @project_data.setter
    def project_data(self, data):
        """Set the project data and populate the model."""
        self._project_data = data
        self.populate_model()

    def populate_model(self):
        """Populate the model with the project data."""
        self.setRowCount(0)
        for project in self._project_data:
            self._append_project(project)

    def _append_project(self, project):
        """Append a project to the model."""
        item = ProjectItem(project)
        _id = ProjectColumnItem(str(project.get("id", "")))
        _status = ProjectColumnItem(project.get("sg_status", "") or project.get("status", ""))
        _start_date = ProjectColumnItem(project.get("start_date", ""))
        _end_date = ProjectColumnItem(project.get("end_date", ""))

        self.appendRow([item, _id, _status, _start_date, _end_date])
        return item


class ProjectIconView(QtWidgets.QListView):
    """Custom QListView for the Management platform."""

    # pylint: disable=too-few-public-methods
    def __init__(self):
        """Initialize the view."""
        super().__init__()
        self.setAlternatingRowColors(False)
        self.setViewMode(QtWidgets.QListView.IconMode)
        self.setMovement(QtWidgets.QListView.Static)
        self.setResizeMode(QtWidgets.QListView.Adjust)

    def set_size(self, size):
        """Set the size of the icons in the view."""
        _size = size + 40
        self.setIconSize(QtCore.QSize(_size, _size))
        self.setGridSize(QtCore.QSize(int(_size * 1.1), int(_size * 1.4)))


class ProjectTreeView(QtWidgets.QTreeView):
    """Custom QTreeView for the Management platform."""

    def __init__(self):
        """Initialize the view."""
        super().__init__()
        self.setAlternatingRowColors(False)
        self.setSortingEnabled(True)
        self.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setIndentation(20)
        self.setUniformRowHeights(True)
        self.setWordWrap(True)
        self.setAllColumnsShowFocus(True)
        self.setAnimated(True)
        self.setIndentation(20)
        self.setRootIsDecorated(False)

        # adjust the size of the columns

    def expandAll(self):  # pylint: disable=invalid-name
        """Expand all the items in the view and resize the columns."""
        super().expandAll()
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)
        self.resizeColumnToContents(2)
        self.resizeColumnToContents(3)
        self.resizeColumnToContents(4)

    def set_size(self, size):
        """Set the size of the icons in the view."""
        self.setIconSize(QtCore.QSize(size, size))


class LayoutsDataContainer:
    """Layouts data container for the Management platform."""

    def __init__(self):
        self.master_layout: (QtWidgets.QVBoxLayout, QtWidgets.QHBoxLayout) = (
            QtWidgets.QVBoxLayout()
        )
        self.button_layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        self.widget_layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        self.__post_init__()

    def __post_init__(self):
        self.master_layout.addLayout(self.button_layout)
        self.master_layout.addLayout(self.widget_layout)


class WidgetDataContainer:
    """Widget data container for the Management platform."""
    def __init__(self):
        self.list_view: QtWidgets.QListView = ProjectTreeView()
        self.icon_view: QtWidgets.QListView = ProjectIconView()
        self.icon_size_slider: QtWidgets.QSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.list_view_button: QtWidgets.QPushButton = TikIconButton(icon_name="view-list", circle=False)
        self.icon_view_button: QtWidgets.QPushButton = TikIconButton(icon_name="view-icon", circle=False)
        self.__post_init__()

    def __post_init__(self):
        self.icon_size_slider.setFixedSize(QtCore.QSize(200, 50))
        self.icon_size_slider.setMinimum(20)
        self.icon_size_slider.setMaximum(250)
        self.icon_size_slider.setValue(40)
        self.icon_size_slider.setTickInterval(10)
        self.icon_size_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)


class ProjectPickWidget(QtWidgets.QWidget):
    """Widget to pick a project from Management Platform."""

    def __init__(self, management_handler, parent=None):
        super().__init__()
        # self.tik_main = management_handler.tik_main

        self.model = ProjectModel()

        self.layouts = LayoutsDataContainer()
        self.setLayout(self.layouts.master_layout)

        self.widgets = WidgetDataContainer()

        self.wait_dialog = WaitDialog(
            message=f"Please wait while collecting projects from {management_handler.nice_name}...",
            parent=parent,
        )
        self.wait_dialog.show()

        self.model.project_data = management_handler.get_projects()

        self.wait_dialog.close()

        self.build_ui()

        self.widgets.list_view.expandAll()

    def build_ui(self):
        """Put widgets into layouts and connect signals."""
        # crete two buttons at the top to switch between list and icon view
        self.layouts.button_layout.addWidget(self.widgets.list_view_button)

        self.layouts.button_layout.addWidget(self.widgets.icon_view_button)
        self.layouts.button_layout.addStretch()

        self.widgets.list_view.setModel(self.model)
        self.layouts.widget_layout.addWidget(self.widgets.list_view)
        # self.icon_view = SgProjectIconView()
        self.widgets.icon_view.setModel(self.model)
        self.layouts.widget_layout.addWidget(self.widgets.icon_view)

        self.layouts.widget_layout.addWidget(self.widgets.icon_size_slider)
        self.on_size_changed(self.widgets.icon_size_slider.value())

        # self.layouts.widget_layout.addWidget(self.widgets.test_button)

        # SIGNALS
        self.widgets.list_view_button.clicked.connect(self.show_list_view)
        self.widgets.icon_view_button.clicked.connect(self.show_icon_view)
        self.widgets.icon_size_slider.valueChanged.connect(self.on_size_changed)

        # self.widgets.test_button.clicked.connect(self.get_selected_item)

        # show the list view by default
        self.show_list_view()

    def show_list_view(self):
        """Show the list view and hide the icon view."""
        self.widgets.list_view.show()
        self.widgets.icon_view.hide()

    def show_icon_view(self):
        """Show the icon view and hide the list view."""
        self.widgets.list_view.hide()
        self.widgets.icon_view.show()

    def on_size_changed(self, value):
        """Change the size of the icons in the icon view."""
        self.widgets.icon_view.set_size(value)
        self.widgets.list_view.set_size(value)

    def get_selected_item(self):
        """Return the selected project definition."""
        if self.widgets.list_view.isVisible():
            selected_indices = self.widgets.list_view.selectedIndexes()
        else:
            selected_indices = self.widgets.icon_view.selectedIndexes()
        if selected_indices:
            item = self.model.itemFromIndex(selected_indices[0])
            return item.project_definition
        return None

    def get_selected_project_id(self):
        """Return the selected project id."""
        item = self.get_selected_item()
        if item:
            return item.get("id")
        return None

