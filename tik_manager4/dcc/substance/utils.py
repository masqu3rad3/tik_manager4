"""Utility functions for Substance Painter."""

import substance_painter

from tik_manager4.ui.Qt import QtGui

def get_save_project_action():
        """Return the QAction which triggers Substance Painter's save project action."""
        main_window = substance_painter.ui.get_main_window()

        menubar = main_window.menuBar()
        save_action = None
        for action in menubar.actions():
            menu = action.menu()
            if not menu:
                continue
            if menu.objectName() != "file":
                continue

            save_action = next(action for action in menu.actions() if action.shortcut() == QtGui.QKeySequence.Save)
            break
        return save_action

def get_scene_path():
    """Get the current scene path."""
    if not substance_painter.project.is_open():
        return ""

    file_path = substance_painter.project.file_path()
    # for some reason when the file is not saved,
    # substance returns .spt file as file path.
    if file_path and file_path.endswith(".spt"):
        return ""

    return file_path
