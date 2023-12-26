"""Module for picking stuff."""
import sys
from pathlib import Path

from tik_manager4.ui.Qt import QtCore, QtGui

# if it is frozen,
_FROZEN = getattr(sys, 'frozen', False)
DIRECTORY = Path(__file__).parent if not _FROZEN else Path(sys.executable).parent / "ui"
IMAGES_FOLDER = DIRECTORY / "images"
THEME_FOLDER = DIRECTORY / "theme"
# ICON_FOLDER = DIRECTORY / "icons"
RC_FOLDER = THEME_FOLDER / "rc"

def pixmap(image_name):
    """Instantiate an QPixmap from an image in the images' folder."""
    return QtGui.QPixmap(str(IMAGES_FOLDER / image_name))


def icon(icon_name):
    """Instantiate an QIcon from an image in the theme/rc folder."""
    return QtGui.QIcon(str(RC_FOLDER / icon_name))


def style_file():
    """Returns the style file as QtCore.QFile object."""
    QtCore.QDir.addSearchPath("css", str(THEME_FOLDER))
    QtCore.QDir.addSearchPath("rc", str(RC_FOLDER))
    style_qfile = QtCore.QFile("css:tikManager.qss")
    style_qfile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
    return style_qfile
