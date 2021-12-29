# import pytest
import uuid
from pprint import pprint
import shutil

import os
from tik_manager4.objects import project, user

# class PropertyTest(object):
pr = project.Project()


def test_initialize():
    assert pr


def test_project_path():
    test_project = os.path.join(os.path.expanduser("~"), "test_project")
    if os.path.exists(test_project):
        shutil.rmtree(test_project)
    pr.path = test_project
    assert pr.path == test_project


def test_project_name():
    """Test for changing the project name"""
    pr.name = "test_project"
    assert pr.name == "test_project"


def test_project_resolution():
    """Test for changing project resolution"""
    pr.resolution = [1280, 720]
    assert pr.resolution == [1280, 720]


def test_creating_existing_sub_project():
    """Tests the scenario where duplicate sub-project creation attempt"""
    pr.add_sub_project("duplicate_test")
    assert pr.add_sub_project("duplicate_test") == 0


def test_create_a_shot_asset_project_structure():
    asset_categories = ["Model", "LookDev", "Rig"]
    shot_categories = ["Layout", "Animation", "Lighting", "Render"]

    assets = pr.add_sub_project("Assets")
    print("***********")
    print(assets)
    chars = assets.add_sub_project("Characters")
    props = assets.add_sub_project("Props")
    env = assets.add_sub_project("Environment")

    leaf_assets = [chars.add_sub_project("Soldier"),
                   props.add_sub_project("Rifle"),
                   props.add_sub_project("Knife"),
                   env.add_sub_project("Tree"),
                   env.add_sub_project("Ground")]

    for leaf in leaf_assets:
        for category in asset_categories:
            leaf.add_category(category)

    shots = pr.add_sub_project("Shots")
    sequence_a = shots.add_sub_project("SequenceA")
    leaf_shots = [sequence_a.add_sub_project("SHOT_010"), sequence_a.add_sub_project("SHOT_020"),
                  sequence_a.add_sub_project("SHOT_030"), sequence_a.add_sub_project("SHOT_040")]

    sequence_b = shots.add_sub_project("SequenceB")
    leaf_shots.append(sequence_b.add_sub_project("SHOT_010"))
    leaf_shots.append(sequence_b.add_sub_project("SHOT_070"))
    leaf_shots.append(sequence_b.add_sub_project("SHOT_120"))

    for leaf in leaf_shots:
        for category in shot_categories:
            leaf.add_category(category)

    # print("\n")
    # print("Project:", pr.name)
    # print("Assets:")
    # pprint(pr.subs)
    print("\n")
    # assert pr.subs["Assets"].subs["Characters"].subs["Soldier"].name == "Soldier"
    # pprint(list(pr.get_sub_project_names(recursive=True)))
    pr.save_structure()
    pprint(pr.get_sub_tree())

    pr.create_folders(pr.database_path)
    pr.create_folders(pr._path)


def test_validating_existing_project():
    """Tests reading an existing project structure and compares it to the created one on-the-fly"""
    existing_project = project.Project()
    existing_project.path = pr.path
    pprint(existing_project.get_sub_tree())
    # check if read and written match
    # print(pr.subs["Assets"].subs["Characters"].id, existing_project.subs["Assets"].subs["Characters"].id)
    assert pr.get_sub_tree() == existing_project.get_sub_tree(), "Read and Write of project structure does not match"


#
# def test_subproject():
#     test_sub_project_name = "sample_sub_project"
#     pr.add_sub_project(test_sub_project_name)
#     assert len(pr.sub_projects) == 1
#     assert str(pr.sub_projects[0]) == test_sub_project_name

# def test_second_level_sub_project():
#     second_level_sub_project_name = "second_level_test"
#     pr.sub_projects[0].add_sub_project(second_level_sub_project_name)
#     assert len(pr.sub_projects[0].sub_projects) == 1
#     assert str(pr.sub_projects[0].sub_projects[0]) == second_level_sub_project_name
#     print(pr.sub_projects[0].sub_projects[0]._relative_path)


def test_initializing_user():
    # create a mockup common folder
    mockup_common = os.path.join(os.path.expanduser("~"), "mockup_common")
    if os.path.exists(mockup_common):
        shutil.rmtree(mockup_common)
    os.mkdir(mockup_common)

    # temporarily rename the TikManager4 folder if there is one
    revert_flag = False
    salt = str(uuid.uuid4()).split("-")[-1]
    t4_folder = os.path.normpath(os.path.join(os.path.expanduser('~'), "TikManager4"))
    if os.path.isdir(t4_folder):
        revert_flag = True
        os.rename(t4_folder, t4_folder.replace("TikManager4", "TikManager4_%s" % salt))

    # test creating one from scratch
    user_init_from_scratch = user.User(commons_directory=mockup_common)
    print("User initialized from scratch")
    assert user_init_from_scratch._validate_user_data() == 1, "Existing user data cannot be initialized"

    if revert_flag:
        # back to the original one
        shutil.rmtree(t4_folder)
        os.rename(t4_folder.replace("TikManager4", "TikManager4_%s" % salt), t4_folder)
