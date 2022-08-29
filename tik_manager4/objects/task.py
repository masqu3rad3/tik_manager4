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
        self._creator = self.get_property("creator") or self._guard.user
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
        _categories = OrderedDict()
        for category in category_list:
            _categories[category] = (Category(name=category, parent_task=self))
        return _categories


    def add_category(self, category):
        """Add a category to the task."""
        state = self._check_permissions(level=2)
        if state != 1:
            return -1
        # categories are very simple entities which can be constructed with a name and a path
        if category not in self._categories:

            _category = Category(name=category, parent_task=self)
            self._categories.append(_category)
            self.create_category_folders()
            self.apply_settings()

    def delete_category(self, category, force=False):
        """
        Delete a category from the task.
        Args:
            category: (str) Category to delete
            force: (bool) If True will delete the category with all its contents. If False will only delete it from the database

        Returns:

        """
        state = self._check_permissions(level=2)
        if state != 1:
            return -1
        if category not in self._categories:
            LOG.warning("Category '{0}' does not exist in task '{1}'.".format(category, self.name))
            return

        self._categories.remove(category)
        self.apply_settings()

        if force:
            LOG.warning("Deleting category '{0}' from task '{1}'.".format(category, self.name))
            shutil.rmtree(self.get_abs_database_path(category))
            shutil.rmtree(self.get_abs_project_path(category))

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

    # def scan_category(self, category, all_dcc=False):
    #     """
    #     Scan the task category for works and publishes.
    #     Args:
    #         category: (str) Category to scan
    #         all_dcc: (bool) If True, scans for all dcc versions
    #
    #     Returns:
    #
    #     """
    #     # self._works.clear()
    #     if category not in self._categories:
    #         LOG.error("Category '{0}' does not exist in task '{1}'.".format(category, self.name), proceed=False)
    #         return
    #
    #     _works = []
    #     _publishes = []
    #
    #     # override the all_dcc flag if its standalone
    #     if self._guard.dcc == "Standalone":
    #         all_dcc = True
    #
    #     if not all_dcc:
    #         _works_search_dir = self.get_abs_database_path(category, self._guard.dcc, "work")  # this is DCC specific directory
    #         _work_paths = glob(os.path.join(_works_search_dir, '*.twork'))
    #         _pub_search_dir = self.get_abs_database_path(category, self._guard.dcc, "publish")  # this is DCC specific directory
    #         _pub_paths = glob(os.path.join(_pub_search_dir, '*.tpub'))
    #     else:
    #         _search_dir = self.get_abs_database_path()
    #         _work_paths = [y for x in os.walk(_search_dir) if x == category for y in glob(os.path.join(x[0], '*.twork'))]
    #         _pub_paths = [y for x in os.walk(_search_dir) if x == category for y in glob(os.path.join(x[0], '*.tpub'))]
    #     print(_search_dir)
    #     print("***")
    #     print("***")
    #     print("***")
    #     print("***")
    #     print(_work_paths)
    #     print("***")
    #     print("***")
    #     print("***")
    #     print("***")
    #     # for b_path in _base_scene_paths:
    #     #     self._versions.append(Task(b_path))

    # def scan_publishes(self, all_dcc=False):
    #     """
    #     Scan the task for publishes.
    #     Args:
    #         all_dcc:
    #
    #     Returns: (bool) If True
    #     """
    #     self._publishes.clear()
    #
    #     # override the all_dcc flag if its standalone
    #     if self._guard.dcc == "Standalone":
    #         all_dcc = True
    #
    #     if not all_dcc:
    #         _search_dir = self.get_abs_database_path(self._guard.dcc)
    #         _work_paths = glob(os.path.join(_search_dir, '{0}.tpub'.format(self.name)))
    #     else:
    #         _search_dir = self.get_abs_database_path()
    #         _work_paths = [y for x in os.walk(_search_dir) for y in glob(os.path.join(x[0], '{0}.tpub'.format(self.name)))]


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

    # @creator.setter
    # def creator(self, val):
    #     self._creator = val
    #     self.add_property("creator", val)

    # @property
    # def path(self):
    #     return self._path

    # @path.setter
    # def path(self, val):
    #     self._path = val
    #     self.add_property("path", val)

    # @property
    # def works(self):
    #     return self._works

    # @works.setter
    # def works(self, val):
    #     self._works = val
    #     self.add_property("versions", val)

    # @property
    # def publishes(self):
    #     return self._publishes

    # @publishes.setter
    # def publishes(self, val):
    #     self._publishes = val
    #     self.add_property("publishes", val)

    @property
    def reference_id(self):
        return self._task_id

    # @reference_id.setter
    # def reference_id(self, val):
    #     self.reference_id = val
    #     self.add_property("referenceID", val)

    def create_category_folders(self):
        """Creates folders for subprojects and categories below this starting from 'root' path"""
        # unfortunately python 2.x does not support  exist_ok argument...
        for category_name in self.categories.keys():
            _f = os.path.join(self.get_abs_database_path(category_name))
            if not os.path.exists(_f):
                os.makedirs(_f)
