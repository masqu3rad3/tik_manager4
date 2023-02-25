# pylint: disable=consider-using-f-string
# pylint: disable=super-with-arguments

from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui


class TikTaskItem(QtGui.QStandardItem):
    def __init__(self, structure_object, txt='', font_size=12, set_bold=False, rgb=None, *args, **kwargs):
        super(TikTaskItem, self).__init__(*args, **kwargs)

        self.data = None
        #
        fnt = QtGui.QFont('Open Sans', font_size)
        fnt.setBold(set_bold)
        self.setEditable(False)

        if rgb:
            self.setForeground(QtGui.QColor(*rgb))
        self.setFont(fnt)
        self.setText(txt)

        self.task = None
        self.set_data(structure_object)

    def set_data(self, structure_object):
        self.task = self.check_data(structure_object)

    @staticmethod
    def check_data(structure_object):
        """checks if this is a proper structural data"""
        return structure_object
        # if not isinstance(structure_object, task.Task):
        #     raise Exception("The data that feeds into the TikListItem must be a Task object")
        # return structure_object


class TikCategoryModel(QtGui.QStandardItemModel):
    columns = ["name", "date", "owner", "version_count", "publish_count"]

    def __init__(self, structure_object):
        super(TikCategoryModel, self).__init__()

        # self.setHorizontalHeaderLabels(self.columns)
        #
        self.category = None
        self.set_data(structure_object)

    def set_data(self, structure_object):
        self.category = self.check_data(structure_object)

    @staticmethod
    def check_data(structure_object):
        """checks if this is a proper structural data"""
        return structure_object
        # if not isinstance(structure_object, category.Category):
        #     raise Exception("The data that feeds into the TikListModel must be a Category object")
        # return structure_object


class TikCategoryView(QtWidgets.QTreeView):
    def __init__(self, parent=None):
        super(TikCategoryView, self).__init__(parent)


class TikCategoryLayout(QtWidgets.QVBoxLayout):
    def __init__(self, *args, **kwargs):
        super(TikCategoryLayout, self).__init__(*args, **kwargs)

        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)

        # create a test label
        self.test_label = QtWidgets.QLabel("TikCategoryLayout Test")
        self.addWidget(self.test_label)


# test the TikCategoryLayout
if __name__ == "__main__":
    import sys
    import os
    import tik_manager4

    app = QtWidgets.QApplication(sys.argv)

    test_project_path = os.path.join(os.path.expanduser("~"), "t4_test_manual_DO_NOT_USE")
    tik = tik_manager4.initialize("Standalone")
    tik.user.set("Admin", "1234")
    tik.set_project(test_project_path)

    # create a test dialog and add the layout
    test_dialog = QtWidgets.QDialog()
    category_layout = TikCategoryLayout()
    # show the category layout
    test_dialog.setWindowTitle("TikCategoryLayout Test")
    test_dialog.setLayout(category_layout)
    test_dialog.show()

    # test_dialog.setWindowTitle("TikCategoryLayout Test")
    # test_dialog.setLayout(category_layout)
    # test_dialog.show()

    app.exec_()

    sys.exit(app.exec_())
