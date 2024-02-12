# pylint: disable=import-error
"""Data classes for the dialogs."""

import dataclasses
from tik_manager4.ui.Qt import QtWidgets


@dataclasses.dataclass
class MainLayout:
    """Main layout structure for the settings dialog and contents."""

    master_layout: (QtWidgets.QVBoxLayout, QtWidgets.QHBoxLayout) = None
    header_layout: QtWidgets.QVBoxLayout = None
    body_layout: QtWidgets.QVBoxLayout = None
    splitter: QtWidgets.QSplitter = None
    left_v_lay: QtWidgets.QVBoxLayout = None
    right_v_lay: QtWidgets.QVBoxLayout = None
    button_box_lay: QtWidgets.QHBoxLayout = None
