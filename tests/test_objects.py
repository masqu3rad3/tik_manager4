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
revert_flag = True
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
    # assert test_user.get_active_user() == "Generic"
    assert test_user.set_active_user("Admin") == ("Admin", "Success")
    assert not test_user.is_authenticated
    assert test_user.set_active_user("Generic", password="1234")
    assert test_user.is_authenticated

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

    assert test_user.set_active_user("Test_AdminUser", password="password") == ("Test_AdminUser", "Success")
    # assert test_user.set_active_user("Test_AdminUser") == ("Test_AdminUser", "Success")
    assert test_user.create_new_user("Extra_User", "ext", "extra", 2) == (1, "Success")

def test_change_user_password():
    # Change active user passes
    assert test_user.set_active_user("Generic")
    # test providing wrong password
    assert test_user.change_user_password("WRONG_PASS", "amazing_password") == (-1, "Old password for Generic does not match")
    assert not test_user.is_authenticated
    assert test_user.authenticate_active_user("amazing_password") == (-1, "Wrong password provided for user Generic")
    assert not test_user.is_authenticated
    # test correct password
    assert test_user.change_user_password("1234", "amazing_password") == (1, "Success")
    assert not test_user.is_authenticated
    assert test_user.authenticate_active_user("amazing_password") == (1, "Success")
    assert test_user.authenticate_active_user("wtf") == (-1, "Wrong password provided for user Generic")
    assert not test_user.is_authenticated


    # Change other user passes
    assert test_user.change_user_password("WRONG_PASS", "awesome_password", user_name="Admin") == (-1, "Old password for Admin does not match")
    assert test_user.set_active_user("Admin", password="awesome_password")
    assert test_user.change_user_password("1234", "awesome_password", user_name="Admin") == (1, "Success")
    assert test_user.set_active_user("Admin", password="awesome_password") == ("Admin", "Success")

def test_delete_user():
    test_user.set_active_user("Test_ProjectUser", password="password")
    assert test_user.delete_user("Extra_User") == (-1, "User Test_ProjectUser has no permission to delete users")
    test_user.set_active_user("Test_AdminUser")
    assert test_user.delete_user("Admin") == (-1, "Active user is not authenticated or the password is wrong")
    test_user.authenticate_active_user("password")

    assert test_user.delete_user("Admin") == (-1, "Admin User cannot be deleted")
    assert test_user.delete_user("Generic") == (-1, "Generic User cannot be deleted")
    assert test_user.delete_user("NoOne") == (-1, "User NoOne does not exist. Aborting")
    assert test_user.delete_user("Extra_User") == (1, "Success")

def test_add_and_remove_project_bookmarks():
    assert test_user.add_project_bookmark("SOME_PROJECT", "some\\path") == (1, "Project SOME_PROJECT added to bookmarks")
    assert test_user.add_project_bookmark("shitPro", "some\\more\\path") == (1, "Project shitPro added to bookmarks")
    assert test_user.add_project_bookmark("SOME_PROJECT", "some\\path") == (-1, "Project SOME_PROJECT already exists in user bookmarks")
    #
    assert test_user.delete_project_bookmark("shitPro") == (1, "Project shitPro removed from bookmarks")
    assert test_user.delete_project_bookmark("shitPro") == (-1, "Project shitPro does not exist in bookmarks. Aborting")
    #

def test_get_bookmarks():
    print("\n", test_user.get_project_bookmarks())

# if revert_flag:
#     # back to the original one
#     shutil.rmtree(t4_folder)
#     os.rename(t4_folder.replace("TikManager4", "TikManager4_%s" % salt), t4_folder)
