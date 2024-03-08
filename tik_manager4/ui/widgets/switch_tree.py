"""Switch Tree Widget and Item for managing visibilities of widgets."""

from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.core import filelog
from tik_manager4.ui.dialog.feedback import Feedback
from tik_manager4.ui.dialog.user_dialog import LoginDialog

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")


class SwitchTreeItem(QtWidgets.QTreeWidgetItem):
    """Custom QTreeWidgetItem which holds and switch visibility of the content widgets."""

    def __init__(self, *args, content=None, permission_level=0, **kwargs):
        super().__init__(*args, **kwargs)
        self._content = content
        self.permission_level = permission_level

    @property
    def content(self):
        """Return the content widget"""
        return self._content

    @content.setter
    def content(self, widget):
        """Set the content widget"""
        # validata if the widget is a QWidget or None
        if widget is not None and not isinstance(widget, QtWidgets.QWidget):
            raise ValueError("The content must be a QWidget")
        self._content = widget

    def delete_content(self):
        """Delete the content widget"""
        if self._content:
            self._content.deleteLater()
            self._content = None


class SwitchTreeWidget(QtWidgets.QTreeWidget):
    """Custom QtreeWidget which holds and switch visibility of the content widgets."""

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_item = None
        self._last_valid_item = None
        self._user_object = user
        self.feedback = Feedback(parent=self)

        # currentItemChanged is not setting back the current item
        # like the itemClicked does. However it has better interaction.
        self.currentItemChanged.connect(self.switch_content)

    def clear(self):
        """Reset the tree widget."""
        self._current_item = None
        self._last_valid_item = None
        self.blockSignals(True)
        # delete the content widgets
        for idx in range(self.topLevelItemCount()):
            item = self.topLevelItem(idx)
            item.delete_content()
        super().clear()
        self.blockSignals(False)


    def switch_content(self, item):
        """Switch the content widget."""
        # block signals
        self.blockSignals(True)
        # check if the user is authenticated
        if self._user_object:
            if not self._user_object.is_authenticated:
                dialog = LoginDialog(self._user_object, parent=self)
                dialog.setWindowTitle("User Needs to be Authenticated")
                state = dialog.exec_()
                if not state:
                    self.blockSignals(False)
                    return
                #     # switch back to the self._current_item
                #     self.setCurrentItem(self._current_item)
                #     # unblock signals
                #     self.blockSignals(False)
                #     return
            # first check the clearance level
            if item.permission_level:
        # if self._user_object and item.permission_level:
                if self._user_object.check_permissions(level=item.permission_level) == -1:

                    message, title = LOG.get_last_message()
                    self.feedback.pop_info(title.capitalize(), message, critical=True)
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
