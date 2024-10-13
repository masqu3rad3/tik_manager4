# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from ...util import login
from ...errors import TankError

from .entity import Entity
from .util import translate_filter_tokens


class UserWorkspace(Entity):
    """
    Represents a user workspace folder.

    A workspace folder is deferred by default and is typically created
    in a second pass, just before application startup.
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
        filters = metadata.get("filters", [])
        entity_filter = translate_filter_tokens(filters, parent, full_path)

        # validate
        if sg_name_expression is None:
            raise TankError("Missing name token in yml metadata file %s" % full_path)

        return UserWorkspace(
            tk, parent, full_path, metadata, sg_name_expression, entity_filter
        )

    def __init__(
        self, tk, parent, full_path, metadata, field_name_expression, entity_filter
    ):
        """
        constructor
        """

        # lazy setup: we defer the lookup of the current user until the folder node
        # is actually being utilized, see extract_shotgun_data_upwards() below
        self._user_initialized = False

        # user work spaces are always deferred so make sure to add a setting to the metadata
        # note: This should ideally be a parameter passed to the base class.
        metadata["defer_creation"] = True

        Entity.__init__(
            self,
            tk,
            parent,
            full_path,
            metadata,
            "HumanUser",
            field_name_expression,
            entity_filter,
            create_with_parent=True,
        )

    def create_folders(
        self, io_receiver, path, sg_data, is_primary, explicit_child_list, engine
    ):
        """
        Inherited and wrapps base class implementation
        """

        # first we need to check to see if folders should be created. if the
        # folder creation is deferred, for example, until a specific engine
        # is run.
        if not self._should_item_be_processed(engine, is_primary):
            return

        # wraps around the Entity.create_folders() method and adds
        # the current user to the filer query in case this has not already been done.
        # having this set up before the first call to create_folders rather than in the
        # constructor is partly for performance, but primarily so that a valid current user
        # isn't required unless you actually create a user sandbox folder. For example,
        # if you have a dedicated machine that creates higher level folders, this machine
        # shouldn't need to have a user id set up - only the artists that actually create
        # the user folders should need to.

        if not self._user_initialized:

            # this query confirms that there is a matching HumanUser in shotgun for the local login
            user = login.get_current_user(self._tk)

            if not user:
                msg = (
                    "Folder Creation Error: Could not find a HumanUser in PTR with login "
                    "matching the local login. Check that the local login corresponds to a "
                    "user in shotgun."
                )
                raise TankError(msg)

            user_filter = {"path": "id", "relation": "is", "values": [user["id"]]}
            self._filters["conditions"].append(user_filter)
            self._user_initialized = True

        return Entity.create_folders(
            self, io_receiver, path, sg_data, is_primary, explicit_child_list, engine
        )
