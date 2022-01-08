"""Tests for User related functions"""
from .mockup import Mockup, clean_user
from tik_manager4.objects import user


class TestUser:
    mock = Mockup()
    mock.prepare()
    user.User(commons_directory=mock.common)
    from tik_manager4.objects.main import Main
    tik = Main()

    @clean_user
    def test_reinitializing_user(self):
        """Tests validating the user information (again)"""
        assert self.tik.user._validate_user_data() == 1, "Existing user data cannot be initialized"

    @clean_user
    def test_query_users(self):
        """Tests getting the user list from commons database"""
        user_list = self.tik.user.commons.get_users()
        assert user_list

    @clean_user
    def test_get_active_user(self):
        """Tests getting the currently active user from user database"""
        assert self.tik.user.get_active_user() == "Generic"

    @clean_user
    def test_authenticating_user(self):
        """Tests authenticating the active user"""
        assert self.tik.user
        assert self.tik.user.authenticate("1234")

    @clean_user
    def test_switching_users(self):
        """Tests switching between users"""
        # setting user without password authentication
        assert self.tik.user.set_active_user("Admin") == ("Admin", "Success")
        assert not self.tik.user.is_authenticated
        # setting user with password authentication
        assert self.tik.user.set_active_user("Generic", password="1234")
        assert self.tik.user.is_authenticated

    @clean_user
    def test_adding_new_users(self):
        """Tests adding new users to database"""
        # test adding by users by not permitted users
        assert self.tik.user.set_active_user("Generic", password="1234")
        assert self.tik.user.create_new_user("Test_BasicUser", "tbu", "password", 0) == \
               (-1, 'User Generic has no permission to create new users')

        assert self.tik.user.set_active_user("Admin")  # non-authenticated Admin
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

        assert self.tik.user.set_active_user("Test_AdminUser", password="password") == ("Test_AdminUser", "Success")
        assert self.tik.user.create_new_user("Extra_User", "ext", "extra", 2) == (1, "Success")

    @clean_user
    def test_change_user_password(self):
        # Change active user passes
        assert self.tik.user.set_active_user("Generic")
        # test providing wrong password
        assert self.tik.user.change_user_password("WRONG_PASS", "amazing_password") == (-1, "Old password for Generic does "
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
        assert self.tik.user.set_active_user("Admin", password="awesome_password")
        assert self.tik.user.change_user_password("1234", "awesome_password", user_name="Admin") == (1, "Success")
        assert self.tik.user.set_active_user("Admin", password="awesome_password") == ("Admin", "Success")

    @clean_user
    def test_delete_user(self):
        # self.test_adding_new_users()
        self.tik.user.set_active_user("Test_ProjectUser", password="password")
        assert self.tik.user.delete_user("Extra_User") == (-1, "User Test_ProjectUser has no permission to delete users")
        self.tik.user.set_active_user("Test_AdminUser")
        assert self.tik.user.delete_user("Admin") == (-1, "Active user is not authenticated or the password is wrong")
        self.tik.user.authenticate("password")

        assert self.tik.user.delete_user("Admin") == (-1, "Admin User cannot be deleted")
        assert self.tik.user.delete_user("Generic") == (-1, "Generic User cannot be deleted")
        assert self.tik.user.delete_user("NoOne") == (-1, "User NoOne does not exist. Aborting")
        assert self.tik.user.delete_user("Extra_User") == (1, "Success")
