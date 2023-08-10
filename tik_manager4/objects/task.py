# pylint: disable=consider-using-f-string
# pylint: disable=super-with-arguments

import shutil
from tik_manager4.core.settings import Settings
from tik_manager4.objects.category import Category
from tik_manager4.objects.entity import Entity
from tik_manager4.core import filelog

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")


class Task(Settings, Entity):
    def __init__(
        self,
        absolute_path,
        name=None,
        categories=None,
        path="",
        file_name=None,
        task_type=None,
        parent_sub=None,
        task_id=None,
    ):
        # self._task_id = None
        super(Task, self).__init__()
        self.settings_file = absolute_path
        self._name = self.get_property("name") or name
        self._creator = self.get_property("creator") or self.guard.user
        self._works = {}
        self._publishes = {}
        # self._task_id = self.get_property("task_id") or self._id
        self._task_id = self.get_property("task_id") or task_id
        # self._task_id = self.get_property("task_id") or self.generate_id()
        self._relative_path = self.get_property("path") or path
        self._file_name = self.get_property("file_name") or file_name
        self._type = self.get_property("type") or task_type

        self._categories = {}
        self.build_categories(self.get_property("categories") or categories)

        self.parent_sub = parent_sub

    @property
    def file_name(self):
        return self._file_name

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        # if not self._id:
        #     self._id = self.generate_id()
        return self._task_id

    @property
    def type(self):
        return self._type

    @property
    def creator(self):
        return self._creator

    @property
    def categories(self):
        return self._categories

    def build_categories(self, category_list):
        """
        Builds a category objects from a list of category names

        Does not create folders or apply settings.
        Args: category_list: (list) List of category names
        """
        self._categories = {}
        for category in category_list:
            category_definition = self.guard.category_definitions.get_property(category)
            self._categories[category] = Category(
                name=category, parent_task=self, definition=category_definition
            )

        return self._categories

    def add_category(self, category):
        """Add a category to the task."""
        state = self.check_permissions(level=2)
        if state != 1:
            return -1
        if category not in self.guard.category_definitions.properties.keys():
            LOG.error(
                "Category '{0}' is not defined in category definitions.".format(
                    category
                ),
                proceed=False,
            )
        if category not in self._categories.keys():
            self._categories[category] = Category(name=category, parent_task=self)
            self._currentValue["categories"] = list(self._categories.keys())
            self.apply_settings()
            return self._categories[category]
        else:
            LOG.warning(
                "Category '{0}' already exists in task '{1}'.".format(
                    category, self.name
                )
            )
            return -1

    def edit(self, name=None, task_type=None, categories=None):
        """Edit the task"""
        state = self.check_permissions(level=2)
        if state != 1:
            return -1
        if name and name != self.name:
            # check the sibling tasks to see if the name is already taken
            if name in self.parent_sub.tasks:
                LOG.error(
                    "Task name '{0}' already exists in sub '{1}'.".format(
                        name, self.parent_sub.name
                    )
                )
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
                    LOG.error(
                        "Category '{0}' is not defined in category definitions.".format(
                            category
                        ),
                        proceed=False,
                    )
            self._categories = self.build_categories(categories)
            self.edit_property("categories", list(categories))
        self.apply_settings()

    def delete_category(self, category):
        """
        Delete a category from the task.
        Args:
            category: (str) Category to delete
            force: (bool) If True will delete the category with all its contents.
                            If False will only delete it from the database

        Returns:

        """
        if category not in self._categories:
            LOG.warning(
                "Category '{0}' does not exist in task '{1}'.".format(
                    category, self.name
                )
            )
            return -1

        _is_empty = self._categories[category].is_empty()
        permission_level = 2 if _is_empty else 3

        state = self.check_permissions(level=permission_level)
        if state != 1:
            return -1

        # delete category from database
        self._categories.pop(category)
        self._currentValue["categories"] = list(self._categories.keys())
        self.apply_settings()

        if not _is_empty:
            LOG.warning(
                "Sending category '{0}' from task '{1}' to purgatory.".format(
                    category, self.name
                )
            )
            self._io.folder_check(self.get_purgatory_database_path(category))
            self._io.folder_check(self.get_purgatory_project_path(category))
            shutil.move(
                self.get_abs_database_path(self.name, category),
                self.get_purgatory_database_path(self.name, category),
            )
            shutil.move(
                self.get_abs_project_path(self.name, category),
                self.get_purgatory_project_path(self.name, category),
            )

        return 1

    def order_categories(self, new_order):
        """
        Order the categories of the task.
        Args:
            new_order: (list) Categories with new order

        Returns:

        """
        state = self.check_permissions(level=2)
        if state != 1:
            return -1
        if len(new_order) != len(self._categories):
            LOG.error(
                "New order list is not the same length as the current categories list.",
                proceed=False,
            )
        for x in new_order:
            if x not in self.categories:
                LOG.error(
                    "New order list contains a category "
                    "that is not in the current categories list.",
                    proceed=False,
                )
        self.edit_property("categories", new_order)
        self.apply_settings()
        return 1
