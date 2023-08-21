"""Tests for User related functions"""
from .mockup import Mockup
from tik_manager4.objects import user
import pytest


@pytest.fixture(autouse=True, scope='function')
def clean_user():
    # NOTE: There are other modules where clean_user is used as the decorator
    # under tests/mockup.py.  Since we don't wanna replicate this in each of
    # these files, this piece of code can be moved to a `conftest.py` (see
    # pytest documentation) and autouse may be disabled.  In this case, the
    # clean_user fixture should be explicitly added to all test arguments.
    # Explicit is better than implicit anyways...
    m = Mockup()
    m.backup_user()
    user.User(common_directory=m.mockup_commons_path)
    yield
    m.revert()


class TestUser(object):
    """Uses a fresh mockup_common folder and test_project under user directory for all tests"""
    mock = Mockup()
    mock.prepare()
    user.User(common_directory=mock.common)  # this is for not popping up the "missing common folder" message
    import tik_manager4  # importing main checks the common folder definition, thats why its here
    tik = tik_manager4.initialize("Standalone")

    def test_reinitializing_user(self):
        """Tests validating the user information (again)"""
        self.tik.project.__init__()
        self.tik.user.__init__()
        assert self.tik.user._validate_user_data() == 1, "Existing user data failed to initialize"

    def test_query_users(self):
        """Tests getting the user list from commons database"""
        self.tik.project.__init__()
        self.tik.user.__init__()
        user_list = self.tik.user.commons.get_users()
        assert user_list

    def test_query_structures(self):
        """Tests if preset structures can be returned"""
        self.tik.project.__init__()
        self.tik.user.__init__()
        structures = self.tik.user.commons.get_project_structures()
        assert structures

    def test_get_active_user(self):
        """Tests getting the currently active user from user database"""
        self.tik.project.__init__()
        self.tik.user.__init__()
        assert self.tik.user.get() == "Generic"
        assert self.tik.project.guard.user == "Generic"

    def test_authenticating_user(self):
        """Tests authenticating the active user"""
        self.tik.project.__init__()
        self.tik.user.__init__()
        assert self.tik.user
        assert self.tik.user.authenticate("1234")
        assert self.tik.project.guard.is_authenticated == True

    def test_switching_users(self):
        """Tests switching between users"""
        self.tik.project.__init__()
        self.tik.user.__init__()
        # setting user without password authentication
        assert self.tik.user.set("Admin") == ("Admin", "Success")
        assert not self.tik.user.is_authenticated
        # setting user with password authentication
        assert self.tik.user.set("Generic", password="1234")
        assert self.tik.user.is_authenticated

    def test_adding_new_users(self):
        """Tests adding new users to database"""
        self.tik.project.__init__()
        self.tik.user.__init__()
        # test adding by users by not permitted users
        assert self.tik.user.set("Generic", password="1234")
        assert self.tik.user.create_new_user("Test_BasicUser", "tbu", "password", 0) == \
               (-1, 'User Generic has no permission to create new users')

        assert self.tik.user.set("Admin")  # non-authenticated Admin
        assert self.tik.user.create_new_user("Test_BasicUser", "tbu", "password", 0) == \
               (-1, "Active user is not authenticated or the password is wrong")
        assert self.tik.user.create_new_user("Test_BasicUser", "tbu", "password", 0,
                                             active_user_password="WRONG_PASS") == \
               (-1, "Active user is not authenticated or the password is wrong")
        assert self.tik.user.create_new_user("Test_BasicUser", "tbu", "password", 0,
                                             active_user_password="1234") == \
               (1, "Success")
        assert self.tik.user.create_new_user("Test_TaskUser", "ttu", "password", 1) == (1, 'Success')
        assert self.tik.user.create_new_user("Test_ProjectUser", "ttu", "password", 2) == (1, 'Success')
        assert self.tik.user.create_new_user("Test_AdminUser", "ttu", "password", 3) == (1, 'Success')

        assert self.tik.user.create_new_user("Test_BasicUser", "tbu", "password", 0) == \
               (-1, 'User Test_BasicUser already exists. Aborting')

        assert self.tik.user.set("Test_AdminUser", password="password") == ("Test_AdminUser", "Success")
        assert self.tik.user.create_new_user("Extra_User", "ext", "extra", 2) == (1, "Success")

    def test_change_user_password(self):
        self.tik.project.__init__()
        self.tik.user.__init__()
        # Change active user passes
        assert self.tik.user.set("Generic")
        # test providing wrong password
        assert self.tik.user.change_user_password("WRONG_PASS", "amazing_password") == (
            -1, "Old password for Generic does "
                "not match")
        assert not self.tik.user.is_authenticated
        assert self.tik.user.authenticate("amazing_password") == (-1, "Wrong password provided for user Generic")
        assert not self.tik.user.is_authenticated
        # test correct password
        assert self.tik.user.change_user_password("1234", "amazing_password") == (1, "Success")
        assert not self.tik.user.is_authenticated
        assert self.tik.user.authenticate("amazing_password") == (1, "Success")
        assert self.tik.user.authenticate("wtf") == (-1, "Wrong password provided for user Generic")
        assert not self.tik.user.is_authenticated

        # Change other user passes
        assert self.tik.user.change_user_password("WRONG_PASS", "awesome_password", user_name="Admin") == \
               (-1, "Old password for Admin does not match")
        assert self.tik.user.set("Admin", password="awesome_password")
        assert self.tik.user.change_user_password("1234", "awesome_password", user_name="Admin") == (1, "Success")
        assert self.tik.user.set("Admin", password="awesome_password") == ("Admin", "Success")

    def test_change_permission_levels(self):
        self.tik.project.__init__()
        self.tik.user.__init__()
        assert self.tik.user.set("Generic")
        assert self.tik.user.change_permission_level("Test_TaskUser", 3) == \
               (-1, "User Generic has no permission to change permission level of other users")
        assert self.tik.user.set("Admin")
        assert self.tik.user.change_permission_level("Test_TaskUser", 3) == \
               (-1, "Active user is not authenticated or the password is wrong")
        self.tik.user.authenticate("1234")
        assert self.tik.user.change_permission_level("Admin", 3) == \
               (-1, "Admin permission levels cannot be altered")
        assert self.tik.user.change_permission_level("Generic", 3) == \
               (-1, "Generic User permission levels cannot be altered")
        assert self.tik.user.change_permission_level("Burhan Altintop", 3) == \
               (-1, "User Burhan Altintop does not exist. Aborting")
        assert self.tik.user.change_permission_level("Test_TaskUser", 3) == \
               (1, "Success")

    def test_delete_user(self):
        self.tik.project.__init__()
        self.tik.user.__init__()
        self.tik.user.set("Test_ProjectUser", password="password")
        assert self.tik.user.delete_user("Extra_User") == \
               (-1, "User Test_ProjectUser has no permission to delete users")
        self.tik.user.set("Test_AdminUser")
        assert self.tik.user.delete_user("Admin") == (-1, "Active user is not authenticated or the password is wrong")
        self.tik.user.authenticate("password")

        assert self.tik.user.delete_user("Admin") == (-1, "Admin User cannot be deleted")
        assert self.tik.user.delete_user("Generic") == (-1, "Generic User cannot be deleted")
        assert self.tik.user.delete_user("Burhan Altintop") == (-1, "User Burhan Altintop does not exist. Aborting")
        assert self.tik.user.delete_user("Extra_User") == (1, "Success")

    def test_adding_new_project_bookmarks(self):
        self.tik.project.__init__()
        self.tik.user.__init__()
        assert self.tik.user.add_project_bookmark("/path/to/projectA") == 1
        assert self.tik.user.add_project_bookmark("/path/to/projectB") == 1
        assert self.tik.user.add_project_bookmark("/path/to/projectB") == -1

    def test_delete_project_bookmarks(self):
        self.tik.project.__init__()
        self.tik.user.__init__()
        self.tik.user.add_project_bookmark("/path/to/ProjectToRemove")
        assert len(self.tik.user.get_project_bookmarks()) == 1
        assert self.tik.user.delete_project_bookmark("/path/to/ProjectToRemove") == 1
        assert len(self.tik.user.get_project_bookmarks()) == 0
        assert self.tik.user.delete_project_bookmark("/non/existing/project") == -1

    def test_get_project_bookmarks(self):
        self.tik.project.__init__()
        self.tik.user.__init__()
        assert self.tik.user.get_project_bookmarks() == []
        self.tik.user.add_project_bookmark("/path/to/a_project")
        assert self.tik.user.get_project_bookmarks() == ["/path/to/a_project"]
