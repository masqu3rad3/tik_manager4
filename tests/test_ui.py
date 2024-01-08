"""Tests for the UI elements."""
from pathlib import Path
import shutil
import pytest
import sys
from tik_manager4.core import utils

import tik_manager4
from tik_manager4.ui import main
from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.ui.dialog.work_dialog import NewWorkDialog, NewVersionDialog
from tik_manager4.ui.dialog.publish_dialog import PublishSceneDialog
from tik_manager4.ui.dialog.feedback import Feedback

class TestUI:
    """Test UI."""

    @pytest.fixture(scope='function')
    def main_object(self, tik):
        project_path = Path(utils.get_home_dir(), "t4_UI_test_project_DO_NOT_USE")
        if project_path.exists():
            shutil.rmtree(str(project_path))
        tik.user.set("Admin", "1234")
        tik.create_project(str(project_path), structure_template="empty")
        return tik


    def test_launch_main_ui(self, qtbot):
        m = main.launch(dcc="Standalone")
        qtbot.addWidget(m)
        assert m.windowTitle() == main.WINDOW_NAME
        assert m.objectName() == main.WINDOW_NAME

    def test_launch_ui_with_wrong_dcc(self, qtbot):
        # make sure all the modules are reloaded
        kill_list = []
        for name, _module in sys.modules.items():
            if name.startswith("tik_manager4"):
                kill_list.append(name)
        for x in kill_list:
            sys.modules.pop(x)

        with pytest.raises(ImportError) as e_info:
            main.launch(dcc="Maya")
            assert e_info == "cannot import name 'cmds' from 'maya' (unknown location)"

    def test_launch_ui_manually(self, qtbot, main_object):
        parent = main_object.dcc.get_main_window()
        m = main.MainUI(main_object, parent=parent)
        m.show()
        qtbot.addWidget(m)
        assert m.windowTitle() == main.WINDOW_NAME
        assert m.objectName() == main.WINDOW_NAME

    def test_main_ui_buttons(self, qtbot, main_object, monkeypatch):
        m = main.launch(dcc="Standalone")
        m.show()
        qtbot.addWidget(m)

        # Test buttons
        # get all the buttons under work_buttons_layout
        buttons_layout = m.work_buttons_layout
        widget_count = buttons_layout.count()
        for nmb in range(widget_count):
            button = buttons_layout.itemAt(nmb).widget()
            if button:
                button_text = button.text()
                if button_text == "Save New Work":
                    monkeypatch.setattr(NewWorkDialog, "exec_", lambda *args: QtWidgets.QMessageBox.Yes)
                    button.click()
                elif button_text == "Increment Version":
                    monkeypatch.setattr(m.feedback, "pop_info", lambda *args: QtWidgets.QMessageBox.Yes)
                    button.click()
                elif button_text == "Ingest Version":
                    monkeypatch.setattr(m.feedback, "pop_info", lambda *args, **kwargs: QtWidgets.QMessageBox.Yes)
                    button.click()
                # elif button_text == "Publish":
                #     monkeypatch.setattr(PublishSceneDialog.feedback, "pop_info", lambda *args: QtWidgets.QMessageBox.Yes)
                #     button.click()
                # else:
                #     print(button)
                #     print(button.text())
                #     raise ValueError("Button not found")

