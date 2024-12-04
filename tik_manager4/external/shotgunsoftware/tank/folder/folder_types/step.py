# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os

from ...errors import TankError

from .entity import Entity
from .util import translate_filter_tokens
from .expression_tokens import FilterExpressionToken, CurrentStepExpressionToken


class ShotgunStep(Entity):
    """
    Represents a Shotgun Pipeline Step
    """

    @classmethod
    def create(cls, tk, parent, full_path, metadata):
        """
        Factory method for this class

        :param tk: Tk API instance
        :param parent: Parent :class:`Folder` object.
        :param full_path: Full path to the configuration file
        :param metadata: Contents of configuration file.
        :returns: :class:`Entity` instance.
        """
        # get config
        sg_name_expression = metadata.get("name")
        if sg_name_expression is None:
            raise TankError("Missing name token in yml metadata file %s" % full_path)

        create_with_parent = metadata.get("create_with_parent", True)

        entity_type = metadata.get("entity_type", "Step")
        task_link_field = metadata.get("task_link_field", "step")
        associated_entity_type = metadata.get("associated_entity_type")

        filters = metadata.get("filters", [])
        entity_filter = translate_filter_tokens(filters, parent, full_path)

        return ShotgunStep(
            tk,
            parent,
            full_path,
            metadata,
            sg_name_expression,
            create_with_parent,
            entity_filter,
            entity_type,
            task_link_field,
            associated_entity_type,
        )

    def __init__(
        self,
        tk,
        parent,
        full_path,
        metadata,
        field_name_expression,
        create_with_parent,
        entity_filter,
        entity_type,
        task_link_field,
        associated_entity_type,
    ):
        """
        constructor
        """

        self._entity_type = entity_type
        self._task_link_field = task_link_field

        # look up the tree for the first parent of type Entity which is not a User
        # this is because the user is typically assigned to a sandbox
        # and no-one would have steps actually associated with a user anyways
        # (seems like a highly unlikely case anyone would ever do that)
        # so skip over user in order to support folder configs where
        # you have for example Asset -> User Sandbox -> (Asset) Step
        # refer to this in our query expression.
        #
        # It is also possible to set the associated_entity_type parameter
        # if you want to specifically tie this step to a particular level.
        # This is useful if you are setting up for example
        # Asset > CUSTOM > Step - custom being workspace, application etc.
        # and you want the step to associate.
        #
        sg_parent = parent
        while True:

            if (
                associated_entity_type is None
                and isinstance(sg_parent, Entity)
                and sg_parent.get_entity_type() != "HumanUser"
            ):
                # there is no specific entity type set so
                # grab the first entity we'll find except user workspaces
                break

            elif (
                associated_entity_type is not None
                and isinstance(sg_parent, Entity)
                and sg_parent.get_entity_type() == associated_entity_type
            ):
                # we have found the specific parent that the step is associated with
                break

            elif sg_parent is None:
                raise TankError(
                    "Error in configuration %s - node must be parented "
                    "under a PTR entity." % full_path
                )

            else:
                sg_parent = sg_parent.get_parent()

        # get the parent name for the entity expression, e.g. $shot
        parent_name = os.path.basename(sg_parent.get_path())

        # create a token object to represent the parent link
        parent_expr_token = FilterExpressionToken(parent_name, sg_parent)

        # now create the shotgun filter query for this note that the query
        # uses this weird special syntax to restrict the pipeline steps
        # created only to be ones actually used with the entity

        # The syntax here is $FROM$Task.CONNECTION_FIELD.entity, where the connection field
        # is "step" by default
        step_filter_path = "$FROM$Task.%s.entity" % self.get_task_link_field()

        step_filter = {
            "path": step_filter_path,
            "relation": "is",
            "values": [parent_expr_token],
        }
        entity_filter["conditions"].append(step_filter)

        # if the create_with_parent setting is True, it means that if we create folders for a
        # shot, we want all the steps to be created at the same time.
        # however, if we have create_with_parent set to False, we only want to create
        # this node if we are creating folders for a task.
        if create_with_parent != True:
            # do not auto-create with parent - only create when a task has been specified.
            # create an expression object to represent the current step.
            # we pass in the field which is the connection between the task and the step field
            current_step_id_token = CurrentStepExpressionToken(
                self.get_task_link_field()
            )
            # add this to the filters so that we restrict the filter to be
            # step id is 1234 (where 1234 is the current step derived from the current task
            # and the current task comes from the original folder create request).
            entity_filter["conditions"].append(
                {"path": "id", "relation": "is", "values": [current_step_id_token]}
            )

        Entity.__init__(
            self,
            tk,
            parent,
            full_path,
            metadata,
            self.get_step_entity_type(),
            field_name_expression,
            entity_filter,
            create_with_parent=True,
        )

    def get_task_link_field(self):
        """
        Each step node is associated with a task via special link field on task.
        This method returns the name of that link field as a string
        """
        return self._task_link_field

    def get_step_entity_type(self):
        """
        Returns the Shotgun entity type which is used to represent the pipeline step.
        Shotgun has a built in pipeline step which is a way of grouping tasks together
        into distinct sets, however it is sometimes useful to be able to use a different
        entity to perform this grouping.
        """
        return self._entity_type
