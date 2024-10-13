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

from .errors import EntityLinkTypeMismatch
from .base import Folder
from .expression_tokens import FilterExpressionToken
from .util import translate_filter_tokens, resolve_shotgun_filters


class Entity(Folder):
    """
    Represents an entity in Shotgun
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
        sg_name_expression = metadata.get("name")
        entity_type = metadata.get("entity_type")
        filters = metadata.get("filters")
        create_with_parent = metadata.get("create_with_parent", False)

        # validate
        if sg_name_expression is None:
            raise TankError("Missing name token in yml metadata file %s" % full_path)

        if entity_type is None:
            raise TankError(
                "Missing entity_type token in yml metadata file %s" % full_path
            )

        if filters is None:
            raise TankError("Missing filters token in yml metadata file %s" % full_path)

        entity_filter = translate_filter_tokens(filters, parent, full_path)

        return Entity(
            tk,
            parent,
            full_path,
            metadata,
            entity_type,
            sg_name_expression,
            entity_filter,
            create_with_parent,
        )

    def __init__(
        self,
        tk,
        parent,
        full_path,
        metadata,
        entity_type,
        field_name_expression,
        filters,
        create_with_parent,
    ):
        """
        Constructor.

        The filter syntax for deciding which folders to create
        is a dictionary, often looking something like this:

             {
                 "logical_operator": "and",
                 "conditions": [ { "path": "project", "relation": "is", "values": [ FilterExpressionToken(<Project>) ] } ]
             }

        This is basically a shotgun API filter dictionary, but with interleaved tokens
        (e.g. the FilterExpressionToken object). Tank will resolve any Token fields prior to
        passing the filter to Shotgun for evaluation.
        """

        # the schema name is the same as the PTR entity type
        Folder.__init__(self, parent, full_path, metadata)

        self._tk = tk
        self._entity_type = entity_type
        self._entity_expression = shotgun_entity.EntityExpression(
            self._tk, self._entity_type, field_name_expression
        )
        self._filters = filters
        self._create_with_parent = create_with_parent

    def get_entity_type(self):
        """
        returns the shotgun entity type for this node
        """
        return self._entity_type

    def _should_item_be_processed(self, engine_str, is_primary):
        """
        Checks if this node should be processed, given its deferred status.
        """
        # check our special condition - is this node set to be auto-created with its parent node?
        # note that primary nodes are always created with their parent nodes!
        if is_primary == False and self._create_with_parent == False:
            return False

        # base class implementation
        return super(Entity, self)._should_item_be_processed(engine_str, is_primary)

    def _get_additional_sg_fields(self):
        """
        Returns additional shotgun fields to be retrieved.

        Can be subclassed for special cases.

        :returns: List of shotgun fields to retrieve in addition to those
                  specified in the configuration files.
        """
        return []

    def _create_folders_impl(self, io_receiver, parent_path, sg_data):
        """
        Creates folders.
        """
        items_created = []

        for entity in self.__get_entities(sg_data):

            # generate the field name
            folder_name = self._entity_expression.generate_name(entity)

            # now for the case where the project name is encoded with slashes,
            # we need to translate those into a native representation
            folder_name = folder_name.replace("/", os.path.sep)

            my_path = os.path.join(parent_path, folder_name)

            # get the name field - which depends on the entity type
            # Note: this is the 'name' that will get stored in the path cache for this entity
            name_field = shotgun_entity.get_sg_entity_name_field(self._entity_type)
            name_value = entity[name_field]
            # construct a full entity link dict w name, id, type
            full_entity_dict = {
                "type": self._entity_type,
                "id": entity["id"],
                "name": name_value,
            }

            # register secondary entity links
            self._register_secondary_entities(io_receiver, my_path, entity)

            # call out to callback
            io_receiver.make_entity_folder(
                my_path, full_entity_dict, self._config_metadata
            )

            # copy files across
            self._copy_files_to_folder(io_receiver, my_path)

            # create a new entity dict including our own data and pass it down to children
            my_sg_data = copy.deepcopy(sg_data)
            my_sg_data_key = FilterExpressionToken.sg_data_key_for_folder_obj(self)
            my_sg_data[my_sg_data_key] = {
                "type": self._entity_type,
                "id": entity["id"],
                "computed_name": folder_name,
            }

            # process symlinks
            self._process_symlinks(io_receiver, my_path, my_sg_data)

            items_created.append((my_path, my_sg_data))

        return items_created

    def _register_secondary_entities(self, io_receiver, path, entity):
        """
        Looks in the entity dict for any linked entities and register these
        """
        # get all the link fields from the name expression
        for lf in self._entity_expression.get_shotgun_link_fields():
            entity_link = entity[lf]
            io_receiver.register_secondary_entity(
                path, entity_link, self._config_metadata
            )

    def __get_entities(self, sg_data):
        """
        Returns shotgun data for folder creation
        """
        # first check the constraints: if tokens contains a type/id pair our our type,
        # we should only process this single entity. If not, then use the query filter

        # first, resolve the filter queries for the current ids passed in via tokens
        resolved_filters = resolve_shotgun_filters(self._filters, sg_data)

        # see if the sg_data dictionary has a "seed" entity type matching our entity type
        my_sg_data_key = FilterExpressionToken.sg_data_key_for_folder_obj(self)
        if my_sg_data_key in sg_data:
            # we have a constraint!
            entity_id = sg_data[my_sg_data_key]["id"]
            # add the id constraint to the filters
            resolved_filters["conditions"].append(
                {"path": "id", "relation": "is", "values": [entity_id]}
            )
            # get data - can be None depending on external filters

        # figure out which fields to retrieve
        fields = self._entity_expression.get_shotgun_fields()

        # add any shotgun link fields used in the expression
        fields.update(self._entity_expression.get_shotgun_link_fields())

        # always retrieve the name field for the entity
        fields.add(shotgun_entity.get_sg_entity_name_field(self._entity_type))

        # add any special stuff in
        for custom_field in self._get_additional_sg_fields():
            fields.add(custom_field)

        # convert to a list - sets wont work with the PTR API
        fields_list = list(fields)

        # now find all the items (e.g. shots) matching this query
        entities = self._tk.shotgun.find(
            self._entity_type, resolved_filters, fields_list
        )

        return entities

    def extract_shotgun_data_upwards(self, sg, shotgun_data):
        """
        Extracts the shotgun data necessary to create this object and all its parents.
        The shotgun_data input needs to contain a dictionary with a "seed". For example:
        { "Shot": {"type": "Shot", "id": 1234 } }


        This method will then first extend this structure to ensure that fields needed for
        folder creation are available:
        { "Shot": {"type": "Shot", "id": 1234, "code": "foo", "sg_status": "ip" } }

        Now, if you have structure with Project > Sequence > Shot, the Shot level needs
        to define a configuration entry roughly on the form
        filters: [ { "path": "sg_sequence", "relation": "is", "values": [ "$sequence" ] } ]

        So in addition to getting the fields required for naming the current entry, we also
        get all the fields that are represented by $tokens. These will form the 'seed' for
        when we recurse to the parent level and do the same thing there.


        The return data is on the form:
        {
            'Project':   {'id': 4, 'name': 'Demo Project', 'type': 'Project'},
            'Sequence':  {'code': 'Sequence1', 'id': 2, 'name': 'Sequence1', 'type': 'Sequence'},
            'Shot':      {'code': 'shot_010', 'id': 2, 'type': 'Shot'}
        }

        NOTE! Because we are using a dictionary where we key by type, it would not be possible
        to have a pathway where the same entity type exists multiple times. For example an
        asset / sub asset relationship.
        """

        tokens = copy.deepcopy(shotgun_data)

        # If we don't have an entry in tokens for the current entity type, then we can't
        # extract any tokens. Used by #17726. Typically, we start with a "seed", and then go
        # upwards. For example, if the seed is a Shot id, we then scan upwards, look at the config
        # for shot, which contains [sg_sequence is $sequence], e.g. the shot entry links explicitly
        # to the sequence entry. Because of this link, by the time we move upwards in the hierarchy
        # and reach sequence, we will already have an entry for sequence in the dictionary.
        #
        # however, if we have a free-floating item in the hierarchy, this will not be 'seeded'
        # by its children as we move upwards - for example a step.
        my_sg_data_key = FilterExpressionToken.sg_data_key_for_folder_obj(self)
        if my_sg_data_key in tokens:

            link_map = {}
            fields_to_retrieve = []
            additional_filters = []

            # TODO: Support nested conditions
            for condition in self._filters["conditions"]:
                vals = condition["values"]

                # note the $FROM$ condition below - this is a bit of a hack to make sure we exclude
                # the special $FROM$ step based culling filter that is commonly used. Because steps are
                # sort of free floating and not associated with an entity, removing them from the
                # resolve should be fine in most cases.

                # so - if at the shot level, we have defined the following filter:
                # filters: [ { "path": "sg_sequence", "relation": "is", "values": [ "$sequence" ] } ]
                # the $sequence will be represented by a Token object and we need to get a value for
                # this token. We fetch the id for this token and then, as we recurse upwards, and process
                # the parent folder level (the sequence), this id will be the "seed" when we populate that
                # level.

                if (
                    vals[0]
                    and isinstance(vals[0], FilterExpressionToken)
                    and not condition["path"].startswith("$FROM$")
                ):
                    expr_token = vals[0]
                    # we should get this field (eg. 'sg_sequence')
                    fields_to_retrieve.append(condition["path"])
                    # add to our map for later processing map['sg_sequence'] = 'Sequence'
                    # note that for List fields, the key is EntityType.field
                    link_map[condition["path"]] = expr_token

                elif not condition["path"].startswith("$FROM$"):
                    # this is a normal filter (we exclude the $FROM$ stuff since it is weird
                    # and specific to steps.) So for example 'name must begin with X' - we want
                    # to include these in the query where we are looking for the object, to
                    # ensure that assets with names starting with X are not created for an
                    # asset folder node which explicitly excludes these via its filters.
                    additional_filters.append(condition)

            # add some extra fields apart from the stuff in the config
            field_name = shotgun_entity.get_sg_entity_name_field(self._entity_type)
            fields_to_retrieve.append(field_name)

            # TODO: AND the id query with this folder's query to make sure this path is
            # valid for the current entity. Throw error if not so driver code knows to
            # stop processing. This would be needed in a setup where (for example) Asset
            # appears in several locations in the filesystem and that the filters are responsible
            # for determining which location to use for a particular asset.
            my_id = tokens[my_sg_data_key]["id"]
            additional_filters.append(
                {"path": "id", "relation": "is", "values": [my_id]}
            )

            # append additional filter cruft
            filter_dict = {"logical_operator": "and", "conditions": additional_filters}

            # carry out find
            rec = sg.find_one(self._entity_type, filter_dict, fields_to_retrieve)

            # there are now two reasons why find_one did not return:
            # - the specified entity id does not exist or has been deleted
            # - there are filters which has filtered it out. For example imagine that you
            #   have one folder structure for all assets starting with A and a second structure
            #   for the rest. This would be a filter condition (code does not start with A, and
            #   code starts with A respectively). In these cases, the object does exist but has been
            #   explicitly filtered out - which is not an error!

            if not rec:

                # check if it is a missing id or just a filtered out thing
                if sg.find_one(self._entity_type, [["id", "is", my_id]]) is None:
                    raise TankError(
                        "Could not find PTR %s with id %s as required by "
                        "the folder creation setup." % (self._entity_type, my_id)
                    )
                else:
                    raise EntityLinkTypeMismatch()

            # and append the 'name field' which is always needed.
            # we are OK with getting back a None value as its used for error reporting
            name = rec.get(field_name)
            if name is not None:
                tokens[my_sg_data_key][field_name] = name

            # Step through our token key map and process
            #
            # This is on the form
            # link_map['sg_sequence'] = link_obj
            #
            for field in link_map:

                # do some juggling to make sure we don't double process the
                # name fields.
                value = rec[field]
                link_obj = link_map[field]

                if value is None:
                    # field was none! - cannot handle that!
                    raise TankError(
                        "The %s %s has a required field %s that \ndoes not have a value "
                        "set in Flow Production Tracking. \nDouble check the values and try "
                        "again!\n" % (self._entity_type, name, field)
                    )

                if isinstance(value, dict):
                    # If the value is a dict, assume it comes from a entity link.

                    # now make sure that this link is actually relevant for us,
                    # e.g. that it points to an entity of the right type.
                    # this may be a problem whenever a link can link to more
                    # than one type. See the EntityLinkTypeMismatch docs for example.
                    if value["type"] != link_obj.get_entity_type():
                        raise EntityLinkTypeMismatch()

                # store it in our sg_data prefetch chunk
                tokens[link_obj.get_sg_data_key()] = value

        # now keep recursing upwards
        if self._parent is None:
            return tokens

        else:
            return self._parent.extract_shotgun_data_upwards(sg, tokens)
