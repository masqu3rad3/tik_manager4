# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Classes used as part of the configuration.

The classes below are typically used when the folder creation configuration contains
dynamic tokens such as $something.
"""

import os

from ...errors import TankError
from tank_vendor import six


class SymlinkToken(object):
    """
    Represents a folder level in a symlink target.
    """

    def __init__(self, name):
        """
        Constructor.

        :param name: name of the symlink
        """
        self._name = name

    def __repr__(self):
        return "<SymlinkToken token '%s'>" % self._name

    def resolve_token(self, folder_obj, sg_data):
        """
        Returns a resolved value for this token.

        :param folder_obj: :class:`Folder` to evaluate
        :param sg_data: Shotgun data dictionary.
        """
        if self._name.startswith("$"):

            # strip the dollar sign
            token = self._name[1:]

            # sg_data will contain entries on the following form:
            #
            # {'Project': {'type': 'Project', 'computed_name': 'project_code', 'id': 1},
            #  'Shot': {'computed_name': 'aaa', 'type': 'Shot', 'id': 1},
            #  'Asset.sg_asset_type': 'vehicle',
            #  'current_task_data': None
            # }
            #
            # - listfield tokens contain the value
            # - sg entity values contain the value in a compute_name key
            name_value = None
            for (field_name, field_value) in sg_data.items():

                if token == field_name:
                    if isinstance(field_value, dict):
                        # entity data is contained in a computed_name key (see above)
                        name_value = field_value.get("computed_name")
                        break
                    elif isinstance(field_value, six.string_types):
                        # listfields contain their values as a string
                        name_value = field_value
                        break
                    else:
                        raise ValueError(
                            "Cannot compute symlink target for %s: The reference token '%s' is of "
                            "type %s and cannot be resolved."
                            % (folder_obj, self._name, type(field_value))
                        )

            if name_value is None:
                raise TankError(
                    "Cannot compute symlink target for %s: The reference token '%s' cannot be resolved. "
                    "Available tokens are %s."
                    % (folder_obj, self._name, list(sg_data.keys()))
                )

            return name_value

        else:
            # not an expression
            return self._name


class CurrentStepExpressionToken(object):
    """
    Represents the current step within a configuration
    """

    def __init__(self, sg_task_step_link_field):
        """
        Constructor.

        :param sg_task_step_link_field: The shotgun field that links together a task and a step.
        """
        self._sg_task_step_link_field = sg_task_step_link_field

    def __repr__(self):
        return (
            "<CurrentStepId token. Task link field: %s>" % self._sg_task_step_link_field
        )

    def resolve_shotgun_data(self, shotgun_data):
        """
        Given a shotgun data dictionary, return an appropriate value
        for this expression.

        Because the entire design is centered around "normal" entities,
        the task data is preloaded prior to calling the folder recursion.
        If there is a notion of a current task, this data is contained
        in a current_task_data dictionary which contains information about
        the current task and its connections (for example to a pipeline step).
        """

        sg_task_data = shotgun_data.get("current_task_data")

        if sg_task_data:
            # we have information about the currently processed task
            # now see if there is a link field to a step

            if self._sg_task_step_link_field in sg_task_data:
                # this is a link field linking the task to its associated step
                # (a step does not necessarily need to be a pipeline step)
                # now get the id for this target entity.
                sg_task_shot_link_data = sg_task_data[self._sg_task_step_link_field]

                if sg_task_shot_link_data:
                    # there is a link from task -> step present
                    return sg_task_shot_link_data["id"]

        # if data is missing, return None to indicate this.
        return None


class CurrentTaskExpressionToken(object):
    """
    Represents the current task
    """

    def __init__(self):
        """
        Constructor.
        """
        pass

    def __repr__(self):
        return "<CurrentTaskId token>"

    def resolve_shotgun_data(self, shotgun_data):
        """
        Given a shotgun data dictionary, return an appropriate value
        for this expression.

        Because the entire design is centered around "normal" entities,
        the task data is preloaded prior to calling the folder recursion.
        If there is a notion of a current task, this data is contained
        in a current_task_data dictionary which contains information about
        the current task and its connections (for example to a pipeline step).
        """
        sg_task_data = shotgun_data.get("current_task_data")

        if sg_task_data:
            return sg_task_data.get("id")
        else:
            return None


class FilterExpressionToken(object):
    """
    Represents a $token in a filter expression for entity nodes.
    """

    @classmethod
    def sg_data_key_for_folder_obj(cls, folder_obj):
        """
        Returns the data key to be used with a particular folder object
        For list nodes this is EntityType.fieldname
        For sg nodes this is EntityType

        This data key is used in the data dictionary that is preloaded
        and passed around the folder resolve methods.
        """
        # avoid cyclic imports
        from .entity import Entity
        from .listfield import ListField
        from .static import Static

        if isinstance(folder_obj, Entity):
            # append a token to the filter with the entity TYPE of the sg node
            sg_data_key = folder_obj.get_entity_type()

        elif isinstance(folder_obj, ListField):
            # append a token to the filter of the form Asset.sg_asset_type
            sg_data_key = "%s.%s" % (
                folder_obj.get_entity_type(),
                folder_obj.get_field_name(),
            )

        elif isinstance(folder_obj, Static):
            # Static folders cannot be used with folder $expressions. This error
            # is typically caused by a missing .yml file
            raise TankError(
                "Static folder objects (%s) cannot be used in dynamic folder "
                'expressions using the "$" syntax. Perhaps you are missing '
                "the %s.yml file in your schema?"
                % (folder_obj, os.path.basename(folder_obj._full_path))
            )

        else:
            raise TankError(
                "The folder object %s cannot be used in folder $expressions"
                % folder_obj
            )

        return sg_data_key

    def __init__(self, expression, parent):
        """
        Constructor
        """
        self._expression = expression
        if self._expression.startswith("$"):
            self._expression = self._expression[1:]

        # now find which node is being pointed at
        referenced_node = self._resolve_ref_r(parent)

        if referenced_node is None:
            raise TankError(
                "The configuration expression $%s could not be found in %s or in "
                "any of its parents." % (self._expression, parent)
            )

        self._sg_data_key = self.sg_data_key_for_folder_obj(referenced_node)

        # all the nodes we refer to have a concept of an entity type.
        # store that too so that for later use
        self._associated_entity_type = referenced_node.get_entity_type()

    def __repr__(self):
        return "<FilterExpression '%s' >" % self._expression

    def _resolve_ref_r(self, folder_obj):
        """
        Resolves a $ref_token to an object by going up the tree
        until it finds a match. The token is compared against the
        folder name of the configuration item.
        """
        full_folder_path = folder_obj.get_path()
        folder_name = os.path.basename(full_folder_path)

        if folder_name == self._expression:
            # match!
            return folder_obj

        parent = folder_obj.get_parent()
        if parent is None:
            return parent  # end recursion!

        # try parent
        return self._resolve_ref_r(parent)

    def get_entity_type(self):
        """
        Returns the shotgun entity type for this link
        """
        return self._associated_entity_type

    def resolve_shotgun_data(self, shotgun_data):
        """
        Given a shotgun data dictionary, return an appropriate value
        for this expression.
        """
        if self._sg_data_key not in shotgun_data:
            raise TankError(
                "Cannot resolve data key %s from "
                "PTR data bundle %s" % (self._sg_data_key, shotgun_data)
            )

        value = shotgun_data[self._sg_data_key]
        return value

    def get_sg_data_key(self):
        """
        Returns the data key that is associated with this expression.
        When passing around pre-fetched shotgun data for node population,
        this is done as a dictionary. The sg data key indicates which
        part of this dictionary is associated with a particular $reference token.
        """
        return self._sg_data_key
