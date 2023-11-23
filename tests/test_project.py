"""Tests for Project related functions"""
from pathlib import Path
import shutil
from pprint import pprint
import pytest
from tik_manager4.core import utils

class TestProject:
    """Uses a fresh mockup_common folder and test_project under user directory for all tests"""
    # import tik_manager4 # importing main checks the common folder definition, thats why its here
    # tik = tik_manager4.initialize("Standalone")

    @pytest.fixture(scope='function')
    def project_default_path(self):
        project_path = Path(utils.get_home_dir(), "TM4_default")
        if project_path.exists():
            shutil.rmtree(str(project_path))
        return str(project_path)

    @pytest.fixture(scope='function')
    def project_path(self):
        project_path = Path(utils.get_home_dir(), "t4_test_project_DO_NOT_USE")
        if project_path.exists():
            shutil.rmtree(str(project_path))
        return str(project_path)

    @pytest.fixture(scope='function')
    def project_manual_path(self):
        project_path = Path(utils.get_home_dir(), "t4_test_manual_DO_NOT_USE")
        if project_path.exists():
            shutil.rmtree(str(project_path))
        return str(project_path)


    def test_default_project_paths(self, project_default_path, tik):
        assert tik.project.path == "" # this is overridden by project class and must always return empty string
        tik.set_project(project_default_path)
        assert tik.project.absolute_path == str(Path(utils.get_home_dir(), "TM4_default"))
        assert tik.project.database_path == str(Path(utils.get_home_dir(), "TM4_default", "tikDatabase"))
        assert tik.project.name == "TM4_default"
        assert tik.project.guard.project_root == str(Path(utils.get_home_dir(), "TM4_default"))
        assert tik.project.guard.database_root == str(Path(utils.get_home_dir(), "TM4_default", "tikDatabase"))

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
        assert tik.create_project(project_path, structure_template="asset_shot", resolution=[3840, 2160],
                                       fps=30) == 1
        return project_path

    def test_set_project_with_arguments(self, project_path, tik):
        test_project_path = self.test_create_new_project(project_path, tik)
        tik.project.__init__(path=test_project_path)

    def test_create_sub_project(self, project_path, tik):
        """Tests creating sub-projects with parent id and path"""
        test_project_path = self.test_create_new_project(project_path, tik)
        tik.set_project(test_project_path)

        # no permission test
        tik.user.set("Generic")
        assert tik.project.create_sub_project("testSub", parent_path="") == -1
        assert tik.project.add_sub_project("testSub") == -1

        tik.user.set("Admin", "1234")
        new_sub = tik.project.create_sub_project("testSub", parent_path="")
        assert new_sub.path == "testSub"

        another_sub = tik.project.create_sub_project("anotherSub", parent_uid=new_sub.id)
        assert another_sub.path == "testSub/anotherSub"

        # test the parent.name and parent.id
        assert another_sub.parent.name == "testSub"
        assert another_sub.parent.id == new_sub.id

        # try creating an existing one
        assert tik.project.create_sub_project("anotherSub", parent_uid=new_sub.id) == -1
        assert tik.log.get_last_message() == ("anotherSub already exist in sub-projects of testSub", "warning")

    def test_edit_sub_project(self, project_path, tik):
        """Test editing sub-projects with parent id and path"""

        test_project_path = self.test_create_new_project(project_path, tik)
        tik.set_project(test_project_path)

        # first create a sub project
        tik.user.set("Admin", "1234")
        new_sub = tik.project.create_sub_project("testToEditSub", parent_path="")

        # no permission test
        tik.user.set("Generic")
        assert tik.project.edit_sub_project(uid=new_sub.id, name="testEditedSub", resolution=[4096, 2144], fps=39) == -1
        tik.user.set("Admin", "1234")
        # test with uid
        assert tik.project.edit_sub_project(uid=new_sub.id, name="testEditedSub", resolution=[4096, 2144], fps=39) == 1

        # test with path
        assert tik.project.edit_sub_project(path=new_sub.path, name="testEditedSub", resolution=[4096, 2144], fps=40, lens=50) == 1

    def test_create_a_shot_asset_project_structure(self, project_manual_path, tik, print_results=False):

        tik.user.set("Admin", password="1234")
        tik.create_project(project_manual_path, structure_template="empty")
        tik.set_project(project_manual_path)

        # asset_categories = ["Model", "LookDev", "Rig"]
        # shot_categories = ["Layout", "Animation", "Lighting", "Render"]

        assets = tik.project.add_sub_project("Assets", mode="asset")
        chars = assets.add_sub_project("Characters", fps=60)
        props = assets.add_sub_project("Props", metatest="uberMetaTestingen")
        env = assets.add_sub_project("Environment")

        leaf_assets = [chars.add_sub_project("Soldier"),
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
        leaf_shots = [sequence_a.add_sub_project("SHOT_010"), sequence_a.add_sub_project("SHOT_020"),
                      sequence_a.add_sub_project("SHOT_030"), sequence_a.add_sub_project("SHOT_040"),]

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
        test_project_path = self.test_create_a_shot_asset_project_structure(project_manual_path, tik)
        current_subtree = tik.project.get_sub_tree()
        # tik.project.__init__()
        # tik.user.__init__()

        # print(test_project_path)
        tik.set_project(test_project_path)
        existing_subtree = tik.project.get_sub_tree()
        pprint(existing_subtree)
        assert current_subtree == existing_subtree, "Read and Write of project structure does not match"

    def test_deleting_sub_projects(self, project_manual_path, tik):
        """Tests deleting the sub-projects"""
        test_project_path = self.test_create_a_shot_asset_project_structure(project_manual_path, tik, print_results=False)
        tik.set_project(test_project_path)
        tik.user.set("Generic")
        assert tik.project.delete_sub_project(path="Assets/Props") == -1

        tik.user.set("Admin", 1234)
        # wrong arguments
        assert tik.project.delete_sub_project(path=None, uid=None) == -1
        # path methods

        # non existing path
        assert tik.project.delete_sub_project(path="Burhan/Altintop") == -1

        # by path
        assert tik.project.delete_sub_project(path="Assets/Props") == 1

        # uid methods
        uid = tik.project.get_uid_by_path(path="Assets/Characters")

        # non existing uid
        assert tik.project.delete_sub_project(uid=123123123123123123) == -1
        assert tik.project.delete_sub_project(uid=uid) == 1

        # delete a sub-project on root
        assert tik.project.delete_sub_project(path="Assets") == 1

    def test_find_subs_by_path_and_id(self, project_path, tik):
        test_project_path = self.test_create_new_project(project_path, tik)
        tik.set_project(test_project_path)
        sub_by_path = tik.project.find_sub_by_path("Assets")
        assert sub_by_path.path == "Assets"
        sub_by_id = tik.project.find_sub_by_id(sub_by_path.id)
        assert sub_by_id.path == "Assets"
        assert sub_by_path == sub_by_id

        #non existing path
        assert tik.project.find_sub_by_path("Burhan/Altintop") == -1
        assert tik.project.find_sub_by_id(123123123123123123123) == -1

    def test_find_subs_by_wildcard(self, project_manual_path, tik):
        test_project_path = self.test_create_a_shot_asset_project_structure(project_manual_path, tik, print_results=False)
        tik.set_project(test_project_path)
        shots = (tik.project.find_subs_by_wildcard("SHOT_*"))
        assert shots
        assert len(shots) == 7

    def test_get_uid_and_get_path(self, project_path, tik):
        test_project_path = self.test_create_new_project(project_path, tik)
        tik.set_project(test_project_path)
        compare_path = "Assets/Props"
        uid = tik.project.get_uid_by_path("Assets/Props")
        path = tik.project.get_path_by_uid(uid)
        assert path == compare_path

        #non existing path
        assert tik.project.get_uid_by_path("Burhan/Altintop") == -1
        assert tik.project.get_path_by_uid(123123123123123123123) == -1

    def test_creating_and_adding_new_tasks(self, project_manual_path, tik):
        test_project_path = self.test_create_a_shot_asset_project_structure(project_manual_path, tik, print_results=False)
        tik.set_project(test_project_path)

        # create a task from the main project
        task = tik.project.create_task("superman", categories=["Model", "Rig", "LookDev"], parent_path="Assets/Characters/Soldier")
        assert task.name == "superman"
        assert task.creator == "Admin"
        assert list(task.categories.keys()) == ["Model", "Rig", "LookDev"]
        assert task.type == "asset"

        # create a task directly from a sub-project
        task = tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].add_task("batman", categories=["Model", "Rig", "LookDev"], task_type="Asset")

        # TODO make a test to create illegal categories (not defined in the category definitions)

        # try to create a duplicate task
        assert tik.project.create_task("superman", categories=["Model", "Rig", "LookDev"], parent_path="Assets/Characters/Soldier") == -1

        # check if the user permissions check works
        tik.user.set("Generic", password="1234")
        assert tik.project.create_task("this_asset_shouldnt_exist", categories=["Model", "Rig", "LookDev"], parent_path="Assets/Characters/Soldier") == -1
        # check if the log message is correct
        assert tik.log.get_last_message() == ('This user does not have permissions for this action', 'warning')
        tik.user.set("Admin", password="1234")

    def test_edit_task(self, project_manual_path, tik):
        test_project_path = self.test_create_a_shot_asset_project_structure(project_manual_path, tik ,print_results=False)
        tik.set_project(test_project_path)

        # create a task from the main project
        task = tik.project.create_task("Poseidon", categories=["Model", "Rig", "LookDev"], parent_path="Assets/Characters/Soldier")

        assert task.name == "Poseidon"
        assert task.creator == "Admin"
        # assert task.reference_id == task._task_id
        assert task.id == task._task_id

        # no permissions
        tik.user.set("Generic", password="1234")
        assert task.edit(name="Aquaman", categories=["Model", "Rig", "LookDev", "Animation"], task_type="Shot") == -1
        assert tik.log.get_last_message() == ('This user does not have permissions for this action', 'warning')
        tik.user.set("Admin", password="1234")

        # existing task name
        existing_task = tik.project.create_task("Wonderboy", categories=["Model", "Rig", "LookDev"],
                                            parent_path="Assets/Characters/Soldier")
        assert task.edit(name="Wonderboy", categories=["Model", "Rig", "LookDev", "Animation"], task_type="Shot") == -1
        assert tik.log.get_last_message() == ("Task name 'Wonderboy' already exists in sub 'Soldier'.", 'error')

        # wrong category type
        with pytest.raises(Exception):
            task.edit(name="Aquaman", categories="ThisIsWrong", task_type="Shot")
        # category not defined
        with pytest.raises(Exception):
            task.edit(name="Aquaman", categories=["Model", "Rig", "LookDev", "Animation", "ThisIsWrong"], task_type="Shot")

        # edit the task
        task.edit(name="Aquaman", categories=["Model", "Rig", "LookDev", "Animation"], task_type="Shot")

        assert list(task.categories.keys()) == ["Model", "Rig", "LookDev", "Animation"]
        assert task.name == "Aquaman"
        assert task.type == "Shot"

    def test_adding_categories(self, project_manual_path, tik):
        self.test_creating_and_adding_new_tasks(project_manual_path, tik)
        # add a category
        _test_tasks = tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks

        # try to add category without permissions
        tik.user.set("Generic", password="1234")
        assert tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["batman"].add_category("Temp") == -1
        tik.user.set("Admin", password="1234")
        # add the Gotham category to Batman task
        assert tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["batman"].add_category("Temp")

        # try to add a duplicate category
        assert tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["batman"].add_category("Temp") == -1
        # check the log message
        assert tik.log.get_last_message() == ("Category 'Temp' already exists in task 'batman'.", 'warning')

        # try to add a category that is not defined in the category definitions
        with pytest.raises(Exception) as e_info:
            tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["batman"].add_category("Burhan")
        # check the log message
        assert tik.log.get_last_message() == ("Category 'Burhan' is not defined in category definitions.", 'error')

    def test_order_categories(self, project_manual_path, tik):
        self.test_creating_and_adding_new_tasks(project_manual_path, tik)

        # order categories
        _test_tasks = tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks
        assert tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["superman"].order_categories(["Model", "LookDev", "Rig"]) == 1

        # try to order categories without permissions
        tik.user.set("Generic", password="1234")
        assert tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["superman"].order_categories(["Model", "LookDev", "Rig"]) == -1
        tik.user.set("Admin", password="1234")

        # try to order categories with a wrong length
        with pytest.raises(Exception) as e_info:
            tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["superman"].order_categories(["LookDev", "Model"])
        # check the log message
        assert tik.log.get_last_message() == ("New order list is not the same length as the current categories list.", 'error')

        # try to order categories with an item not in the current categories list
        with pytest.raises(Exception) as e_info:
            tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["superman"].order_categories(["Model", "LookDev", "Temp"])
        # check the log message
        assert tik.log.get_last_message() == ("New order list contains a category that is not in the current categories list.", 'error')

    def test_scanning_tasks(self, project_manual_path, tik):
        self.test_creating_and_adding_new_tasks(project_manual_path, tik)

        # scan the tasks
        assert tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].scan_tasks()

        # modify one of the tasks and scan again
        # no permission
        tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["superman"].add_category("Temp")
        tik.user.set("Admin", password=1234)
        assert tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].scan_tasks()

    def test_creating_works(self, project_manual_path, tik):
        self.test_creating_and_adding_new_tasks(project_manual_path, tik)

        tik.user.set("Admin", 1234)

        #create some addigional tasks
        asset_categories = ["Model", "Rig", "LookDev"]

        bizarro_task = tik.project.create_task("bizarro", categories=asset_categories, parent_path="Assets/Characters/Soldier")
        ultraman_task = tik.project.create_task("ultraman", categories=asset_categories, parent_path="Assets/Characters/Soldier")
        superboy_task = tik.project.create_task("superboy", categories=asset_categories, parent_path="Assets/Characters/Soldier")

        # check if a category is empty or not
        assert superboy_task.categories["Model"].is_empty() == True

        tik.user.set("Observer", 1234)
        assert bizarro_task.categories["Model"].create_work("default") == -1

        tik.user.set("Admin", 1234)

        # create a work
        bizarro_task.categories["Model"].create_work("default")
        bizarro_task.categories["Model"].create_work("main", file_format=".txt", notes="This is a note. Very default.")
        bizarro_task.categories["Model"].create_work("lod300", file_format=".txt", notes="This is a note. Lod300.")

        bizarro_task.categories["Rig"].create_work("default")
        bizarro_task.categories["Rig"].create_work("main", file_format=".txt", notes="This is a note. Very default Rig.")
        bizarro_task.categories["Rig"].create_work("lod300", file_format=".txt", notes="This is a note. Lod300 Rig.")

        ultraman_task.categories["Model"].create_work("varA", notes="This is a Model note for varA")
        ultraman_task.categories["Model"].create_work("varB", notes="This is a Model note for varB")
        ultraman_task.categories["Model"].create_work("varC", notes="This is a Model note for varC")

        ultraman_task.categories["Rig"].create_work("varA", notes="This is a note for varA")
        ultraman_task.categories["Rig"].create_work("varB", notes="This is a note for varB")
        ultraman_task.categories["Rig"].create_work("varC", notes="This is a note for varC")

        # when an existing work name used, it should iterate a version over existing work
        this_should_have_2_versions = ultraman_task.categories["Rig"].create_work("varC", notes="this is a complete new version of varC")
        assert this_should_have_2_versions.version_count == 2

    def test_scanning_works(self, project_manual_path, tik):
        self.test_creating_works(project_manual_path, tik)

        # scan all works
        assert tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["bizarro"].categories["Model"].scan_works(all_dcc=True)

        # add another work version to the first work and scan again
        _w = tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["bizarro"].categories["Model"]._works
        work_obj = (_w[list(_w.keys())[0]])
        work_obj.new_version()

        assert tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["bizarro"].categories["Model"].scan_works(all_dcc=True)

        # override the guard.dcc
        # tik.project.guard._dcc = "Maya"
        # assert tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["bizarro"].categories["Model"].scan_works(all_dcc=False) == {}

    def test_deleting_empty_task(self, project_manual_path, tik):
        self.test_creating_and_adding_new_tasks(project_manual_path, tik)

        # try to delete a task without permissions
        tik.user.set("Generic", password="1234")
        assert tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].delete_task("superman") == -1
        # check if the log message is correct
        assert tik.log.get_last_message() == ('This user does not have permissions for this action', 'warning')
        # try to delete a non-existing task
        assert tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].delete_task("this_task_doesnt_exist") == -1

        # delete the task
        tik.user.set("Admin", password="1234")
        assert tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].delete_task("superman") == 1

    def test_deleting_empty_categories(self, project_manual_path, tik):
        self.test_adding_categories(project_manual_path, tik)

        # try to delete a category without permissions
        tik.user.set("Generic", password="1234")
        assert tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["batman"].delete_category("Model") == -1
        tik.user.set("Admin", password="1234")
        # try to delete a non-existing category
        assert tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["batman"].delete_category("Burhan") == -1
        # delete the Gotham category from Batman task
        tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["batman"].delete_category("Gotham")
        assert "Gotham" not in tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["batman"].categories.keys()

    def test_deleting_non_empty_categories(self, project_manual_path, tik):
        self.test_adding_categories(project_manual_path, tik)
        # add a version to the Gotham category
        tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["batman"].categories["Temp"].create_work("test_work")
        # try to delete a non-empty category
        tik.user.set("Admin", password="1234")
        assert tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["batman"].categories["Temp"].is_empty() == False
        tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["batman"].delete_category("Temp")
        # check the log message
        assert tik.log.get_last_message() == ("Sending category 'Temp' from task 'batman' to purgatory.", 'warning')

    def test_deleting_non_empty_tasks(self, project_manual_path, tik):
        self.test_creating_works(project_manual_path, tik)
        tik.user.set("Admin", password="1234")
        assert tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].delete_task("superboy") == 1