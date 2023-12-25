"""Switch Tree Widget and Item for managing visibilities of widgets."""

from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.core import filelog
from tik_manager4.ui.dialog.feedback import Feedback

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")


class SwitchTreeItem(QtWidgets.QTreeWidgetItem):
    """Custom QTreeWidgetItem which holds and switch visibility of the content widgets."""

    def __init__(self, *args, content=None, permission_level=0, **kwargs):
        super(SwitchTreeItem, self).__init__(*args, **kwargs)
        self.content = content
        self.permission_level = permission_level


class SwitchTreeWidget(QtWidgets.QTreeWidget):
    """Custom QtreeWidget which holds and switch visibility of the content widgets."""

    def __init__(self, *args, user=None, **kwargs):
        super(SwitchTreeWidget, self).__init__(*args, **kwargs)
        self._current_item = None
        self._last_valid_item = None
        self._user_object = user
        self.feedback = Feedback(parent=self)
        # self.itemClicked.connect(self.switch_content)
        # make it work when programmatically changed too
        # set the current item to the first item

        # self.currentItemChanged.connect(self.switch_content)
        self.itemClicked.connect(self.switch_content)

    def switch_content(self, item):
        """Switch the content widget."""
        # block signals
        self.blockSignals(True)
        # first check the clearance level

        if self._user_object and item.permission_level:
            if self._user_object.check_permissions(level=item.permission_level) == -1:

                message, title = LOG.get_last_message()
                self.feedback.pop_info(title.capitalize(), message)
                # switch back to the self._current_item
                self.setCurrentItem(self._current_item)

                # unblock signals
                self.blockSignals(False)
                return
        if self._current_item:
            if self._current_item.content:
                self._current_item.content.setVisible(False)
            # self._current_item.content.setVisible(False)
        if item.content:
            item.content.setVisible(True)
        self._current_item = item
        self._last_valid_item = item
        # unblock signals
        self.blockSignals(False)
