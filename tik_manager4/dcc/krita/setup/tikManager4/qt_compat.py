# PyQt5 -> PyQt6 compatibility

from tik_manager4.ui.Qt import QtCore, QtGui, QtWidgets

_QT6 = int(QtCore.qVersion().split(".")[0]) >= 6

if _QT6:
    # -------------------------------------------------------------------------
    # 1. ENUM NAMESPACE PATCHES
    # -------------------------------------------------------------------------
    _enum_patches = {
        QtCore.Qt: [
            "ItemDataRole",         # DisplayRole, EditRole, UserRole, DecorationRole,
                                    # CheckStateRole, ToolTipRole, ForegroundRole
            "AlignmentFlag",        # AlignLeft, AlignRight, AlignCenter, AlignVCenter,
                                    # AlignTop, AlignBottom, AlignHCenter
            "Orientation",          # Horizontal, Vertical
            "CheckState",           # Checked, Unchecked, PartiallyChecked
            "SortOrder",            # AscendingOrder, DescendingOrder
            "WindowType",           # Window, Dialog, Popup, Tool, SplashScreen,
                                    # FramelessWindowHint, WindowStaysOnTopHint,
                                    # WindowContextHelpButtonHint
            "KeyboardModifier",     # ControlModifier, ShiftModifier, AltModifier, NoModifier
            "MouseButton",          # LeftButton, RightButton, MiddleButton, NoButton
            "CursorShape",          # PointingHandCursor, ArrowCursor, WaitCursor,
                                    # SizeHorCursor, CrossCursor
            "TextElideMode",        # ElideRight, ElideLeft, ElideMiddle, ElideNone
            "MatchFlag",            # MatchExactly, MatchContains, MatchRecursive,
                                    # MatchStartsWith, MatchWildcard
            "AspectRatioMode",      # KeepAspectRatio, IgnoreAspectRatio,
                                    # KeepAspectRatioByExpanding
            "TransformationMode",   # SmoothTransformation, FastTransformation
            "GlobalColor",          # transparent, white, black, red, green, blue, gray
            "FocusPolicy",          # StrongFocus, NoFocus, TabFocus, ClickFocus, WheelFocus
            "DropAction",           # CopyAction, MoveAction, LinkAction, IgnoreAction
            "ContextMenuPolicy",    # CustomContextMenu, DefaultContextMenu, NoContextMenu
            "ScrollBarPolicy",      # ScrollBarAlwaysOff, ScrollBarAlwaysOn, ScrollBarAsNeeded
            "ScrollHint",           # EnsureVisible, PositionAtTop, PositionAtBottom,
                                    # PositionAtCenter
            "TextInteractionFlag",  # TextSelectableByMouse, TextSelectableByKeyboard,
                                    # TextBrowserInteraction, TextEditable
            "TextFormat",           # RichText, PlainText, AutoText, MarkdownText
            "TextFlag",             # TextSingleLine, TextWordWrap, TextExpandTabs
            "ToolButtonStyle",      # ToolButtonIconOnly, ToolButtonTextOnly,
                                    # ToolButtonTextBesideIcon
            "ArrowType",            # NoArrow, UpArrow, DownArrow, LeftArrow, RightArrow
            "BrushStyle",           # NoBrush, SolidPattern
            "PenStyle",             # NoPen, SolidLine, DashLine, DotLine
            "ItemFlag",             # ItemIsEnabled, ItemIsSelectable, ItemIsEditable,
                                    # ItemIsUserCheckable, ItemIsDragEnabled, ItemIsDropEnabled
            "WidgetAttribute",      # WA_DeleteOnClose, WA_TranslucentBackground,
                                    # WA_NoSystemBackground
            "ApplicationAttribute", # AA_DontUseNativeMenuBar, AA_EnableHighDpiScaling
            "Key",                  # Key_Control, Key_Shift, Key_Alt, Key_Return, Key_Escape
            "Corner",               # TopLeftCorner, TopRightCorner, BottomLeftCorner
            "DockWidgetArea",       # LeftDockWidgetArea, RightDockWidgetArea
            "ToolBarArea",          # LeftToolBarArea, RightToolBarArea, TopToolBarArea
            "ShortcutContext",      # WindowShortcut, ApplicationShortcut, WidgetShortcut
            "ConnectionType",       # AutoConnection, DirectConnection, QueuedConnection
        ],
        QtCore.QFile: [
            "OpenModeFlag",         # ReadOnly, WriteOnly, ReadWrite, Append, Text, Truncate
        ],
        QtCore.QDir: [
            "Filter",               # Files, Dirs, AllEntries, Hidden, NoDotAndDotDot
            "SortFlag",             # Name, Time, Size, Unsorted
        ],
        QtCore.QItemSelectionModel: [
            "SelectionFlag",        # Select, Deselect, Toggle, Current, Rows, Columns,
                                    # SelectCurrent, ToggleCurrent, ClearAndSelect, Clear
        ],
        QtGui.QPalette: [
            "ColorRole",            # Window, WindowText, Base, Text, Highlight,
                                    # HighlightedText, Button, ButtonText, AlternateBase
            "ColorGroup",           # Active, Inactive, Disabled, Normal
        ],
        QtGui.QFont: [
            "Weight",               # Thin, ExtraLight, Light, Normal, Medium,
                                    # DemiBold, Bold, ExtraBold, Black
            "Style",                # StyleNormal, StyleItalic, StyleOblique
            "Capitalization",       # MixedCase, AllUppercase, AllLowercase, SmallCaps
        ],
        QtGui.QPainter: [
            "RenderHint",           # Antialiasing, SmoothPixmapTransform, TextAntialiasing
            "CompositionMode",      # CompositionMode_SourceOver, CompositionMode_Clear,
                                    # CompositionMode_Source, CompositionMode_Destination
        ],
        QtGui.QTextCursor: [
            "MoveMode",             # MoveAnchor, KeepAnchor
            "MoveOperation",        # NoMove, Start, End, StartOfLine, EndOfLine
            "SelectionType",        # WordUnderCursor, LineUnderCursor, Document
        ],
        QtWidgets.QAbstractItemView: [
            "SelectionMode",        # NoSelection, SingleSelection, MultiSelection,
                                    # ExtendedSelection, ContiguousSelection
            "SelectionBehavior",    # SelectItems, SelectRows, SelectColumns
            "ScrollMode",           # ScrollPerItem, ScrollPerPixel
            "DragDropMode",         # NoDragDrop, DragOnly, DropOnly, DragDrop, InternalMove
            "EditTrigger",          # NoEditTriggers, CurrentChanged, DoubleClicked,
                                    # SelectedClicked, EditKeyPressed, AnyKeyPressed
        ],
        QtWidgets.QAbstractSpinBox: [
            "ButtonSymbols",        # UpDownArrows, PlusMinus, NoButtons
            "CorrectionMode",       # CorrectToPreviousValue, CorrectToNearestValue
            "StepType",             # DefaultStepType, AdaptiveDecimalStepType
        ],
        QtWidgets.QDialog: [
            "DialogCode",           # Accepted, Rejected
        ],
        QtWidgets.QDialogButtonBox: [
            "StandardButton",       # Ok, Open, Save, Cancel, Close, Discard, Apply,
                                    # Reset, RestoreDefaults, Help, Yes, No, Abort, Retry
            "ButtonRole",           # InvalidRole, AcceptRole, RejectRole, DestructiveRole,
                                    # ActionRole, HelpRole, YesRole, NoRole, ApplyRole
        ],
        QtWidgets.QFileDialog: [
            "Option",               # ShowDirsOnly, DontResolveSymlinks, DontUseNativeDialog
            "FileMode",             # AnyFile, ExistingFile, Directory, ExistingFiles
            "AcceptMode",           # AcceptOpen, AcceptSave
            "ViewMode",             # Detail, List
        ],
        QtWidgets.QFrame: [
            "Shape",                # NoFrame, Box, Panel, StyledPanel, HLine, VLine, WinPanel
            "Shadow",               # Plain, Raised, Sunken
        ],
        QtWidgets.QHeaderView: [
            "SectionResizeMode",    # Interactive, Fixed, Stretch, ResizeToContents
        ],
        QtWidgets.QLineEdit: [
            "EchoMode",             # Normal, NoEcho, Password, PasswordEchoOnEdit
            "ActionPosition",       # LeadingPosition, TrailingPosition
        ],
        QtWidgets.QListView: [
            "ViewMode",             # ListMode, IconMode
            "Flow",                 # LeftToRight, TopToBottom
            "ResizeMode",           # Fixed, Adjust
            "Movement",             # Static, Free, Snap
        ],
        QtWidgets.QMessageBox: [
            "StandardButton",       # Ok, Open, Save, Cancel, Close, Yes, No, Abort,
                                    # Retry, Ignore, YesToAll, NoToAll, Help, Apply,
                                    # Reset, RestoreDefaults, Discard, SaveAll
            "Icon",                 # NoIcon, Question, Information, Warning, Critical
        ],
        QtWidgets.QPlainTextEdit: [
            "LineWrapMode",         # NoWrap, WidgetWidth
        ],
        QtWidgets.QTextEdit: [
            "LineWrapMode",         # NoWrap, WidgetWidth, FixedPixelWidth, FixedColumnWidth
            "AutoFormattingFlag",   # AutoNone, AutoBulletList, AutoAll
        ],
        QtWidgets.QRubberBand: [
            "Shape",                # Rectangle, Line
        ],
        QtWidgets.QSizePolicy: [
            "Policy",               # Fixed, Minimum, Maximum, Preferred, Expanding,
                                    # MinimumExpanding, Ignored
            "ControlType",          # DefaultType, ButtonBox, CheckBox, ComboBox, Frame
        ],
        QtWidgets.QSlider: [
            "TickPosition",         # NoTicks, TicksAbove, TicksBelow, TicksBothSides
        ],
        QtWidgets.QStyle: [
            "StateFlag",            # State_Selected, State_Enabled, State_Active,
                                    # State_MouseOver, State_HasFocus
            "ComplexControl",       # CC_ComboBox, CC_SpinBox, CC_ScrollBar, CC_Slider
            "SubControl",           # SC_ComboBoxEditField, SC_ComboBoxArrow,
                                    # SC_ComboBoxFrame, SC_ComboBoxListBoxPopup
            "PrimitiveElement",     # PE_Widget, PE_Frame, PE_PanelButtonCommand
            "ControlElement",       # CE_PushButton, CE_CheckBox, CE_RadioButton
            "PixelMetric",          # PM_ButtonMargin, PM_DefaultFrameWidth
            "StandardPixmap",       # SP_MessageBoxInformation, SP_MessageBoxWarning
        ],
        QtWidgets.QTabBar: [
            "Shape",                # RoundedNorth, RoundedSouth, RoundedWest, RoundedEast
        ],
        QtWidgets.QTabWidget: [
            "TabPosition",          # North, South, East, West
            "TabShape",             # Rounded, Triangular
        ],
        QtWidgets.QToolButton: [
            "ToolButtonPopupMode",  # DelayedPopup, MenuButtonPopup, InstantPopup
        ],
        QtWidgets.QComboBox: [
            "InsertPolicy",         # NoInsert, InsertAtTop, InsertAtCurrent, InsertAtBottom
            "SizeAdjustPolicy",     # AdjustToContents, AdjustToContentsOnFirstShow
        ],
        QtWidgets.QMainWindow: [
            "DockOption",           # AnimatedDocks, AllowNestedDocks, AllowTabbedDocks
        ],
        QtCore.QEvent: [
            "Type",
            # ChildAdded, ChildRemoved, ChildPolished, Timer, KeyPress, KeyRelease,
            # MouseButtonPress, MouseButtonRelease, MouseMove, Resize, Paint,
            # Close, Show, Hide, Enter, Leave, FocusIn, FocusOut, Wheel
        ],
    }

    for _qt_class, _namespaces in _enum_patches.items():
        for _ns_name in _namespaces:
            _ns = getattr(_qt_class, _ns_name, None)
            if _ns is None:
                continue
            for _member in vars(_ns):
                if _member.startswith('_'):
                    continue
                if not hasattr(_qt_class, _member):
                    try:
                        setattr(_qt_class, _member, getattr(_ns, _member))
                    except (AttributeError, TypeError):
                        pass

    # -------------------------------------------------------------------------
    # 2. exec_() -> exec() PATCH
    # -------------------------------------------------------------------------
    _exec_classes = [
        QtWidgets.QDialog,
        QtWidgets.QApplication,
        QtWidgets.QMenu,
        QtWidgets.QMessageBox,
        QtWidgets.QFileDialog,
        QtWidgets.QColorDialog,
        QtWidgets.QFontDialog,
        QtWidgets.QInputDialog,
        QtWidgets.QProgressDialog,
        QtCore.QEventLoop,
        QtCore.QThread,
    ]
    for _cls in _exec_classes:
        if hasattr(_cls, 'exec') and not hasattr(_cls, 'exec_'):
            def _make_exec(cls):
                def exec_(self, *args, **kwargs):
                    return cls.exec(self, *args, **kwargs)
                return exec_
            try:
                _cls.exec_ = _make_exec(_cls)
            except (AttributeError, TypeError):
                pass

    # -------------------------------------------------------------------------
    # 3. METHOD RENAME PATCHES
    # -------------------------------------------------------------------------
    _method_renames = [
        (QtWidgets.QHeaderView, 'setResizeMode',    'setSectionResizeMode'),
        (QtWidgets.QHeaderView, 'resizeMode',       'sectionResizeMode'),
    ]
    for _cls, _old, _new in _method_renames:
        if hasattr(_cls, _new) and not hasattr(_cls, _old):
            try:
                setattr(_cls, _old, getattr(_cls, _new))
            except (AttributeError, TypeError):
                pass

    # -------------------------------------------------------------------------
    # 4. REMOVED CLASS PATCHES
    #    QRegExp removed in Qt6, replaced by QRegularExpression
    # -------------------------------------------------------------------------
    if not hasattr(QtCore, 'QRegExp'):
        QtCore.QRegExp = QtCore.QRegularExpression