"""Creates a mockup commons and user folder"""
import uuid
import shutil
import os
from functools import wraps
from tik_manager4.objects import user
import pdb


class Mockup(object):
    def __init__(self):
        _salt = str(uuid.uuid4()).split("-")[-1]
        self.user_backup_path = os.path.normpath(os.path.join(os.path.expanduser('~'), "TikManager4_BCK%s" % _salt))
        # self.user_backup_path = os.path.normpath(os.path.join(os.path.expanduser('~'), "TikManager4_BCK"))
        self.test_project_path = os.path.normpath(os.path.join(os.path.expanduser('~'), "test_project"))
        self.mockup_commons_path = os.path.normpath(os.path.join(os.path.expanduser('~'), "mockup_common"))
        self.user_path = os.path.normpath(os.path.join(os.path.expanduser('~'), "TikManager4"))

    @property
    def project(self):
        return self.test_project_path

    @property
    def common(self):
        return self.mockup_commons_path

    @property
    def user_folder(self):
        return self.user_path

    def prepare(self):
        self.__create_test_project()
        self.__create_mockup_common()
        # self.backup_user()

    def revert(self):
        if os.path.isdir(self.user_backup_path):
            if os.path.isdir(self.user_path):
                shutil.rmtree(self.user_path)
            os.rename(self.user_backup_path, self.user_path)

    def __create_test_project(self):
        if os.path.isdir(self.test_project_path):
            shutil.rmtree(self.test_project_path)
        os.mkdir(self.test_project_path)

    def __create_mockup_common(self):
        if os.path.isdir(self.mockup_commons_path):
            shutil.rmtree(self.mockup_commons_path)
        os.mkdir(self.mockup_commons_path)

    def backup_user(self):
        if os.path.isdir(self.user_backup_path):
            shutil.rmtree(self.user_backup_path)
        if os.path.isdir(self.user_path):
            os.rename(self.user_path, self.user_backup_path)
        else:
            os.makedirs(self.user_path)


def clean_user(func):
    """Decorator to make a fresh start (user folder)
    """

    @wraps(func)
    def _fresh(*args, **kwargs):
        m = Mockup()
        m.backup_user()
        user.User(commons_directory=m.mockup_commons_path)
        # pdb.set_trace()
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise
        finally:
            m.revert()

    return _fresh
