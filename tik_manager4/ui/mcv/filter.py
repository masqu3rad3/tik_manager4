"""Credits to minimalefforttech for the FilterModel class
Based on the original code from
https://github.com/minimalefforttech
"""

from difflib import SequenceMatcher

from tik_manager4.ui.widgets.common import TikIconButton

from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui

class FilterModel(QtCore.QSortFilterProxyModel):
    """A simple filter model based on sequencematcher quick_ratio.
    ratio is 0-1 value for a match.
    Note: This is not performant, it is an example, ideally you would look into precaching or difflib.get_close_matches() for many items
    https://docs.python.org/3/library/difflib.html
    """

    def __init__(self, ratio: float = 0.6, parent=None):
        super().__init__(parent)
        self._filter_text = ""
        self._ratio = ratio
        self._show_all = False
        self.sort(0, QtCore.Qt.AscendingOrder)

    @QtCore.Slot(str)
    def set_filter_text(self, text: str):
        self._filter_text = str(text).lower()
        self.invalidate()

    @QtCore.Slot(float)
    def set_ratio(self, ratio: float):
        self._ratio = float(ratio)
        self.invalidate()

    @QtCore.Slot(bool)
    def set_show_all(self, show_all: bool):
        self._show_all = bool(show_all)
        self.invalidate()

    def filterAcceptsColumn(
        self, source_column: int, source_parent: QtCore.QModelIndex
    ) -> bool:
        return True

    def filterAcceptsRow(
        self, source_row: int, source_parent: QtCore.QModelIndex
    ) -> bool:
        if self._ratio <= 0.0 or self._show_all or not self._filter_text:
            # Nothing set, show everything
            return True

        # Case-insensitive
        text = (
            self.sourceModel().index(source_row, 0, source_parent).data() or ""
        ).lower()
        if not text:
            return False
        if self._filter_text in text:
            return True
        # First parameter is optional filtering of "junk" text like spaces, default is usually fine.
        # ratio is more accurate but doesn't provide much in this context, real_quick_ratio is not accurate enough.
        ratio = SequenceMatcher(None, self._filter_text, text).quick_ratio()
        # ratio = get_close_matches(self._filter_text, [text], 1, self._ratio)
        return ratio >= self._ratio

    def lessThan(self, left: QtCore.QModelIndex, right: QtCore.QModelIndex) -> bool:
        if not self._filter_text or self._show_all:
            return left.row() < right.row()

        left_ratio = (
            SequenceMatcher(None, self._filter_text, left.data().lower()).quick_ratio()
            if left.data()
            else 0.0
        )
        right_ratio = (
            SequenceMatcher(None, self._filter_text, right.data().lower()).quick_ratio()
            if right.data()
            else 0.0
        )
        # Sort text ascending so ratio is flipped
        return left_ratio > right_ratio

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not self._show_all or role != QtCore.Qt.ForegroundRole or self._ratio <= 0.0:
            return super().data(index, role)

        # Get and normalize text for comparison
        filter_text = self._filter_text or ""
        index_text = (super().data(index, QtCore.Qt.DisplayRole) or "").lower()
        ratio = SequenceMatcher(None, filter_text, index_text).quick_ratio()

        # if ratio < self._ratio:
        if ratio < self._ratio and filter_text:
            # Precompute falloff
            t = ratio * (1.0 / self._ratio)
            luminance = (1 - t) * 20 + t * 255
            scale_factor = luminance / 255

            # Get the original foreground color or default to white
            original_brush = super().data(index, QtCore.Qt.ForegroundRole)
            if original_brush and isinstance(original_brush, QtGui.QBrush):
                color = original_brush.color()
                r, g, b = color.red(), color.green(), color.blue()
            else:
                r = g = b = 255

            # Scale colors and clamp
            r = max(0, min(255, int(r * scale_factor)))
            g = max(0, min(255, int(g * scale_factor)))
            b = max(0, min(255, int(b * scale_factor)))

            return QtGui.QBrush(QtGui.QColor(r, g, b))

        return super().data(index, role)


class FilterWidget(QtWidgets.QWidget):
    """Filter widget with a line edit button and a slider."""
    def __init__(self, filter_model):
        super().__init__()
        if not isinstance(filter_model, FilterModel):
            raise ValueError("Invalid model")
        self._filter_model = filter_model

        self.master_layout = QtWidgets.QVBoxLayout(self)
        self.master_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.master_layout)

        self.basic_lay = QtWidgets.QHBoxLayout()
        # self.master_layout.addLayout(self.basic_lay)

        self.filter_le = QtWidgets.QLineEdit()
        self.filter_le.setPlaceholderText("Filter")
        self.filter_le.setClearButtonEnabled(True)
        self.filter_le.setFocus()

        self.basic_lay.addWidget(self.filter_le)

        self.adv_button = TikIconButton(icon_name="arrow_right", size=22)
        self.basic_lay.addWidget(self.adv_button)

        self.adv_widget = QtWidgets.QWidget()
        # no margins
        self.adv_widget.setContentsMargins(0, 0, 0, 0)
        self.adv_widget.setVisible(False)

        self.adv_lay = QtWidgets.QHBoxLayout()
        # no margins
        self.adv_lay.setContentsMargins(0, 0, 0, 0)
        self.adv_widget.setLayout(self.adv_lay)
        self.show_all_cb = QtWidgets.QCheckBox("All")
        self.show_all_cb.setChecked(False)
        self.show_all_cb.setToolTip("Show all items")
        self.adv_lay.addWidget(self.show_all_cb)

        self.ratio_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.ratio_slider.setRange(1, 100)
        self.ratio_slider.setValue(60)
        self.ratio_slider.setToolTip("Ratio")
        self.adv_lay.addWidget(self.ratio_slider)

        # add first the advanced widget
        self.master_layout.addWidget(self.adv_widget)
        # then the basic layout
        self.master_layout.addLayout(self.basic_lay)

        # SIGNALS
        self.filter_le.textChanged.connect(self._filter_model.set_filter_text)
        self.show_all_cb.toggled.connect(self._filter_model.set_show_all)
        self.ratio_slider.valueChanged.connect(self.on_set_ratio)
        self.adv_button.clicked.connect(self.toggle_advanced)

    def on_set_ratio(self, value):
        self._filter_model.set_ratio(value / 100.0)

    def toggle_advanced(self):
        self.adv_widget.setVisible(not self.adv_widget.isVisible())
        self.adv_button.set_icon("arrow_up" if self.adv_widget.isVisible() else "arrow_right")




