# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from .pyside2_patcher import PySide2Patcher

import imp

class PySide6Patcher(PySide2Patcher):
    """
    PySide6 backwards compatibility layer for use with PySide code.

    Patches PySide6 so it can be API compatible with PySide. This is the first step to provide
    support for PySide6. The next step will be to deprecate Qt4/PySide, and make Qt6/PySide6
    the default base qt module.

    .. code-block:: python
        from PySide6 import QtGui, QtCore, QtWidgets
        import PySide6
        PySide6Patcher.patch(QtCore, QtGui, QtWidgets, PySide6)
    """

    # These classes have been moved from QtGui to QtOpenGL in Qt6. Move them back to QtGui to
    # preserve compatibility between Qt6 and Qt4.
    _opengl_to_gui = set(
        [
            "QOpenGLBuffer",
            "QOpenGLDebugLogger",
            "QOpenGLDebugMessage",
            "QOpenGLFramebufferObject",
            "QOpenGLFramebufferObjectFormat",
            "QOpenGLPixelTransferOptions",
            "QOpenGLShader",
            "QOpenGLShaderProgram",
            "QOpenGLTexture",
            "QOpenGLTextureBlitter",
            "QOpenGLTimeMonitor",
            "QOpenGLTimerQuery",
            "QOpenGLVersionProfile",
            "QOpenGLVertexArrayObject",
            "QOpenGLWindow",
        ]
    )

    @classmethod
    def _patch_QAbstractItemView(cls, QtGui):
        """Patch QAbstractItemView."""

        def viewOptions(self):
            """Patch the viewOptions method."""

            option = QtGui.QStyleOptionViewItem()
            self.initViewItemOption(option)
            return option

        # First apply the patch from PySide2 patcher
        super(PySide6Patcher, cls)._patch_QAbstractItemView(QtGui)

        # Now apply any PySide6 specific patches
        QtGui.QAbstractItemView.viewOptions = viewOptions

    @classmethod
    def _patch_QTextCodec(cls, QtCore):
        """
        Patch QTextCodec.

        QTextCodec has been removed in Qt6. Using this class will do nothing.
        """

        class QTextCodec():
            @staticmethod
            def codecForName(name):
                return None

            @staticmethod
            def setCodecForCStrings(codec):
                pass

        QtCore.QTextCodec = QTextCodec

    @classmethod
    def _patch_QPixmap(cls, QtGui):
        """
        Patch QPixmap.

        QPixmap constructor no longer can take None as the first argument, instead no argument
        must be passed.
        """

        original_QPixmap = QtGui.QPixmap

        class QPixmap(original_QPixmap):
            def __init__(self, *args, **kwargs):
                if len(args) == 1 and args[0] is None:
                    original_QPixmap.__init__(self)
                else:
                    original_QPixmap.__init__(self, *args, **kwargs)

            @staticmethod
            def grabWindow(window=0, x=0, y=0, width=-1, height=-1):
                """
                Add deprecated method
                https://doc.qt.io/qt-5/qpixmap-obsolete.html#grabWindow
                """
                screen = QtGui.QApplication.primaryScreen()
                return screen.grabWindow(window, x, y, width, height)


        QtGui.QPixmap = QPixmap

    @classmethod
    def _patch_QIcon(cls, QtGui):
        """
        Patch QIcon.

        QIcon.pixmap method should create object from the patched QPixmap class
        """

        original_QIcon_pixmap = QtGui.QIcon.pixmap  # Returns a native QPixmap

        def pixmap(self, *args, **kwargs):
            return QtGui.QPixmap(original_QIcon_pixmap(self, *args, **kwargs))

        QtGui.QIcon.pixmap = pixmap


    @classmethod
    def _patch_QLabel(cls, QtGui):
        """
        Patch QLabel.

        Related to changes in QPixmap, None cannot be passed as null pixmap, instead an
        instance QPixmap must be created with no arguments.
        """

        original_QLabel_setPixmap = QtGui.QLabel.setPixmap

        def setPixmap(self, *args, **kwargs):
            if len(args) == 1 and args[0] is None:
                return original_QLabel_setPixmap(self, QtGui.QPixmap())
            return original_QLabel_setPixmap(self, *args, **kwargs)

        QtGui.QLabel.setPixmap = setPixmap

    @classmethod
    def _patch_QScreen(cls, QtCore, QtGui):
        """
        Patch the QScreen.

        Modify QScreen to be accessed as if it were QDesktopWidget to provide backward
        compatibility for QDesktopWidget.
        """

        class QDesktopWidget_screenCountChanged(QtCore.QObject):
            """Patch for QDesktopWidget screenCountChanged signal."""

            @staticmethod
            def connect(receiver):
                QtGui.QApplication.instance().screenAdded.connect(receiver)
                QtGui.QApplication.instance().screenRemoved.connect(receiver)

            @staticmethod
            def disconnect(receiver):
                QtGui.QApplication.instance().screenAdded.disconnect(receiver)
                QtGui.QApplication.instance().screenRemoved.disconnect(receiver)

            @staticmethod
            def emit(new_count):
                num_screens = len(QtGui.QGuiApplication.screens())
                if num_screens < new_count:
                    # screenAdded requires one arg, the QScreen that was added. Pass None
                    # since we do not have this data available to us here.
                    QtGui.QApplication.instance().screenAdded.emit(None)
                elif num_screens > new_count:
                    # screenRemoved requires one arg, the QScreen that was added. Pass None
                    # since we do not have this data available to us here.
                    QtGui.QApplication.instance().screenRemoved.emit(None)

        class QDesktopWidget_resized(QtCore.QObject):
            """Patch for QDesktopWidget resized signal."""

            @staticmethod
            def connect(receiver):
                # NOTE since we do not have the screen info, this signal will only work for
                # the primary screen
                screen = QtGui.QGuiApplication.primaryScreen()
                screen.geometryChanged.connect(receiver)

            @staticmethod
            def disconnect(receiver):
                # NOTE since we do not have the screen info, this signal will only work for
                # the primary screen
                screen = QtGui.QGuiApplication.primaryScreen()
                screen.geometryChanged.disconnect(receiver)

            @staticmethod
            def emit(screen_index):
                try:
                    screens = QtGui.QGuiApplication.screens()
                    screen = screens[screen_index]
                    screen.geometryChanged.emit()
                except:
                    pass


        original_QScreen_availableGeometry = QtGui.QScreen.availableGeometry
        def availableGeometry(self, widget=None):
            """Patch QScreen to also act as QDesktopWidget."""
            if widget is None:
                return original_QScreen_availableGeometry(self)

            if isinstance(widget, int):
                screens = QtGui.QGuiApplication.screens()
                try:
                    screen = screens[widget]
                except IndexError:
                    return QtCore.QRect()
            else:
                screen = widget.screen()

            return screen.availableGeometry()

        def screenNumber(self, widget):
            """Provide QDesktopWidget method through QScreen."""

            screen = widget.screen()
            try:
                return QtGui.QGuiApplication.screens().index(screen)
            except IndexError:
                return -1

        def screenCount(self):
            """Provide QDesktopWidget method through QScreen."""

            return len(QtGui.QGuiApplication.screens())

        def winId(self):
            """
            Provide QDesktopWidget method through QScreen.

            For QDesktopWidget, this would have returned the window system identifier of the
            desktop widget; however, QScreen is not a widget, so just return default value 0.
            """

            return 0

        # QDesktopWidget methods patched onto QScreen
        QtGui.QScreen.availableGeometry = availableGeometry
        QtGui.QScreen.screenGeometry = availableGeometry
        QtGui.QScreen.screenNumber = screenNumber
        QtGui.QScreen.screenCount = screenCount
        QtGui.QScreen.winId = winId

        # QDesktopWidget signals patched onto QScreen
        # https://doc.qt.io/qt-5/qdesktopwidget-obsolete.html#resized
        QtGui.QScreen.resized = QDesktopWidget_resized()
        QtGui.QScreen.screenCountChanged = QDesktopWidget_screenCountChanged()

    @classmethod
    def _patch_QOpenGLContext(cls, QtGui):
        """Patch QOpenGLContext."""

        def versionFunctions(self, version_profile=None):
            if version_profile:
                return QtGui.QOpenGLVersionFunctionsFactory.get(versionProfile=version_profile, context=self)
            return QtGui.QOpenGLVersionFunctionsFactory.get(context=self)

        QtGui.QOpenGLContext.versionFunctions = versionFunctions

    @classmethod
    def _patch_QWheelEvent(cls, QtGui):
        """Patch QWheelEvent."""

        def delta(self):
            """Patch the delta method."""

            # Use the more common mouse vertical scroll as the delta.
            # Horizontal scroll is ignored, use angleDelta().x() if the horizontal scroll is needed.
            return self.angleDelta().y()

        QtGui.QWheelEvent.delta = delta

    @classmethod
    def _patch_QModelIndex(cls, QtCore):
        """Patch QModelIndex."""

        def child(self, row, column):
            """Patch the child method."""

            return self.model().index(row, column, self)

        QtCore.QModelIndex.child = child

    @classmethod
    def _patch_QRegularExpression(cls, QtCore):
        """Patch QRegularExpression."""

        original_QRegularExpression = QtCore.QRegularExpression

        class QRegularExpression(original_QRegularExpression):
            def __init__(self, *args, **kwargs):
                if not args:
                    original_QRegularExpression.__init__(self)
                else:
                    nargs = len(args)

                    case_sensitivity = kwargs.get("cs")
                    if not case_sensitivity and nargs > 1:
                        case_sensitivity = args[1]

                    # FIXME can we port pattern syntax?
                    pattern_syntax = kwargs.get("syntax")
                    if not pattern_syntax and nargs > 2:
                        pattern_syntax = args[2]

                    if case_sensitivity is None:
                        original_QRegularExpression.__init__(self, args[0])
                    else:
                        if case_sensitivity == original_QRegularExpression.CaseInsensitiveOption:
                            opts = original_QRegularExpression.CaseInsensitiveOption
                        else:
                            opts = original_QRegularExpression.NoPatternOption
                        original_QRegularExpression.__init__(self, args[0], options=opts)

                self.isEmpty = lambda *args, **kwargs: QRegularExpression.isEmpty(self, *args, **kwargs)
                self.indexIn = lambda *args, **kwargs: QRegularExpression.indexIn(self, *args, **kwargs)
                self.matchedLength = lambda *args, **kwargs: QRegularExpression.matchedLength(self, *args, **kwargs)
                self.setCaseSensitivity = lambda *args, **kwargs: QRegularExpression.setCaseSensitivity(self, *args, **kwargs)
                self.pos = lambda *args, **kwargs: QRegularExpression.pos(self, *args, **kwargs)
                self.cap = lambda *args, **kwargs: QRegularExpression.cap(self, *args, **kwargs)

            @staticmethod
            def isEmpty(re):
                """Patch the QRegExp isEmpty method."""

                return not re.pattern()

            @staticmethod
            def indexIn(re, subject, offset=0):
                """Patch the QRegExp indexIn method."""

                if offset < 0:
                    return -1

                re_match = re.match(subject, offset)
                start = re_match.capturedStart(0)
                return start

            @staticmethod
            def setCaseSensitivity(re, value):
                """Patch QRegExp setCaseSensitivity method."""

                options = re.patternOptions()
                if value == original_QRegularExpression.CaseInsensitiveOption:
                    options |= original_QRegularExpression.CaseInsensitiveOption
                else:
                    options &= ~original_QRegularExpression.CaseInsensitiveOption
                re.setPatternOptions(options)

            @staticmethod
            def matchedLength(re):
                """
                This cannot be patched.

                Requires regular expression itself to have state, when regular expressions
                now return QRegularExpressionMatch objects.
                """
                return -1

            @staticmethod
            def pos(re, n):
                """
                This cannot be patched.

                Requires regular expression itself to have state, when regular expressions
                now return QRegularExpressionMatch objects.
                """
                return -1

            @staticmethod
            def cap(re, n):
                """
                This cannot be patched.

                Requires regular expression itself to have state, when regular expressions
                now return QRegularExpressionMatch objects.
                """
                return ""

        QtCore.QRegularExpression.isEmpty = QRegularExpression.isEmpty
        QtCore.QRegularExpression.indexIn = QRegularExpression.indexIn
        QtCore.QRegularExpression.matchedLength = QRegularExpression.matchedLength
        QtCore.QRegularExpression.setCaseSensitivity = QRegularExpression.setCaseSensitivity
        QtCore.QRegularExpression.pos = QRegularExpression.pos

        # This pattern matching flag is obsolete now.
        QtCore.QRegularExpression.FixedString = None

        # Class must be set last
        QtCore.QRegularExpression = QRegularExpression

    @classmethod
    def _patch_QCoreApplication_flush(cls, QtCore):
        """
        Patch QCoreApplication obsolete flush method for compatibility.
        """

        def flush():
            """
            No-op function to serve as a placeholder for QCoreApplication.flush().
            """
            pass

        # Add the no-op flush method to QCoreApplication
        QtCore.QCoreApplication.flush = flush

    @classmethod
    def patch(cls):
        """
        Patch the PySide6 modules, classes and function to conform to the PySide interface.

        Note that when referring to PySide and Qt version, these are equivalent:

            PySide == Qt4, PySide2 == Qt5, Qt6 == PySide6

        :param QtCore: The QtCore module for PySide6.
        :param QtGui: The QtGui module for PySide6.
        :param QtWidgets: The QtWidgets module for PySide6.

        :return: The PySide6 modules QtCore and QtGui patched as PySide modules.
        :rtype: tuple
        """

        import PySide6
        from PySide6 import (
            QtCore,
            QtGui,
            QtWidgets,
            QtOpenGL,
            QtWebEngineWidgets,
            QtWebEngineCore,
        )

        # First create new modules to act as the PySide modules
        qt_core_shim = imp.new_module("PySide.QtCore")
        qt_gui_shim = imp.new_module("PySide.QtGui")
        qt_web_engine_widgets_shim = imp.new_module("PySide.QtWebEnginWidgets")

        # Move everything from QtGui and QtWidgets to the QtGui shim since they belonged there
        # in PySide.
        cls._move_attributes(qt_gui_shim, QtWidgets, dir(QtWidgets))
        cls._move_attributes(qt_gui_shim, QtGui, dir(QtGui))

        # Some classes from QtGui have been moved to QtCore, so put them back into QtGui
        cls._move_attributes(qt_gui_shim, QtCore, cls._core_to_qtgui)
        # Move the rest of QtCore in the new core shim.
        cls._move_attributes(
            qt_core_shim, QtCore, set(dir(QtCore)) - cls._core_to_qtgui
        )

        # Some classes from QtGui have been moved to QtOpenGL, so put them back into QtGui for
        # compatibility with Qt4
        # https://doc.qt.io/qt-6/gui-changes-qt6.html#opengl-classes
        cls._move_attributes(qt_gui_shim, QtOpenGL, cls._opengl_to_gui)

        # Move everything from QtWebEngineWidgets to the QtWebEngineWidgets shim
        cls._move_attributes(qt_web_engine_widgets_shim, QtWebEngineWidgets, dir(QtWebEngineWidgets))

        # Patch classes from PySide6 to PySide, as done for PySide2 (these will call the
        # PySide2 patcher methods.)
        cls._patch_QCoreApplication(qt_core_shim)
        cls._patch_QApplication(qt_gui_shim)
        cls._patch_QStandardItemModel(qt_gui_shim)
        if PySide6.__version_info__[0] < 5:
            cls._patch_QMessageBox(qt_gui_shim)
        cls._patch_QDesktopServices(qt_gui_shim, qt_core_shim)

        # ------------------------------------------------------------------------------------
        # Patch specific for PySide6
        # ------------------------------------------------------------------------------------

        # QtCore
        # ------------------------------------------------------------------------------------

        # Attribute renamed
        qt_core_shim.Qt.MidButton = qt_core_shim.Qt.MiddleButton

        # QTextCodec class removed
        cls._patch_QTextCodec(qt_core_shim)

        # QModelIndex.child method removed
        # https://doc.qt.io/qt-5/qmodelindex-obsolete.html
        cls._patch_QModelIndex(qt_core_shim)

        # QRegExp replaced by QRegularExpression.
        # https://doc.qt.io/qt-6/qtcore-changes-qt6.html#regular-expression-classes
        # cls._patch_QRegExp(qt_core_shim)
        cls._patch_QRegularExpression(qt_core_shim)
        qt_core_shim.QRegExp = qt_core_shim.QRegularExpression
        # Rename RegExp functions to RegularExpression
        qt_gui_shim.QSortFilterProxyModel.filterRegExp = qt_gui_shim.QSortFilterProxyModel.filterRegularExpression
        qt_gui_shim.QSortFilterProxyModel.setFilterRegExp = qt_gui_shim.QSortFilterProxyModel.setFilterRegularExpression

        # Patch the QCoreApplication.flush() method to ensure compatibility with code
        # that expects this method, which is marked as obsolete.
        # https://doc.qt.io/qt-5/qcoreapplication-obsolete.html#flush
        cls._patch_QCoreApplication_flush(qt_core_shim)

        # QtGui
        # ------------------------------------------------------------------------------------

        # QLabel cannot be instantiated with None anymore
        cls._patch_QPixmap(qt_gui_shim)
        cls._patch_QLabel(qt_gui_shim)

        # QIcon.pixmap method should create object from the patched QPixmap class
        cls._patch_QIcon(qt_gui_shim)

        # QWheelEvent delta is obsolete
        # https://doc.qt.io/qt-5/qwheelevent-obsolete.html#delta
        cls._patch_QWheelEvent(qt_gui_shim)

        # QOpenGLContext.versionFunctions replaced
        # https://doc.qt.io/qt-6/gui-changes-qt6.html#the-qopenglcontext-class
        cls._patch_QOpenGLContext(qt_gui_shim)

        # QAbstractItemView.viewOptions renamed and changed
        # https://doc.qt.io/qt-6/widgets-changes-qt6.html#the-qabstractitemview-class
        cls._patch_QAbstractItemView(qt_gui_shim)

        # QDesktopWidget removed along with QApplication.desktop, in favor or QScreen. Patch
        # QScreen such that it can be used as if it were a QDesktopWidget instance
        # https://doc.qt.io/qt-6/widgets-changes-qt6.html#qdesktopwidget-and-qapplication-desktop
        cls._patch_QScreen(qt_core_shim, qt_gui_shim)
        qt_gui_shim.QDesktopWidget = qt_gui_shim.QScreen
        qt_gui_shim.QApplication.desktop = lambda: qt_gui_shim.QApplication.primaryScreen()

        # The default timeout parameter removed. This param, if given, will be ignored. It will
        # always timeout after 100 ms
        # https://doc.qt.io/qt-6/widgets-changes-qt6.html#the-qabstractbutton-class
        qt_gui_shim.QAbstractButton.animateClick = lambda self, msec=0: self.animateClick()

        # Changes to QFont
        # https://doc.qt.io/qt-6/gui-changes-qt6.html#the-qfont-class
        qt_gui_shim.QFontMetrics.width = qt_gui_shim.QFontMetrics.horizontalAdvance
        qt_gui_shim.QFont.setWeight = qt_gui_shim.QFont.setLegacyWeight

        # QHeaderView method rename
        qt_gui_shim.QHeaderView.setResizeMode = qt_gui_shim.QHeaderView.setSectionResizeMode

        # QPainter HighQualityAntialiasing is obsolete. Use Antiasliasing instead.
        # https://doc.qt.io/qt-5/qpainter.html#RenderHint-enum
        qt_gui_shim.QPainter.HighQualityAntialiasing = qt_gui_shim.QPainter.Antialiasing

        # QPaelette Background is obsolete. Use Window instead.
        # https://doc.qt.io/qt-5/qpalette.html#ColorRole-enum
        qt_gui_shim.QPalette.Background = qt_gui_shim.QPalette.Window

        # QtWwebEngineWidgets
        # ----------------------------------------------------------------------
        qt_web_engine_widgets_shim.QWebEnginePage = QtWebEngineCore.QWebEnginePage
        qt_web_engine_widgets_shim.QWebEngineProfile = QtWebEngineCore.QWebEngineProfile

        return qt_core_shim, qt_gui_shim, qt_web_engine_widgets_shim
