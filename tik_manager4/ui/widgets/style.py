"""Style related custom widgets"""

from tik_manager4.ui.Qt import QtWidgets, QtCore


class ColorKeepingDelegate(QtWidgets.QStyledItemDelegate):
    """Custom item delegate to make sure the selected item won't lose its color when selected."""
    def paint(self, painter, option, index):
        if option.state & QtWidgets.QStyle.State_Selected:
            painter.save()
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(option.palette.highlight())
            painter.drawRect(option.rect)
            painter.restore()
            option.state &= ~QtWidgets.QStyle.State_Selected
        super().paint(painter, option, index)