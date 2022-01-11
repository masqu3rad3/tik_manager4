"""Tests for Project related functions"""
import os
from .mockup import Mockup, clean_user
from tik_manager4.objects import user


class TestProject:
    """Uses a fresh mockup_common folder and test_project under user directory for all tests"""
    mock = Mockup()
    mock.prepare()
    user.User(commons_directory=mock.common)  # this is for not popping up the "missing common folder" message
    from tik_manager4.objects.main import Main  # importing main checks the common folder definition, thats why its here
    tik = Main()

    @clean_user
    def test_default_project_paths(self):
        assert self.tik.project.path == "" # this is overridden by project class and must always return empty string
        assert self.tik.project.absolute_path == os.path.join(os.path.expanduser("~"), "TM4_default")
        assert self.tik.project.database_path == os.path.join(os.path.expanduser("~"), "TM4_default", "tikDatabase")
        assert self.tik.project.name == "TM4_default"

    @clean_user
    def test_create_new_project(self):
        self.tik.user.set_active_user("Admin", password="1234")
        test_project_path = os.path.join(os.path.expanduser("~"), "t4_test_project")
        assert self.tik.create_project(test_project_path, "asset_shot") == (1, "Success")