"""Project management related tests for Maya."""

import shutil
import pytest
from pathlib import Path
from tik_manager4.core import utils

# try to import the cmds module from maya. If it fails, skip the tests.
try:
    from maya import cmds
except ImportError:
    pytest.skip('Maya is not installed.', allow_module_level=True)


@pytest.mark.usefixtures("clean_user")
@pytest.mark.usefixtures("prepare")
class TestMayaProject():
    """Maya Project related tests."""

    @pytest.fixture(autouse=True, scope='function')
    def reset(self):
        """Reset the maya scene."""
        cmds.file(new=True, force=True)

    @pytest.fixture(scope='function')
    def project(self, tik):
        project_path = Path(utils.get_home_dir(), "t4_maya_test_project_DO_NOT_USE")
        if project_path.exists():
            shutil.rmtree(str(project_path))
        tik.user.set("Admin", "1234")
        tik.create_project(str(project_path), structure_template="empty")
        return tik.project

    def test_create_a_work(self, project):
        """Tests creating a work"""

        test_task = project.create_task("test_task", categories=["Model"], parent_uid=project.id)
        assert test_task != -1

        # create a cube and save it as a work with binary format
        test_cube = cmds.polyCube(name="test_cube")
        work_obj = test_task.categories["Model"].create_work("test_cube", file_format=".mb", notes="This is the test cube.")

        assert work_obj.name == "test_task_Model_test_cube"
        assert work_obj.creator == "Admin"
        assert work_obj.category == "Model"
        assert work_obj.dcc == "Maya"
        assert len(work_obj.versions) == 1
        assert work_obj.task_name == "test_task"
        assert work_obj.task_id == test_task.id
        assert work_obj.path == "test_task/Model"
        assert work_obj.state == "working"

        # iterate a version with .ma format
        work_obj = test_task.categories["Model"].create_work("test_cube", file_format=".ma", notes="Same cube. Only ma format.")
        assert len(work_obj.versions) == 2

        # iterate another version scaling the cube
        cmds.setAttr("test_cube.scale", 4, 4, 4)
        work_obj = test_task.categories["Model"].create_work("test_cube", notes="Scaled the cube.")
        assert len(work_obj.versions) == 3
        return work_obj

    def test_getting_current_work(self, project):
        """Test for getting work object from the scene."""

        _compare_work_obj = self.test_create_a_work(project)

        # reset the scene
        cmds.file(new=True, force=True)
        # try getting the work object from a scene without a work.
        assert project.get_current_work() == (None, None)

        # open the scene and get the work object
        _compare_work_obj.load_version(2)
        test_work, version = project.get_current_work()
        assert test_work.name == _compare_work_obj.name
        assert test_work.id == _compare_work_obj.id

    def test_publishing_a_work(self, project):
        """Test to publish a work."""
        work_obj = self.test_create_a_work(project)

        work_obj.load_version(2)

        print("WIP")
        pass
