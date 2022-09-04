"""Tests for Project related functions"""
import os
import shutil
from pprint import pprint
import pytest
# import uuid
from .mockup import Mockup, clean_user
from tik_manager4.objects import user
from tik_manager4.core import filelog, utils

log = filelog.Filelog(logname=__name__, filename="tik_manager4")



class TestProject:
    """Uses a fresh mockup_common folder and test_project under user directory for all tests"""
    # _salt = str(uuid.uuid4()).split("-")[-1]
    mock = Mockup()
    mock.prepare()
    user.User(common_directory=mock.common)  # this is for not popping up the "missing common folder" message
    # from tik_manager4.objects.main import Main  # importing main checks the common folder definition, thats why its here
    # from tik_manager4.objects.main import Main  # importing main checks the common folder definition, thats why its here
    import tik_manager4 # importing main checks the common folder definition, thats why its here
    # tik = Main()
    tik = tik_manager4.initialize("Standalone")

    @clean_user
    def test_default_project_paths(self):
        assert self.tik.project.path == "" # this is overridden by project class and must always return empty string
        assert self.tik.project.absolute_path == os.path.join(utils.get_home_dir(), "TM4_default")
        assert self.tik.project.database_path == os.path.join(utils.get_home_dir(), "TM4_default", "tikDatabase")
        assert self.tik.project.name == "TM4_default"
        assert self.tik.project.guard.project_root == os.path.join(utils.get_home_dir(), "TM4_default")
        assert self.tik.project.guard.database_root == os.path.join(utils.get_home_dir(), "TM4_default", "tikDatabase")

    @clean_user
    def test_resolution_and_fps(self):
        """Tests setting and getting resolution of fps values"""
        test_resolution = [1000, 1000]
        test_fps = 30
        assert self.tik.project.set_resolution(test_resolution) == -1
        assert self.tik.project.set_fps(test_fps) == -1
        self.tik.user.set("Admin")
        assert self.tik.project.set_resolution(test_resolution) == -1
        assert self.tik.project.set_fps(test_fps) == -1
        self.tik.user.authenticate("1234")
        assert self.tik.project.set_resolution(test_resolution) == 1
        assert self.tik.project.set_fps(test_fps) == 1

        # fails
        with pytest.raises(Exception) as e_info:
            self.tik.project.set_resolution("NOT VALID RESOLUTION")
        with pytest.raises(Exception) as e_info:
            self.tik.project.set_fps("NOT VALID FPS")

        self.tik.project.save_structure()

        # # re-init the project and read back the values
        self.tik.project.set(os.path.join(utils.get_home_dir(), "TM4_default"))
        assert self.tik.project.resolution == test_resolution
        assert self.tik.project.fps == test_fps

    @clean_user
    def test_create_new_project(self):
        # no user permission
        test_project_path = os.path.join(utils.get_home_dir(), "t4_test_project_DO_NOT_USE")
        if os.path.exists(test_project_path):
            shutil.rmtree(test_project_path)
        assert self.tik.create_project(test_project_path, structure_template="asset_shot") == -1
        self.tik.user.set("Admin")
        assert self.tik.create_project(test_project_path, structure_template="asset_shot") == -1
        self.tik.user.authenticate("1234")
        assert self.tik.create_project(test_project_path, structure_template="hedehot") == 1
        assert self.tik.create_project(test_project_path, structure_template="empty") == -1
        shutil.rmtree(test_project_path)
        assert self.tik.create_project(test_project_path, structure_template="asset_shot", resolution=[3840, 2160],
                                       fps=30) == 1
        return test_project_path

    @clean_user
    def test_set_project_with_arguments(self):
        test_project_path = self.test_create_new_project()
        self.tik.project.__init__(path=test_project_path)

    @clean_user
    def test_create_sub_project(self):
        """Tests creating sub-projects with parent id and path"""
        test_project_path = self.test_create_new_project()
        self.tik.project.set(test_project_path)

        # no permission test
        self.tik.user.set("Generic")
        assert self.tik.project.create_sub_project("testSub", parent_path="") == -1
        assert self.tik.project.add_sub_project("testSub") == -1

        self.tik.user.set("Admin", "1234")
        new_sub = self.tik.project.create_sub_project("testSub", parent_path="")
        assert new_sub.path == "testSub"

        another_sub = self.tik.project.create_sub_project("anotherSub", parent_uid=new_sub.id)
        assert another_sub.path == "testSub/anotherSub"

        # test the parent.name and parent.id
        assert another_sub.parent.name == "testSub"
        assert another_sub.parent.id == new_sub.id

        # try creating an existing one
        assert self.tik.project.create_sub_project("anotherSub", parent_uid=new_sub.id) == -1
        assert log.get_last_message() == ("anotherSub already exist in sub-projects of testSub", "warning")

        # try creating a sub-project with a wrong parent id
        pytest.raises(Exception, self.tik.project.create_sub_project, "wrongSub", parent_uid=0)

        # try creating a sub-project with a wrong parent path
        pytest.raises(Exception, self.tik.project.create_sub_project, "wrongSub", parent_path="THIS_PATH_DOES_NOT_EXIST")

        # try creating a sub-project without a parent path or parent id
        pytest.raises(Exception, self.tik.project.create_sub_project, "wrongSub")

    # @clean_user
    # def test_create_category(self):
    #     test_project_path = self.test_create_new_project()
    #     self.tik.project.set(test_project_path)
    #
    #     # no permission test
    #     self.tik.user.set("Generic")
    #     assert self.tik.project.create_category("testCategory", parent_path="Assets") == -1
    #     assert self.tik.project.subs["Assets"].add_category("testCategory") == -1
    #
    #     self.tik.user.set("Admin", "1234")
    #     new_category = self.tik.project.create_category("testCategory", parent_path="Assets")
    #     assert new_category.path == "Assets/testCategory"
    #
    #     # try creating an existing one
    #     assert self.tik.project.create_category("testCategory", parent_path="Assets") == -1
    #     assert log.last_warning == "testCategory already exists in categories of Assets"

    @clean_user
    def test_create_a_shot_asset_project_structure(self, print_results=False):
        self.tik.project.__init__()
        self.tik.user.__init__()

        test_project_path = os.path.join(utils.get_home_dir(), "t4_test_manual_DO_NOT_USE")
        if os.path.exists(test_project_path):
            shutil.rmtree(test_project_path)

        self.tik.user.set("Admin", password="1234")
        self.tik.create_project(test_project_path, structure_template="empty")
        self.tik.project.set(test_project_path)

        # asset_categories = ["Model", "LookDev", "Rig"]
        # shot_categories = ["Layout", "Animation", "Lighting", "Render"]

        assets = self.tik.project.add_sub_project("Assets", )
        chars = assets.add_sub_project("Characters", fps=60, mode="asset")
        props = assets.add_sub_project("Props")
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

        # for leaf in leaf_assets:
        #     for category in asset_categories:
        #         leaf.add_category(category)

        shots = self.tik.project.add_sub_project("Shots")
        sequence_a = shots.add_sub_project("SequenceA", mode="sequence")
        leaf_shots = [sequence_a.add_sub_project("SHOT_010"), sequence_a.add_sub_project("SHOT_020", mode="shot"),
                      sequence_a.add_sub_project("SHOT_030"), sequence_a.add_sub_project("SHOT_040", mode="shot"),]

        sequence_b = shots.add_sub_project("SequenceB", mode="sequence")
        leaf_shots.append(sequence_b.add_sub_project("SHOT_010", mode="shot"))
        leaf_shots.append(sequence_b.add_sub_project("SHOT_070", mode="shot"))
        leaf_shots.append(sequence_b.add_sub_project("SHOT_120", mode="shot"))

        # for leaf in leaf_shots:
        #     for category in shot_categories:
        #         leaf.add_category(category)

        # print("\n")

        self.tik.project.save_structure()
        if print_results:
            pprint(self.tik.project.get_sub_tree())

        # self.tik.project.create_folders(self.tik.project.database_path)
        # print(pr.database_path, pr._path)
        # self.tik.project.create_folders(self.tik.project.absolute_path)
        return test_project_path

    @clean_user
    def test_validating_existing_project(self):
        """Tests reading an existing project structure and compares it to the created one on-the-fly"""
        test_project_path = self.test_create_a_shot_asset_project_structure()
        current_subtree = self.tik.project.get_sub_tree()
        self.tik.project.__init__()
        self.tik.user.__init__()

        # print(test_project_path)
        self.tik.project.set(test_project_path)
        existing_subtree = self.tik.project.get_sub_tree()
        pprint(existing_subtree)
        assert current_subtree == existing_subtree, "Read and Write of project structure does not match"

    @clean_user
    def test_deleting_sub_projects(self):
        """Tests deleting the sub-projects"""
        test_project_path = self.test_create_a_shot_asset_project_structure(print_results=False)
        self.tik.project.set(test_project_path)
        self.tik.user.set("Generic")
        assert self.tik.project.delete_sub_project(path="Assets/Props") == -1

        self.tik.user.set("Admin", 1234)
        # wrong arguments
        assert self.tik.project.delete_sub_project(path=None, uid=None) == -1
        # path methods

        # non existing path
        assert self.tik.project.delete_sub_project(path="Burhan/Altintop") == -1
        assert self.tik.project.delete_sub_project(path="Assets/Props") == 1

        # uid methods
        uid = self.tik.project.get_uid_by_path(path="Assets/Characters")

        # non existing uid
        assert self.tik.project.delete_sub_project(uid=123123123123123123) == -1
        assert self.tik.project.delete_sub_project(uid=uid) == 1

    @clean_user
    def test_find_subs_by_path_and_id(self):
        test_project_path = self.test_create_new_project()
        self.tik.project.set(test_project_path)
        sub_by_path = self.tik.project.find_sub_by_path("Assets")
        assert sub_by_path.path == "Assets"
        sub_by_id = self.tik.project.find_sub_by_id(sub_by_path.id)
        assert sub_by_id.path == "Assets"
        assert sub_by_path == sub_by_id

        #non existing path
        assert self.tik.project.find_sub_by_path("Burhan/Altintop") == -1
        assert self.tik.project.find_sub_by_id(123123123123123123123) == -1

    @clean_user
    def test_find_subs_by_wildcard(self):
        test_project_path = self.test_create_a_shot_asset_project_structure(print_results=False)
        self.tik.project.set(test_project_path)
        shots = (self.tik.project.find_subs_by_wildcard("SHOT_*"))
        # _ = [print(shot.name) for shot in shots]
        assert shots
        assert len(shots) == 7

    @clean_user
    def test_get_uid_and_get_path(self):
        test_project_path = self.test_create_new_project()
        self.tik.project.set(test_project_path)
        compare_path = "Assets/Props"
        uid = self.tik.project.get_uid_by_path("Assets/Props")
        path = self.tik.project.get_path_by_uid(uid)
        assert path == compare_path

        #non existing path
        assert self.tik.project.get_uid_by_path("Burhan/Altintop") == -1
        assert self.tik.project.get_path_by_uid(123123123123123123123) == -1

    # @clean_user
    # def test_query_category(self):
    #     test_project_path = self.test_create_a_shot_asset_project_structure(print_results=False)
    #     self.tik.project.set(test_project_path)
    #     soldier_sub = self.tik.project.find_sub_by_path("Assets/Characters/Soldier")
    #     print(soldier_sub.categories[0].path)

    @clean_user
    def test_creating_and_adding_new_tasks(self):
        test_project_path = self.test_create_a_shot_asset_project_structure(print_results=False)
        self.tik.project.set(test_project_path)

        # create a task from the main project
        task = self.tik.project.create_task("superman", categories=["Model", "Rig", "Lookdev"], parent_path="Assets/Characters/Soldier")
        assert task.name == "superman"
        assert task.creator == "Admin"
        assert list(task.categories.keys()) == ["Model", "Rig", "Lookdev"]
        assert task.type == "asset"

        # create a task directly from a sub-project
        task = self.tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].add_task("batman", categories=["Model", "Rig", "Lookdev"], task_type="Asset")

        # try to create a duplicate task
        assert self.tik.project.create_task("superman", categories=["Model", "Rig", "Lookdev"], parent_path="Assets/Characters/Soldier") == -1

        # check if the user permissions check works
        self.tik.user.set("Generic", password="1234")
        assert self.tik.project.create_task("this_asset_shouldnt_exist", categories=["Model", "Rig", "Lookdev"], parent_path="Assets/Characters/Soldier") == -1
        # check if the log message is correct
        assert self.tik.log.get_last_message() == ('This user does not have permissions for this action', 'warning')

    @clean_user
    def test_adding_categories(self):
        self.test_creating_and_adding_new_tasks()
        # add a category
        _test_tasks = self.tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks

        # try to add category without permissions
        self.tik.user.set("Generic", password="1234")
        assert self.tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["batman"].add_category("Gotham") == -1
        self.tik.user.set("Admin", password="1234")
        # add the Gotham category to Batman task
        assert self.tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["batman"].add_category("Gotham")

        # try to add a duplicate category
        assert self.tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["batman"].add_category("Gotham") == -1
        # check the log message
        assert self.tik.log.get_last_message() == ("Category 'Gotham' already exists in task 'batman'.", 'warning')


    @clean_user
    def test_scanning_tasks(self):
        self.test_creating_and_adding_new_tasks()

        # scan the tasks
        assert self.tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].scan_tasks()

        # modify one of the tasks and scan again
        # no permission
        self.tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["superman"].add_category("Testing")
        self.tik.user.set("Admin", password=1234)
        assert self.tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].scan_tasks()

    @clean_user
    def test_creating_works(self):
        self.test_creating_and_adding_new_tasks()

        self.tik.user.set("Admin", 1234)

        #create some addigional tasks
        asset_categories = ["Model", "Rig", "Lookdev"]

        bizarro_task = self.tik.project.create_task("bizarro", categories=asset_categories, parent_path="Assets/Characters/Soldier")
        ultraman_task = self.tik.project.create_task("ultraman", categories=asset_categories, parent_path="Assets/Characters/Soldier")
        superboy_task = self.tik.project.create_task("superboy", categories=asset_categories, parent_path="Assets/Characters/Soldier")

        # create a work
        bizarro_task.categories["Model"].create_work("default")
        bizarro_task.categories["Model"].create_work("main", file_format=".txt")
        bizarro_task.categories["Model"].create_work("lod300", file_format=".txt")

        bizarro_task.categories["Rig"].create_work("default")
        bizarro_task.categories["Rig"].create_work("main", file_format=".txt")
        bizarro_task.categories["Rig"].create_work("lod300", file_format=".txt")

        ultraman_task.categories["Model"].create_work("varA")
        ultraman_task.categories["Model"].create_work("varB")
        ultraman_task.categories["Model"].create_work("varC")

        ultraman_task.categories["Rig"].create_work("varA")
        ultraman_task.categories["Rig"].create_work("varB")
        ultraman_task.categories["Rig"].create_work("varC")

    @clean_user
    def test_scanning_works(self):
        self.test_creating_works()

        # scan all works
        assert self.tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["bizarro"].categories["Model"].scan_works(all_dcc=True)

        # override the guard.dcc
        self.tik.project.guard._dcc = "Maya"
        assert self.tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["bizarro"].categories["Model"].scan_works(all_dcc=False) == {}

    def test_deleting_empty_task(self):
        self.test_creating_and_adding_new_tasks()

        # try to delete a task without permissions
        self.tik.user.set("Generic", password="1234")
        assert self.tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].delete_task("superman") == -1
        # check if the log message is correct
        assert self.tik.log.get_last_message() == ('This user does not have permissions for this action', 'warning')
        # try to delete a non-existing task
        assert self.tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].delete_task("this_task_doesnt_exist") == -1

        # delete the task
        self.tik.user.set("Admin", password="1234")
        assert self.tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].delete_task("superman") == 1
    @clean_user
    def test_deleting_non_empty_tasks(self):
        self.test_creating_works()
        self.tik.user.set("Admin", password="1234")
        assert self.tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].delete_task("superboy") == 1

    @clean_user
    def test_deleting_empty_categories(self):
        self.test_adding_categories()

        # try to delete a category without permissions
        self.tik.user.set("Generic", password="1234")
        assert self.tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["batman"].delete_category("Gotham") == -1
        self.tik.user.set("Admin", password="1234")
        # try to delete a non-existing category
        assert self.tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["batman"].delete_category("Burhan") == -1
        # delete the Gotham category from Batman task
        self.tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["batman"].delete_category("Gotham")
        assert "Gotham" not in self.tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["batman"].categories.keys()

    @clean_user
    def test_deleting_non_empty_categories(self):
        self.test_adding_categories()
        # add a version to the Gotham category
        self.tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["batman"].categories["Gotham"].create_work("test_work")
        # try to delete a non-empty category
        self.tik.user.set("Admin", password="1234")
        assert self.tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["batman"].categories["Gotham"].is_empty() == False
        self.tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["batman"].delete_category("Gotham")
        # check the log message

