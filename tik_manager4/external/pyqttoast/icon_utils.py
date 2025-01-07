from tik_manager4.ui.Qt.QtGui import QPixmap, QColor, QImage, qRgba
from .toast_enums import ToastIcon
from .os_utils import OSUtils
from tik_manager4.ui import pick


class IconUtils:

    @staticmethod
    def get_icon_from_enum(enum_icon: ToastIcon):
        """Get a QPixmap from a ToastIcon

        :param enum_icon: ToastIcon
        :return: pixmap of the ToastIcon
        """

        if enum_icon == ToastIcon.SUCCESS:
            return pick.pixmap("success")
            # return QPixmap(OSUtils.get_current_directory() + '/icons/success.png')
        elif enum_icon == ToastIcon.WARNING:
            return pick.pixmap("warning")
            # return QPixmap(OSUtils.get_current_directory() + '/icons/warning.png')
        elif enum_icon == ToastIcon.ERROR:
            return pick.pixmap("error")
            # return QPixmap(OSUtils.get_current_directory() + '/icons/error.png')
        elif enum_icon == ToastIcon.INFORMATION:
            return pick.pixmap("information")
            # return QPixmap(OSUtils.get_current_directory() + '/icons/information.png')
        elif enum_icon == ToastIcon.CLOSE:
            return pick.pixmap("close")
            # return QPixmap(OSUtils.get_current_directory() + '/icons/close.png')

    @staticmethod
    def recolor_image(image: QImage, color: QColor | None):
        """Take an image and return a copy with the colors changed

        :param image: image to recolor
        :param color: new color (None if the image should not be recolored)
        :return: recolored image
        """

        # Leave image as is if color is None
        if color is None:
            return image

        # Loop through every pixel
        for x in range(0, image.width()):
            for y in range(0, image.height()):
                # Get current color of the pixel
                current_color = image.pixelColor(x, y)
                # Replace the rgb values with rgb of new color and keep alpha the same
                new_color_r = color.red()
                new_color_g = color.green()
                new_color_b = color.blue()
                new_color = QColor.fromRgba(
                    qRgba(new_color_r, new_color_g, new_color_b, current_color.alpha()))
                image.setPixelColor(x, y, new_color)
        return image
