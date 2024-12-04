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
import copy

from ...errors import TankError
from ...util import shotgun_entity

from .base import Folder
from .expression_tokens import FilterExpressionToken


class ListField(Folder):
    """
    Represents values from a Shotgun list field in the file system (like Asset.sg_asset_type)
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
        # read configuration
        entity_type = metadata.get("entity_type")
        field_name = metadata.get("field_name")
        skip_unused = metadata.get("skip_unused", False)
        create_with_parent = metadata.get("create_with_parent", False)

        # validate
        if entity_type is None:
            raise TankError(
                "Missing entity_type token in yml metadata file %s" % full_path
            )

        if field_name is None:
            raise TankError(
                "Missing field_name token in yml metadata file %s" % full_path
            )

        return ListField(
            tk,
            parent,
            full_path,
            metadata,
            entity_type,
            field_name,
            skip_unused,
            create_with_parent,
        )

    def __init__(
        self,
        tk,
        parent,
        full_path,
        metadata,
        entity_type,
        field_expr,
        skip_unused,
        create_with_parent,
    ):
        """
        Constructor
        """

        Folder.__init__(self, parent, full_path, metadata)

        self._tk = tk
        self._entity_type = entity_type
        self._create_with_parent = create_with_parent
        self._field_expr_obj = shotgun_entity.EntityExpression(
            self._tk, self._entity_type, field_expr
        )
        self._skip_unused = skip_unused

        # now ensure that the expression only contains a single field
        if len(self._field_expr_obj.get_shotgun_fields()) != 1:
            raise TankError(
                "Configuration error in %s: Field expression '%s' must contain "
                "exactly one field!" % (full_path, field_expr)
            )

        # get the single shotgun field that the expression is based on
        sg_fields = self._field_expr_obj.get_shotgun_fields()
        # get the first element of the returned set
        self._field_name = list(sg_fields)[0]

    def _should_item_be_processed(self, engine_str, is_primary):
        """
        Checks if this node should be processed, given its deferred status.
        """
        # list fields are only created when they are on the primary path,
        # e.g. we don't recurse down to create asset types when shots are created,
        # but only when assets are created.
        if is_primary == False and self._create_with_parent == False:
            return False

        # base class implementation
        return super(ListField, self)._should_item_be_processed(engine_str, is_primary)

    def get_entity_type(self):
        """
        Returns the entity type associated with this node
        """
        return self._entity_type

    def get_field_name(self):
        """
        Returns the field name associated with this list field
        """
        return self._field_name

    def _create_folders_impl(self, io_receiver, parent_path, sg_data):
        """
        Creates a list field folder.
        """

        # first see if this item has already been declared inside the sg_data structure
        # this would happen if for example the same structure was defined twice:
        # /project/asset_type/asset/asset_type/work
        # it also happens when we recurse upwards to preload the sg_data dict
        # from an entity.
        #
        token_name = FilterExpressionToken.sg_data_key_for_folder_obj(self)

        if token_name in sg_data:
            values = [sg_data[token_name]]

        else:

            # get all list field values from shotgun by querying the schema methods
            # using schema_field_read()
            #
            # example response:
            #
            # {'sg_asset_type': {'data_type': {'editable': False, 'value': 'list'},
            #                    'description': {'editable': True, 'value': ''},
            #                    'editable': {'editable': False, 'value': True},
            #                    'entity_type': {'editable': False, 'value': 'Asset'},
            #                    'mandatory': {'editable': False, 'value': False},
            #                    'name': {'editable': True, 'value': 'Type'},
            #                    'properties': {'default_value': {'editable': False,
            #                                                     'value': None},
            #                                   'summary_default': {'editable': True,
            #                                                       'value': 'none'},
            #                                   'valid_values': {'editable': True,
            #                                                    'value': ['Character',
            #                                                              'Vehicle',
            #                                                              'Prop',
            #                                                              'Environment',
            #                                                              'Matte Painting']}}}}
            #

            if "." in self._field_name:
                # this looks like a deep link - entity.EntityType.fieldname
                # unfold the expression before getting the values
                try:
                    chunks = self._field_name.split(".")
                    entity_type = chunks[1]
                    field_name = chunks[2]
                except:
                    msg = (
                        "Folder creation error: Cannot resolve the field expression %s."
                        % self._field_name
                    )
                    raise TankError(msg)

            else:
                # field name is a non-deep-link field (e.g 'sg_asset_type')
                entity_type = self._entity_type
                field_name = self._field_name

            try:
                resp = self._tk.shotgun.schema_field_read(entity_type, field_name)

                # validate that the data type is of type list
                field_type = resp[field_name]["data_type"]["value"]
            except Exception as e:
                msg = "Folder creation error: Cannot retrieve values for PTR list field "
                msg += "%s.%s. Error reported: %s" % (entity_type, field_name, e)
                raise TankError(msg)

            if field_type != "list":
                msg = "Folder creation error: Only list fields can be used with the list field type. "
                msg += "%s.%s is of type %s which is unsupported." % (
                    entity_type,
                    field_name,
                    field_type,
                )
                raise TankError(msg)

            # get all values
            values = resp[field_name]["properties"]["valid_values"]["value"]

            if self._skip_unused:
                # cull values based on their usage - EXPENSIVE WITH ONE PTR QUERY PER VALUE
                values = self.__filter_unused_list_values(
                    entity_type, field_name, values, sg_data.get("Project")
                )

        # process each value independently
        products = []

        for sg_value in values:

            # render field expression
            folder_name = self._field_expr_obj.generate_name(
                {self._field_name: sg_value}
            )

            # construct folder
            my_path = os.path.join(parent_path, folder_name)
            io_receiver.make_folder(my_path, self._config_metadata)

            # copy files across
            self._copy_files_to_folder(io_receiver, my_path)

            # create a new tokens dict including our own data. This will be used
            # by the main folder recursion when processing the child folder objects.
            new_sg_data = copy.deepcopy(sg_data)
            new_sg_data[token_name] = sg_value

            # process symlinks
            self._process_symlinks(io_receiver, my_path, new_sg_data)

            products.append((my_path, new_sg_data))

        return products

    def __filter_unused_list_values(self, entity_type, field_name, values, project):
        """
        Remove values which are not used by entities in this project.

        - WARNING! SLOW! Will do a shotgun query for every value in values.
        - WARNING! This logic will check if a value is 'unused' by looking at all items
                   for that entity type. This may be perfectly fine (in the case of asset type
                   and asset for example, however it will not be relevant if other filter criteria
                   are also applied at the same time (e.g. if we are for example only processing
                   tasks of type Foo then we would ideally want to query the unused-ness based on
                   this subset, not based on all tasks in the project.
        """
        used_values = []

        for value in values:

            # eg. sg_asset_type is prop
            filters = [[field_name, "is", value]]
            if project:
                filters.append(["project", "is", project])

            summary = self._tk.shotgun.summarize(
                entity_type, filters, [{"field": field_name, "type": "count"}]
            )
            if summary.get("summaries", {}).get(field_name):
                used_values.append(value)

        return used_values
