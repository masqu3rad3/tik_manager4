# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import logging
from tank_vendor.six.moves import queue
import sys


class ToolkitEngineHandler(logging.Handler):
    """
    Log handling for engines that are using the
    new logging system introduced in 0.18. This will
    intercept all log messages in the stream to which
    it is connected and execute the :meth:`Engine._emit_log_message`
    on each of them, in a thread safe manner.
    """

    def __init__(self, engine):
        """
        :param engine: Engine to which log messages should be forwarded.
        :type engine: :class:`Engine`
        """
        # avoiding super in order to be py25-compatible
        logging.Handler.__init__(self)
        self._engine = engine

    def emit(self, record):
        """
        Emit a log message back to the engine logging callback.

        :param record: std log record to handle logging for
        """
        # for simplicity, add a 'basename' property to the record to
        # only contain the leaf part of the logging name
        # sgtk.env.asset.tk-maya -> tk-maya
        # sgtk.env.asset.tk-maya.tk-multi-publish -> tk-multi-publish
        record.basename = record.name.rsplit(".", 1)[-1]

        # emit log message from log handler to display implementation.
        self._engine._emit_log_message(self, record)


class ToolkitEngineLegacyHandler(logging.Handler):
    """
    Legacy handling of logging for engines which have not
    implemented :meth:`Engine._emit_log_message` but are
    still use log_debug, log_info etc.

    This will intercept all log messages in the stream to which
    it is connected and execute the various log_xxx callbacks
    based on the status of the log message.
    """

    def __init__(self, engine):
        """
        :param engine: Engine to which log messages should be forwarded.
        :type engine: :class:`Engine`
        """
        # avoiding super in order to be py25-compatible
        logging.Handler.__init__(self)
        self._engine = engine
        self._inside_dispatch_stack = queue.Queue()

    @property
    def inside_dispatch(self):
        """
        returns True if the handler is currently
        issuing a log dispatch call, false if not.
        """
        return not self._inside_dispatch_stack.empty()

    def emit(self, record):
        """
        Emit a log message back to the engine logging callback.

        :param record: std log record to handle logging for
        """
        if self.inside_dispatch:
            # the handler was triggered from a log emission which
            # in turn was triggered from this handler. This can happen
            # for example an log_xxx method writes to a logger rather than
            # outputting data to a console UI. In that case, make sure we
            # avoid an endless loop.
            return

        if hasattr(self._engine.sgtk, "log"):
            # legacy implementations of the shell and shotgun engines
            # handle their logging implementation by picking up a logger
            # passed from the tank command in a sgtk.log property. The logging
            # from these engines are then just writing to that logger.
            # We detect this here in order to avoid any double emission of
            # log messages, since the log_xxx methods that we would otherwise
            # be calling would simply just duplicate the log message.
            return

        # for simplicity, add a 'basename' property to the record to
        # only contain the leaf part of the logging name
        # sgtk.env.asset.tk-maya -> tk-maya
        # sgtk.env.asset.tk-maya.tk-multi-publish -> tk-multi-publish
        record.basename = record.name.rsplit(".", 1)[-1]

        # format the message
        msg_str = self.format(record)

        try:
            # push our thread safe stack to indicate that we
            # are inside the internal logging loop
            self._inside_dispatch_stack.put(True)

            if record.levelno < logging.INFO:
                self._engine.log_debug(msg_str)
            elif record.levelno < logging.WARNING:
                self._engine.log_info(msg_str)
            elif record.levelno < logging.ERROR:
                self._engine.log_warning(msg_str)
            else:
                self._engine.log_error(msg_str)

        finally:
            # take one item out
            self._inside_dispatch_stack.get()
