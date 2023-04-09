"""Module for picking stuff."""
import os
from tik_manager4.ui.Qt.QtGui import QPixmap

IMAGES_FOLDER = os.path.join(os.path.dirname(__file__), 'images')
def image(image_name):
    """Instantiate an QPixmap from an image in the images folder."""
    print(os.path.join(IMAGES_FOLDER, image_name))
    return QPixmap(os.path.join(IMAGES_FOLDER, image_name))