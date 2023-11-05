"""Tests for core modules."""
import pytest
import platform
import codecs
from pathlib import Path
from tik_manager4.core import filelog
from tik_manager4.core import io
from tik_manager4.external.filelock import FileLock, Timeout


def test_filelog(tmp_path: Path):
    """Test filelog module."""
    tmp_path_ = str(tmp_path)  # FIXME: remove when FileLog is typed
    # test new log
    logbasename = "test_log"
    
    test_log_path = tmp_path / f"{logbasename}.log"
    log = filelog.Filelog(logname=__name__, filename=f"{logbasename}", filedir=tmp_path_)

    assert log.header("Header Test") == "Header Test"
    assert log.title("Title Test") == "Title Test"
    assert log.seperator()
    assert log.info("Test info message") == "Test info message"
    assert log.warning("Test warning message") == "Test warning message"
    assert log.error("Test error message") == "Test error message"
    pytest.raises(Exception, log.error, "do_not_proceed", proceed=False)
    assert log.get_last_message() == ("do_not_proceed", "error")

    # test continuing from existing log
    log = filelog.Filelog(logname="new_log_name", filename="test_log", filedir=tmp_path_, date=False, time=False, size_cap=0)
    assert log._get_now() == ""
    assert log.title("Test") == "Test"
    log.clear()
    
    with open(tmp_path / 'test_log.log') as fin:
        log_file_contents = fin.read()

    log_file_contents_truth = "============\nnew_log_name\n============\n\n"
    assert log_file_contents == log_file_contents_truth
    
    # We should probably supply the encoding argument?
    bytes_ = codecs.encode(log_file_contents_truth)
    newline_count = bytes_.count(b"\n")
    nbytes = len(bytes_)
    nbytes_truth_per_system = {
            "Linux": nbytes,
            "Windows": nbytes + newline_count  # 2 chars for newline on windows
            }
    assert log.get_size() == nbytes_truth_per_system[platform.system()]


def test_io(tmp_path):
    """Test io module"""
    # create a io module without any arguments
    _io = io.IO()
    # try defining non-valid file type
    with pytest.raises(Exception):
        _io.file_path = str(tmp_path / "test_io.NA")
    # no extension error
    with pytest.raises(Exception):
        _io.file_path = str(tmp_path / "test_io")
    # directory
    _io.file_path = str(tmp_path / "test_io.json")
    assert _io.file_path == str(tmp_path / "test_io.json")

    # create io object with arguments
    _io = io.IO(file_path=str(tmp_path / "test_io.json"))

    test_data = {"test": "test"}

    # test locked files
    _lock = FileLock(str(tmp_path/"test_io.json.lock"))
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
    _io.read(file_path=str(tmp_path / "test_io.json"))

    # try to read data from file that does not exist
    assert _io.file_exists(str(tmp_path / "test_io.NA")) == False
    with pytest.raises(Exception):
        _io.read(file_path=str(tmp_path/"test_io.NA"))

    # corrupt the test_io.json file purpose is to test the file_exists function
    with open(tmp_path / "test_io.json", "w") as f:
        f.write("test")

    # test reading corrupted file
    pytest.raises(Exception, _io.read)
