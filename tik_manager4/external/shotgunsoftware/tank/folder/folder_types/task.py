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
from .expression_tokens import FilterExpressionToken, CurrentTaskExpressionToken
from .step import ShotgunStep


class ShotgunTask(Entity):
    """
    Represents a Shotgun Task
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

        create_with_parent = metadata.get("create_with_parent", False)

        associated_entity_type = metadata.get("associated_entity_type")

        filters = metadata.get("filters", [])
        entity_filter = translate_filter_tokens(filters, parent, full_path)

        return ShotgunTask(
            tk,
            parent,
            full_path,
            metadata,
            sg_name_expression,
            create_with_parent,
            entity_filter,
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
        associated_entity_type,
    ):
        """
        constructor
        """

        # look up the tree for the first parent of type Entity
        # refer to this in our query expression

        # look up the tree for the first parent of type Entity which is not a User
        # this is because the user is typically assigned to a sandbox
        # and no-one would have tasks actually associated with a user anyways
        # (seems like a highly unlikely case anyone would ever do that)
        # so skip over user in order to support folder configs where
        # you have for example Asset -> User Sandbox -> (Asset) Task
        # refer to this in our query expression.
        #
        # It is also possible to set the associated_entity_type parameter
        # if you want to specifically tie this task to a particular level.
        # This is useful if you are setting up for example
        # Asset > CUSTOM > Task - custom being workspace, application etc.
        # and you want the step to associate.
        #
        sg_parent_entity = None
        sg_parent_step = None
        curr_parent = parent

        while True:

            if (
                associated_entity_type is None
                and isinstance(curr_parent, Entity)
                and not isinstance(curr_parent, ShotgunStep)
                and curr_parent.get_entity_type() != "HumanUser"
            ):
                # found an entity! Job done!
                sg_parent_entity = curr_parent
                break

            elif isinstance(curr_parent, ShotgunStep):
                sg_parent_step = curr_parent

            elif curr_parent is None:
                raise TankError(
                    "Error in configuration %s - node must be parented "
                    "under a PTR entity." % full_path
                )

            elif (
                associated_entity_type is not None
                and isinstance(curr_parent, Entity)
                and curr_parent.get_entity_type() == associated_entity_type
            ):
                # we have found the specific parent that the step is associated with
                sg_parent_entity = curr_parent
                break

            curr_parent = curr_parent.get_parent()

        # get the parent name for the entity expression, e.g. $shot
        # create a token object to represent the parent link
        parent_entity_name = os.path.basename(sg_parent_entity.get_path())
        parent_entity_expr_token = FilterExpressionToken(
            parent_entity_name, sg_parent_entity
        )

        # now create the base shotgun filter query for this
        task_filter = {
            "path": "entity",
            "relation": "is",
            "values": [parent_entity_expr_token],
        }
        entity_filter["conditions"].append(task_filter)

        # check if there is a step filter defined above this task node in the hierarchy
        if sg_parent_step:
            # this task has a step above it in the hierarchy
            # make sure we include that in the filter
            parent_step_name = os.path.basename(sg_parent_step.get_path())
            parent_step_expr_token = FilterExpressionToken(
                parent_step_name, sg_parent_step
            )
            entity_filter["conditions"].append(
                {
                    "path": sg_parent_step.get_task_link_field(),
                    "relation": "is",
                    "values": [parent_step_expr_token],
                }
            )

        # if the create_with_parent setting is True, it means that if we create folders for a
        # shot, we want all the tasks to be created at the same time.
        # however, if we have create_with_client set to False, we only want to create
        # this node if we are creating folders for a task.
        if create_with_parent != True:
            # do not auto-create with parent - only create when a task has been specified.
            # create an expression object to represent the current step
            current_task_id_token = CurrentTaskExpressionToken()
            # add this to the filters so that we restrict the filter to be
            # step id is 1234 (where 1234 is the current step derived from the current task
            # and the current task comes from the original folder create request).
            entity_filter["conditions"].append(
                {"path": "id", "relation": "is", "values": [current_task_id_token]}
            )

        Entity.__init__(
            self,
            tk,
            parent,
            full_path,
            metadata,
            "Task",
            field_name_expression,
            entity_filter,
            create_with_parent=True,
        )

    def _get_additional_sg_fields(self):
        """
        Returns additional shotgun fields to be retrieved.

        Subclassed for tasks so that the step data is always
        retrieved at the same time as the task data.

        :returns: List of shotgun fields to retrieve in addition to those
                  specified in the configuration files.
        """
        return ["step"]

    def _register_secondary_entities(self, io_receiver, path, entity):
        """
        Process secondary entities for tasks.

        Subclassed from the base implementation to ensure task entities always
        register their task as an associated secondary entity

        :param io_receiver: An object which handles any io processing request. Note that
                            processing may be deferred and happen after the recursion has completed.
        :param path:        The file system path to the location where this folder should be
                            created.

        :param entity:      Shotgun data dictionary for the item, containing all fields required by
                            the configuration + the ones specified by :meth:`_get_additional_sg_fields`.
        """
        # call base class implementation
        super(ShotgunTask, self)._register_secondary_entities(io_receiver, path, entity)

        # for tasks, the associated step is always registered as a secondary entity
        if entity.get("step"):
            io_receiver.register_secondary_entity(
                path, entity["step"], self._config_metadata
            )
