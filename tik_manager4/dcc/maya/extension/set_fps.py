
from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.dcc.extension_core import ExtensionCore
from tik_manager4.ui.dialog.preview_dialog import PreviewDialog
from tik_manager4.ui.dialog.feedback import Feedback
from tik_manager4.dcc.maya import utils


class Preview(ExtensionCore):
    """Test Extension."""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.tik = parent.tik
        self.feedback = Feedback(parent=self.parent)
        self.menu_item = None

    def execute(self):
        """Execute."""
        self.add_main_menu()

    def add_main_menu(self):
        """Add the extension commands to the main menu."""
        if not self.menu_item:
            raise ValueError("Menu item is not set.")

        set_fps_action = QtWidgets.QAction("&Set FPS", self.parent)
        self.menu_item.addAction(set_fps_action)

        set_fps_action.triggered.connect(lambda: self.on_set_fps())

    def on_set_fps(self):
        """Preview."""
        work, version = self.get_work_and_version()
        if not work or not version:
            return
        task = self.tik.project.find_task_by_id(work.task_id)
        metadata = task.metadata

        fps = metadata.get_value(
            "fps", fallback_value=None
        )

        # if neither start or end frame is found in the metadata
        if not fps:
            self.feedback.pop_info(
                title="No FPS set",
                text="Cannot find fps value in the metadata."
            )

        utils.set_scene_fps(fps)