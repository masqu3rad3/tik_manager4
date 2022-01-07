"""Creates a mockup commons and user folder"""
import uuid
import shutil
import os
from functools import wraps

class Mockup(object):
    def __init__(self):
        self._original_user_folder = None
        self._user_folder = None
        self._common_folder = None
        # self._salt = str(uuid.uuid4()).split("-")[-1]
        self._salt = "BCK"

    @property
    def common_folder(self):
        return self._common_folder

    def prepare(self):
        self._common_folder = self._create_mockup_common()
        self._original_user_folder = self._backup_user_folder()

    def revert(self):
        if self._original_user_folder:
            shutil.rmtree(self._user_folder)
            os.rename(self._user_folder.replace("TikManager4", "TikManager4_%s" % self._salt), self._user_folder)

    def _create_mockup_common(self):
        mockup_common = os.path.join(os.path.expanduser("~"), "mockup_common")
        if os.path.exists(mockup_common):
            shutil.rmtree(mockup_common)
        os.mkdir(mockup_common)
        return mockup_common

    def _backup_user_folder(self):
        self._user_folder = os.path.normpath(os.path.join(os.path.expanduser('~'), "TikManager4"))
        backup_folder = os.path.join(os.path.expanduser("~"), "TikManager4_%s" % self._salt)
        if os.path.exists(backup_folder):
            shutil.rmtree(self._user_folder)
            return None
        if os.path.isdir(self._user_folder):
            return os.rename(self._user_folder, self._user_folder.replace("TikManager4", "TikManager4_%s" % self._salt))
        return None

def fresh_start(func):
    """Decorator to make a fresh start (commons and user folder)
    """
    @wraps(func)
    def _fresh(*args, **kwargs):
        m = Mockup()
        m.prepare()
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise
        finally:
            m.revert()
            print("User folder reverted back")
    return _fresh

# a = Mockup()
# a.prepare()
# a.revert()