import logging
from pathlib import Path

from tik_manager4.core import utils

import datetime

class Filelog():
    # FIXME(ckutlu): We should definitely rethink the need for global state as
    # part of the class variable.
    last_message = None
    last_message_type = None

    def __init__(self, logname = None, filename="tik_manager4", filedir=None, date=True, time=True, size_cap=500000):
        # FIXME(ckutlu): Perhaps we can live with only a path argument
        super(Filelog, self).__init__()
        self.file_name = filename if filename else "defaultLog"
        self.file_dir = filedir or utils.get_home_dir()
        self.file_path_obj = Path(self.file_dir, f"{self.file_name}.log")
        self.logger = logging.getLogger(self.file_name)
        self.logger.setLevel(logging.DEBUG)
        self.log_name = logname if logname else self.file_name
        self.is_date = date
        self.is_time = time
        if not self.file_path_obj.is_file():
            self._welcome()
        if self.get_size() > size_cap:
            self.clear()

    @classmethod
    def __set_last_message(cls, msg, message_type):
        cls.last_message = msg
        cls.last_message_type = message_type

    @classmethod
    def get_last_message(cls):
        """Return the last message and its type."""
        return cls.last_message, cls.last_message_type

    def _get_now(self):
        if self.is_date or self.is_time:
            now = datetime.datetime.now()
            now_data = []
            if self.is_date:
                now_data.append(now.strftime("%d/%m/%y"))
            if self.is_time:
                now_data.append(now.strftime("%H:%M"))
            now_string = " - ".join(now_data)
            return "%s - " %now_string
        else:
            return ""

    def _welcome(self):
        self._start_logging()
        self.logger.debug("=" * len(self.log_name))
        self.logger.debug(self.log_name)
        self.logger.debug("=" * len(self.log_name))
        self.logger.debug("")
        self._end_logging()
        return self.log_name

    def info(self, msg):
        stamped_msg = "%sINFO     : %s" %(self._get_now(), msg)
        self._start_logging()
        self.logger.info(stamped_msg)
        self.__set_last_message(msg, "info")
        self._end_logging()
        return msg

    def warning(self, msg):
        stamped_msg = "%sWARNING  : %s" % (self._get_now(), msg)
        self._start_logging()
        self.logger.warning(stamped_msg)
        self.__set_last_message(msg, "warning")
        self._end_logging()
        return msg

    def error(self, msg, proceed=True):
        stamped_msg = "%sERROR    : %s" % (self._get_now(), msg)
        self._start_logging()
        self.logger.error(stamped_msg)
        self.__set_last_message(msg, "error")
        self._end_logging()
        if not proceed:
            raise Exception(msg)
        return msg

    def exception(self, msg):
        stamped_msg = "%sEXCEPTION: %s" % (self._get_now(), msg)
        self._start_logging()
        self.logger.exception(stamped_msg)
        self.__set_last_message(msg, "error")
        self._end_logging()
        return msg

    def title(self, msg):
        self._start_logging()
        self.logger.debug("")
        self.logger.debug("="*(len(msg)))
        self.logger.debug(msg)
        self.logger.debug("="*(len(msg)))
        # self.logger.debug("\n")
        self._end_logging()
        return msg

    def header(self, msg):
        self._start_logging()
        self.logger.debug("")
        self.logger.debug(msg)
        self.logger.debug("=" * (len(msg)))
        # self.logger.debug("\n")
        self._end_logging()
        return msg

    def seperator(self):
        self._start_logging()
        self.logger.debug("")
        self.logger.debug("-"*30)
        # self.logger.debug("\n")
        self._end_logging()
        return True

    def clear(self):
        if self.file_path_obj.is_file():
            self.file_path_obj.unlink()
        self._welcome()

    def _start_logging(self):
        """Prepares logger to write into log file"""
        file_logger = logging.FileHandler(str(self.file_path_obj))
        self.logger.addHandler(file_logger)

    def _end_logging(self):
        """Deletes handlers once the logging into file finishes"""
        for handler in self.logger.handlers:
            self.logger.removeHandler(handler)
            handler.flush()
            handler.close()

    def get_size(self):
        return self.file_path_obj.stat().st_size
