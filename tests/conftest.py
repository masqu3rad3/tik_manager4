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
    user.User(common_directory=m.common)
    yield
    m.revert()

@pytest.fixture(scope='function')
def prepare():
    print("\n")
    print("----------------------------")
    print("Preparing mockup folders")
    print("----------------------------")
    m = Mockup()
    m.prepare()
    user.User(common_directory=m.common)  # this is for not popping up the "missing common folder" message
    return

@pytest.fixture(scope='function')
def tik():
    """Initialize tik_manager4 for testing."""
    print("\n")
    print("----------------------------")
    print("Tik Manager 4 is initializing...")
    print("----------------------------")
    from importlib import reload
    import tik_manager4 # importing main checks the common folder definition, thats why its here
    reload(tik_manager4)
    return tik_manager4.initialize("Standalone")
