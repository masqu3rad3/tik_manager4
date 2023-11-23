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

    def test_create_a_sub_project(self, project):
        """Test to create a subproject."""
        sub_project = project.create_sub_project("test_subproject", parent_path="")
        assert sub_project != -1
        assert sub_project.path == "test_subproject"

    def test_delete_a_sub_project(self, project):
        """Test to delete a subproject."""
        self.test_create_a_sub_project(project)
        # try to delete a non existing sub-project
        assert project.delete_sub_project(path="non_existing_subproject") == -1
        # delete an existing one
        assert project.delete_sub_project(path="test_subproject") == 1

    def test_create_a_task(self, project):
        """Test to create a task"""
        self.test_create_a_sub_project(project)
        task = project.create_task("test_task", categories=["Model", "Rig", "LookDev"],
                                       parent_path="test_subproject")
        assert task.name == "test_task"
        assert task.creator == "Admin"
        assert list(task.categories.keys()) == ["Model", "Rig", "LookDev"]
        assert task.path == "test_subproject"
        return task

    # @pytest.mark.parametrize("category", ["Model", "Rig", "LookDev"])
    def test_create_a_work(self, project, category="Model"):
        """Tests creating a work"""
        test_task = self.test_create_a_task(project)
        cmds.file(new=True, force=True)
        # create a cube and save it as a work with binary format
        test_cube = cmds.polyCube(name="test_cube")
        work_obj = test_task.categories[category].create_work("test_cube", file_format=".mb", notes="This is the test cube.")

        assert work_obj.name == f"test_task_{category}_test_cube"
        assert work_obj.creator == "Admin"
        assert work_obj.category == category
        assert work_obj.dcc == "Maya"
        assert len(work_obj.versions) == 1
        assert work_obj.task_name == "test_task"
        assert work_obj.task_id == test_task.id
        assert work_obj.path == f"test_subproject/test_task/{category}/Maya"
        assert work_obj.state == "working"

        # iterate a version with .ma format
        work_obj = test_task.categories[category].create_work("test_cube", file_format=".ma", notes="Same cube. Only ma format.")
        assert len(work_obj.versions) == 2

        # iterate another version scaling the cube
        cmds.setAttr("test_cube.scale", 4, 4, 4)
        work_obj = test_task.categories[category].create_work("test_cube", notes="Scaled the cube.")
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

    @pytest.mark.parametrize("category", ["Rig", "LookDev", "Model"])
    def test_publishing_from_work(self, project, category):
        """Test to publish a work."""
        # create works for each category
        work_obj = self.test_create_a_work(project, category=category)
        # attempt to resolve a work with an empty scene
        cmds.file(new=True, force=True)
        assert project.publisher.resolve() == False

        work_obj.load_version(2)

        # publish the same work 3 times
        for count in range(1, 4):
            # RESOLVE
            project.publisher.resolve()
            assert work_obj.path == project.publisher._work_object.path
            assert work_obj.name == project.publisher._work_object.name
            assert work_obj.id == project.publisher._work_object.id
            assert project.publisher.publish_version == count
            if category == "Model":
                assert project.publisher.extract_names == ["scene", "alembic"]
                assert project.publisher.validation_names == ["unique_names", "forbidden_nodes"]
            # TODO add the extracts and validations as they are implemented

            assert project.publisher.relative_data_path == f"tikDatabase/test_subproject/test_task/{category}/Maya/publish/test_task_{category}_test_cube"
            assert project.publisher.relative_scene_path == f"test_subproject/test_task/{category}/Maya/publish/test_task_{category}_test_cube"

            # RESERVE
            project.publisher.reserve()
            with pytest.raises(ValueError):
                # try to reserve a publish with the same version
                project.publisher.reserve()
            assert project.publisher._published_object.get_property("name") == f"test_task_{category}_test_cube"
            assert project.publisher._published_object.get_property("creator") == "Admin"
            assert project.publisher._published_object.get_property("category") == category
            assert project.publisher._published_object.get_property("dcc") == "Maya"
            assert project.publisher._published_object.get_property("version") == count
            assert project.publisher._published_object.get_property("work_version") == 2
            assert project.publisher._published_object.get_property("task_name") == "test_task"
            assert project.publisher._published_object.get_property("path") == f"test_subproject/test_task/{category}/Maya/publish"

            assert isinstance(project.publisher.publish_name, str)
            _data_path = Path(project.publisher.absolute_data_path)
            assert _data_path.exists()
            assert _data_path.is_dir()
            # scene folder should not be created yet
            assert project.publisher.absolute_scene_path


            # VALIDATE
            project.publisher.validate()
            for val_name, val_object in project.publisher._resolved_validators.items():
                assert val_object.state == "passed"

            # EXTRACT
            project.publisher.extract()
            for ext_name, ext_object in project.publisher._resolved_extractors.items():
                assert ext_object.status == "extracted"

            # PUBLISH
            project.publisher.publish()
            for element in project.publisher._published_object.get_property("elements"):
                # path is relative, get the absolute against the root
                # element_path = Path(project.publisher._published_object.guard.project_root, element["path"])
                element_path = Path(project.publisher._published_object.get_abs_project_path(), element["path"])
                assert Path(element_path).exists()

        return work_obj

    def test_scanning_publishes(self, project):
        """Test to scan the publishes."""
        # create a work
        work_obj = self.test_publishing_from_work(project, category="Model")

        for file_path, publish_obj in work_obj.publishes.items():
            assert Path(file_path).exists()
            assert publish_obj.name == work_obj.name
            assert publish_obj.creator == work_obj.creator
            assert publish_obj.category == work_obj.category
            assert publish_obj.dcc == work_obj.dcc
            assert isinstance(publish_obj.version, int)
            assert publish_obj.task_name == work_obj.task_name
            assert publish_obj.task_id == work_obj.task_id
            assert isinstance(publish_obj.publish_id, int)
            assert isinstance(publish_obj.relative_path, str)
            assert isinstance(publish_obj.software_version, str)
            assert publish_obj.is_promoted() == False
            assert Path(publish_obj.get_abs_project_path()).exists()
            assert publish_obj.dcc_version == work_obj.dcc_version
            for element in publish_obj.elements:
                assert isinstance(element["type"], str)
                element_path = Path(publish_obj.get_abs_project_path(), element["path"])
                assert element_path.exists()

    def test_promoting_publish(self, project):
        """Test to promote a publish."""
        # create a work
        work_obj = self.test_publishing_from_work(project, category="Model")
        # promote the first publish
        for file_path, publish_obj in work_obj.publishes.items():
            assert publish_obj.is_promoted() == False
            publish_obj.promote()
            assert publish_obj.is_promoted() == True



