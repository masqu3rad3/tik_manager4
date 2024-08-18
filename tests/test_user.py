"""Tests for User related functions"""

from pathlib import Path
import pytest


def test_reinitializing_user(tik):
    """Tests validating the user information (again)"""
    tik.project.__init__()
    tik.user.__init__()
    assert (
        tik.user._validate_user_data() == 1
    ), "Existing user data failed to initialize"


def test_validating_commons_folder(tik, tmp_path, monkeypatch):
    """Test validating the commons folder."""
    tik.project.__init__()
    # Create a mock commons folder
    mock_commons = Path(tmp_path, "mock_commons")
    mock_commons.mkdir(exist_ok=True)

    # pretend there is a permission error to the folder
    def mock_copy(src, dst):
        raise PermissionError

    monkeypatch.setattr("shutil.copy", mock_copy)
    # test what happens when there is a permission error
    tik.user.commons.__init__(mock_commons.as_posix())
    assert not tik.user.commons.is_valid
    monkeypatch.undo()

    tik.user.commons.__init__(mock_commons.as_posix())
    assert tik.user.commons.is_valid


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


def test_user_level_through_entity(tik):
    """Test authenticating the user through the entity"""
    tik.project.__init__()
    tik.user.__init__()
    # set the user but don't authenticate
    tik.user.set("Admin")
    assert tik.project.check_permissions(3) == -1
    assert tik.log.get_last_message() == (
        "User is not authenticated",
        "warning",
    )
    tik.user.set("Generic")
    assert tik.project.check_permissions(3) == -1
    assert tik.log.get_last_message() == (
        "This user does not have permissions for this action",
        "warning",
    )

    tik.user.authenticate("1234")
    assert tik.project.check_permissions(1) == 1


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
    assert tik.user.create_new_user("Test_BasicUser", "tbu", "password", 0) == (
        -1,
        "User Generic has no permission to create new users",
    )

    assert tik.user.set("Admin")  # non-authenticated Admin
    assert tik.user.create_new_user("Test_BasicUser", "tbu", "password", 0) == (
        -1,
        "Active user is not authenticated or the password is wrong",
    )
    assert tik.user.create_new_user(
        "Test_BasicUser", "tbu", "password", 0, active_user_password="WRONG_PASS"
    ) == (-1, "Active user is not authenticated or the password is wrong")
    assert tik.user.create_new_user(
        "Test_BasicUser", "tbu", "password", 0, active_user_password="1234"
    ) == (1, "Success")
    assert tik.user.create_new_user("Test_TaskUser", "ttu", "password", 1) == (
        1,
        "Success",
    )
    assert tik.user.create_new_user("Test_ProjectUser", "ttu", "password", 2) == (
        1,
        "Success",
    )
    assert tik.user.create_new_user("Test_AdminUser", "ttu", "password", 3) == (
        1,
        "Success",
    )

    assert tik.user.create_new_user("Test_BasicUser", "tbu", "password", 0) == (
        -1,
        "User Test_BasicUser already exists. Aborting",
    )

    assert tik.user.set("Test_AdminUser", password="password") == (
        "Test_AdminUser",
        "Success",
    )
    assert tik.user.create_new_user("Extra_User", "ext", "extra", 2) == (1, "Success")


@pytest.mark.parametrize(
    "user, expected_level",
    [
        ("Admin", 3),
        ("Experienced", 2),
        ("Generic", 1),
        ("Observer", 0),
    ],
)
def test_check_permission_levels(tik, user, expected_level):
    tik.user.set(user)
    # fail the permission level
    assert tik.user.check_permissions(expected_level + 1) == -1
    # fail the authentication
    assert tik.user.check_permissions(expected_level) == -1
    tik.user.authenticate("1234")
    assert tik.user.check_permissions(expected_level) == 1


def test_get_and_set_last_project(tik):
    tik.user.set("Admin")
    assert tik.user.last_project
    tik.user.last_project = "Test_Project"
    assert tik.user.last_project == "Test_Project"


def test_get_and_set_last_task(tik):
    tik.user.set("Admin")
    # print(tik.user.resume.get_property("task"))
    assert tik.user.last_task == tik.user.resume.get_property("task")
    tik.user.last_task = 999
    assert tik.user.last_task == 999

def test_get_and_set_last_category(tik):
    tik.user.set("Admin")
    assert tik.user.last_category == tik.user.resume.get_property("category")
    tik.user.last_category = "Test_Category"
    assert tik.user.last_category == "Test_Category"

def test_get_and_set_last_work(tik):
    tik.user.set("Admin")
    assert tik.user.last_work == tik.user.resume.get_property("work")
    tik.user.last_work = "Test_Work"
    assert tik.user.last_work == "Test_Work"

def test_get_and_set_last_version(tik):
    tik.user.set("Admin")
    assert tik.user.last_version == tik.user.resume.get_property("version")
    tik.user.last_version = "Test_Version"
    assert tik.user.last_version == "Test_Version"

def test_change_user_password(tik):
    tik.project.__init__()
    tik.user.__init__()
    # Change active user passes
    assert tik.user.set("Generic")
    # test providing wrong password
    assert tik.user.change_user_password("WRONG_PASS", "amazing_password") == (
        -1,
        "Old password for Generic does " "not match",
    )
    assert not tik.user.is_authenticated
    assert tik.user.authenticate("amazing_password") == (
        -1,
        "Wrong password provided for user Generic",
    )
    assert not tik.user.is_authenticated
    # test correct password
    assert tik.user.change_user_password("1234", "amazing_password") == (1, "Success")
    assert not tik.user.is_authenticated
    assert tik.user.authenticate("amazing_password") == (1, "Success")
    assert tik.user.authenticate("wtf") == (
        -1,
        "Wrong password provided for user Generic",
    )
    assert not tik.user.is_authenticated

    # Change other user passes
    assert tik.user.change_user_password(
        "WRONG_PASS", "awesome_password", user_name="Admin"
    ) == (-1, "Old password for Admin does not match")
    assert tik.user.set("Admin", password="awesome_password")
    assert tik.user.change_user_password(
        "1234", "awesome_password", user_name="Admin"
    ) == (1, "Success")
    assert tik.user.set("Admin", password="awesome_password") == ("Admin", "Success")


def test_change_permission_levels(tik):
    test_adding_new_users(tik)
    assert tik.user.set("Generic")
    assert tik.user.change_permission_level("Test_TaskUser", 3) == (
        -1,
        "User Generic has no permission to change permission level of other users",
    )
    assert tik.user.set("Admin")
    assert tik.user.change_permission_level("Test_TaskUser", 3) == (
        -1,
        "Active user is not authenticated or the password is wrong",
    )
    tik.user.authenticate("1234")
    assert tik.user.change_permission_level("Admin", 3) == (
        -1,
        "Admin permission levels cannot be altered",
    )
    assert tik.user.change_permission_level("Generic", 3) == (
        -1,
        "Generic User permission levels cannot be altered",
    )
    assert tik.user.change_permission_level("Burhan Altintop", 3) == (
        -1,
        "User Burhan Altintop does not exist. Aborting",
    )
    assert tik.user.change_permission_level("Test_TaskUser", 3) == (1, "Success")


def test_delete_user(tik):
    test_adding_new_users(tik)

    tik.user.set("Test_ProjectUser", password="password")
    assert tik.user.delete_user("Extra_User") == (
        -1,
        "User Test_ProjectUser has no permission to delete users",
    )
    tik.user.set("Test_AdminUser")
    assert tik.user.delete_user("Admin") == (
        -1,
        "Active user is not authenticated or the password is wrong",
    )
    tik.user.authenticate("password")

    assert tik.user.delete_user("Admin") == (-1, "Admin User cannot be deleted")
    assert tik.user.delete_user("Generic") == (-1, "Generic User cannot be deleted")
    assert tik.user.delete_user("Burhan Altintop") == (
        -1,
        "User Burhan Altintop does not exist. Aborting",
    )
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
