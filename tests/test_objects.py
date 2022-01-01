# import pytest
import uuid
from pprint import pprint
import shutil

import os
from tik_manager4.objects import project, user

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

# initialize project and user
pr = project.Project()
test_user = user.User(commons_directory=mockup_common)


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

    pr.save_structure()
    # pprint(pr.get_sub_tree())

    pr.create_folders(pr.database_path)
    pr.create_folders(pr._path)


def test_validating_existing_project():
    """Tests reading an existing project structure and compares it to the created one on-the-fly"""
    existing_project = project.Project()
    existing_project.path = pr.path
    # pprint(existing_project.get_sub_tree())

    # check if read and written match
    # print(pr.subs["Assets"].subs["Characters"].id, existing_project.subs["Assets"].subs["Characters"].id)
    assert pr.get_sub_tree() == existing_project.get_sub_tree(), "Read and Write of project structure does not match"


def test_reinitializing_user():
    """Tests creating a common folder and user databases"""
    assert test_user._validate_user_data() == 1, "Existing user data cannot be initialized"


def test_switching_users():
    # test switching to admin
    assert test_user.get_active_user() == "Generic"
    assert test_user.set_active_user("Admin") == ("Admin", "Success")
    assert not test_user.is_authenticated
    assert test_user.set_active_user("Generic", password="1234")
    assert test_user.is_authenticated

# def test_changing_user_passwords():



def test_adding_new_users_to_database():
    """Tests to add new users to commons database"""

    # test adding by users by not permitted users
    assert test_user.set_active_user("Generic", password="1234")
    assert test_user.create_new_user("Test_BasicUser", "tbu", "password", 0) == (-1, 'User Generic has no permission to create new users')

    assert test_user.set_active_user("Admin") # non-authenticated Admin
    assert test_user.create_new_user("Test_BasicUser", "tbu", "password", 0) == (-1, "Active user is not authenticated or the password is wrong")
    assert test_user.create_new_user("Test_BasicUser", "tbu", "password", 0, active_user_password="WRONG_PASS") == (-1, "Active user is not authenticated or the password is wrong")
    assert test_user.create_new_user("Test_BasicUser", "tbu", "password", 0, active_user_password="1234") == (1, "Success")
    assert test_user.create_new_user("Test_TaskUser", "ttu", "password", 1) == (1, 'Success')
    assert test_user.create_new_user("Test_ProjectUser", "ttu", "password", 2) == (1, 'Success')
    assert test_user.create_new_user("Test_AdminUser", "ttu", "password", 3) == (1, 'Success')

    assert test_user.create_new_user("Test_BasicUser", "tbu", "password", 0) == (-1, 'User Test_BasicUser already exists. Aborting')

    assert test_user.set_active_user("Test_AdminUser", password="1234")
    assert test_user.create_new_user("Extra_User", "ext", "extra", 2) == (1, "Success")

# TODO add tests to change passwords

if revert_flag:
    # back to the original one
    shutil.rmtree(t4_folder)
    os.rename(t4_folder.replace("TikManager4", "TikManager4_%s" % salt), t4_folder)
