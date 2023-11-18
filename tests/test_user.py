"""Tests for User related functions"""

from pathlib import Path

# import pytest

# from mockup import Mockup
# from tik_manager4.objects import user

# @pytest.mark.usefixtures("clean_user")
# @pytest.mark.usefixtures("prepare")
# class TestUser():
#     """Uses a fresh mockup_common folder and test_project under user directory for all tests"""
    # mock = Mockup()
    # mock.prepare()
    # user.User(common_directory=mock.common)  # this is for not popping up the "missing common folder" message

    # import tik_manager4  # importing main checks the common folder definition, thats why its here
    # tik = tik_manager4.initialize("Standalone")

def test_reinitializing_user(tik):
    """Tests validating the user information (again)"""
    tik.project.__init__()
    tik.user.__init__()
    assert tik.user._validate_user_data() == 1, "Existing user data failed to initialize"

def test_query_users(tik):
    """Tests getting the user list from commons database"""
    tik.project.__init__()
    tik.user.__init__()
    user_list = tik.user.commons.get_users()
    assert user_list

def test_query_structures(tik):
    """Tests if preset structures can be returned"""
    tik.project.__init__()
    tik.user.__init__()
    structures = tik.user.commons.get_project_structures()
    assert structures

def test_get_active_user(tik):
    """Tests getting the currently active user from user database"""
    tik.project.__init__()
    tik.user.__init__()
    assert tik.user.get() == "Generic"
    assert tik.project.guard.user == "Generic"

def test_authenticating_user(tik):
    """Tests authenticating the active user"""
    tik.project.__init__()
    tik.user.__init__()
    assert tik.user
    assert tik.user.authenticate("1234")
    assert tik.project.guard.is_authenticated == True

def test_switching_users(tik):
    """Tests switching between users"""
    tik.project.__init__()
    tik.user.__init__()
    # setting user without password authentication
    assert tik.user.set("Admin") == ("Admin", "Success")
    assert not tik.user.is_authenticated
    # setting user with password authentication
    assert tik.user.set("Generic", password="1234")
    assert tik.user.is_authenticated

def test_adding_new_users(tik):
    """Tests adding new users to database"""
    tik.project.__init__()
    tik.user.__init__()
    # test adding by users by not permitted users
    assert tik.user.set("Generic", password="1234")
    assert tik.user.create_new_user("Test_BasicUser", "tbu", "password", 0) == \
           (-1, 'User Generic has no permission to create new users')

    assert tik.user.set("Admin")  # non-authenticated Admin
    assert tik.user.create_new_user("Test_BasicUser", "tbu", "password", 0) == \
           (-1, "Active user is not authenticated or the password is wrong")
    assert tik.user.create_new_user("Test_BasicUser", "tbu", "password", 0,
                                         active_user_password="WRONG_PASS") == \
           (-1, "Active user is not authenticated or the password is wrong")
    assert tik.user.create_new_user("Test_BasicUser", "tbu", "password", 0,
                                         active_user_password="1234") == \
           (1, "Success")
    assert tik.user.create_new_user("Test_TaskUser", "ttu", "password", 1) == (1, 'Success')
    assert tik.user.create_new_user("Test_ProjectUser", "ttu", "password", 2) == (1, 'Success')
    assert tik.user.create_new_user("Test_AdminUser", "ttu", "password", 3) == (1, 'Success')

    assert tik.user.create_new_user("Test_BasicUser", "tbu", "password", 0) == \
           (-1, 'User Test_BasicUser already exists. Aborting')

    assert tik.user.set("Test_AdminUser", password="password") == ("Test_AdminUser", "Success")
    assert tik.user.create_new_user("Extra_User", "ext", "extra", 2) == (1, "Success")

def test_change_user_password(tik):
    tik.project.__init__()
    tik.user.__init__()
    # Change active user passes
    assert tik.user.set("Generic")
    # test providing wrong password
    assert tik.user.change_user_password("WRONG_PASS", "amazing_password") == (
        -1, "Old password for Generic does "
            "not match")
    assert not tik.user.is_authenticated
    assert tik.user.authenticate("amazing_password") == (-1, "Wrong password provided for user Generic")
    assert not tik.user.is_authenticated
    # test correct password
    assert tik.user.change_user_password("1234", "amazing_password") == (1, "Success")
    assert not tik.user.is_authenticated
    assert tik.user.authenticate("amazing_password") == (1, "Success")
    assert tik.user.authenticate("wtf") == (-1, "Wrong password provided for user Generic")
    assert not tik.user.is_authenticated

    # Change other user passes
    assert tik.user.change_user_password("WRONG_PASS", "awesome_password", user_name="Admin") == \
           (-1, "Old password for Admin does not match")
    assert tik.user.set("Admin", password="awesome_password")
    assert tik.user.change_user_password("1234", "awesome_password", user_name="Admin") == (1, "Success")
    assert tik.user.set("Admin", password="awesome_password") == ("Admin", "Success")

def test_change_permission_levels(tik):
    test_adding_new_users(tik)
    assert tik.user.set("Generic")
    assert tik.user.change_permission_level("Test_TaskUser", 3) == \
           (-1, "User Generic has no permission to change permission level of other users")
    assert tik.user.set("Admin")
    assert tik.user.change_permission_level("Test_TaskUser", 3) == \
           (-1, "Active user is not authenticated or the password is wrong")
    tik.user.authenticate("1234")
    assert tik.user.change_permission_level("Admin", 3) == \
           (-1, "Admin permission levels cannot be altered")
    assert tik.user.change_permission_level("Generic", 3) == \
           (-1, "Generic User permission levels cannot be altered")
    assert tik.user.change_permission_level("Burhan Altintop", 3) == \
           (-1, "User Burhan Altintop does not exist. Aborting")
    assert tik.user.change_permission_level("Test_TaskUser", 3) == \
           (1, "Success")

def test_delete_user(tik):
    test_adding_new_users(tik)

    tik.user.set("Test_ProjectUser", password="password")
    assert tik.user.delete_user("Extra_User") == \
           (-1, "User Test_ProjectUser has no permission to delete users")
    tik.user.set("Test_AdminUser")
    assert tik.user.delete_user("Admin") == (-1, "Active user is not authenticated or the password is wrong")
    tik.user.authenticate("password")

    assert tik.user.delete_user("Admin") == (-1, "Admin User cannot be deleted")
    assert tik.user.delete_user("Generic") == (-1, "Generic User cannot be deleted")
    assert tik.user.delete_user("Burhan Altintop") == (-1, "User Burhan Altintop does not exist. Aborting")
    assert tik.user.delete_user("Extra_User") == (1, "Success")

def test_get_project_bookmarks(tik):
    assert tik.user.get_project_bookmarks() == []
    tik.user.add_project_bookmark("/path/to/a_project")
    assert tik.user.get_project_bookmarks() == ["/path/to/a_project"]

def test_delete_project_bookmarks(tik):
    tik.user.add_project_bookmark("/path/to/ProjectToRemove")

    assert len(tik.user.get_project_bookmarks()) == 1
    assert tik.user.delete_project_bookmark("/path/to/ProjectToRemove") == 1
    assert len(tik.user.get_project_bookmarks()) == 0
    assert tik.user.delete_project_bookmark("/non/existing/project") == -1

def test_adding_new_project_bookmarks(tik):
    assert tik.user.add_project_bookmark("/path/to/projectA") == 1
    assert tik.user.add_project_bookmark("/path/to/projectB") == 1
    assert tik.user.add_project_bookmark("/path/to/projectB") == -1







