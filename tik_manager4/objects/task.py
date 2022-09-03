# pylint: disable=consider-using-f-string
# pylint: disable=super-with-arguments

import os
import shutil
from glob import glob
from tik_manager4.core.settings import Settings
from tik_manager4.objects.category import Category
from tik_manager4.objects.entity import Entity
from tik_manager4.core import filelog

from collections import OrderedDict

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")

class Task(Settings, Entity):
    def __init__(self, absolute_path,
                 name=None,
                 categories=None,
                 path=None,
                 task_type=None,
                 ):
        super(Task, self).__init__()
        self.settings_file = absolute_path
        self._name = self.get_property("name") or name
        self._creator = self.get_property("creator") or self.guard.user
        # self._dcc = self.get_property("dcc") or self._guard.dcc
        self._works = {}
        self._publishes = {}
        self._task_id = self.get_property("task_id") or self.id
        self._relative_path = self.get_property("path") or path
        self._type = self.get_property("type") or task_type

        self._categories = self.__build_categories(self.get_property("categories") or categories)

    @property
    def type(self):
        return self._type

    @property
    def categories(self):
        return self._categories

    def __build_categories(self, category_list):
        """
        Builds a category objects from a list of category names

        Does not create folders or apply settings.
        Args: category_list: (list) List of category names
        """
        # _categories = OrderedDict()
        _categories = {}
        for category in category_list:
            _categories[category] = (Category(name=category, parent_task=self))
        return _categories


    def add_category(self, category):
        """Add a category to the task."""
        state = self._check_permissions(level=2)
        if state != 1:
            return -1
        # categories are very simple entities which can be constructed with a name and a path
        if category not in self._categories.keys():
            self._categories[category] = Category(name=category, parent_task=self)
            self._currentValue["categories"] = (list(self._categories.keys()))
            self.apply_settings()
            return self._categories[category]
        else:
            LOG.warning("Category '{0}' already exists in task '{1}'.".format(category, self.name))
            return -1
    def delete_category(self, category):
        """
        Delete a category from the task.
        Args:
            category: (str) Category to delete
            force: (bool) If True will delete the category with all its contents. If False will only delete it from the database

        Returns:

        """
        if category not in self._categories:
            LOG.warning("Category '{0}' does not exist in task '{1}'.".format(category, self.name))
            return -1

        _is_empty = self._categories[category].is_empty()
        permission_level = 2 if _is_empty else 3

        state = self._check_permissions(level=permission_level)
        if state != 1:
            return -1

        # delete category from database
        self._categories.pop(category)
        self._currentValue["categories"] = (list(self._categories.keys()))
        self.apply_settings()

        if not _is_empty:
            LOG.warning("Sending category '{0}' from task '{1}' to purgatory.".format(category, self.name))
            self._io.folder_check(self.get_purgatory_database_path(category))
            self._io.folder_check(self.get_purgatory_project_path(category))
            shutil.move(self.get_abs_database_path(category), self.get_purgatory_database_path(category))
            shutil.move(self.get_abs_project_path(category), self.get_purgatory_project_path(category))
        # shutil.rmtree(self.get_abs_database_path(category))
        # shutil.rmtree(self.get_abs_project_path(category))

        return 0

    def order_categories(self, new_order):
        """
        Order the categories of the task.
        Args:
            new_order: (list) Categories with new order

        Returns:

        """
        if len(new_order) != len(self._categories):
            LOG.error("New order list is not the same length as the current categories list.", proceed=False)
        for x in new_order:
            if x not in self.categories:
                LOG.error("New order list contains a category that is not in the current categories list.", proceed=False)
        self._categories = new_order
        self.apply_settings()
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        self._name = val
        self.add_property("name", val)

    @property
    def creator(self):
        return self._creator

    @property
    def reference_id(self):
        return self._task_id

    def create_category_folders(self):
        """Creates folders for subprojects and categories below this starting from 'root' path"""
        # unfortunately python 2.x does not support  exist_ok argument...
        for category_name in self.categories.keys():
            _f = os.path.join(self.get_abs_database_path(category_name))
            if not os.path.exists(_f):
                os.makedirs(_f)
