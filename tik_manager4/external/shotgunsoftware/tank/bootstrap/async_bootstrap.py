# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

# Import Qt without having to worry about the version to use.
from ..util.qt_importer import QtImporter

importer = QtImporter()
QtCore = importer.QtCore
QtGui = importer.QtGui
if QtCore is None:
    # Raise an exception when Qt is not available.
    raise ImportError


class AsyncBootstrapWrapper(QtCore.QObject):
    """
    Wrapper class that can bootstrap an :class:`~sgtk.Sgtk` instance
    asynchronously in a background thread, followed by the synchronous launching
    of an :class:`~sgtk.platform.Engine` instance in the main application thread.
    """

    def __init__(
        self,
        toolkit_manager,
        engine_name,
        entity,
        completed_callback,
        failed_callback,
        parent=None,
    ):
        """
        Initializes an instance of the asynchronous bootstrap wrapper.

        The callback functions used to signify the completion and the failure of the bootstrap
        must have the following signatures:

            ``completed_callback(engine)``

            where:
            - ``engine`` is the launched :class:`~sgtk.platform.Engine` instance.

            ``failed_callback(phase, exception)``

            where:
            - ``phase`` is the bootstrap phase that raised the exception,
                        ``ToolkitManager.TOOLKIT_BOOTSTRAP_PHASE`` or ``ToolkitManager.ENGINE_STARTUP_PHASE``.
                        Using this phase, the callback can decide if the toolkit core needs
                        to be re-imported to ensure usage of a swapped in version.
            - ``exception`` is the python exception raised while bootstrapping.

        :param toolkit_manager: :class:`~sgtk.bootstrap.ToolkitManager` instance bootstrapping the engine.
        :param engine_name: Name of the engine to launch.
        :param entity: Shotgun entity used to resolve a project context.
        :type entity: Dictionary with keys ``type`` and ``id``, or ``None`` for the site.
        :param completed_callback: Callback function that handles cleanup after successful completion of the bootstrap.
        :param failed_callback: Callback function that handles cleanup after failed completion of the bootstrap.
        :param parent: The parent object that will be used for for the bootstrapper.
        """

        super(AsyncBootstrapWrapper, self).__init__(parent=parent)

        self._toolkit_manager = toolkit_manager
        self._engine_name = engine_name
        self._entity = entity
        self._completed_callback = completed_callback
        self._failed_callback = failed_callback

        # Create a worker that can bootstrap the toolkit asynchronously in a background thread.
        self._worker = _BootstrapToolkitWorker(
            self._toolkit_manager, engine_name, entity
        )

        # This QThread object will live in the main thread, not in the new thread it will manage.
        self._thread = QtCore.QThread(parent=self)

        # Make the worker operate with the new thread affinity and use the QThread object event loop.
        self._worker.moveToThread(self._thread)

        # Start to work when the QThread object will have started its event loop in its new thread context.
        self._thread.started.connect(self._worker.work)

        # Make the worker report on the toolkit bootstrap progress.
        self._worker.progressing.connect(self._progress_bootstrap)

        # Handle completion of the toolkit bootstrap by the worker.
        self._worker.completed.connect(self._complete_bootstrap)

        # Handle failure of the toolkit bootstrap by the worker.
        self._worker.failed.connect(self._fail_bootstrap)

        # Make the QThread object exit its event loop when the work will be done.
        self._worker.done.connect(self._thread.quit)

    def bootstrap(self):
        """
        Starts the asynchronous bootstrap logic.
        """

        # Start the QThread object event loop in its new thread context.
        self._thread.start()

    # A decorator is used to shield against the slot threading issue described here:
    # http://stackoverflow.com/questions/20752154/pyqt-connecting-a-signal-to-a-slot-to-start-a-background-operation
    @QtCore.Slot(float, str)
    def _progress_bootstrap(self, progress_value, message):
        """
        Callback slot that reports back on the toolkit and engine bootstrap progress.

        This method calls the toolkit manager progress reporting callback.

        :param progress_value: Current progress value, ranging from 0.0 to 1.0.
        :param message: Progress message to report.
        """

        self._toolkit_manager.progress_callback(progress_value, message)

    # A decorator is used to shield against the slot threading issue described here:
    # http://stackoverflow.com/questions/20752154/pyqt-connecting-a-signal-to-a-slot-to-start-a-background-operation
    @QtCore.Slot()
    def _complete_bootstrap(self):
        """
        Callback slot that handles cleanup after successful completion of the toolkit bootstrap.
        """

        try:

            # Ladies and Gentlemen, start your engines!
            engine = self._toolkit_manager._start_engine(
                self._worker.get_sgtk(), self._engine_name, self._entity
            )

        except Exception as exception:

            # Handle cleanup after failed completion of the engine startup.
            self._failed_callback(self._toolkit_manager.ENGINE_STARTUP_PHASE, exception)

            return

        # Handle cleanup after successful completion of the engine startup.
        self._completed_callback(engine)

    # A decorator is used to shield against the slot threading issue described here:
    # http://stackoverflow.com/questions/20752154/pyqt-connecting-a-signal-to-a-slot-to-start-a-background-operation
    @QtCore.Slot(Exception)
    def _fail_bootstrap(self, exception):
        """
        Callback slot that handles cleanup after failed completion of the toolkit bootstrap.

        :param exception: Exception raised while bootstrapping the toolkit.
        """

        # Handle cleanup after failed completion of the toolkit bootstrap.
        self._failed_callback(self._toolkit_manager.TOOLKIT_BOOTSTRAP_PHASE, exception)


class _BootstrapToolkitWorker(QtCore.QObject):
    """
    Bootstrap worker that can bootstrap an :class:`~sgtk.Sgtk` instance asynchronously in a background thread.

    :signal: ``progressing(float, str)`` - Emitted while the bootstrap toolkit worker is progressing
             in its work in the background. The parameters are the current progress value and
             the progress message to report.
    :signal: ``completed()`` - Emitted when the bootstrap toolkit worker successfully completes
             its work in the background. Use ``get_sgtk()`` to retrieve the bootstrapped toolkit instance.
    :signal: ``failed(Exception)`` - Emitted when the bootstrap toolkit worker fails to complete
             its work in the background. The parameter is the python exception raised while bootstrapping.
    :signal: ``done()`` - Emitted when the bootstrap toolkit worker has done (whether completed or failed)
             its work in the background.
    """

    # Qt signal emitted while the bootstrap toolkit worker is progressing in its work in the background.
    progressing = QtCore.Signal(float, str)

    # Qt signal emitted when the bootstrap toolkit worker successfully completes its work in the background.
    completed = QtCore.Signal()

    # Qt signal emitted when the bootstrap toolkit worker fails to complete its work in the background.
    failed = QtCore.Signal(Exception)

    # Qt signal emitted when the bootstrap toolkit worker has done its work in the background.
    done = QtCore.Signal()

    def __init__(self, toolkit_manager, engine_name, entity, parent=None):
        """
        Initializes an instance of the bootstrap toolkit worker.

        :param toolkit_manager: :class:`~sgtk.bootstrap.ToolkitManager` instance bootstrapping the engine.
        :param engine_name: Name of the engine used to resolve a configuration.
        :param entity: Shotgun entity used to resolve a project context.
        :type entity: Dictionary with keys ``type`` and ``id``, or ``None`` for the site.
        :param parent: The parent object that will be used for the worker.
        """

        super(_BootstrapToolkitWorker, self).__init__(parent=parent)

        self._toolkit_manager = toolkit_manager
        self._engine_name = engine_name
        self._entity = entity

        # Bootstrapped toolkit instance for the given engine and entity.
        self._sgtk = None

    def get_sgtk(self):
        """
        Get the toolkit instance bootstrapped by the worker.

        :return: Bootstrapped :class:`~sgtk.Sgtk` instance.
        """

        return self._sgtk

    # A decorator is used to shield against the slot threading issue described here:
    # http://stackoverflow.com/questions/20752154/pyqt-connecting-a-signal-to-a-slot-to-start-a-background-operation
    @QtCore.Slot()
    def work(self):
        """
        Bootstraps a toolkit instance for the given engine and entity and
        signal the progress, and the completion or the failure of this work.
        """

        try:

            # Bootstrap a toolkit instance for the given engine and entity,
            # using a local thread-safe progress reporting callback.
            self._sgtk = self._toolkit_manager._bootstrap_sgtk(
                self._engine_name, self._entity, self._report_progress
            )

            # Signal completion of the toolkit bootstrap.
            self.completed.emit()

        except Exception as exception:

            # Signal failure of the toolkit bootstrap.
            self.failed.emit(exception)

        # Make the worker operate with the main thread affinity
        # where the main event loop can handle its deletion.
        # Only the worker can push itself to the main thread.
        #
        # This is NOT good if we're in a PySide2/Qt5 environment. It causes an
        # immediate crash.
        if QtCore.__version__.startswith("4."):
            self.moveToThread(QtCore.QCoreApplication.instance().thread())

        # Signal that the work is done.
        self.done.emit()

    def _report_progress(self, progress_value, message):
        """
        Callback function that reports back on the toolkit bootstrap progress.

        :param progress_value: Current progress value, ranging from 0.0 to 1.0.
        :param message: Progress message to report.
        """

        # Signal the toolkit bootstrap progress.
        self.progressing.emit(progress_value, message)


def _get_thread_info_msg(caller):
    """
    Debugging function that generates a message about the thread the calling process is running in.

    :param caller: Name of the calling process to include in the information message.
    :return: Generated information message.
    """

    if QtGui.QApplication.instance():
        if QtCore.QThread.currentThread() == QtGui.QApplication.instance().thread():
            msg = "%s is running in main Qt thread."
        else:
            msg = "%s is running in background Qt thread."
    else:
        msg = "%s in not running in a Qt thread!"

    return msg % caller
