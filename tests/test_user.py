"""Tests for User related functions"""
from .mockup import Mockup, clean_user
from tik_manager4.objects import user

class TestUser(object):
    """Uses a fresh mockup_common folder and test_project under user directory for all tests"""
    mock = Mockup()
    mock.prepare()
    user.User(common_directory=mock.common)  # this is for not popping up the "missing common folder" message
    from tik_manager4.objects.main import Main  # importing main checks the common folder definition, thats why its here
    tik = Main()

    @clean_user
    def test_reinitializing_user(self):
        """Tests validating the user information (again)"""
        self.tik.project.__init__()
        self.tik.user.__init__()
        assert self.tik.user._validate_user_data() == 1, "Existing user data failed to initialize"

    @clean_user
    def test_query_users(self):
        """Tests getting the user list from commons database"""
        self.tik.project.__init__()
        self.tik.user.__init__()
        user_list = self.tik.user.commons.get_users()
        assert user_list

    @clean_user
    def test_query_structures(self):
        """Tests if preset structures can be returned"""
        self.tik.project.__init__()
        self.tik.user.__init__()
        structures = self.tik.user.commons.get_project_structures()
        assert structures

    @clean_user
    def test_get_active_user(self):
        """Tests getting the currently active user from user database"""
        self.tik.project.__init__()
        self.tik.user.__init__()
        assert self.tik.user.get() == "Generic"
        assert self.tik.project.guard.user == "Generic"

    @clean_user
    def test_authenticating_user(self):
        """Tests authenticating the active user"""
        self.tik.project.__init__()
        self.tik.user.__init__()
        assert self.tik.user
        assert self.tik.user.authenticate("1234")
        assert self.tik.project.guard.is_authenticated == True

    @clean_user
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


    @clean_user
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

    @clean_user
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

    @clean_user
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

    @clean_user
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

    @clean_user
    def test_adding_new_project_bookmarks(self):
        self.tik.project.__init__()
        self.tik.user.__init__()
        assert self.tik.user.add_project_bookmark("projectA", "/path/to/projectA") == (1, "projectA added to bookmarks")
        assert self.tik.user.add_project_bookmark("projectB", "/path/to/projectB") == (1, "projectB added to bookmarks")
        assert self.tik.user.add_project_bookmark("projectB", "/path/to/projectB") == \
               (-1, "projectB already exists in user bookmarks")

    @clean_user
    def test_delete_project_bookmarks(self):
        self.tik.project.__init__()
        self.tik.user.__init__()
        self.tik.user.add_project_bookmark("ProjectToRemove", "/path/to/ProjectToRemove")
        assert len(self.tik.user.get_project_bookmarks()) == 1
        assert self.tik.user.delete_project_bookmark("ProjectToRemove") == (1, "Success")
        assert len(self.tik.user.get_project_bookmarks()) == 0
        assert self.tik.user.delete_project_bookmark("Ghosts") == (-1, "Ghosts doesn't exist in bookmarks. Aborting")

    @clean_user
    def test_get_project_bookmarks(self):
        self.tik.project.__init__()
        self.tik.user.__init__()
        assert self.tik.user.get_project_bookmarks() == []
        self.tik.user.add_project_bookmark("a_project", "/path/to/a_project")
        assert self.tik.user.get_project_bookmarks() == [{'name': 'a_project', 'path': '/path/to/a_project'}]



