"""Configuration for pytest."""
import pytest
from .mockup import Mockup
from tik_manager4.objects import user
@pytest.fixture(scope='function')
def clean_user():
    print("\n")
    print("----------------------------")
    print("Creating a clean user folder")
    print("----------------------------")
    m = Mockup()
    m.backup_user()
    user.User(common_directory=m.mockup_commons_path)
    yield
    m.revert()

@pytest.fixture(scope='session')
def prepare():
    print("\n")
    print("----------------------------")
    print("Preparing mockup folders")
    print("----------------------------")
    m = Mockup()
    m.prepare()
    user.User(common_directory=m.common)  # this is for not popping up the "missing common folder" message
    return