# pylint: skip-file
"""Tests for Project related functions"""
import time
from pathlib import Path
import shutil
from pprint import pprint
from unittest.mock import patch
import pytest

import tik_manager4
from tik_manager4.core import settings
from tik_manager4.core import utils


class TestProject:
    """Uses a fresh mockup_common folder and test_project under user directory for all tests"""

    # import tik_manager4 # importing main checks the common folder definition, thats why its here
    # tik = tik_manager4.initialize("Standalone")

    @pytest.fixture(scope="function")
    def project_default_path(self, files):
        project_path = Path(utils.get_home_dir(), "TM4_default")
        if project_path.exists():
            files.force_remove_directory(project_path)
        return str(project_path)

    @pytest.fixture(scope="function")
    def project_path(self, files):
        project_path = Path(utils.get_home_dir(), "t4_test_project_DO_NOT_USE")
        if project_path.exists():
            files.force_remove_directory(project_path)
        return str(project_path)

    @pytest.fixture(scope="function")
    def project_manual_path(self, files):
        project_path = Path(utils.get_home_dir(), "t4_test_manual_DO_NOT_USE")
        if project_path.exists():
            files.force_remove_directory(project_path)
        return str(project_path)

    def _new_asset_shot_project(self, project_path, tik):
        tik.user.set("Admin", "1234")
        tik.create_project(
            project_path,
            structure_template="asset_shot",
            resolution=[3840, 2160],
            fps=30,
        )
        return project_path

    def _new_empty_project(self, project_path, tik):
        tik.user.set("Admin", "1234")
        tik.create_project(project_path, structure_template="empty")
        return project_path

    def _create_a_subproject_task_and_work(self, project_path, tik):
        project_path = self._new_empty_project(project_path, tik)
        tik.set_project(project_path)
        sub = tik.project.create_sub_project(
            "test_subproject", mode="asset", parent_path=""
        )
        task = tik.project.create_task(
            "test_task",
            categories=["Model", "Rig", "LookDev"],
            parent_path=sub.path,
        )
        work = task.categories["Model"].create_work("test_work")
        return sub, task, work

    def test_default_project_paths(self, project_default_path, tik):
        assert (
            tik.project.path == ""
        )  # this is overridden by project class and must always return empty string
        tik.set_project(project_default_path)
        assert tik.project.absolute_path == str(
            Path(utils.get_home_dir(), "TM4_default")
        )
        assert tik.project.database_path == str(
            Path(utils.get_home_dir(), "TM4_default", "tikDatabase")
        )
        assert tik.project.name == "TM4_default"
        assert tik.project.guard.project_root == str(
            Path(utils.get_home_dir(), "TM4_default")
        )
        assert tik.project.guard.database_root == str(
            Path(utils.get_home_dir(), "TM4_default", "tikDatabase")
        )

        # test what happens when the structure file is already present.
        assert tik._create_default_project() == False

    def test_create_new_project(self, project_path, tik):
        # no user permission
        tik.user.set("Generic", "1234", save_to_db=False, clear_db=True)

        # no permission test
        assert tik.create_project(project_path, structure_template="asset_shot") == -1

        # not authenticated test
        tik.user.set("Admin")
        assert tik.create_project(project_path, structure_template="asset_shot") == -1

        tik.user.authenticate("1234")
        assert tik.create_project(project_path, structure_template="hedehot") == 1
        assert tik.create_project(project_path, structure_template="empty") == -1
        shutil.rmtree(project_path)
        assert (
            tik.create_project(
                project_path,
                structure_template="asset_shot",
                resolution=[3840, 2160],
                fps=30,
            )
            == 1
        )
        # return project_path

    def test_set_project_with_arguments(self, project_path, tik):
        test_project_path = self._new_asset_shot_project(project_path, tik)
        tik.project.__init__(path=test_project_path)
        # try to set a non-existing project
        assert tik.set_project(test_project_path) == 1
        assert tik.set_project("Burhan") == -1

    def test_create_sub_project(self, project_path, tik):
        """Tests creating sub-projects with parent id and path"""
        test_project_path = self._new_asset_shot_project(project_path, tik)
        tik.set_project(test_project_path)

        # no permission test
        tik.user.set("Generic")
        assert tik.project.create_sub_project("testSub", parent_path="") == -1
        assert tik.project.add_sub_project("testSub") == -1

        tik.user.set("Admin", "1234")
        new_sub = tik.project.create_sub_project("testSub", parent_path="")
        assert new_sub.path == "testSub"

        # test when the parent sub doesnt exist.
        assert tik.project.create_sub_project("no_parent", parent_path="burhan") == -1

        another_sub = tik.project.create_sub_project(
            "anotherSub", parent_uid=new_sub.id
        )
        assert another_sub.path == "testSub/anotherSub"

        # test the parent.name and parent.id
        assert another_sub.parent.name == "testSub"
        assert another_sub.parent.id == new_sub.id

        # try creating an existing one
        assert tik.project.create_sub_project("anotherSub", parent_uid=new_sub.id) == -1
        assert tik.log.get_last_message() == (
            "anotherSub already exist in sub-projects of testSub",
            "warning",
        )

        # raise an exception when none of the parent_uid or parent_path is provided
        with pytest.raises(Exception):
            tik.project.create_sub_project("anotherSub")

    def test_edit_sub_project(self, project_path, tik):
        """Test editing sub-projects with parent id and path"""

        test_project_path = self._new_asset_shot_project(project_path, tik)
        tik.set_project(test_project_path)

        # first create a sub project
        tik.user.set("Admin", "1234")
        new_sub = tik.project.create_sub_project("testToEditSub", parent_path="")

        # no permission test
        tik.user.set("Generic")
        assert (
            tik.project.edit_sub_project(
                uid=new_sub.id, name="testEditedSub", resolution=[4096, 2144], fps=39
            )
            == -1
        )
        tik.user.set("Admin", "1234")
        # test with uid
        assert (
            tik.project.edit_sub_project(
                uid=new_sub.id, name="testEditedSub", resolution=[4096, 2144], fps=39
            )
            == 1
        )

        # test with path
        assert (
            tik.project.edit_sub_project(
                path=new_sub.path,
                name="testEditedSub",
                resolution=[4096, 2144],
                fps=40,
                lens=50,
            )
            == 1
        )

        # test when the parent sub cannot be found
        tik.project.edit_sub_project(path="burhan") == -1

    def test_create_a_shot_asset_project_structure(
        self, project_manual_path, tik, print_results=False
    ):
        tik.user.set("Admin", password="1234")
        tik.create_project(project_manual_path, structure_template="empty")
        tik.set_project(project_manual_path)

        assets = tik.project.add_sub_project("Assets", mode="asset")
        chars = assets.add_sub_project("Characters", fps=60)
        props = assets.add_sub_project("Props", metatest="uberMetaTestingen")
        env = assets.add_sub_project("Environment")

        leaf_assets = [
            chars.add_sub_project("Soldier"),
            props.add_sub_project("Rifle"),
            props.add_sub_project("Knife"),
            env.add_sub_project("Tree"),
            env.add_sub_project("Ground"),
            env.add_sub_project("GroundA"),
            env.add_sub_project("GroundB"),
            env.add_sub_project("GroundC"),
            env.add_sub_project("GroundD"),
        ]

        shots = tik.project.add_sub_project("Shots", mode="shot")
        sequence_a = shots.add_sub_project("SequenceA")
        leaf_shots = [
            sequence_a.add_sub_project("SHOT_010"),
            sequence_a.add_sub_project("SHOT_020"),
            sequence_a.add_sub_project("SHOT_030"),
            sequence_a.add_sub_project("SHOT_040"),
        ]

        sequence_b = shots.add_sub_project("SequenceB")
        leaf_shots.append(sequence_b.add_sub_project("SHOT_010"))
        leaf_shots.append(sequence_b.add_sub_project("SHOT_070"))
        leaf_shots.append(sequence_b.add_sub_project("SHOT_120"))

        tik.project.save_structure()
        if print_results:
            pprint(tik.project.get_sub_tree())

        return project_manual_path

    def test_validating_existing_project(self, project_manual_path, tik):
        """Tests reading an existing project structure and compares it to the created one on-the-fly"""
        test_project_path = self.test_create_a_shot_asset_project_structure(
            project_manual_path, tik
        )
        current_subtree = tik.project.get_sub_tree()
        tik.set_project(test_project_path)
        existing_subtree = tik.project.get_sub_tree()
        pprint(existing_subtree)
        assert (
            current_subtree == existing_subtree
        ), "Read and Write of project structure does not match"

    def test_delete_sub_project(self, project_manual_path, tik):
        """Test deleting sub-projects."""
        sub, task, work = self._create_a_subproject_task_and_work(
            project_manual_path, tik
        )

        soft_sub = sub.add_sub_project("soft_sub")

        # delete sub-project without an uid or path will raise an Exception
        with pytest.raises(Exception):
            tik.project.delete_sub_project(uid=None, path=None)

        # not permissions to delete
        tik.user.set("Generic", password="1234")
        assert tik.project.delete_sub_project(uid=sub.id) == -1

        # not enough permissions for populated sub-projects
        tik.user.set("Experienced", password="1234")
        assert tik.project.delete_sub_project(uid=sub.id) == -1

        # wrong uid
        tik.user.set("Admin", password="1234")
        assert tik.project.delete_sub_project(uid=-999) == -1

        # wrong path
        assert tik.project.delete_sub_project(path="Burhan/Altintop") == -1

        # delete with uid
        assert tik.project.delete_sub_project(uid=soft_sub.id) == 1

        # delete with path
        assert tik.project.delete_sub_project(path=sub.path) == 1

    # def test_deleting_sub_projects(self, project_manual_path, tik):
    #     """Tests deleting the sub-projects"""
    #     test_project_path = self.test_create_a_shot_asset_project_structure(
    #         project_manual_path, tik, print_results=False
    #     )
    #     tik.set_project(test_project_path)
    #     tik.user.set("Generic")
    #     assert tik.project.delete_sub_project(path="Assets/Props") == -1
    #
    #     tik.user.set("Admin", 1234)
    #     # wrong arguments
    #     assert tik.project.delete_sub_project(path=None, uid=None) == -1
    #     # path methods
    #
    #     # non existing path
    #     assert tik.project.delete_sub_project(path="Burhan/Altintop") == -1
    #
    #     # by path
    #     assert tik.project.delete_sub_project(path="Assets/Props") == 1
    #
    #     # uid methods
    #     uid = tik.project.get_uid_by_path(path="Assets/Characters")
    #
    #     # non existing uid
    #     assert tik.project.delete_sub_project(uid=123123123123123123) == -1
    #     assert tik.project.delete_sub_project(uid=uid) == 1
    #
    #     # delete a sub-project on root
    #     assert tik.project.delete_sub_project(path="Assets") == 1

    def test_find_subs_by_path(self, project_manual_path, tik):
        test_project_path = self._new_asset_shot_project(project_manual_path, tik)
        tik.set_project(test_project_path)
        sub_by_path = tik.project.find_sub_by_path("Assets")
        assert sub_by_path.path == "Assets"
        assert tik.project.find_sub_by_path("Burhan/Altintop") == -1

    def test_find_subs_by_id(self, project_manual_path, tik):
        sub, task, work = self._create_a_subproject_task_and_work(
            project_manual_path, tik
        )
        assert tik.project.find_sub_by_id(sub.id) == sub
        assert sub.find_sub_by_id(sub.id) == sub
        assert tik.project.find_sub_by_id(-999) == -1

    def test_find_subs_by_wildcard(self, project_manual_path, tik):
        test_project_path = self.test_create_a_shot_asset_project_structure(
            project_manual_path, tik, print_results=False
        )
        tik.set_project(test_project_path)
        shots = tik.project.find_subs_by_wildcard("SHOT_*")
        assert shots
        assert len(shots) == 7

    def test_get_uid_and_get_path(self, project_path, tik):
        test_project_path = self._new_asset_shot_project(project_path, tik)
        tik.set_project(test_project_path)
        compare_path = "Assets/Props"
        uid = tik.project.get_uid_by_path("Assets/Props")
        path = tik.project.get_path_by_uid(uid)
        assert path == compare_path

        # non existing path
        assert tik.project.get_uid_by_path("Burhan/Altintop") == -1
        assert tik.project.get_path_by_uid(123123123123123123123) == -1

    def test_creating_and_adding_new_tasks(self, project_manual_path, tik):
        test_project_path = self.test_create_a_shot_asset_project_structure(
            project_manual_path, tik, print_results=False
        )
        tik.set_project(test_project_path)

        # create a task from the main project
        task = tik.project.create_task(
            "superman",
            categories=["Model", "Rig", "LookDev"],
            parent_path="Assets/Characters/Soldier",
        )
        assert task.file_name == "superman.ttask"
        assert task.name == "superman"
        assert task.creator == "Admin"
        assert list(task.categories.keys()) == ["Model", "Rig", "LookDev"]
        assert task.type == "asset"

        # test when neither parent_uid nor parent_path provided
        assert (
            tik.project.create_task("burhan", parent_uid=None, parent_path=None) == -1
        )

        # test creating a duplicate task with the same path.
        assert (
            tik.project.create_task(
                "superman",
                categories=["Model", "Rig", "LookDev"],
                parent_path="Assets/Characters/Soldier",
            )
            == -1
        )

        # create a task directly from a sub-project
        task = (
            tik.project.subs["Assets"]
            .subs["Characters"]
            .subs["Soldier"]
            .add_task(
                "batman", categories=["Model", "Rig", "LookDev"], task_type="Asset"
            )
        )

        # TODO make a test to create illegal categories (not defined in the category definitions)

        # try to create a duplicate task
        assert (
            tik.project.create_task(
                "superman",
                categories=["Model", "Rig", "LookDev"],
                parent_path="Assets/Characters/Soldier",
            )
            == -1
        )

        # check if the user permissions check works
        tik.user.set("Generic", password="1234")
        assert (
            tik.project.create_task(
                "this_asset_shouldnt_exist",
                categories=["Model", "Rig", "LookDev"],
                parent_path="Assets/Characters/Soldier",
            )
            == -1
        )
        # check if the log message is correct
        assert tik.log.get_last_message() == (
            "This user does not have permissions for this action",
            "warning",
        )
        tik.user.set("Admin", password="1234")

    def test_edit_task(self, project_manual_path, tik):
        test_project_path = self.test_create_a_shot_asset_project_structure(
            project_manual_path, tik, print_results=False
        )
        tik.set_project(test_project_path)

        # create a task from the main project
        task = tik.project.create_task(
            "Poseidon",
            categories=["Model", "Rig", "LookDev"],
            parent_path="Assets/Characters/Soldier",
        )

        assert task.name == "Poseidon"
        assert task.creator == "Admin"
        # assert task.reference_id == task._task_id
        assert task.id == task._task_id

        # no permissions
        tik.user.set("Generic", password="1234")
        assert (
            task.edit(
                nice_name="Aquaman",
                categories=["Model", "Rig", "LookDev", "Animation"],
                metadata_overrides={"mode": "shot"},
            )[0]
            == -1
        )
        assert tik.log.get_last_message() == (
            "This user does not have permissions for this action",
            "warning",
        )
        tik.user.set("Admin", password="1234")

        # existing task name
        existing_task = tik.project.create_task(
            "Wonderboy",
            categories=["Model", "Rig", "LookDev"],
            parent_path="Assets/Characters/Soldier",
        )

        assert (
            task.edit(
                nice_name="Wonderboy",
                categories=["Model", "Rig", "LookDev", "Animation"],
                metadata_overrides={"mode": "shot"},
            )[0]
            == -1
        )
        assert tik.log.get_last_message() == (
            "Task name 'Wonderboy' already exists in sub 'Soldier'.",
            "error",
        )

        # wrong category type
        with pytest.raises(Exception):
            task.edit(nice_name="Aquaman", categories="ThisIsWrong", metadata_overrides={"mode": "shot"})
        # category not defined
        assert (
            task.edit(
                nice_name="Aquaman",
                categories=["Model", "Rig", "LookDev", "Animation", "ThisIsWrong"],
                metadata_overrides={"mode": "shot"},
            )[0]
            == -1
        )

        # edit the task
        task.edit(
            nice_name="Aquaman",
            categories=["Model", "Rig", "LookDev", "Animation"],
            metadata_overrides={"mode": "shot"},
        )

        assert list(task.categories.keys()) == ["Model", "Rig", "LookDev", "Animation"]
        assert task.nice_name == "Aquaman"
        assert task.name == "Poseidon"

    def test_adding_categories(self, project_manual_path, tik):
        self.test_creating_and_adding_new_tasks(project_manual_path, tik)
        # add a category
        _test_tasks = (
            tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks
        )

        # try to add category without permissions
        tik.user.set("Generic", password="1234")
        assert (
            tik.project.subs["Assets"]
            .subs["Characters"]
            .subs["Soldier"]
            .tasks["batman"]
            .add_category("Temp")
            == -1
        )
        tik.user.set("Admin", password="1234")
        # add the Gotham category to Batman task
        assert (
            tik.project.subs["Assets"]
            .subs["Characters"]
            .subs["Soldier"]
            .tasks["batman"]
            .add_category("Temp")
        )

        # try to add a duplicate category
        assert (
            tik.project.subs["Assets"]
            .subs["Characters"]
            .subs["Soldier"]
            .tasks["batman"]
            .add_category("Temp")
            == -1
        )
        # check the log message
        assert tik.log.get_last_message() == (
            "'Temp' already exists in task 'batman'.",
            "warning",
        )

    def test_order_categories(self, project_manual_path, tik):
        self.test_creating_and_adding_new_tasks(project_manual_path, tik)

        # order categories
        _test_tasks = (
            tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks
        )
        assert (
            tik.project.subs["Assets"]
            .subs["Characters"]
            .subs["Soldier"]
            .tasks["superman"]
            .order_categories(["Model", "LookDev", "Rig"])
            == 1
        )

        # try to order categories without permissions
        tik.user.set("Generic", password="1234")
        assert (
            tik.project.subs["Assets"]
            .subs["Characters"]
            .subs["Soldier"]
            .tasks["superman"]
            .order_categories(["Model", "LookDev", "Rig"])
            == -1
        )
        tik.user.set("Admin", password="1234")

        # try to order categories with a wrong length
        with pytest.raises(Exception) as e_info:
            tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks[
                "superman"
            ].order_categories(["LookDev", "Model"])
        # check the log message
        assert tik.log.get_last_message() == (
            "New order list is not the same length as the current categories list.",
            "error",
        )

        # try to order categories with an item not in the current categories list
        with pytest.raises(Exception) as e_info:
            tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks[
                "superman"
            ].order_categories(["Model", "LookDev", "Temp"])
        # check the log message
        assert tik.log.get_last_message() == (
            "New order list contains a category that is not in the current categories list.",
            "error",
        )

    def test_scanning_tasks(self, project_manual_path, tik):
        sub, task, work = self._create_a_subproject_task_and_work(
            project_manual_path, tik
        )

        # self.test_creating_and_adding_new_tasks(project_manual_path, tik)

        # sub = tik.project.subs["Assets"].subs["Characters"].subs["Soldier"]
        # scan the tasks
        assert sub.scan_tasks() == sub.tasks

        # create another instance of the tik and pretend as someone else
        tik2 = tik_manager4.initialize("Standalone")
        tik2.user.set("Admin", password="1234")
        tik2.set_project(project_manual_path)
        tik2.project.subs[sub.name].add_task(
            "second_task", categories=["Model", "Rig", "LookDev"]
        )

        # scan the tasks
        assert sub.scan_tasks() == sub.tasks

        tik2.project.subs[sub.name].tasks["second_task"].add_category("Temp")

        assert sub.scan_tasks() == sub.tasks

        tik2.project.subs[sub.name].delete_task("second_task")

        assert tik2.project.subs[sub.name].tasks != tik2.project.subs[sub.name].all_tasks


    def test_if_a_task_is_empty(self, project_manual_path, tik):
        sub, task, work = self._create_a_subproject_task_and_work(
            project_manual_path, tik
        )
        assert sub.is_task_empty(task) == False
        fresh_task = sub.add_task("fresh_task", categories=["Model"])
        assert sub.is_task_empty(fresh_task) == True

    def test_creating_works_and_versions(self, project_manual_path, tik, monkeypatch):
        self.test_creating_and_adding_new_tasks(project_manual_path, tik)

        tik.user.set("Admin", 1234)

        # create some addigional tasks
        asset_categories = ["Model", "Rig", "LookDev"]

        bizarro_task = tik.project.create_task(
            "bizarro",
            categories=asset_categories,
            parent_path="Assets/Characters/Soldier",
        )
        ultraman_task = tik.project.create_task(
            "ultraman",
            categories=asset_categories,
            parent_path="Assets/Characters/Soldier",
        )
        superboy_task = tik.project.create_task(
            "superboy",
            categories=asset_categories,
            parent_path="Assets/Characters/Soldier",
        )

        # check if a category is empty or not
        assert superboy_task.categories["Model"].is_empty() == True

        tik.user.set("Observer", 1234)
        assert bizarro_task.categories["Model"].create_work("default") == -1

        tik.user.set("Admin", 1234)

        # create a work
        bizarro_task.categories["Model"].create_work("default")
        bizarro_task.categories["Model"].create_work(
            "main", file_format="", notes="This is a note. Very default."
        )
        bizarro_task.categories["Model"].create_work(
            "lod300", file_format="", notes="This is a note. Lod300."
        )

        bizarro_task.categories["Rig"].create_work("default")
        bizarro_task.categories["Rig"].create_work(
            "main", file_format="", notes="This is a note. Very default Rig."
        )
        bizarro_task.categories["Rig"].create_work(
            "lod300", file_format="", notes="This is a note. Lod300 Rig."
        )

        ultraman_task.categories["Model"].create_work(
            "varA", notes="This is a Model note for varA"
        )
        ultraman_task.categories["Model"].create_work(
            "varB", notes="This is a Model note for varB"
        )
        ultraman_task.categories["Model"].create_work(
            "varC", notes="This is a Model note for varC"
        )

        ultraman_task.categories["Rig"].create_work(
            "varA", notes="This is a note for varA"
        )
        ultraman_task.categories["Rig"].create_work(
            "varB", notes="This is a note for varB"
        )
        ultraman_task.categories["Rig"].create_work(
            "varC", notes="This is a note for varC"
        )

        # when an existing work name used, it should iterate a version over existing work
        this_should_have_2_versions = ultraman_task.categories["Rig"].create_work(
            "varC", notes="this is a complete new version of varC"
        )
        assert this_should_have_2_versions.version_count == 2

        # try to create a new version without permissions
        tik.user.set("Observer", password="1234")
        assert (
            ultraman_task.categories["Rig"].create_work(
                "varC", notes="this is a complete new version of varC"
            )
            == -1
        )

        tik.user.set("Admin", password="1234")
        # try to create a new version with a wrong format
        with pytest.raises(ValueError) as e_info:
            ultraman_task.categories["Rig"].create_work(
                "varC",
                file_format=".burhan",
                notes="this is a complete new version of varC",
            )
            assert e_info == "File format is not valid."

        # create a new work ignoring the checks
        assert ultraman_task.categories["Rig"].create_work("varD", ignore_checks=False)

        # monkeypatch the work.check_dcc_version_mismatch method to return a value for testing
        from tik_manager4.objects.work import Work

        def mock_check_dcc_version_mismatch(*args, **kwargs):
            return "something", "something_else"

        monkeypatch.setattr(
            Work, "check_dcc_version_mismatch", mock_check_dcc_version_mismatch
        )
        assert (
            ultraman_task.categories["Rig"].create_work("varE", ignore_checks=False)
            == -1
        )
        monkeypatch.undo()

    def test_create_work_from_path(
        self, project_manual_path, tik, monkeypatch, tmp_path
    ):
        self.test_creating_and_adding_new_tasks(project_manual_path, tik)
        tik.user.set("Admin", 1234)

        # get the superman task
        superman_task = (
            tik.project.subs["Assets"]
            .subs["Characters"]
            .subs["Soldier"]
            .tasks["superman"]
        )
        model_category = superman_task.categories["Model"]
        # create an empty test file on tmp_path
        test_file = tmp_path / "test_file.txt"
        test_file.touch()

        # mock the tik_manager4.dcc.standalone.main.text_to_image method to return a value for testing
        def mock_text_to_image(*args, **kwargs):
            return Path(args[1]).with_suffix(".png")

        from tik_manager4.dcc.standalone.main import Dcc

        monkeypatch.setattr(Dcc, "text_to_image", mock_text_to_image)

        work = model_category.create_work_from_path(
            "test_file", str(test_file), notes="This is a test file"
        )
        # check if the file is created
        assert work.settings_file.exists()

        # add the same file again to create a new version
        work = model_category.create_work_from_path(
            "test_file", str(test_file), notes="This is a test file"
        )

        # validate that there are two versions of this work
        assert work.version_count == 2

        monkeypatch.undo()

    def test_getting_templates_and_creating_works_from_templates(
        self, project_path, tik, monkeypatch
    ):
        test_project_path = self._new_asset_shot_project(project_path, tik)
        tik.set_project(test_project_path)

        assert tik.collect_template_paths() == []
        assert tik.get_template_names() == []
        assert tik.get_template_path_by_name("non_existing") == (None, None)

        # create a fake template under the project/_templates folder
        templates_path = Path(test_project_path, "_templates")
        templates_path.mkdir(parents=True, exist_ok=True)
        template_file_path = Path(templates_path, "test_template.ma")
        template_file_path.touch()

        assert tik.collect_template_paths() == [template_file_path]
        assert tik.get_template_names() == ["test_template"]
        assert tik.get_template_path_by_name("test_template") == (
            "maya",
            template_file_path.as_posix(),
        )

        # create a default task to test the create_work_from_template method
        tik.project.scan_tasks()

        from tik_manager4.dcc.standalone.main import Dcc

        def mock_text_to_image(*args, **kwargs):
            return Path(args[1]).with_suffix(".png")

        monkeypatch.setattr(Dcc, "text_to_image", mock_text_to_image)

        work = (
            tik.project.tasks["main"]
            .categories["Model"]
            .create_work_from_template("template_test", template_file_path, "maya")
        )
        # check if the file is created
        assert work.settings_file.exists()

        # add the same file again to create a new version
        work = (
            tik.project.tasks["main"]
            .categories["Model"]
            .create_work_from_template("template_test", template_file_path, "maya")
        )

        # validate that there are two versions of this work
        assert work.version_count == 2

        # fake the dcc name to test the create_work_from_template method
        monkeypatch.setattr(tik.dcc, "name", "mari")
        assert tik.get_template_names() == []

        monkeypatch.undo()

    def test_versioning_up(self, project_manual_path, tik, monkeypatch):
        self.test_creating_works_and_versions(project_manual_path, tik, monkeypatch)
        # try to create a new version with checks
        sub = tik.project.subs["Assets"].subs["Characters"].subs["Soldier"]
        model_category = sub.tasks["bizarro"].categories["Model"]
        _works = model_category.works
        work = list(_works.values())[0]  # get the first work
        assert work.new_version(ignore_checks=False) != -1
        # alter the dcc version and monkeypatch the get_dcc_version method to return a value for testing
        work._dcc_version = "this_should_fail"
        monkeypatch.setattr(
            work._dcc_handler, "get_dcc_version", lambda: "mocked_dcc_version"
        )
        assert work.new_version(ignore_checks=False) == -1

        # monkeypatch the self._dcc_handler.save_as method to return a value for testing
        monkeypatch.setattr(
            work._dcc_handler, "save_as", lambda x: Path(x).with_suffix(".burhan")
        )
        test_version = work.new_version(ignore_checks=True)
        assert test_version.file_format == ".burhan"

        # try to create a new version without permissions
        tik.user.set("Observer", password="1234")
        assert work.new_version(ignore_checks=False) == -1

        monkeypatch.undo()

    def test_checking_dcc_version_mismatch(self, project_manual_path, tik, monkeypatch):
        self.test_creating_works_and_versions(project_manual_path, tik, monkeypatch)

        sub = tik.project.subs["Assets"].subs["Characters"].subs["Soldier"]
        model_category = sub.tasks["bizarro"].categories["Model"]
        works = model_category.scan_works()
        work_object = list(works.values())[0]

        t = work_object.check_dcc_version_mismatch()
        # this should return False. Standalone doesnt even have a dcc version
        assert work_object.check_dcc_version_mismatch() == False

        # mock the get_dcc_version method to return a value for testing
        monkeypatch.setattr(
            work_object._dcc_handler, "get_dcc_version", lambda: "mocked_dcc_version"
        )
        # moch the object's _dcc_version to return the same value for testing
        work_object._dcc_version = "mocked_dcc_version"
        assert work_object.check_dcc_version_mismatch() == False  # no mismatch

        work_object._dcc_version = "this_mock_should_fail"
        assert work_object.check_dcc_version_mismatch() == (
            "this_mock_should_fail",
            "mocked_dcc_version",
        )

        #monkeypatch all instances of the metadata.get_value method to return a value for testing
        def mock_get_value(*args, **kwargs):
            return "monkeypatched_version"

        import tik_manager4.objects.metadata
        monkeypatch.setattr(tik_manager4.objects.metadata.Metadata, "get_value", mock_get_value)


        assert work_object.check_dcc_version_mismatch() == (
            "monkeypatched_version",
            "mocked_dcc_version",
        )

        # in the case of where ther is no parent task at all:
        work_object._parent_task = None
        assert work_object.check_dcc_version_mismatch() == (
            "this_mock_should_fail",
            "mocked_dcc_version",
        )

        monkeypatch.undo()

    def test_find_tasks_by_wildcard(self, project_manual_path, tik):
        sub, task, work = self._create_a_subproject_task_and_work(
            project_manual_path, tik
        )
        assert sub.find_tasks_by_wildcard(f"{task.name[:-2]}*")

        # create additional nested subprojects and find tasks by wildcard

        sub1a = sub.add_sub_project("sub1a")
        sub1a.add_task("wild_task1", categories=["Model"])
        sub1b = sub.add_sub_project("sub1b")
        sub1b.add_task("wild_task2", categories=["Model"])
        sub2a = sub1a.add_sub_project("sub2a")
        sub2a.add_task("wild_task3", categories=["Model"])
        sub2b = sub1b.add_sub_project("sub2b")
        sub2b.add_task("wild_task4", categories=["Model"])

        collected_tasks = sub.find_tasks_by_wildcard("wild*")
        assert len(collected_tasks) == 4

    def test_find_task_by_id(self, project_manual_path, tik):
        sub, task, work = self._create_a_subproject_task_and_work(
            project_manual_path, tik
        )
        found_task = sub.find_task_by_id(task.id)
        assert found_task.name == task.name

        # create a task in a deeper level
        sub1 = sub.add_sub_project("sub1")
        sub2 = sub1.add_sub_project("sub2")
        sub2_task = sub2.add_task("sub2_task", categories=["Model"])

        sub.find_task_by_id(sub2_task.id) == sub2_task

        # non existing task id
        assert sub.find_task_by_id(123123123123123123123) == -1

    def test_find_works_by_wildcard(self, project_manual_path, tik, monkeypatch):
        self.test_creating_works_and_versions(project_manual_path, tik, monkeypatch)
        lod300_works = (
            tik.project.subs["Assets"]
            .subs["Characters"]
            .subs["Soldier"]
            .tasks["bizarro"]
            .find_works_by_wildcard("*lod300")
        )

        # there should be 2 lod300 works. One in Model and one in Rig
        assert len(lod300_works) == 2

        # find a work by wildcard in a specific category
        model_lod300 = (
            tik.project.subs["Assets"]
            .subs["Characters"]
            .subs["Soldier"]
            .tasks["bizarro"]
            .categories["Model"]
            .get_works_by_wildcard("*_lod300")
        )

        # there should be only one lod300 work in Model category
        assert len(model_lod300) == 1
        assert model_lod300[0].name == "bizarro_Model_lod300"

    def test_find_work_by_absolute_path(self, project_manual_path, tik):
        sub, task, work = self._create_a_subproject_task_and_work(
            project_manual_path, tik
        )
        version = work.versions[0]
        version_path = work.get_abs_project_path(version.scene_path)
        found_work, version_number = tik.project.find_work_by_absolute_path(
            version_path
        )
        assert found_work.id == work.id
        assert version_number == 1

        # test trying to find within the project but doesn't exist
        non_existing_version_path = work.get_abs_project_path("burhan")
        assert tik.project.find_work_by_absolute_path(non_existing_version_path) == (
            None,
            None,
        )

        # test trying to find outside the project
        assert tik.project.find_work_by_absolute_path("/burhan") == (None, None)

    def test_get_current_work(self, project_manual_path, tik, monkeypatch):
        sub, task, work = self._create_a_subproject_task_and_work(
            project_manual_path, tik
        )

        # mock the dcc_handler.get_scene_file() to return None for testing
        monkeypatch.setattr(
            tik.project.guard._dcc_handler, "get_scene_file", lambda: None
        )
        assert tik.project.get_current_work() == (None, None)

        # mock the dcc_handler.get_scene_file() to return a valid value
        version = work.versions[0]
        version_path = work.get_abs_project_path(version.scene_path)
        monkeypatch.setattr(
            tik.project.guard._dcc_handler,
            "get_scene_file",
            lambda: version_path,
        )
        found_work, found_version = tik.project.get_current_work()
        assert found_work.id == work.id
        assert found_version == 1

    def test_scanning_works(self, project_manual_path, tik, monkeypatch):
        self.test_creating_works_and_versions(project_manual_path, tik, monkeypatch)

        # scan all works
        initial_scan = (
            tik.project.subs["Assets"]
            .subs["Characters"]
            .subs["Soldier"]
            .tasks["bizarro"]
            .categories["Model"]
            .scan_works()
        )
        assert initial_scan
        initial_scan_count = int(len(initial_scan.keys()))
        assert initial_scan_count == 3

        # add another work version to the first work and scan again
        _w = (
            tik.project.subs["Assets"]
            .subs["Characters"]
            .subs["Soldier"]
            .tasks["bizarro"]
            .categories["Model"]
            ._works
        )
        work_obj = _w[list(_w.keys())[0]]
        work_obj.new_version()
        work_obj_2 = _w[list(_w.keys())[1]]

        second_scan = (
            tik.project.subs["Assets"]
            .subs["Characters"]
            .subs["Soldier"]
            .tasks["bizarro"]
            .categories["Model"]
            .scan_works()
        )
        assert second_scan
        second_scan_count = int(len(second_scan.keys()))
        assert second_scan_count == initial_scan_count

        # temporarily disable (change the extension) of one of the work paths and scan again
        _temp = work_obj.settings_file.rename(
            work_obj.settings_file.with_suffix(".bck")
        )
        # scan again and compare with the previous scan
        third_scan = (
            tik.project.subs["Assets"]
            .subs["Characters"]
            .subs["Soldier"]
            .tasks["bizarro"]
            .categories["Model"]
            .scan_works()
        )
        assert third_scan
        third_scan_count = int(len(third_scan.keys()))
        assert third_scan_count == second_scan_count - 1

        # mock if someone else changed the file meantime
        _temp_settings = settings.Settings(str(work_obj_2.settings_file))
        _temp_settings.edit_property("creator", "Burhan")
        _temp_settings.apply_settings(force=True)
        # scan again and compare with the previous scan
        fourth_scan = (
            tik.project.subs["Assets"]
            .subs["Characters"]
            .subs["Soldier"]
            .tasks["bizarro"]
            .categories["Model"]
            .scan_works()
        )

        # scan and get all works using the property method
        assert tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["bizarro"].categories["Model"].all_works

    def test_deleting_works(self, project_manual_path, tik, monkeypatch):
        self.test_creating_works_and_versions(project_manual_path, tik, monkeypatch)

        model_category = (
            tik.project.subs["Assets"]
            .subs["Characters"]
            .subs["Soldier"]
            .tasks["bizarro"]
            .categories["Model"]
        )
        works = model_category.scan_works()
        target_work = list(works.values())[0]

        # try to delete a work without permissions
        tik.user.set("Generic", password="1234")
        assert target_work.destroy()[0] == -1
        assert model_category.delete_works()[0] == False

        tik.user.set("Admin", password="1234")
        # delete the work
        assert target_work.destroy()[0] == 1

    def test_deleting_empty_task(self, project_manual_path, tik):
        self.test_creating_and_adding_new_tasks(project_manual_path, tik)

        # try to delete a task without permissions
        tik.user.set("Generic", password="1234")
        assert (
            tik.project.subs["Assets"]
            .subs["Characters"]
            .subs["Soldier"]
            .delete_task("superman")[0]
            == False
        )
        # check if the log message is correct
        assert tik.log.get_last_message() == (
            "This user does not have permissions for this action",
            "warning",
        )
        # try to delete a non-existing task
        assert (
            tik.project.subs["Assets"]
            .subs["Characters"]
            .subs["Soldier"]
            .delete_task("this_task_doesnt_exist")[0]
            == False
        )

        # delete the task
        tik.user.set("Admin", password="1234")
        assert (
            tik.project.subs["Assets"]
            .subs["Characters"]
            .subs["Soldier"]
            .delete_task("superman")[0]
            == True
        )

    def test_deleting_non_empty_task(self, project_manual_path, tik, monkeypatch):
        sub, task, work = self._create_a_subproject_task_and_work(
            project_manual_path, tik
        )
        tik.user.set("Admin", "1234")
        # create an additional work
        task.categories["Model"].create_work("test_work_to_double_delete")
        result = sub.delete_task(task.name)
        assert result == (True, "success")

        # create the same task and same work again
        task = sub.add_task(task.name, categories=["Model", "Rig", "LookDev"])
        task.categories["Model"].create_work("test_work_to_double_delete")

        result = sub.delete_task(task.name)
        assert result == (True, "success")

    def test_deleting_empty_categories(self, project_manual_path, tik):
        self.test_adding_categories(project_manual_path, tik)

        # try to delete a category without permissions
        tik.user.set("Generic", password="1234")
        assert (
            tik.project.subs["Assets"]
            .subs["Characters"]
            .subs["Soldier"]
            .tasks["batman"]
            .delete_category("Model")
            == -1
        )
        tik.user.set("Admin", password="1234")
        # try to delete a non-existing category
        assert (
            tik.project.subs["Assets"]
            .subs["Characters"]
            .subs["Soldier"]
            .tasks["batman"]
            .delete_category("Burhan")
            == -1
        )
        # delete the Gotham category from Batman task
        tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks[
            "batman"
        ].delete_category("Gotham")
        assert (
            "Gotham"
            not in tik.project.subs["Assets"]
            .subs["Characters"]
            .subs["Soldier"]
            .tasks["batman"]
            .categories.keys()
        )

    def test_deleting_non_empty_categories(self, project_manual_path, tik):
        self.test_adding_categories(project_manual_path, tik)
        # add a version to the Gotham category
        tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks[
            "batman"
        ].categories["Temp"].create_work("test_work")
        # try to delete a non-empty category
        tik.user.set("Admin", password="1234")
        assert (
            tik.project.subs["Assets"]
            .subs["Characters"]
            .subs["Soldier"]
            .tasks["batman"]
            .categories["Temp"]
            .is_empty()
            == False
        )
        tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks[
            "batman"
        ].delete_category("Temp")
        # check the log message
        assert tik.log.get_last_message() == (
            "Sending category 'Temp' from task 'batman' to purgatory.",
            "warning",
        )

    def test_deleting_non_empty_tasks(self, project_manual_path, tik, monkeypatch):
        self.test_creating_works_and_versions(project_manual_path, tik, monkeypatch)
        tik.user.set("Admin", password="1234")
        assert (
            tik.project.subs["Assets"]
            .subs["Characters"]
            .subs["Soldier"]
            .delete_task("superboy")[0]
            == True
        )

    def test_delete_works_failure(self, project_manual_path, tik, monkeypatch):
        """Test delete_works method when work cannot be destroyed."""
        sub, task, work = self._create_a_subproject_task_and_work(
            project_manual_path, tik)
        model_category = task.categories["Model"]

        # Create a work
        new_work = model_category.create_work("work_to_delete")

        # Mock the destroy method to return False and a failure message
        def mock_destroy():
            return False, "Failed to delete work"

        monkeypatch.setattr(new_work, "destroy", mock_destroy)

        # Attempt to delete the work
        result = new_work.destroy()
        assert result == (False, "Failed to delete work")
