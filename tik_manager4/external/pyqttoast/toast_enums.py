from enum import Enum


class ToastPreset(Enum):
    SUCCESS = 1
    WARNING = 2
    ERROR = 3
    INFORMATION = 4
    SUCCESS_DARK = 5
    WARNING_DARK = 6
    ERROR_DARK = 7
    INFORMATION_DARK = 8


class ToastIcon(Enum):
    SUCCESS = 1
    WARNING = 2
    ERROR = 3
    INFORMATION = 4
    CLOSE = 5


class ToastPosition(Enum):
    BOTTOM_LEFT = 1
    BOTTOM_MIDDLE = 2
    BOTTOM_RIGHT = 3
    TOP_LEFT = 4
    TOP_MIDDLE = 5
    TOP_RIGHT = 6
    CENTER = 7


class ToastButtonAlignment(Enum):
    TOP = 1
    MIDDLE = 2
    BOTTOM = 3
