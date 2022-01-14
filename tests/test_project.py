"""Tests for Project related functions"""
import os
import shutil
# import uuid
from .mockup import Mockup, clean_user
from tik_manager4.objects import user


class TestProject:
    """Uses a fresh mockup_common folder and test_project under user directory for all tests"""
    # _salt = str(uuid.uuid4()).split("-")[-1]
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
    def test_resolution_and_fps(self):
        pass

    @clean_user
    def test_create_new_project(self):
        # no user permission
        test_project_path = os.path.join(os.path.expanduser("~"), "t4_test_project_DO_NOT_USE")
        if os.path.exists(test_project_path):
            shutil.rmtree(test_project_path)
        assert self.tik.create_project(test_project_path, structure_template="asset_shot") == \
               (-1, "This user does not have rights to perform this action")
        self.tik.user.set_active_user("Admin")
        assert self.tik.create_project(test_project_path, structure_template="asset_shot") == \
               (-1, "User is not authenticated")
        self.tik.user.authenticate("1234")
        assert self.tik.create_project(test_project_path, structure_template="hedehot") == (1, "Success")
        assert self.tik.create_project(test_project_path, structure_template="empty") == \
               (-1, "Project already exists. Aborting")
        shutil.rmtree(test_project_path)
        assert self.tik.create_project(test_project_path, structure_template="asset_shot", resolution=[3840, 2160],
                                       fps=30) == (1, "Success")
