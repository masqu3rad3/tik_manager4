import logging
import os
import datetime


class Filelog(object):
    last_message = None
    last_message_type = None

    def __init__(
        self,
        logname=None,
        filename=None,
        filedir=None,
        date=True,
        time=True,
        size_cap=500000,
        *args,
        **kwargs
    ):
        super(Filelog, self).__init__()
        self.fileName = filename if filename else "defaultLog"
        self.fileDir = filedir if filedir else os.path.expanduser("~")
        self.filePath = os.path.join(self.fileDir, "%s.log" % self.fileName)
        self.logger = logging.getLogger(self.fileName)
        self.logger.setLevel(logging.DEBUG)
        self.log_name = logname if logname else self.fileName
        self.is_date = date
        self.is_time = time
        if not os.path.isfile(self.filePath):
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
            return "%s - " % now_string
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
        stamped_msg = "%sINFO    : %s" % (self._get_now(), msg)
        self._start_logging()
        self.logger.info(stamped_msg)
        self.__set_last_message(msg, "info")
        self._end_logging()
        return msg

    def warning(self, msg):
        stamped_msg = "%sWARNING : %s" % (self._get_now(), msg)
        self._start_logging()
        self.logger.warning(stamped_msg)
        self.__set_last_message(msg, "warning")
        self._end_logging()
        return msg

    def error(self, msg, proceed=True):
        stamped_msg = "%sERROR   : %s" % (self._get_now(), msg)
        self._start_logging()
        self.logger.error(stamped_msg)
        self.__set_last_message(msg, "error")
        self._end_logging()
        if not proceed:
            raise Exception(msg)
        return msg

    def title(self, msg):
        self._start_logging()
        self.logger.debug("")
        self.logger.debug("=" * (len(msg)))
        self.logger.debug(msg)
        self.logger.debug("=" * (len(msg)))
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
        self.logger.debug("-" * 30)
        # self.logger.debug("\n")
        self._end_logging()
        return True

    def clear(self):
        if os.path.isfile(self.filePath):
            os.remove(self.filePath)
        self._welcome()

    def _start_logging(self):
        """Prepares logger to write into log file"""
        file_logger = logging.FileHandler(self.filePath)
        self.logger.addHandler(file_logger)

    def _end_logging(self):
        """Deletes handlers once the logging into file finishes"""
        for handler in self.logger.handlers:
            self.logger.removeHandler(handler)
            handler.flush()
            handler.close()

    def get_size(self):
        size = os.path.getsize(self.filePath)
        return size
