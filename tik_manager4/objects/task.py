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
                 file_name=None,
                 task_type=None,
                 parent_sub=None,
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
        self._file_name = self.get_property("file_name") or file_name
        self._type = self.get_property("type") or task_type

        self._categories = self.__build_categories(self.get_property("categories") or categories)

        self.parent_sub = parent_sub

    @property
    def file_name(self):
        return self._file_name

    @property
    def name(self):
        return self._name

    # @name.setter
    # def name(self, val):
    #     state = self._check_permissions(level=2)
    #     if state != 1:
    #         return -1
    #     self._name = val
    #     self.edit_property("name", val)
    #     self.apply_settings()
    @property
    def type(self):
        return self._type

    # @type.setter
    # def type(self, task_type):
    #     state = self._check_permissions(level=2)
    #     if state != 1:
    #         return -1
    #     self._type = task_type
    #     self.edit_property("type", task_type)
    #     self.apply_settings()

    @property
    def creator(self):
        return self._creator

    @property
    def reference_id(self):
        return self._task_id

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
            category_definition = self.guard.category_definitions.get_property(category)
            _categories[category] = (Category(name=category, parent_task=self, definition=category_definition))
            # check if the category defined in category definitions
            # if category in self.guard.category_definitions.properties.keys():
            #     category_definition = self.guard.category_definitions.get_property(category)
            #     _categories[category] = (Category(name=category, parent_task=self, definition=category_definition))
            # else:
            #     LOG.error("Category '{0}' is not defined in category definitions.".format(category), proceed=False)
        return _categories

    def add_category(self, category):
        """Add a category to the task."""
        state = self._check_permissions(level=2)
        if state != 1:
            return -1
        if category not in self.guard.category_definitions.properties.keys():
            LOG.error("Category '{0}' is not defined in category definitions.".format(category), proceed=False)
        # categories are very simple entities which can be constructed with a name and a path
        if category not in self._categories.keys():
            self._categories[category] = Category(name=category, parent_task=self)
            self._currentValue["categories"] = (list(self._categories.keys()))
            self.apply_settings()
            return self._categories[category]
        else:
            LOG.warning("Category '{0}' already exists in task '{1}'.".format(category, self.name))
            return -1

    def edit(self, name=None, task_type=None, categories=None):
        """Edit the task"""
        state = self._check_permissions(level=2)
        if state != 1:
            return -1
        if name and name != self.name:
            # check the sibling tasks to see if the name is already taken
            if name in self.parent_sub.tasks:
                LOG.error("Task name '{0}' already exists in sub '{1}'.".format(name, self.parent_sub.name))
                return -1
            self._name = name
            self.edit_property("name", name)
        if task_type and task_type != self.type:
            self._type = task_type
            self.edit_property("type", task_type)
        if categories and categories != list(self.categories.keys()):
            # check if the categories are list or tuple
            if not isinstance(categories, (list, tuple)):
                LOG.error("Categories must be a list or tuple.", proceed=False)
            # check if the categories are in the category definitions
            for category in categories:
                if category not in self.guard.category_definitions.properties.keys():
                    LOG.error("Category '{0}' is not defined in category definitions.".format(category), proceed=False)
            self._categories = self.__build_categories(categories)
            self.edit_property("categories", list(categories))
        self.apply_settings()

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

        return 1

    # def delete(self):
    #     """Deletes the task from the database"""
    #
    #     # check all categories are empty
    #     _is_empty = any([self._categories[x].is_empty() for x in self._categories])
    #     permission_level = 2 if _is_empty else 3
    #     state = self._check_permissions(level=permission_level)
    #     if state != 1:
    #         return -1


        # # delete task from database
        # shutil.rmtree(self.get_abs_database_path())
        # shutil.rmtree(self.get_abs_project_path())
        # return 0

    def order_categories(self, new_order):
        """
        Order the categories of the task.
        Args:
            new_order: (list) Categories with new order

        Returns:

        """
        state = self._check_permissions(level=2)
        if state != 1:
            return -1
        if len(new_order) != len(self._categories):
            LOG.error("New order list is not the same length as the current categories list.", proceed=False)
        for x in new_order:
            if x not in self.categories:
                LOG.error("New order list contains a category that is not in the current categories list.", proceed=False)
        self.edit_property("categories", new_order)
        self.apply_settings()
        return 1

    # def apply_settings(self, **kwargs):
    #     super(Task, self).apply_settings(**kwargs)
    #     self._categories = self.__build_categories(self.get_property("categories"))



    # def create_category_folders(self):
    #     """Creates folders for subprojects and categories below this starting from 'root' path"""
    #     # unfortunately python 2.x does not support  exist_ok argument...
    #     for category_name in self.categories.keys():
    #         _f = os.path.join(self.get_abs_database_path(category_name))
    #         if not os.path.exists(_f):
    #             os.makedirs(_f)
