import hou

import tik_manager4
from tik_manager4.ui.dialog.project_dialog import SetProjectDialog
from tik_manager4.ui.dialog.subproject_dialog import SelectSubprojectDialog


class Callbacks:
    version_exceptions = {
        "LIVE": -1,
        "PRO": 0
    }

    def __init__(self):
        self.valid_elements = ["alembic", "usd", "usd_lop"]
        self.tik_m = tik_manager4.initialize("houdini")

    def _collect_parameter_values(self, node):
        """Collect the field valuels into a dictionary.

        Args:
            node (hou.Node): The node to collect the values from.
        """
        project = node.parm("project").eval()
        subproject = node.parm("subproject").eval()
        task = None
        category = None
        published_work = None
        version = None
        element = None
        if node.parm("task").menuLabels():
            task = node.parm("task").menuLabels()[node.parm("task").eval()]
        if node.parm("category").menuLabels():
            category = node.parm("category").menuLabels()[node.parm("category").eval()]
        if node.parm("published_work").menuLabels():
            published_work = node.parm("published_work").menuLabels()[
                node.parm("published_work").eval()
            ]
        if node.parm("version").menuLabels():
            version = node.parm("version").menuLabels()[node.parm("version").eval()]
        if node.parm("element").menuLabels():
            element = node.parm("element").menuLabels()[node.parm("element").eval()]

        return {
            "project": project,
            "subproject": subproject,
            "task": task,
            "category": category,
            "published_work": published_work,
            "version": version,
            "element": element,
        }

    def set_project(self, kwargs):
        """Set the project line in Houdini parameters.

        Args:
            kwargs (dict): The keyword arguments.
        """
        dialog = SetProjectDialog(self.tik_m)
        ret = dialog.exec_()

        if ret:
            node = kwargs["node"]
            self.populate_project(node, dialog.active_project)

    def set_project_line(self, kwargs):
        """Set the project line in Houdini parameters.

        Args:
            kwargs (dict): The keyword arguments.
        """
        node = kwargs["node"]
        path = kwargs["script_value0"]
        self.tik_m.set_project(path)
        self.populate_project(node, path)

    def set_subproject(self, kwargs):
        """Set the sub-project line in Houdini parameters.

        Args:
            kwargs (dict): The keyword arguments.
        """
        subproject_dialog = SelectSubprojectDialog(self.tik_m.project)
        ret = subproject_dialog.exec()

        if ret:
            node = kwargs["node"]
            self.populate_subproject(node, subproject_dialog.selected_subproject.path)
            return

    def set_subproject_line(self, kwargs):
        """Set the sub-project line in Houdini parameters.

        Args:
            kwargs (dict): The keyword arguments.
        """
        node = kwargs["node"]
        path = kwargs["script_value0"]
        self.populate_subproject(node, path)

    def set_task(self, kwargs):
        """Set the task.

        Args:
            kwargs (dict): The keyword arguments.
        """
        node = kwargs["node"]
        parameters = self._collect_parameter_values(node)
        # override the category with new value
        parameters["task"] = kwargs["script_value"]
        subproject_obj = self.get_subproject(parameters)
        subproject_obj.scan_tasks()
        self.populate_categories(node, subproject_obj.tasks[parameters["task"]])
        return

    def set_category(self, kwargs):
        """Set the category.

        Args:
            kwargs (dict): The keyword arguments.
        """
        node = kwargs["node"]
        parameters = self._collect_parameter_values(node)
        # override the category with new value
        parameters["category"] = kwargs["script_value"]
        task_obj = self.get_task(parameters)
        self.populate_publishes(node, task_obj.categories[parameters["category"]])
        return

    def set_published_work(self, kwargs):
        """Set the published work.

        Args:
            kwargs (dict): The keyword arguments.
        """
        node = kwargs["node"]
        parameters = self._collect_parameter_values(node)
        # override the published work with new value
        parameters["published_work"] = kwargs["script_value"]
        category_obj = self.get_category(parameters)
        # find the work
        for work in category_obj.works.values():
            if work.name == parameters["published_work"]:
                self.populate_versions(node, work.publish)
                return

    def set_version(self, kwargs):
        """Set the version.

        Args:
            kwargs (dict): The keyword arguments.
        """
        node = kwargs["node"]
        parameters = self._collect_parameter_values(node)
        # override the published work with new value
        parameters["version"] = kwargs["script_value"]
        published_work = self.get_published_work(parameters)
        if parameters["version"] in self.version_exceptions.keys():
            # set the version to the exception value
            version_number = self.version_exceptions[parameters["version"]]
        else:
            version_number = int(parameters["version"])
        # we need to explicitly scan the versions.
        published_work.scan_publish_versions()
        self.populate_elements(
            node, published_work.get_version(version_number)
        )
        return

    def set_element(self, kwargs):
        """Set hhe element.

        Args:
            kwargs (dict): The keyword arguments.
        """
        node = kwargs["node"]
        parameters = self._collect_parameter_values(node)
        # override the published work with new value
        parameters["element"] = kwargs["script_value"]
        version = self.get_version(parameters)
        self.update_path(version, parameters["element"])

    def get_project(self, parameters):
        """Resolve the task object.

        Args:
            parameters (dict): The parameters dictionary.
        """
        self.tik_m.set_project(parameters["project"])
        return self.tik_m.project

    def get_subproject(self, parameters):
        """Get the subproject object.

        Args:
            parameters (dict): The parameters dictionary.
        """
        project = self.get_project(parameters)
        return project.find_sub_by_path(parameters["subproject"])

    def get_task(self, parameters):
        """Get the task object.

        Args:
            parameters (dict): The parameters dictionary.
        """
        subproject = self.get_subproject(parameters)
        subproject.scan_tasks()
        return subproject.tasks[parameters["task"]]

    def get_category(self, parameters):
        """Get the category object.

        Args:
            parameters (dict): The parameters dictionary.
        """
        task = self.get_task(parameters)
        return task.categories[parameters["category"]]

    def get_published_work(self, parameters):
        """Get the published work object.

        Args:
            parameters (dict): The parameters dictionary.
        """
        category = self.get_category(parameters)
        for work in category.works.values():
            if work.name == parameters["published_work"]:
                return work.publish

    def get_version(self, parameters):
        """Get the version object.

        Args:
            parameters (dict): The parameters dictionary.
        """
        published_work = self.get_published_work(parameters)
        # we need to explicitly scan the versions.
        published_work.scan_publish_versions()
        if parameters["version"] in self.version_exceptions.keys():
            # set the version to the exception value
            version_number = self.version_exceptions[parameters["version"]]
        else:
            version_number = int(parameters["version"])
        return published_work.get_version(version_number)

    def populate_project(self, node, active_project):
        """ Populate the project.
        Args:
            node (hou.Node): The node to populate.
            active_project (str): The active project.

        Returns:
            str: The active project.
        """
        project_line = node.parm("project")
        project_line.set(active_project)
        self.populate_subproject(node)
        return active_project

    def populate_subproject(self, node, active_subproject=""):
        """Populate the subproject.

        Args:
            node (hou.Node): The node to populate.
            active_subproject (str, optional): The active subproject.
                Defaults to "".
        """
        # return the root
        subproject_obj = self.tik_m.project.find_sub_by_path(active_subproject)
        subproject_line = node.parm("subproject")
        subproject_line.set(active_subproject)
        self.populate_tasks(node, subproject_obj)
        return ""

    def populate_tasks(self, node, subproject_obj):
        """Populate the tasks.

        Args:
            node (hou.Node): The node to populate.
            subproject_obj (tik_manager4.core.subproject.Subproject):
                The subproject object.
        """
        tasks = subproject_obj.scan_tasks()

        task_names = ";".join(tasks.keys())
        node.setUserData("tasks", task_names)
        tasks_combo = node.parm("task")
        tasks_combo.eval()
        tasks_combo.set(0)
        pass_value = next(iter(tasks.values())) if tasks.values() else None
        self.populate_categories(node, pass_value)
        return task_names

    def populate_categories(self, node, task_obj=None):
        """Populate the categories.

        Args:
            node (hou.Node): The node to populate.
            task_obj (tik_manager4.core.task.Task): The task object.
        """
        if task_obj:
            categories = task_obj.categories
            category_names = ";".join(categories.keys())
            pass_value = next(iter(categories.values())) if categories else None
        else:
            category_names = ""
            pass_value = None

        node.setUserData("categories", category_names)

        categories_combo = node.parm("category")
        categories_combo.eval()
        categories_combo.set(0)
        self.populate_publishes(node, pass_value)
        return category_names

    def populate_publishes(self, node, category_obj=None):
        """Populate the published works.

        Args:
            node (hou.Node): The node to populate.
            category_obj (tik_manager4.core.category.Category): The category
                object.
        """

        if category_obj:
            works = category_obj.works
            for work_obj in works.values():
                work_obj.publish.scan_publish_versions()
            publishes = [
                work_obj.publish
                for work_obj in works.values()
                if work_obj.publish.versions
            ]
            publish_names = ";".join([x.name for x in publishes])
            pass_value = publishes[0] if publishes else None
        else:
            publish_names = ""
            pass_value = None
        node.setUserData("published_works", publish_names)
        published_work_combo = node.parm("published_work")
        published_work_combo.eval()
        published_work_combo.set(0)
        self.populate_versions(node, pass_value)
        return publish_names

    def populate_versions(self, node, publish_obj=None):
        """Populate the versions.

        Args:
            node (hou.Node): The node to populate.
            publish_obj (tik_manager4.core.publish.Publish): The publish
                object.
        """
        if publish_obj:
            versions = publish_obj.get_versions()
            version_names = ";".join([x.nice_name for x in versions])
            pass_value = versions[-1] if versions else None
            last_version = publish_obj.get_last_version()
        else:
            version_names = ""
            pass_value = None
            last_version = 0

        node.setUserData("versions", version_names)
        version_combo = node.parm("version")
        version_combo.eval()
        version_combo.set(last_version)
        self.populate_elements(node, pass_value)
        return version_names

    def populate_elements(self, node, version_obj=None):
        """Populate the elements.

        Args:
            node (hou.Node): The node to populate.
            version_obj (tik_manager4.core.version.Version): The version
                object.
        """
        allow_all_elements = hou.pwd().parm("allowAllElements").eval()
        if version_obj:
            elements = [x for x in version_obj.element_types if x
                        in self.valid_elements or allow_all_elements]
            element_names = ";".join(elements)
            pass_value = elements[0] if elements else None
        else:
            element_names = ""
            pass_value = None
        node.setUserData("elements", element_names)
        element_combo = node.parm("element")
        element_combo.eval()
        element_combo.set(0)

        self.update_path(version_obj, pass_value)
        return element_names

    def update_path(self, version_obj, element_type):
        """Update the path based on the version and element type.

        -- THIS METHOD SHOULD BE OVERRIDEN IN THE CHILD CLASSES --

        Args:
            version_obj (tik_manager4.core.version.Version): The version
                object.
            element_type (str): The element type.
        """
        pass
