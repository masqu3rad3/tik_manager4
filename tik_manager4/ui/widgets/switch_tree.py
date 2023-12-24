"""Switch Tree Widget and Item for managing visibilities of widgets."""

from tik_manager4.ui.Qt import QtWidgets

class SwitchTreeItem(QtWidgets.QTreeWidgetItem):
    """Custom QTreeWidgetItem which holds and switch visibility of the content widgets."""

    def __init__(self, *args, **kwargs):
        super(SwitchTreeItem, self).__init__(*args, **kwargs)
        self.content = None


class SwitchTreeWidget(QtWidgets.QTreeWidget):
    """Custom QtreeWidget which holds and switch visibility of the content widgets."""

    def __init__(self, *args, **kwargs):
        super(SwitchTreeWidget, self).__init__(*args, **kwargs)
        self._current_item = None
        # self.itemClicked.connect(self.switch_content)
        # make it work when programmatically changed too
        self.currentItemChanged.connect(self.switch_content)

    def switch_content(self, item):
        """Switch the content widget."""
        if self._current_item:
            if self._current_item.content:
                self._current_item.content.setVisible(False)
            # self._current_item.content.setVisible(False)
        if item.content:
            item.content.setVisible(True)
        self._current_item = item
