"""Reload all references in the current Maya scene."""

import logging

from maya import cmds


from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.dcc.extension_core import ExtensionCore
from tik_manager4.ui.dialog.feedback import Feedback
from tik_manager4.ui import pick

LOG = logging.getLogger(__name__)


class ReloadReferences(ExtensionCore):
    """Reload all references in the current Maya scene."""

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

        reload_references_action = QtWidgets.QAction(pick.icon("reload"), "&Reload All References  ", self.parent)
        self.menu_item.addAction(reload_references_action)

        reload_references_action.triggered.connect(lambda: self.on_reload_references())

    def on_reload_references(self):
        """Reload all references in the current scene."""
        # Get all references in the scene
        references = cmds.file(query=True, reference=True)

        # Reload each reference
        for ref in references:
            try:
                cmds.file(ref, loadReference=True)
                cmds.inViewMessage(
                    assistMessage='<span style="color: #FE7E00;">All References Reloaded</span>',
                    position='topCenter', backColor=0x00000000  ,fade=True)

                # cmds.inViewMessage(amg='Reload complete.', pos='topCenter', fade=True)

            except Exception as e:
                LOG.error(f"Failed to reload {ref}: {e}")
                cmds.inViewMessage(
                    assistMessage='<span style="color: #000000;">Reload Failed - Check log output for details</span>',
                    position='topCenter', backColor=0x00FF0000, fade=True)
