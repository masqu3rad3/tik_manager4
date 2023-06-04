"""Tests for core modules."""
import os
import glob
import pytest
from tik_manager4.core import filelog
from tik_manager4.core import io
from tik_manager4.external.filelock import FileLock, Timeout


def test_filelog():
    """Test filelog module."""
    # test new log
    _test_log_dir =os.path.expanduser("~")
    # if the log file exists, delete it
    if os.path.exists(os.path.join(_test_log_dir, "test_log.log")):
        os.remove(os.path.join(_test_log_dir, "test_log.log"))
    log = filelog.Filelog(logname=__name__, filename="test_log")

    assert log.header("Header Test") == "Header Test"
    assert log.title("Title Test") == "Title Test"
    assert log.seperator()
    assert log.info("Test info message") == "Test info message"
    assert log.warning("Test warning message") == "Test warning message"
    assert log.error("Test error message") == "Test error message"
    pytest.raises(Exception, log.error, "do_not_proceed", proceed=False)
    assert log.get_last_message() == ("do_not_proceed", "error")

    # test continuing from existing log
    log = filelog.Filelog(logname="new_log_name", filename="test_log", file_dir=_test_log_dir, date=False, time=False, size_cap=0)
    assert log._get_now() == ""
    assert log.title("Test") == "Test"
    log.clear()
    assert log.get_size() == 44

def test_io():
    """Test io module"""
    test_io_files = glob.glob(os.path.join(os.path.expanduser("~"), "test_io.*"))
    # if there are any, delete them
    if test_io_files:
        for test_io_file in test_io_files:
            os.remove(test_io_file)

    # create a io module without any arguments
    _io = io.IO()
    # try defining non-valid file type
    with pytest.raises(Exception):
        _io.file_path = os.path.join(os.path.expanduser("~"), "test_io.NA")
    # no extension error
    with pytest.raises(Exception):
        _io.file_path = os.path.join(os.path.expanduser("~"), "test_io")
    # directory
    _io.file_path = os.path.join(os.path.expanduser("~"), "test_io.json")
    assert _io.file_path == os.path.join(os.path.expanduser("~"), "test_io.json")

    # create io object with arguments
    # _io = io.IO(file_name="test_io.json", folder_name="", root_path=os.path.expanduser("~"))
    _io = io.IO(file_path=os.path.join(os.path.expanduser("~"), "test_io.json"))

    test_data = {"test": "test"}

    # test locked files
    _lock = FileLock(os.path.join(os.path.expanduser("~"), "test_io.json.lock"))
    _lock.acquire()
    # write data to file
    with pytest.raises(Timeout):
        _io.write(test_data)
    _lock.release()

    # write data to file
    _io.write(test_data)

    # read data from file
    test_data_read = _io.read()
    assert test_data == test_data_read

    # read data from file with different file_path
    _io.read(file_path=os.path.join(os.path.expanduser("~"), "test_io.json"))

    # try to read data from file that does not exist
    assert _io.file_exists(os.path.join(os.path.expanduser("~"), "test_io.NA")) == False
    with pytest.raises(Exception):
        _io.read(file_path=os.path.join(os.path.expanduser("~"), "test_io.NA"))

    # create the non existing folder
    _io.folder_check(os.path.join(os.path.expanduser("~"), "test_io_folder", "test_io.json"))

    # delete the folder with os.rmdir
    os.rmdir(os.path.join(os.path.expanduser("~"), "test_io_folder"))

    # corrupt the test_io.json file purpose is to test the file_exists function
    with open(os.path.join(os.path.expanduser("~"), "test_io.json"), "w") as f:
        f.write("test")

    # test reading corrupted file
    pytest.raises(Exception, _io.read)





