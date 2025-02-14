
from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.dcc.extension_core import ExtensionCore
from tik_manager4.ui.dialog.feedback import Feedback
from tik_manager4.dcc.max import utils


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

        set_ranges_action = QtWidgets.QAction("&Set Ranges", self.parent)
        self.menu_item.addAction(set_ranges_action)

        set_ranges_action.triggered.connect(lambda: self.on_set_ranges())

    def on_set_ranges(self):
        """Preview."""
        work, version = self.get_work_and_version()
        if not work or not version:
            return
        task = self.tik.project.find_task_by_id(work.task_id)
        metadata = task.metadata

        range_start = metadata.get_value(
            "start_frame", fallback_value=None
        )
        range_end = metadata.get_value(
            "end_frame", fallback_value=None
        )
        # if neither start or end frame is found in the metadata
        if not range_start and not range_end:
            self.feedback.pop_info(
                title="No Start and End Frame",
                text="Cannot find start and end frame in the metadata."
            )

        current_range = utils.get_ranges()
        set_start = range_start or current_range[0]
        set_end = range_end or current_range[-1]

        utils.set_ranges([set_start, set_start, set_end, set_end])

