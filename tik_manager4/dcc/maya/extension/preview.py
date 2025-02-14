
from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.dcc.extension_core import ExtensionCore
from tik_manager4.ui.dialog.preview_dialog import PreviewDialog
from tik_manager4.ui import pick


class Preview(ExtensionCore):
    """Test Extension."""

    def __init__(self, parent):
        super().__init__(parent)
        self.menu_item = None

    def execute(self):
        """TEsting."""
        self.add_main_menu()

    def add_main_menu(self):
        """Add the extension commands to the main menu."""
        # Check if the menu already exists
        if not self.menu_item:
            raise ValueError("Menu item is not set.")

        preview_action = QtWidgets.QAction(
                pick.icon("camera"), "&Create Preview", self.parent
            )
        self.menu_item.addAction(preview_action)

        preview_action.triggered.connect(lambda: self.on_create_preview())

    def on_create_preview(self):
        """Preview."""
        work, version = self.get_work_and_version()
        if not work or not version:
            return
        task = self.tik.project.find_task_by_id(work.task_id)
        metadata = task.metadata

        resolution = metadata.get_value(
            "resolution", fallback_value=None
        )
        range_start = metadata.get_value(
            "start_frame", fallback_value=None
        )
        range_end = metadata.get_value(
            "end_frame", fallback_value=None
        )
        range_list = [range_start, range_end]

        dialog = PreviewDialog(
            work_object=work,
            version=version,
            resolution=resolution,
            frame_range=range_list,
            parent=self.parent,
        )
        dialog.show()


