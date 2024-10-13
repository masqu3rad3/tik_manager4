# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Main thread invoker utility class

--------------------------------------------------------------------------------
NOTE! This module is part of the authentication library internals and should
not be called directly. Interfaces and implementation of this module may change
at any point.
--------------------------------------------------------------------------------
"""

from .. import LogManager

logger = LogManager.get_logger(__name__)


# When importing qt_abstraction, a lot of code is executed to detects which
# version of Qt is being used. Running business logic at import time is not
# something usually done by the Toolkit. The worry is that the import may fail
# in the context of a DCC, but occur too early for the Toolkit logging to be
# fully in place to record it.
try:
    from .ui.qt_abstraction import QtCore, QtGui
except Exception:
    QtCore, QtGui = None, None


def create():
    """
    Create the object used to invoke function calls on the main thread when
    called from a different thread.

    You typically use this method like this:

        def show_ui():
            # show QT dialog
            dlg = MyQtDialog()
            result = dlg.exec_()
            return result

        # create invoker object
        my_invoker = invoker.create()

        # launch dialog - invoker ensures that the UI
        # gets launched in the main thread
        result = my_invoker(show_ui)

    :returns: Invoker instance. If Qt is not available or there is no UI, a
              simple pass through method will execute the code in the same
              thread will be produced.
    """
    # If we are already in the main thread, no need for an invoker, invoke directly in this thread.
    if QtCore.QThread.currentThread() == QtGui.QApplication.instance().thread():
        return lambda fn, *args, **kwargs: fn(*args, **kwargs)

    class MainThreadInvoker(QtCore.QObject):
        """
        Class that allows sending message to the main thread. This can be useful
        when a background thread needs to prompt the user via a dialog. The
        method passed into the invoker will be invoked on the main thread and
        the result, either a return value or exception, will be brought back
        to the invoking thread as if it was the thread that actually executed
        the code.
        """

        def __init__(self):
            """
            Constructor.
            """
            QtCore.QObject.__init__(self)
            self._res = None
            self._exception = None
            # Make sure that the invoker is bound to the main thread
            self.moveToThread(QtGui.QApplication.instance().thread())

        def __call__(self, fn, *args, **kwargs):
            """
            Asks the MainTheadInvoker to call a function with the provided parameters in the main
            thread.
            :param fn: Function to call in the main thread.
            :param args: Array of arguments for the method.
            :param kwargs: Dictionary of named arguments for the method.
            :returns: The result from the function.
            """
            self._fn = lambda: fn(*args, **kwargs)
            self._res = None

            logger.debug("Sending ui request to main thread.")

            QtCore.QMetaObject.invokeMethod(
                self, "_do_invoke", QtCore.Qt.BlockingQueuedConnection
            )

            # If an exception has been thrown, rethrow it.
            if self._exception:
                raise self._exception
            return self._res

        @QtCore.Slot()
        def _do_invoke(self):
            """
            Execute function and return result
            """
            try:
                logger.debug("Invoking from main thread.")
                self._res = self._fn()
            except Exception as e:
                self._exception = e

    return MainThreadInvoker()
