"""Tests for the UI elements."""
import os
import pytest

IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"
if IN_GITHUB_ACTIONS:
    pytest.skip("Skipping UI tests in GitHub Actions", allow_module_level=True)

from pathlib import Path
import shutil
import sys
from tik_manager4.core import utils

import tik_manager4
from tik_manager4.ui import main
from tik_manager4.ui.Qt import QtWidgets, QtGui
from tik_manager4.ui import pick
from tik_manager4.ui.dialog.work_dialog import NewWorkDialog, NewVersionDialog
from tik_manager4.ui.dialog.preview_dialog import PreviewDialog
from tik_manager4.ui.dialog.project_dialog import SetProjectDialog
from tik_manager4.ui.dialog.publish_dialog import PublishSceneDialog
from tik_manager4.ui.dialog.settings_dialog import SettingsDialog
from tik_manager4.ui.dialog.user_dialog import NewUserDialog
from tik_manager4.ui.dialog.work_dialog import NewWorkDialog
from tik_manager4.ui.dialog.feedback import Feedback
from tik_manager4.ui.widgets import common

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

    def _kill_modules(self):
        kill_list = []
        for name, _module in sys.modules.items():
            if name.startswith("tik_manager4"):
                kill_list.append(name)
        for x in kill_list:
            sys.modules.pop(x)

    def test_launch_main_ui(self, qtbot):
        m = main.launch(dcc="Standalone")
        qtbot.addWidget(m)
        assert m.windowTitle() == main.WINDOW_NAME
        assert m.objectName() == main.WINDOW_NAME

    def test_launch_ui_with_wrong_dcc(self, qtbot):
        # make sure all the modules are reloaded
        self._kill_modules()

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
        self._kill_modules()
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
                monkeypatch.setattr(m.feedback, "pop_info", lambda *args, **kwargs: None)
                monkeypatch.setattr(NewWorkDialog, "exec_", lambda *args: QtWidgets.QMessageBox.Yes)
                monkeypatch.setattr(Feedback, "pop_info", lambda *args, **kwargs: None)

                if button_text == "Save New Work":
                    button.click()
                elif button_text == "Increment Version":
                    # monkeypatch the pop_info method of m.feedback to return None
                    button.click()
                elif button_text == "Ingest Version":
                    # monkeypatch the pop_info method of m.feedback to return None
                    button.click()
                elif button_text == "Publish":
                    button.click()

    def test_feedback_pop_ups(self, qtbot, monkeypatch):
        """Test the feedback module"""

        feedback = Feedback()
        monkeypatch.setattr(common.TikMessageBox, "exec_", lambda *args: QtWidgets.QMessageBox.Yes)
        feedback.pop_info(title="Test", text="Test", details="Test", critical=False, button_label="Test", modal=False)
        feedback.pop_info(title="Test", text="Test", details="Test", critical=True, button_label="Test", modal=True)
        feedback.pop_question(title="Test", text="Test", details="Test", buttons=["yes", "no", "cancel"], modal=False)
        feedback.pop_question(title="Test", text="Test", details="Test", buttons=["save", "continue", "ok"], modal=True)

    def test_preview_dialog(self, qtbot, main_object):
        # create a new work
        main_object.project.scan_tasks()
        work = main_object.project.tasks["main"].categories["Model"].create_work("test_work")
        dialog = PreviewDialog(work, 1)
        qtbot.addWidget(dialog)
        style_file = pick.style_file()
        dialog.setStyleSheet(str(style_file.readAll(), "utf-8"))
        dialog.show()
        # qtbot.stop()

    def test_project_dialog(self, qtbot, main_object):
        dialog = SetProjectDialog(main_object)
        qtbot.addWidget(dialog)
        style_file = pick.style_file()
        dialog.setStyleSheet(str(style_file.readAll(), "utf-8"))
        dialog.show()
        # qtbot.stop()

    def test_publish_dialog(self, qtbot, monkeypatch, main_object):
        # create a new work
        main_object.project.scan_tasks()
        work = main_object.project.tasks["main"].categories["Model"].create_work("test_work")
        # main_object.project.publisher._work_object = work
        monkeypatch.setattr(main_object.project, "get_current_work", lambda: (work, 1))
        main_object.project.publisher.resolve()
        dialog = PublishSceneDialog(main_object.project)
        qtbot.addWidget(dialog)
        style_file = pick.style_file()
        dialog.setStyleSheet(str(style_file.readAll(), "utf-8"))
        dialog.show()
        # qtbot.stop()

    def test_settings_dialog(self, qtbot, main_object):
        dialog = SettingsDialog(main_object)
        qtbot.addWidget(dialog)
        style_file = pick.style_file()
        dialog.setStyleSheet(str(style_file.readAll(), "utf-8"))
        dialog.show()
        # qtbot.stop()

    def test_user_dialog(self, qtbot, main_object):
        dialog = NewUserDialog(main_object.user)
        qtbot.addWidget(dialog)
        style_file = pick.style_file()
        dialog.setStyleSheet(str(style_file.readAll(), "utf-8"))
        dialog.show()
        # qtbot.stop()

    def test_create_new_work_dialog(self, qtbot, main_object):
        dialog = NewWorkDialog(main_object)
        qtbot.addWidget(dialog)
        style_file = pick.style_file()
        dialog.setStyleSheet(str(style_file.readAll(), "utf-8"))
        dialog.show()
        # qtbot.stop()

    def test_create_new_version_dialog(self, qtbot, main_object):
        main_object.project.scan_tasks()
        work = main_object.project.tasks["main"].categories["Model"].create_work("test_work")
        dialog = NewVersionDialog(work, ingest=False)
        qtbot.addWidget(dialog)
        style_file = pick.style_file()
        dialog.setStyleSheet(str(style_file.readAll(), "utf-8"))
        dialog.show()
        # qtbot.stop()

    def test_create_new_version_dialog_ingest(self, qtbot, main_object):
        main_object.project.scan_tasks()
        work = main_object.project.tasks["main"].categories["Model"].create_work("test_work")
        dialog = NewVersionDialog(work, ingest=True)
        qtbot.addWidget(dialog)
        style_file = pick.style_file()
        dialog.setStyleSheet(str(style_file.readAll(), "utf-8"))
        dialog.show()
        # qtbot.stop()

    # def test_standard_item_model(self, qtmodeltester):
    #     model = QtGui.QStandardItemModel()
    #     items = [QtGui.QStandardItem(str(i)) for i in range(4)]
    #     model.setItem(0, 0, items[0])
    #     model.setItem(0, 1, items[1])
    #     model.setItem(1, 0, items[2])
    #     model.setItem(1, 1, items[3])
    #     qtmodeltester.check(model)