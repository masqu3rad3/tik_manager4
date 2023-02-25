# pylint: disable=consider-using-f-string
# pylint: disable=super-with-arguments

from tik_manager4.ui.Qt import QtWidgets, QtCore, QtGui


class TikWorkItem(QtGui.QStandardItem):
    def __init__(self, structure_object, txt='', font_size=12, set_bold=False, rgb=None, *args, **kwargs):
        super(TikWorkItem, self).__init__(*args, **kwargs)

        self.work = None
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


# class CategoryTabWidget(QtWidgets.QTabWidget):
#     """Custom tab widget to hold the category items too"""
#
#     def __init__(self):
#         super(CategoryTabWidget, self).__init__()
#
#     def add_category(self, category_name, category_data):
#         # create a widget to hold the
#




class TikCategoryLayout(QtWidgets.QVBoxLayout):
    def __init__(self, *args, **kwargs):
        super(TikCategoryLayout, self).__init__(*args, **kwargs)

        self.setContentsMargins(0, 0, 0, 0)
        # self.setSpacing(0)

        # create two radio buttons one for work and one for publish
        self.work_radio_button = QtWidgets.QRadioButton("Work")
        self.publish_radio_button = QtWidgets.QRadioButton("Publish")

        # TODO: this needs to come from the last state of the user
        self.work_radio_button.setChecked(True)

        # create a horizontal layout for the radio buttons
        self.radio_button_layout = QtWidgets.QHBoxLayout()
        # self.radio_button_layout.setContentsMargins(0, 0, 0, 0)
        self.radio_button_layout.setSpacing(6)
        self.radio_button_layout.addWidget(self.work_radio_button)
        self.radio_button_layout.addWidget(self.publish_radio_button)

        # add a spacer to the layout
        self.radio_button_layout.addStretch()

        # add the radio button layout to the main layout
        self.addLayout(self.radio_button_layout)


        self.category_tab_widget = QtWidgets.QTabWidget()
        self.category_tab_widget.setObjectName("category_tab_widget")
        self.addWidget(self.category_tab_widget)

        self.task = None

        # SIGNALS

        self.category_tab_widget.currentChanged.connect(self.on_category_change)

    def set_task(self, task):
        """Set the task"""
        self.task = task
        self.populate_categories(self.task.categories)

        # TODO: Instead of setting the current index to 0, try set it to the last tab that was open
        # set the current tab to the first tab
        self.category_tab_widget.setCurrentIndex(0)

    def populate_categories(self, categories):
        """Populate the layout with categories"""
        # clear the layout
        self.category_tab_widget.clear()
        for key, category in categories.items():
            # print(type(category))
            pre_tab = QtWidgets.QWidget()
            pre_tab.setObjectName(key)
            self.category_tab_widget.addTab(pre_tab, key)
            # self.append_category(category)

    def on_category_change(self, index):
        """When the category tab changes"""
        print(index)
        # get the current tab name
        current_tab_name = self.category_tab_widget.tabText(index)
        print(current_tab_name)
        if self.work_radio_button.isChecked():
            works = self.task.categories[current_tab_name].works
            print(works)
            self.populate_work()
        else:
            self.populate_publish()
        pass

    def populate_work(self):
        """Populate the work tab"""
        pass

    def populate_publish(self):
        """Populate the publish tab"""
        pass



# test the TikCategoryLayout
if __name__ == "__main__":
    import sys
    from time import sleep
    import os
    import tik_manager4

    app = QtWidgets.QApplication(sys.argv)

    test_project_path = os.path.join(os.path.expanduser("~"), "t4_test_manual_DO_NOT_USE")
    tik = tik_manager4.initialize("Standalone")
    tik.user.set("Admin", "1234")
    tik.set_project(test_project_path)

    # get an example task
    # tasks = tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks
    tasks = tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].scan_tasks()
    example_task_a = tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["superman"]
    example_task_b = tik.project.subs["Assets"].subs["Characters"].subs["Soldier"].tasks["batman"]

    # create a test dialog and add the layout
    test_dialog = QtWidgets.QDialog()
    category_layout = TikCategoryLayout()
    category_layout.set_task(example_task_a)
    # show the category layout
    test_dialog.setWindowTitle("TikCategoryLayout Test")
    test_dialog.setLayout(category_layout)
    # resize the dialog
    test_dialog.resize(800, 600)
    test_dialog.show()

    # sleep(3)
    # print("setting task to batman")
    # category_layout.set_task(example_task_b)


    app.exec_()

    sys.exit(app.exec_())
