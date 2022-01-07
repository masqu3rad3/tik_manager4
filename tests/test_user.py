"""Tests for User related functions"""
from .mockup import Mockup
from tik_manager4.objects import user, main


class TestUser:
    mock = Mockup()
    mock.prepare()
    user.User(commons_directory=mock.common_folder)
    tik = main.Main()

    def test_query_users(self):
        user_list = self.tik.user.commons.get_users()
        assert user_list
        self.mock.revert()

    def test_get_active_user(self):
        assert self.tik.user.get_active_user() == "Generic"
        self.mock.revert()

    def test_authenticating_user(self):
        assert self.tik.user
        assert self.tik.user.authenticate("1234")
        self.mock.revert()

    def test_switching_users(self):
        assert self.tik.user.set_active_user("Admin") == ("Admin", "Success")
        assert not self.tik.user.is_authenticated
        assert self.tik.user.set_active_user("Generic", password="1234")
        assert self.tik.user.is_authenticated
        self.mock.revert()




