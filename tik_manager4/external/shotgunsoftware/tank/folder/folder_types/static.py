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

from .base import Folder
from .entity import Entity
from .util import translate_filter_tokens, resolve_shotgun_filters


class Static(Folder):
    """
    Represents a static folder in the file system
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
        # get data
        constrain_by_entity = metadata.get("constrain_by_entity")
        constraints = metadata.get("constraints")

        create_with_parent = metadata.get("create_with_parent", True)

        # validate
        if constrain_by_entity is not None and constraints is None:
            raise TankError(
                "Missing constraints parameter in yml metadata file %s" % full_path
            )

        if constraints is not None and constrain_by_entity is None:
            raise TankError(
                "Configuration error in %s: Need to have a "
                "constrain_by_entity token in order "
                "for the constraints parameter to be picked up." % full_path
            )

        # resolve dynamic constraints filter ($shot, $step etc).
        if constraints:
            constraints_filter = translate_filter_tokens(constraints, parent, full_path)

            # resolve the constrained_by_entity ($shot, $step etc)
            resolved_constrain_node = None
            curr_parent = parent
            while curr_parent:
                full_folder_path = curr_parent.get_path()
                folder_name = os.path.basename(full_folder_path)
                if folder_name == constrain_by_entity[1:]:
                    resolved_constrain_node = curr_parent
                    break
                else:
                    curr_parent = curr_parent.get_parent()

            if resolved_constrain_node is None:
                raise TankError(
                    "Configuration error in %s: constrain_by_entity '%s' could not "
                    "be resolved into a parent node. It needs to be on the form '$name', "
                    "where name is the name of a parent yaml "
                    "configuration file." % (full_path, constrain_by_entity)
                )

            if not isinstance(resolved_constrain_node, Entity):
                raise TankError(
                    "Configuration error in %s: constrain_by_entity points "
                    "at a node which is not associated with any PTR data. "
                    "You can only constrain based on nodes which have a PTR "
                    "representation." % full_path
                )

        else:
            # no constraints active for this static node
            resolved_constrain_node = None
            constraints_filter = None

        return Static(
            parent,
            full_path,
            metadata,
            tk,
            create_with_parent,
            resolved_constrain_node,
            constraints_filter,
        )

    def __init__(
        self,
        parent,
        full_path,
        metadata,
        tk,
        create_with_parent,
        constrain_node,
        constraints_filter,
    ):
        """
        Constructor.
        """
        Folder.__init__(self, parent, full_path, metadata)

        # The name parameter represents the folder name that will be created in the file system.
        self._name = os.path.basename(full_path)

        self._constrain_node = constrain_node
        self._constraints_filter = constraints_filter
        self._create_with_parent = create_with_parent
        self._tk = tk

        self._cached_sg_data = {}

    def is_dynamic(self):
        """
        Returns true if this folder node requires some sort of dynamic input
        """
        return False

    def _should_item_be_processed(self, engine_str, is_primary):
        """
        Checks if this node should be processed, given its deferred status.
        """
        # check our special condition - is this node set to be auto-created with its parent node?
        # note that primary nodes are always created with their parent nodes!
        if is_primary == False and self._create_with_parent == False:
            return False

        # base class implementation
        return super(Static, self)._should_item_be_processed(engine_str, is_primary)

    def _create_folders_impl(self, io_receiver, parent_path, sg_data):
        """
        Creates a static folder.
        """

        # first check if we have any conditionals that need evaluating
        if self._constrain_node:

            # resolve our sg filter expression based on the current shotgun data
            # for the current parent objects (for example if the query expression
            # contains $shot or other dynamic tokens)
            resolved_filters = resolve_shotgun_filters(
                self._constraints_filter, sg_data
            )

            # so now resolved_filters is something like:
            # {'logical_operator': 'and',
            #  'conditions': [{'path': 'code', 'values': ['a'], 'relation': 'contains'}] }
            #
            # and the configuration states that the constraint object is $shot
            # which is resolved into self._constrain_node
            #
            # now we want to get the current parent $shot id. This can be extrated
            # from the sg_data dict which is on the form:
            # {'Project': {'id': 88, 'type': 'Project'},
            # 'Sequence': {'id': 32, 'type': 'Sequence'},
            # 'Shot': {'id': 1184, 'type': 'Shot'},
            # 'Step': {'id': 5, 'type': 'Step'}}
            #
            # once extracted, we can add that to the sg filter to get our final filter:
            #
            # {'logical_operator': 'and',
            #  'conditions': [{'path': 'code', 'values': ['a'], 'relation': 'contains'},
            #                 {'path': 'id', 'values': [1184], 'relation': 'is'} ] }

            constrain_entity_id = sg_data[self._constrain_node.get_entity_type()]["id"]
            id_filter = {
                "path": "id",
                "values": [constrain_entity_id],
                "relation": "is",
            }
            resolved_filters["conditions"].append(id_filter)

            # depending on the filter, it is possible that the same static query will
            # be generated more than once - so cache the results so that we can minimize
            # shotgun queries.
            hash_key = hash(str(resolved_filters))

            if hash_key in self._cached_sg_data:
                data = self._cached_sg_data[hash_key]

            else:
                # call out to shotgun
                data = self._tk.shotgun.find_one(
                    self._constrain_node.get_entity_type(), resolved_filters
                )
                # and cache it
                self._cached_sg_data[hash_key] = data

            if data is None:
                # no match! this means that our constraints filter did not match the current object
                return []

        # create our folder
        my_path = os.path.join(parent_path, self._name)

        # call out to callback
        io_receiver.make_folder(my_path, self._config_metadata)

        # copy files across
        self._copy_files_to_folder(io_receiver, my_path)

        # process symlinks
        self._process_symlinks(io_receiver, my_path, sg_data)

        return [(my_path, sg_data)]
