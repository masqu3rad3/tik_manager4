"""Module for picking stuff."""
import os
# from tik_manager4.ui.Qt.QtGui import QPixmap
from tik_manager4.ui.Qt import QtCore, QtGui

DIRECTORY = os.path.dirname(os.path.abspath(__file__))
IMAGES_FOLDER = os.path.join(DIRECTORY, 'images')
THEME_FOLDER = os.path.join(DIRECTORY, "theme")
RC_FOLDER = os.path.join(THEME_FOLDER, "rc")
def pixmap(image_name):
    """Instantiate an QPixmap from an image in the images folder."""
    return QtGui.QPixmap(os.path.join(IMAGES_FOLDER, image_name))

def icon(icon_name):
    """Instantiate an QIcon from an image in the images folder."""
    return QtGui.QIcon(os.path.join(RC_FOLDER, icon_name))

def style_file():
    """Returns the style file as QtCore.QFile object."""
    QtCore.QDir.addSearchPath("css", THEME_FOLDER)
    QtCore.QDir.addSearchPath("rc", RC_FOLDER)
    style_file = QtCore.QFile("css:tikManager.qss")
    style_file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
    return style_file