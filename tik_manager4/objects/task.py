# pylint: disable=consider-using-f-string
# pylint: disable=super-with-arguments
"""Module for Task object."""

from pathlib import Path
import shutil
from tik_manager4.objects.metadata import Metadata
from tik_manager4.core.settings import Settings
from tik_manager4.objects.category import Category
from tik_manager4.objects.entity import Entity
from tik_manager4.core import filelog

LOG = filelog.Filelog(logname=__name__, filename="tik_manager4")


class Task(Settings, Entity):
    """Task object to handle works and publishes.

    Task objects are getting populated by the subproject objects.
    All the task settings are stored in the task settings file.
    During the initial instantiation, the optional arguments are used
    to create the settings file if it does not exist.
    """
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
        """Initialize Task object.

        Args:
            absolute_path (str): Absolute path to the task settings file
            name (str, optional): Name of the task
            categories (list, optional): List of categories
            path (str, optional): Relative path to the task
            file_name (str, optional): File name of the task settings file
            task_type (str, optional): Type of the task
            parent_sub (Sub, optional): Parent sub of the task
            task_id (str, optional): Unique ID of the task
        """
        # self._task_id = None
        super().__init__()
        self.settings_file = absolute_path
        self._name = self.get_property("name") or name
        self._creator = self.get_property("creator") or self.guard.user
        self._works = {}
        self._publishes = {}
        self._task_id = self.get_property("task_id") or task_id
        self._relative_path = self.get_property("path") or path
        self._file_name = self.get_property("file_name") or file_name
        self._type = self.get_property("type") or task_type

        self._categories = {}
        self.build_categories(self.get_property("categories") or categories)

        self._parent_sub = parent_sub

        self._metadata_overrides = self.get_property("metadata_overrides") or {}

    @property
    def file_name(self):
        """File Name of the task settings file."""
        return self._file_name

    @property
    def name(self):
        """Name of the task."""
        return self._name

    @property
    def id(self):
        """Unique ID of the task."""
        return self._task_id

    @property
    def type(self):
        """Type of the task."""
        return self._type

    @property
    def creator(self):
        """Creator of the task."""
        return self._creator

    @property
    def categories(self):
        """Available categories in the task."""
        return self._categories

    @property
    def parent_sub(self):
        """Parent sub of the task."""
        return self._parent_sub

    @property
    def metadata(self):
        """Metadata of the task."""
        if self._parent_sub:
            _metadata = self._parent_sub.metadata.copy()
            _metadata.override(self._metadata_overrides)
            return _metadata
        return Metadata(self._metadata_overrides)

    def build_categories(self, category_list):
        """Create category objects.

        Builds a dictionary of category objects from a list of category names.
        Does NOT create folders or apply settings.

        Args:
            category_list (list): List of category names

        Returns:
            dict: Dictionary of categories
        """
        self._categories = {}
        for category in category_list:
            category_definition = self.guard.category_definitions.get_property(category)
            self._categories[category] = Category(
                name=category, parent_task=self, definition=category_definition
            )

        return self._categories

    def add_category(self, category):
        """Add a category to the task.

        Args:
            category (str): Category name

        Returns:
            Category: The category object
        """
        state = self.check_permissions(level=2)
        if state != 1:
            return -1
        if category not in self.guard.category_definitions.properties.keys():
            msg = f"'{category}' is not defined in category definitions."
            LOG.error(msg)
            raise ValueError(msg)
        if category in self._categories.keys():
            msg = f"'{category}' already exists in task '{self.name}'."
            LOG.warning(msg)
            return -1
        self._categories[category] = Category(name=category, parent_task=self)
        self._current_value["categories"] = list(self._categories.keys())
        self.apply_settings()
        return self._categories[category]

    def edit(self, name=None, task_type=None, categories=None, metadata_overrides=None):
        """Edit the task.

        Edits the given arguments of the task and applies the settings.
        If no argument is given, the function does nothing.
        This method requires level 2 permissions.

        Args:
            name (str): New name for the task
            task_type (str): New type for the task
            categories (list): New categories for the task

        Returns:
            int: 1 if successful, -1 if failed
        """
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
        if metadata_overrides is not None: # explicitly check for None
            self._metadata_overrides = metadata_overrides
            self.edit_property("metadata_overrides", metadata_overrides)
        self.apply_settings()
        return 1

    def delete_category(self, category):
        """Delete a category from the task.

        Args:
            category: (str) Category to delete

        Returns:
            int: 1 if successful, -1 if failed
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
        self._current_value["categories"] = list(self._categories.keys())
        self.apply_settings()

        if not _is_empty:
            LOG.warning(
                "Sending category '{0}' from task '{1}' to purgatory.".format(
                    category, self.name
                )
            )
            Path(self.get_purgatory_database_path(category)).mkdir(parents=True, exist_ok=True)
            Path(self.get_purgatory_project_path(category)).mkdir(parents=True, exist_ok=True)
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
        """Order the categories of the task.

        Args:
            new_order: (list) Categories with new order

        Returns:
            int: 1 if successful, -1 if failed
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

    def find_works_by_wildcard(self, wildcard):
        """Search for works by wildcard among all categories.

        Args:
            wildcard: (str) Wildcard to search

        Returns:
            list: List of works that match the wildcard
        """
        matched_works = []
        for category in self.categories:
            matched_works.extend(self.categories[category].get_works_by_wildcard(wildcard))
        return matched_works
