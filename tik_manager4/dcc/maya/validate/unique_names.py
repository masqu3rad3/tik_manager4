"""Validation for unique names in Maya scene"""

import maya.cmds as cmds
from tik_manager4.dcc.validate_core import ValidateCore

class UniqueNames(ValidateCore):
    """Validate class for Maya"""

    name = "Unique Names"
    def __init__(self):
        super(UniqueNames, self).__init__()

        self.autofixable = True
        self.ignorable = True
    def validate(self):
        """Validate unique names in Maya scene."""
        collection = []
        for obj in cmds.ls():
            pathway = obj.split("|")
            if len(pathway) > 1:
                self.unique_name(pathway[-1])
                collection.append(obj)
        if collection:
            self.error = True

    def fix(self):
        """Auto fix the validation."""
        self.make_names_unique()

    @staticmethod
    def unique_name(name, return_counter=False, suffix=None):
        """
        Searches the scene for match and returns a unique name for given name
        Args:
            name: (String) Name to query
            return_counter: (Bool) If true, returns the next available number instead of the object name
            suffix: (String) If defined and if name ends with this suffix, the increment numbers will be put before the.

        Returns: (String) uniquename

        """
        search_name = name
        base_name = name
        if suffix and name.endswith(suffix):
            base_name = name.replace(suffix, "")
        else:
            suffix = ""
        id_counter = 0
        while cmds.objExists(search_name):
            search_name = "{0}{1}{2}".format(base_name, str(id_counter + 1), suffix)
            id_counter = id_counter + 1
        if return_counter:
            return id_counter
        else:
            if id_counter:
                result_name = "{0}{1}{2}".format(base_name, str(id_counter), suffix)
            else:
                result_name = name
            return result_name

    def make_names_unique(self, ):
        """
        Makes sure that everything is named uniquely. Returns list of renamed nodes and list of new names

        Args:
            query: (Boolean) If True, returns only non-unique nodes without changing anything

        Returns: [List of old names, list of new names]

        """

        collection = []
        for obj in cmds.ls():
            pathway = obj.split("|")
            if len(pathway) > 1:
                self.unique_name(pathway[-1])
                collection.append(obj)
        collection.reverse()
        old_names = []
        new_names = []
        for xe in collection:
            pathway = xe.split("|")
            old_names.append(pathway[-1])
            new_names.append(cmds.rename(xe, self.unique_name(pathway[-1])))
        return old_names, new_names